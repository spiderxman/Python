# -*- mode: python -*-

block_cipher = None


a = Analysis(['C:\\Tang\\Develop\\Python\\Image2Code\\Image2Code.py'],
             pathex=['C:\\Tang\\Develop\\Python\\Image2Code'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Image2Code',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
