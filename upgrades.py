import sys, os
# sys.path.append(os.path.dirname(__file__).join('.'))
print(sys.path)

from System import settings

from alembic.config import Config
from alembic import command

def run():
    a_cfg = Config(settings.PROJECT_ROOT_PATH + "/alembic.ini")
    command.current(a_cfg)
    command.history(a_cfg)
    command.upgrade(a_cfg, "head")

if __name__ == '__main__':
    sys.path.append(".")
    if sys.argv is not None and len(sys.argv) > 1:
        projectDir = sys.argv[1]
        sys.path.append(projectDir)

    # ensure assets folder exists
    if not os.path.exists(settings.PROJECT_ROOT_PATH + "/assets"):
        os.mkdir(settings.PROJECT_ROOT_PATH + "/assets")

    run()
