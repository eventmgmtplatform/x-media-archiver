#!/usr/bin/env bash
set -eu
test "${XMA_ALLOW_PUBLIC_TEST:-}" = YES || { echo 'public acceptance not authorized' >&2; exit 2; }
test -n "${XMA_AUTH_PROFILE:-}" || { echo 'Firefox profile is required' >&2; exit 2; }
target=${1:?target required}
repository=${2:?repository required}
shift 2
test -x .venv/bin/xma || { echo 'local xma executable is unavailable' >&2; exit 2; }
exec .venv/bin/xma download "$target" --repository "$repository" \
  --auth-browser firefox --auth-profile "$XMA_AUTH_PROFILE" \
  --quality best --max-scan 500 --discovery-timeout 30 --discovery-attempts 2 --json "$@"
