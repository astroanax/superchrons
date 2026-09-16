#!/usr/bin/env bash
# Pack an exact-revision archive (fix §7). The old repomix-output.xml snapshot
# is STALE (still holds the MPI-only launcher) and must NOT be used for audit.
# This script tars the working tree plus a manifest of the git revision and
# per-file sha256 checksums, so any audit can verify exactly what it reviews.
# Usage: bash tools/pack_snapshot.sh [output-dir]
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-.}"
REV="$(git rev-parse HEAD 2>/dev/null || echo NO_GIT)"
STAMP="$(date +%Y%m%d_%H%M%S)"
NAME="superchrons-${STAMP}-${REV:0:8}"
find . -type f -not -path "./.git/*" -exec sha256sum {} + | sort > "/tmp/${NAME}.sha256"
tar --exclude=.git -czf "$OUT/${NAME}.tar.gz" .
cp "/tmp/${NAME}.sha256" "$OUT/${NAME}.sha256"
echo "$REV" > "$OUT/${NAME}.revision"
echo "packed $OUT/${NAME}.tar.gz (+ .sha256, .revision)"
echo "NOTE: repomix-output.xml is deprecated; audit the archive above instead."
