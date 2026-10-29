# Exporta um .pptx para PDF pelo Microsoft PowerPoint (Windows).
# Uso: powershell -ExecutionPolicy Bypass -File export_pdf.ps1 arquivo.pptx [saida.pdf]
param([string]$In, [string]$Out)
$In = (Resolve-Path $In).Path
if (-not $Out) { $Out = [IO.Path]::ChangeExtension($In, ".pdf") }
$Out = [IO.Path]::GetFullPath($Out)
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($In, $true, $false, $false)  # somente leitura, sem janela
$pres.SaveAs($Out, 32)                                        # 32 = ppSaveAsPDF
$pres.Close()
$app.Quit()
Write-Output "PDF: $Out"
