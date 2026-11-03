#!/bin/bash
# Exporta um .pptx para PDF pelo Microsoft PowerPoint (Mac). Uso: ./export_pdf.sh arquivo.pptx [saida.pdf]
set -e
IN="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT="${2:-${IN%.pptx}.pdf}"
case "$OUT" in /*) ;; *) OUT="$(pwd)/$OUT" ;; esac

# Só mexe na cópia temporária, pelo nome único dela. Nunca use "active presentation": o usuário pode estar com outro
# deck aberto, e ele seria exportado no lugar deste e fechado sem salvar.
export_once() {
  local nome; nome="$(basename "$1")"
  osascript -e "tell application \"Microsoft PowerPoint\"
    open POSIX file \"$1\"
    repeat 60 times
      if exists presentation \"$nome\" then exit repeat
      delay 0.5
    end repeat
    save presentation \"$nome\" in POSIX file \"$2\" as save as PDF
    close presentation \"$nome\" saving no
  end tell" >/dev/null
}

# Arquivo inválido trava o PowerPoint para todos: recusa antes de abrir.
if command -v python3 >/dev/null && ! python3 "$(dirname "$0")/validar_pptx.py" "$IN"; then
  echo "Arquivo inválido: corrija antes de exportar." >&2
  exit 4
fi

# Um PowerPoint só: vários agentes exportando juntos travam o app (erro -9074). Fila por pasta de trava.
LOCK="/tmp/slide-studio-ppt.lock"
n=0
until mkdir "$LOCK" 2>/dev/null; do
  sleep 3; n=$((n+1))
  # trava esquecida por um processo morto: libera depois de 5 minutos
  if [ $n -gt 100 ]; then rmdir "$LOCK" 2>/dev/null; n=0; fi
done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

# PowerPoint fechado (erro -600): abrir e esperar
if ! pgrep -xq "Microsoft PowerPoint"; then open -a "Microsoft PowerPoint"; sleep 8; fi

# Sempre por uma cópia AO LADO do arquivo (o PowerPoint não alcança /tmp), com nome que ninguém mais tem aberto
TMP="$(dirname "$IN")/.export_tmp_$$"; mkdir -p "$TMP"
trap 'rm -rf "${TMP:?}"; rmdir "$LOCK" 2>/dev/null' EXIT
ALVO="slidestudio_export_$$.pptx"
cp "$IN" "$TMP/$ALVO"
if ! export_once "$TMP/$ALVO" "$TMP/saida.pdf"; then
  echo "O PowerPoint recusou a exportação. Causa provável: um arquivo anterior o deixou parado em aviso de reparo. Não repita: peça ao usuário para fechar o aviso ou reiniciar o PowerPoint, e rode scripts/validar_pptx.py no arquivo." >&2
  exit 3
fi
mv "$TMP/saida.pdf" "$OUT"
echo "PDF: $OUT"
