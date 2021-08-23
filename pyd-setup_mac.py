from Cython.Build import cythonize
from distutils.core import setup
from distutils.command.build_ext import build_ext as BuildExt
import os


#from distutils import sysconfig
#vars = sysconfig.get_config_vars()
#print(" ***** LDSHARED: " + vars['LDSHARED'])
#vars['LDSHARED'] = vars['LDSHARED'].replace('-bundle', '-dynamiclib')
#vars['LDSHARED'] = vars['LDSHARED'].replace('-bundle', '')
#print(" ***** LDSHARED: " + vars['LDSHARED'])


'''
cythonize and strip command example

# .py file to .c file
cython ValueId.py -3
cython ValueIdEnum.py -3
cython test_upx.py -3 --embed

# clang, compile .c file to .o file
/usr/bin/clang -fno-strict-aliasing -Wsign-compare -fno-common -dynamic -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes -g -arch x86_64 -I/Users/dev/workspace_PPP/Personal/venv/include -I/Library/Frameworks/Python.framework/Versions/3.6/include/python3.6m -c ValueId.c -o ValueId.o

# clang, link .o file to .so shared object
/usr/bin/clang -bundle -undefined dynamic_lookup -g -arch x86_64 ValueId.o -o ValueId.cpython-36m-darwin.so

# example to executable formate
# /usr/bin/clang -undefined dynamic_lookup -g -arch x86_64 ValueId.o -o ValueId.cpython-36m-darwin.so
# example to dynamic library formate
# /usr/bin/clang -dynamiclib -undefined dynamic_lookup -g -arch x86_64 ValueId.o -o ValueId.cpython-36m-darwin.so

# clang, compile .c file to executable
/usr/bin/clang -Os -I/Library/Frameworks/Python.framework/Versions/3.6/include/python3.6m -L/Library/Frameworks/Python.framework/Versions/3.6/lib -lpython3.6m -o test_upx.out test_upx.c

# strip symbols
strip -ur ValueId.cpython-36m-darwin.so

# check symbol table
nm -an ValueId.cpython-36m-darwin.so
# or
objdump -t ValueId.cpython-36m-darwin.so
 
'''

class MyBuildExt(BuildExt):

    def do_pre_install_stuff(self):
        pass

    def run(self):
        self.do_pre_install_stuff()
        BuildExt.run(self)
        self.do_strip_symbols()
        # upx did not support macho file well. The details as function comments below.
        #self.do_upx_compress()
        self.do_post_install_stuff()

    def do_post_install_stuff(self):
        for ext in self.extensions:
            print(ext.name)
            print(ext.sources)
            os.remove(ext.sources[0])

    def do_strip_symbols(self):
        from System import settings
        count = 0
        root = os.path.abspath(self.build_lib)
        cmd_cd = "cd \"{path}\"".format(path=settings.PROJECT_ROOT_PATH)

        print("do cmd: " + cmd_cd)
        print("result: " + str(os.system(cmd_cd)))

        for path, subdirs, files in os.walk(root):
            for name in files:
                if name.endswith(".so"):
                    count += 1
                    filePath = os.path.join(path, name)
                    cmd_strip = "strip -ur \"{path}\"".format(path=filePath)

                    print(str(count) + ".do cmd: " + str(cmd_strip))
                    print("result: " + str(os.system(cmd_strip)))

    # upx did not support macho file well, it caused header corrupted, then could not be load when execution.
    # upx 3.95 and the latest dev commit 8aadbcd7(Sun Mar 3 14:27:33 2019) both cannot deal with macho file well.
    '''def do_upx_compress(self):
        from System import settings
        count = 0
        root = os.path.abspath(self.build_lib)
        cmd_cd = "cd {path}".format(path=settings.PROJECT_ROOT_PATH)

        print("do cmd: " + cmd_cd)
        print("result: " + str(os.system(cmd_cd)))

        for path, subdirs, files in os.walk(root):
            for name in files:
                if name.endswith(".so"):
                    count += 1
                    filePath = os.path.join(path, name)
                    cmd_upx = "upx {path}".format(path=filePath)

                    print(str(count) + ".do cmd: " + str(cmd_upx))
                    print("result: " + str(os.system(cmd_upx)))
    '''

options = {
        'build_ext': {
            'inplace':0
        }
    }

setup(name='PowerPanel Personal',
        version='0.1',
        description='',
        options=options,
        cmdclass={'build_ext': MyBuildExt},
        ext_modules = cythonize(["System/*.py",
                                 "controllers/*.py",
                                 "model_Json/*.py",
                                 "ClientModel/*.py",
                                 "handler_refactor/*.py",
                                 "ClientHandler/*.py",
                                 "Utility/*.py",
                                 "Events/*.py",
                                 "major/*.py",
                                 "Daemon.py",
                                 ],
                                 exclude=["System/__init__.py","controllers/__init__.py","major/__init__.py","ClientHandler/__init__.py","ClientModel/__init__.py","model_Json/__init__.py","handler_refactor/__init__.py","Utility/__init__.py","Events/__init__.py"],
                                 compiler_directives={'language_level': '3'}
        )
    )
