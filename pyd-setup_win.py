from Cython.Build import cythonize
from distutils.core import setup
from distutils.command.build_ext import build_ext as BuildExt
import os

class MyBuildExt(BuildExt):

    def do_pre_install_stuff(self):
        pass

    def run(self):
        self.do_pre_install_stuff()
        BuildExt.run(self)
        self.do_upx_compress()
        self.do_post_install_stuff()

    def do_post_install_stuff(self):
        for ext in self.extensions:
            print(ext.name)
            print(ext.sources)
            print("2")
            os.remove(ext.sources[0])

    def do_upx_compress(self):

        from System import settings
        count = 0
        root = os.path.abspath(self.build_lib)
        cmd1 = '"{replace}"'
        cmd1 = "cd " + cmd1.format(replace=settings.PROJECT_ROOT_PATH)

        print("do cmd: " + cmd1)
        print(os.system(cmd1))

        for path, subdirs, files in os.walk(root):
            for name in files:
                if name.endswith(".pyd"):
                    count += 1
                    filePath = os.path.join(path, name)
                    tempCmd = '"{replace}"'
                    tempCmd = tempCmd.format(replace=filePath)
                    cmd = "upx.exe " + tempCmd

                    print(str(count) + ".do cmd: " + str(cmd))
                    print(os.system(cmd))

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
        # ext_modules = cythonize(["controllers/DeviceMonitor.py",
        #                         "ValueId.py",
        #                         "DBSession.py",
        #                         "systemDefine.py",
        #                         "systemFunction.py"])
        ext_modules = cythonize(["System/*.py",
                                 # "ValueId.py",
                                 # "systemDefine.py",
                                 # "systemFunction.py",
                                 # "signalMapper.py",
                                 # "DBSession.py",
                                 "controllers/*.py",
                                 "model_Json/*.py",
                                 "ClientModel/*.py",
                                 "handler_refactor/*.py",
                                 "ClientHandler/*.py",
                                 "Utility/*.py",
                                 "Events/*.py",
                                 "major/*.py",
                                 "Daemon.py"
                                 ],
                                 exclude=["System/__init__.py","controllers/__init__.py","major/__init__.py","ClientHandler/__init__.py","ClientModel/__init__.py","model_Json/__init__.py","handler_refactor/__init__.py","Utility/__init__.py","Events/__init__.py"],
                                 compiler_directives={'language_level': '3'}
        )
    )