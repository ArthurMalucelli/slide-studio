# Exporta um .pptx para PDF pelo Microsoft PowerPoint (Windows).
# Uso: powershell -ExecutionPolicy Bypass -File export_pdf.ps1 arquivo.pptx [saida.pdf]
# Saída: 0 = PDF pronto. 3 = o PowerPoint não exportou. 4 = arquivo inválido, nem chegou a abrir.
param([string]$In, [string]$Out)
$ErrorActionPreference = 'Stop'

$In = (Resolve-Path -LiteralPath $In).Path
if (-not $Out) { $Out = [IO.Path]::ChangeExtension($In, '.pdf') }
$Out = [IO.Path]::GetFullPath($Out)

# Arquivo inválido trava o PowerPoint para todos: recusa antes de abrir. `python3` pode ser o atalho da loja do Windows,
# que existe e não roda nada: só vale o que responde.
$python = $null
foreach ($name in 'python3', 'python') {
  $found = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) {
    & $found.Source --version *> $null
    if ($LASTEXITCODE -eq 0) { $python = $found.Source; break }
  }
}
if ($python) {
  & $python (Join-Path $PSScriptRoot 'validar_pptx.py') $In
  if ($LASTEXITCODE -ne 0) {
    [Console]::Error.WriteLine('Arquivo invalido: corrija antes de exportar.')
    exit 4
  }
}

# Um PowerPoint só: vários agentes exportando juntos travam o app. A trava morre com o processo, sem sobrar.
$lock = New-Object System.Threading.Mutex($false, 'Global\slide-studio-ppt')
try {
  [void]$lock.WaitOne()
} catch [System.Threading.AbandonedMutexException] {
  # Quem segurava morreu: a trava agora é nossa.
}

# Sempre por uma cópia ao lado do arquivo, com nome que ninguém mais tem aberto.
$tmp = Join-Path (Split-Path -LiteralPath $In) ".export_tmp_$PID"
$app = $null
$pres = $null
$code = 0
try {
  New-Item -ItemType Directory -Path $tmp -Force | Out-Null
  $copy = Join-Path $tmp "slidestudio_export_$PID.pptx"
  $pdf = Join-Path $tmp 'saida.pdf'
  Copy-Item -LiteralPath $In -Destination $copy

  # O COM se liga ao PowerPoint que já estiver aberto, com o trabalho do usuário. Por isso só se mexe no objeto da própria
  # cópia, sem "active presentation" nem índice, e nunca se chama $app.Quit(): ele fecharia o PowerPoint inteiro.
  $app = New-Object -ComObject PowerPoint.Application
  $pres = $app.Presentations.Open($copy, $true, $false, $false)  # somente leitura, sem janela
  $pres.SaveAs($pdf, 32)                                         # 32 = ppSaveAsPDF
  Move-Item -LiteralPath $pdf -Destination $Out -Force
  Write-Output "PDF: $Out"
} catch {
  [Console]::Error.WriteLine("O PowerPoint recusou a exportacao: $($_.Exception.Message)")
  $code = 3
} finally {
  # Solta as referências em vez de sair do app: um PowerPoint que só existia por causa desta exportação fecha sozinho.
  if ($pres) {
    try { $pres.Close() } catch { }
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($pres)
  }
  if ($app) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app) }
  Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
  $lock.ReleaseMutex()
  $lock.Dispose()
}
exit $code
