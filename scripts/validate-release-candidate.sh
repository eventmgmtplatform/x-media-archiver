#!/usr/bin/env bash
set -euo pipefail

artifact_dir=${1:-release-artifacts}
test_dir=$(mktemp -d -t xma-rc-validate.XXXXXX)
trap 'rm -rf -- "$test_dir"' EXIT

(cd "$artifact_dir" && sha256sum -c SHA256SUMS)
uv run python scripts/generate-release-manifest.py --validate "$artifact_dir"
tar -C "$test_dir" -xzf "$artifact_dir/xma-v0.2.0-linux-x86_64.tar.gz"
binary="$test_dir/xma-v0.2.0-linux-x86_64/xma"

echo "validate: xma --help"
env -i PATH=/usr/bin:/bin HOME="$test_dir" "$binary" --help >/dev/null
echo "validate: xma version"
env -i PATH=/usr/bin:/bin HOME="$test_dir" "$binary" version --short | grep -Fx 0.2.0
for command in inspect sync download archive status; do
  echo "validate: xma $command --help"
  env -i PATH=/usr/bin:/bin HOME="$test_dir" "$binary" "$command" --help >/dev/null
done

test -f "$artifact_dir/sbom.cdx.json"
test -f "$artifact_dir/THIRD_PARTY_NOTICES.md"
test -f "$artifact_dir/RELEASE-MANIFEST.json"
test -f "$artifact_dir/gallery_dl-1.32.18.tar.gz"
printf '%s  %s\n' \
  1c5562af3799a0bec96be0f64d95a416aee688fd09fe3893ca3a6c87bbe65bcd \
  "$artifact_dir/gallery_dl-1.32.18.tar.gz" | sha256sum -c -
test -f "$test_dir/xma-v0.2.0-linux-x86_64/LICENSE"
test -f "$test_dir/xma-v0.2.0-linux-x86_64/README.md"
test -f "$test_dir/xma-v0.2.0-linux-x86_64/THIRD_PARTY_NOTICES.md"
test -f "$test_dir/xma-v0.2.0-linux-x86_64/QUICKSTART.md"
test -f "$test_dir/xma-v0.2.0-linux-x86_64/docs/operations/XMA-CLI-001_BAU-OPERATIONS_v1.0.0.md"
test -f "$test_dir/xma-v0.2.0-linux-x86_64/docs/operations/XMA-CLI-001_LOCAL-CLI-RUNBOOK_v0.1.0.md"
grep -Fq 'GNU GENERAL PUBLIC LICENSE' "$test_dir/xma-v0.2.0-linux-x86_64/LICENSE"
grep -Fq 'END OF TERMS AND CONDITIONS' "$test_dir/xma-v0.2.0-linux-x86_64/LICENSE"
unzip -p "$artifact_dir/x_media_archiver-0.2.0-py3-none-any.whl" \
  '*/licenses/LICENSE' > "$test_dir/wheel-LICENSE"
tar -xOf "$artifact_dir/x_media_archiver-0.2.0.tar.gz" \
  x_media_archiver-0.2.0/LICENSE > "$test_dir/sdist-LICENSE"
cmp LICENSE "$test_dir/wheel-LICENSE"
cmp LICENSE "$test_dir/sdist-LICENSE"
