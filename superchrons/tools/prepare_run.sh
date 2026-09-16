#!/usr/bin/env bash
# Create one self-contained run directory (review round 2 §7).
# Stages: binary + input + flux maps + manifest copy + env record, so the
# launch directory never depends on the submission cwd containing the repo.
# Also resolves the restart-flag agreement BEFORE submission: --restart
# requires the par file to set restart=1, --fresh requires restart=0.
# Usage: prepare_run.sh --case W02 --par xshells.par.W02 --map cmb_Y21.txt
#          --binary ~/superchrons/build-bench/xsbig_hyb --manifest MANIFEST.md
#          [--restart|--fresh] [--outdir runs/W02]
set -euo pipefail
CASE=""; PAR=""; MAPS=""; BINARY=""; MANIFEST=""; MODE="--fresh"; OUTDIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --case) CASE="$2"; shift 2;;
    --par) PAR="$2"; shift 2;;
    --map) MAPS="$MAPS $2"; shift 2;;
    --binary) BINARY="$2"; shift 2;;
    --manifest) MANIFEST="$2"; shift 2;;
    --restart|--fresh) MODE="$1"; shift;;
    --outdir) OUTDIR="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done
[[ -n "$CASE" && -n "$PAR" && -n "$BINARY" && -n "$MANIFEST" && -n "$OUTDIR" ]] \
  || { echo "usage: prepare_run.sh --case C --par P [--map M]... --binary B --manifest M [--restart|--fresh] --outdir D" >&2; exit 2; }
[[ -f "$PAR" && -x "$BINARY" && -f "$MANIFEST" ]] \
  || { echo "REFUSED: par/binary/manifest missing" >&2; exit 2; }
RST="$(grep -E '^\s*restart\s*=' "$PAR" | tail -1 | sed 's/.*=\s*//;s/\s//g')"
if [[ "$MODE" == "--restart" && "$RST" != "1" ]]; then
  echo "REFUSED: --restart but par sets restart=$RST" >&2; exit 2
fi
if [[ "$MODE" == "--fresh" && "$RST" != "0" ]]; then
  echo "REFUSED: --fresh but par sets restart=$RST" >&2; exit 2
fi
if [[ -e "$OUTDIR" && "$MODE" == "--fresh" && -n "$(ls -A "$OUTDIR")" ]]; then
  echo "REFUSED: fresh run but $OUTDIR non-empty" >&2; exit 2
fi
mkdir -p "$OUTDIR"
cp "$PAR" "$OUTDIR/xshells.par"
cp "$BINARY" "$OUTDIR/xsbig_hyb"
cp "$MANIFEST" "$OUTDIR/MANIFEST.md"
for m in $MAPS; do cp "$m" "$OUTDIR/"; done
{
  echo "case: $CASE"; echo "mode: $MODE"; echo "prepared: $(date -u +%FT%TZ)"
  sha256sum "$OUTDIR/xshells.par" "$OUTDIR/xsbig_hyb"
} > "$OUTDIR/PREP_RECORD"
cat > "$OUTDIR/env.sh" << 'EOF'
# Runtime environment: must match the recorded build (review round 2 §7).
module load gnu8/8.3.0 openmpi3/3.1.4 2>/dev/null || module load gnu8 openmpi3
export LD_LIBRARY_PATH=/opt/apps/oneapi-mkl/2025.0.1/lib/intel64:${LD_LIBRARY_PATH:-}
export OMP_PLACES=cores
export OMP_PROC_BIND=close
EOF
echo "PREPARED $OUTDIR (mode $MODE)"
