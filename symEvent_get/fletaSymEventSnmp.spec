# -*- mode: python -*-

w=Tree('C:/Python27/Lib/site-packages/pysnmp',prefix='pysnmp',excludes='.py')
y=Tree('C:/Python27/Lib/site-packages/pysnmp/smi',prefix='pysnmp/smi',excludes='.py')
x=Tree('C:/Python27/Lib/site-packages/pysnmp/smi/mibs',prefix='pysnmp/smi/mibs',excludes='.py')

block_cipher = None


a = Analysis(['fletaSymEventSnmp.py'],
             pathex=['C:\Fleta\eclipse-workspace\symEvent_snmp_v8'],
             binaries=None,
             datas=None,
             hiddenimports=['_cffi_backend', 'pysnmp.smi.exval', 'pysnmp.cache', 'pysnmp.smi.mibs', 'pysnmp.smi.mibs.instances'],
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
		  w,
		  x,
		  y,
          name='fletaSymEventSnmp',
          debug=False,
          strip=False,
          upx=True,
          console=True )
