#!/usr/bin/env bash
set -euo pipefail

root_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root_dir"
export SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH:-1793246400}

artifact_dir=${1:-release-artifacts}
work_dir=$(mktemp -d -t xma-rc-build.XXXXXX)
trap 'rm -rf -- "$work_dir"' EXIT
gallery_source=gallery_dl-1.32.18.tar.gz
gallery_source_url=https://files.pythonhosted.org/packages/ec/55/e40b8ce403489e7b3122eee28693efd885ca68256a9c6344fdfbd0842c3e/gallery_dl-1.32.18.tar.gz
gallery_source_sha256=1c5562af3799a0bec96be0f64d95a416aee688fd09fe3893ca3a6c87bbe65bcd

rm -rf -- "$artifact_dir"
mkdir -p "$artifact_dir"

uv build --out-dir "$artifact_dir"
uv run pyinstaller --clean --noconfirm --distpath "$work_dir/dist" \
  --workpath "$work_dir/work" packaging/xma.spec
cp LICENSE README.md THIRD_PARTY_NOTICES.md QUICKSTART.md \
  "$work_dir/dist/xma-v0.1.2-linux-x86_64/"
mkdir -p "$work_dir/dist/xma-v0.1.2-linux-x86_64/docs/operations"
cp docs/operations/XMA-CLI-001_BAU-OPERATIONS_v1.0.0.md \
  docs/operations/XMA-CLI-001_LOCAL-CLI-RUNBOOK_v0.1.0.md \
  "$work_dir/dist/xma-v0.1.2-linux-x86_64/docs/operations/"

tar --sort=name --mtime="@$SOURCE_DATE_EPOCH" --owner=0 --group=0 --numeric-owner \
  -C "$work_dir/dist" -czf "$artifact_dir/xma-v0.1.2-linux-x86_64.tar.gz" \
  xma-v0.1.2-linux-x86_64

uv export --locked --no-dev --no-emit-project --no-header --format requirements.txt \
  --output-file "$artifact_dir/requirements-linux-x86_64.txt"
uv run cyclonedx-py requirements "$artifact_dir/requirements-linux-x86_64.txt" \
  --output-reproducible --output-file "$artifact_dir/sbom.cdx.json"
cp LICENSE THIRD_PARTY_NOTICES.md "$artifact_dir/"
curl --fail --location --silent --show-error "$gallery_source_url" \
  --output "$artifact_dir/$gallery_source"
printf '%s  %s\n' "$gallery_source_sha256" "$artifact_dir/$gallery_source" | sha256sum -c -

uv run python scripts/generate-release-manifest.py "$artifact_dir"
(
  cd "$artifact_dir"
  sha256sum LICENSE RELEASE-MANIFEST.json THIRD_PARTY_NOTICES.md \
    "$gallery_source" requirements-linux-x86_64.txt sbom.cdx.json \
    x_media_archiver-0.1.2-py3-none-any.whl x_media_archiver-0.1.2.tar.gz \
    xma-v0.1.2-linux-x86_64.tar.gz > SHA256SUMS
)
