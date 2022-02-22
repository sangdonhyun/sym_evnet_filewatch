from distutils.core import setup
import py2exe



import sys,os

origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
        if os.path.basename(pathname).lower() in ("msvcp71.dll", "dwmapi.dll"):
                return 0
        return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL

sys.argv.append('py2exe')
includes = ['_json']
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter']
packages = []
dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl84.dll',
                'tk84.dll', 'MSVCP90.dll', 'MSVCR80.dll'
                 ,"api-ms-win-core-delayload-l1-1-1.dll"
                ,"api-ms-win-core-rtlsupport-l1-2-0.dll"
                ,"api-ms-win-core-localization-obsolete-l1-3-0.dll"
                ,"api-ms-win-security-activedirectoryclient-l1-1-0.dll"
                ,"api-ms-win-core-string-obsolete-l1-1-0.dll"
                ,"api-ms-win-core-string-l1-1-0.dll"
                ,"api-ms-win-core-registry-l1-1-0.dll"
                ,"api-ms-win-core-errorhandling-l1-1-1.dll"
                ,"api-ms-win-core-string-l2-1-0.dll"
                ,"api-ms-win-core-profile-l1-1-0.dll"
                ,"api-ms-win-core-processthreads-l1-1-2.dll"
                ,"api-ms-win-core-libraryloader-l1-2-1.dll"
                ,"api-ms-win-core-file-l1-2-1.dll"
                ,"api-ms-win-security-base-l1-2-0.dll"
                ,"api-ms-win-eventing-provider-l1-1-0.dll"
                ,"api-ms-win-core-heap-l2-1-0.dll"
                ,"api-ms-win-core-libraryloader-l1-2-0.dll"
                ,"api-ms-win-core-localization-l1-2-1.dll"
                ,"api-ms-win-core-sysinfo-l1-2-1.dll"
                ,"api-ms-win-core-synch-l1-2-0.dll"
                ,"api-ms-win-core-heap-l1-2-0.dll"
                ,"api-ms-win-core-handle-l1-1-0.dll"
                ,"api-ms-win-core-io-l1-1-1.dll"
                ,"api-ms-win-core-com-l1-1-1.dll"
                ,"api-ms-win-core-memory-l1-1-2.dll"
                ,"api-ms-win-core-version-l1-1-1.dll"
                ,"api-ms-win-core-version-l1-1-0.dll"
                ]

data_files = [('config','list.cfg'),('config','config.cfg')]
try:
        setup(
            options = {'py2exe': {"compressed": 2,
                          "optimize": 2,
                          "includes": includes,
                          "excludes": excludes,
                          "packages": packages,
                          "dll_excludes": dll_excludes,
                          "bundle_files": 3,
                          "dist_dir": "dist",
                          "xref": False,
                          "skip_archive": False,
                          "ascii": False,
                          "custom_boot_script": '',
                         }}, 
            console=['fletaFileWatch.py'], 
            zipfile = 'lib\library.zip',
            )
except Exception, e:
    print (e)
    
    
    




#from __future__ import with_statement
#from contextlib import closing
#from zipfile import ZipFile, ZIP_DEFLATED
#import os
#
#def zipdir(basedir, archivename):
#    assert os.path.isdir(basedir)
#    with closing(ZipFile(archivename, "w", ZIP_DEFLATED)) as z:
#        for root, dirs, files in os.walk(basedir):
#            #NOTE: ignore empty directories
#            for fn in files:
#                absfn = os.path.join(root, fn)
#                zfn = absfn[len(basedir)+len(os.sep):] #XXX: relative path
#                z.write(absfn, zfn)
#                
#
#basedir = os.path.join(os.getcwd(),'dist')
#archivename = os.getcwd().split('\\')[-1]+'.zip'
#print basedir
#print archivename
#zipdir(basedir, archivename)             