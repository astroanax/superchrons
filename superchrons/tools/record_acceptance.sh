#!/usr/bin/env bash
# Record an acceptance-test result with the PASS-marker convention that
# slurm/preflight.py enforces (review round 2 §1): the log MUST contain a
# line "RESULT: PASS <test-name>". A log without the marker is not an
# acceptance, however detailed. Usage:
#   record_acceptance.sh <logfile> PASS|FAIL <test-name> [detail...]
set -euo pipefail
LOG="${1:?logfile}"; VERDICT="${2:?PASS|FAIL}"; TEST="${3:?test-name}"
shift 3
{
  echo "date: $(date -u +%FT%TZ)"
  echo "test: $TEST"
  echo "RESULT: $VERDICT $TEST"
  for d in "$@"; do echo "detail: $d"; done
} >> "$LOG"
echo "recorded $VERDICT $TEST -> $LOG"
