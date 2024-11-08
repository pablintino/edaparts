import os.path

from alembic import command
from alembic.config import Config

ALEMBIC_CFG = Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))


def current(verbose=False):
    command.current(ALEMBIC_CFG, verbose=verbose)


def upgrade(revision="head"):
    command.upgrade(ALEMBIC_CFG, revision)


def downgrade(revision):
    command.downgrade(ALEMBIC_CFG, revision)
