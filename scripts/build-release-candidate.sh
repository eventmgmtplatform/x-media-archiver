#!/usr/bin/env bash
set -euo pipefail

root_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root_dir"
export SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH:-1793246400}

artifact_dir=${1:-release-artifacts}
work_dir=$(mktemp -d -t xma-rc-build.XXXXXX)
trap 'rm -rf -- "$work_dir"' EXIT

rm -rf -- "$artifact_dir"
mkdir -p "$artifact_dir"

uv build --out-dir "$artifact_dir"
uv run pyinstaller --clean --noconfirm --distpath "$work_dir/dist" \
  --workpath "$work_dir/work" packaging/xma.spec
cp LICENSE THIRD_PARTY_NOTICES.md QUICKSTART.md \
  "$work_dir/dist/xma-v0.1.0-linux-x86_64/"

tar --sort=name --mtime="@$SOURCE_DATE_EPOCH" --owner=0 --group=0 --numeric-owner \
  -C "$work_dir/dist" -czf "$artifact_dir/xma-v0.1.0-linux-x86_64.tar.gz" \
  xma-v0.1.0-linux-x86_64

uv export --locked --no-dev --no-emit-project --no-header --format requirements.txt \
  --output-file "$artifact_dir/requirements-linux-x86_64.txt"
uv run cyclonedx-py requirements "$artifact_dir/requirements-linux-x86_64.txt" \
  --output-reproducible --output-file "$artifact_dir/sbom.cdx.json"
cp LICENSE THIRD_PARTY_NOTICES.md "$artifact_dir/"
(
  cd "$artifact_dir"
  sha256sum xma-v0.1.0-linux-x86_64.tar.gz \
    x_media_archiver-0.1.0-py3-none-any.whl \
    x_media_archiver-0.1.0.tar.gz \
    requirements-linux-x86_64.txt sbom.cdx.json THIRD_PARTY_NOTICES.md > SHA256SUMS
)
