# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
import click
from scistash.repl.loop import ReplHandler


@click.command()
@click.argument('db', nargs=1)
@click.option('--dryrun', default=False, help='Perform all operations in memory without altering the database.')
@click.option('--create', default=False, help='Create a new database from scratch.')
def main(db, dryrun, create):
    rh = ReplHandler(db, dryrun, create)
    rh.run()


if __name__ == "__main__":
    main()
