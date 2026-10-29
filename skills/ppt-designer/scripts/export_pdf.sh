#!/bin/bash
# Exporta um .pptx para PDF pelo Microsoft PowerPoint (Mac). Uso: ./export_pdf.sh arquivo.pptx [saida.pdf]
set -e
IN="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT="${2:-${IN%.pptx}.pdf}"
case "$OUT" in /*) ;; *) OUT="$(pwd)/$OUT" ;; esac

export_once() {
  osascript -e "tell application \"Microsoft PowerPoint\"
    open POSIX file \"$1\"
    save active presentation in POSIX file \"$2\" as save as PDF
    close active presentation saving no
  end tell" >/dev/null
}

# PowerPoint fechado (erro -600): abrir e esperar
if ! pgrep -xq "Microsoft PowerPoint"; then open -a "Microsoft PowerPoint"; sleep 8; fi

if ! export_once "$IN" "$OUT"; then
  # erro -50 do PowerPoint: exportar por uma cópia temporária AO LADO do arquivo (o PowerPoint não alcança /tmp)
  TMP="$(dirname "$IN")/.export_tmp_$$"; mkdir -p "$TMP"
  cp "$IN" "$TMP/tmp.pptx"
  export_once "$TMP/tmp.pptx" "$TMP/tmp.pdf"
  mv "$TMP/tmp.pdf" "$OUT"
  rm -r "${TMP:?}"
fi
echo "PDF: $OUT"
