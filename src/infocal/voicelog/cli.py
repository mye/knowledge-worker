import sys

import click
import sqlite_utils

from infocal import voicelog_sqlite


@click.command()
@click.argument(
    "database",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
def cli(database):
    "Store timestamped voice transcripts in a SQLite database."
    db = sqlite_utils.Database(database)
    voicelog_sqlite(sys.stdin, db.conn)  # type: ignore
    db.close()
