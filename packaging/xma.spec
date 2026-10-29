# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from pathlib import Path

gallery_datas, gallery_binaries, gallery_hiddenimports = collect_all("gallery_dl")
root = Path(SPECPATH).parent

a = Analysis(
    [str(root / "src/xma/__main__.py")],
    pathex=[str(root)],
    binaries=gallery_binaries,
    datas=gallery_datas + [
        (str(root / "src/xma/adapters/catalog/schema"), "xma/adapters/catalog/schema"),
        (str(root / "LICENSE"), "."),
        (str(root / "README.md"), "."),
        (str(root / "THIRD_PARTY_NOTICES.md"), "."),
        (str(root / "QUICKSTART.md"), "."),
        (str(root / "docs/operations/XMA-CLI-001_BAU-OPERATIONS_v1.0.0.md"), "docs/operations"),
        (str(root / "docs/operations/XMA-CLI-001_LOCAL-CLI-RUNBOOK_v0.1.0.md"), "docs/operations"),
    ],
    hiddenimports=gallery_hiddenimports,
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="xma", console=True)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="xma-v0.1.0-linux-x86_64")
