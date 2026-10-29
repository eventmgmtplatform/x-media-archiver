#!/usr/bin/env bash
set -euo pipefail

artifact_dir=${1:-release-artifacts}
test_dir=$(mktemp -d -t xma-rc-validate.XXXXXX)
trap 'rm -rf -- "$test_dir"' EXIT

(cd "$artifact_dir" && sha256sum -c SHA256SUMS)
tar -C "$test_dir" -xzf "$artifact_dir/xma-v0.1.0-linux-x86_64.tar.gz"
binary="$test_dir/xma-v0.1.0-linux-x86_64/xma"

echo "validate: xma --help"
env -i PATH=/usr/bin:/bin HOME="$test_dir" "$binary" --help >/dev/null
echo "validate: xma version"
env -i PATH=/usr/bin:/bin HOME="$test_dir" "$binary" version --short | grep -Fx 0.1.0
for command in inspect sync download archive status; do
  echo "validate: xma $command --help"
  env -i PATH=/usr/bin:/bin HOME="$test_dir" "$binary" "$command" --help >/dev/null
done

test -f "$artifact_dir/sbom.cdx.json"
test -f "$artifact_dir/THIRD_PARTY_NOTICES.md"
test -f "$test_dir/xma-v0.1.0-linux-x86_64/LICENSE"
