# 1. Analysis - アプリケーションの分析と依存関係の収集
# 2. PYZ - Pythonモジュールのアーカイブ作成
# 3. EXE - 実行ファイルの生成

import sys
from pathlib import Path

a = Analysis(
    ['main.py'],        # エントリーポイント（起動するPythonファイル名）
    pathex=['.'],       # 追加の検索パス
    binaries=[],        # 追加のバイナリファイル
    datas=[             # 追加のデータファイル
        # ('I:/workspace/01_dev/01_web_apps/2024-11-27/2024-11-27_ダッシュボード/.venv/Lib/site-packages/flet', 'flet/'),
        # ('I:/workspace/01_dev/01_web_apps/2024-11-27/2024-11-27_ダッシュボード/.venv/Lib/site-packages/pandas', 'pandas/')
    ],  
    hiddenimports=[],   # 明示的に含めるモジュール
    hookspath=[], 
    hooksconfig={},
    runtime_hooks=[], 
    excludes=[],        # 除外するモジュール
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)    # Pythonモジュールを圧縮してアーカイブ化

exe = EXE(
    pyz,                            # 圧縮されたPythonモジュール
    a.scripts,                      # スクリプトファイル
    a.binaries,                     # バイナリファイル
    a.zipfiles,                     # 圧縮ファイル
    a.datas,                        # データファイル
    [],                             # 追加のオプションが必要な場合はここに記述
    name='your_app_name',           # 生成される実行ファイル名（カスタマイズしてください）
    debug=False,                    # デバッグモードを無効化
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[], 
    runtime_tmpdir=None,
    console=False,                   # コンソールウィンドウを非表示
)