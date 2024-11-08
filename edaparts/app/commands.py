import click
from edaparts.migrations import migrations


@click.command()
@click.option("-v", "--verbose", is_flag=True, default=False, help="Verbose mode")
def db_current_cmd(verbose):
    migrations.current(verbose)


@click.command()
@click.option("-r", "--revision", default="head", help="Revision target")
def db_upgrade_cmd(revision):
    migrations.upgrade(revision)


@click.command()
@click.option("-r", "--revision", required=True, help="Revision target")
def db_downgrade_cmd(revision):
    migrations.downgrade(revision)
