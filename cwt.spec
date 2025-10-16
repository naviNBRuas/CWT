# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['CWT_CLI/main.py'],
             pathex=['.'],
             binaries=[],
             datas=[
                 ('CWT_CLI/**/*.py', 'CWT_CLI/'),
                 ('CWT_CLI/config.ini', 'CWT_CLI/'),
                 ('requirements.txt', '.'),
                 ('run.sh', '.'),
                 ('CWT_CLI/exchange_automators/*.py', 'CWT_CLI/exchange_automators/'),
                 ('CWT_CLI/nft_manager.py', 'CWT_CLI/'),
             ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='cwt',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_info=None,
          console=True,
            disable_windowed_traceback=False,
            argv_emulation=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None )
