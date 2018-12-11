# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
from scistash.entities.author import Author
from scistash.entities.article import Article
from scistash.entities.annotation import Annotation
from scistash.entities.tag import Tag
from scistash.entities.rfile import RefFile
from scistash.entities.reference import Reference
from sqlite3 import Error
import sqlite3
import pathlib
import click
import uuid


class SQLiteHandler:
    # Known tables
    known = ['authors', 'articles', 'annotations', 'tags', 'files', 'references']
    # SQL statements for all tables
    # Given that we will take care of all operations, foreign keys have been forgone. This may not be the best
    # practice, but preserves generality.
    __articlestable = """
    CREATE TABLE IF NOT EXISTS articles (
        uuid text PRIMARY KEY,
        refkey text NOT NULL UNIQUE,
        yyyy int NOT NULL,
        title text NOT NULL,
        journal text NOT NULL,
        volume int NOT NULL,
        numb int not NULL,
        pagstart int NOT NULL,
        pagend int NOT NULL,
        retracted int not NULL
    )
    """

    __authorstable = """
    CREATE TABLE IF NOT EXISTS authors (
        uuid text PRIMARY KEY,
        firstname text NOT NULL,
        lastname text NOT NULL
    )
    """

    __annotationstable = """
   CREATE TABLE IF NOT EXISTS annotations (
        uuid text PRIMARY KEY,
        objuuid text NOT NULL,
        class text NOT NULL,
        info text NOT NULL
    ) 
    """

    __articlesxauthorstable = """
    CREATE TABLE IF NOT EXISTS authorsperarticle (
        artcuuid text,
        authuuid text
    )
    """

    __tagstable = """
    CREATE TABLE IF NOT EXISTS tags (
        uuid PRIMARY KEY,
        objuuid text NOT NULL,
        objclass text NOT NULL,
        content text NOT NULL
    )
    """

    __filestable = """
        CREATE TABLE IF NOT EXISTS files (
            uuid PRIMARY KEY,
            objuuid text NOT NULL,
            objclass text NOT NULL,
            fname text NOT NULL,
            ftype text NOT NULL,
            desc text NOT NULL,
            content blob NOT NULL
        )
        """

    __refstable = """
     CREATE TABLE IF NOT EXISTS refs (
         uuid PRIMARY KEY,
         objcuuid text NOT NULL,
         refuuid text NOT NULL,
         objclass text NOT NULL
     )
     """

    def __init__(self, db, dryrun, create):
        self.__conn = None
        self.__cursor = None
        self.__dryrun = dryrun

        if create:
            try:
                click.echo('[SQLite] Attempting to create new stash...')
                self.__conn = sqlite3.connect(db)
                self.__cursor = self.__conn.cursor()
                click.echo('[SQLite] Stash created successfully...')
                click.echo('[SQLite] Attempting to initialize stash structure...')

                structures = [self.__authorstable, self.__articlestable, self.__annotationstable,
                              self.__articlesxauthorstable, self.__tagstable, self.__refstable, self.__filestable]

                structurenames = ['Authors', 'Articles', 'Annotations', 'Articles per author', 'Tags', 'References',
                                  'Files']

                for strc, name in zip(structures, structurenames):
                    self.__cursor.execute(strc)
                    click.echo('    {0}...'.format(name))

            except Error as e:
                click.echo(click.style('[SQLite] Stash could not be created ({0}).'.format(e), fg='red'))
        else:
            # Tricky part: sqlite will create the db even if it does not exist. We use paths
            # to complete the search
            click.echo('[SQLite] Attempting to connect to existing stash file: \x1b[1m{0}\x1b[0m ...'.format(db))
            if pathlib.Path(db).exists():
                try:
                    self.__conn = sqlite3.connect(db)
                    self.__cursor = self.__conn.cursor()
                    click.echo('[SQLite] Connected to existing stash.')

                except Error as e:
                    click.echo(click.style('[SQLite] Error connecting to the stash ({0}).'.format(e), fg='red'))
            else:
                click.echo(click.style('[SQLite] Stash does not exist.', fg='red'))
                quit()

    def close(self):
        if self.__conn is None:
            click.echo(click.style('[SQLite] No need to close stash.', fg='magenta'))
        else:
            click.echo("[SQLite] Closing database...")
            self.__conn.close()

    # Data management commands
    #
    # All commands here are constructive blocks later to be used by the dispatch function. Almost all operations
    # should be mirrored in the

    # Helper functions
    def __listrender(self, tuple, objtype):
        # Authors can be rendered easily
        if objtype == 'authors':
            id, fn, ln = tuple
            return '\t[{0}]\t\t{2}, {1}'.format(id, fn, ln)
        # For an article tuple, find all authors. If no authors exist, raise error. Otherwise, list last names.
        elif objtype == 'articles':
            id, rk, yy, tt, jn, vm, nm, ps, pe, rt = objtype
            self.__cursor.execute('SELECT * FROM authors INNER JOIN authorsperarticle ON authors.id = authorsperarticle.authuuid WHERE authorsperarticle.artuuid={0}'.format(id))

            auths = self.__cursor.fetchall()

            if not auths:
                click.echo(click.style('[SQLite] Article {0} contains no authors. Please solve.'.format(id), fg='red'))
                return ''
            else:
                lnames = []
                for t in auths:
                    _, _, auln = t
                    lnames.append(auln)

            return '\t[{0}]\t{8}\t{1}. {2}. {3} {4}({5}: {6}--{7})'.format(id, yy, ' ,'.join(lnames), tt, vm, nm, ps, pe, '!' if rt else ' ')
        else:
            return ''

    # List objects in the database
    def list(self, objtable):
        if not self.__cursor:
            click.echo(click.style('[SQLite] Database connection does not exist.', fg='red'))
            return None
        elif not objtable:
            click.echo(click.style('[SQLite] Cannot list unknown object type.', fg='red'))
        else:
            if not objtable in ['authors', 'articles', 'annotations', 'tags', 'files', 'references']:
                click.echo(click.style('[SQLite] Unknown object type.', fg='red'))
                return None
            else:
                # Files require special treatment to avoid pulling blobs
                if objtable != 'files':
                    self.__cursor.execute('SELECT * FROM {0}'.format(objtable))
                else:
                    self.__cursor.execute('SELECT uuid, objuuid, objclass, fname, ftype, desc FROM {0}'.format(objtable))

                rows = self.__cursor.fetchall()

            if not rows:
                click.echo(click.style('[SQLite] Database contains no {0}.'.format(objtable), fg='magenta'))
                return None
            else:
                return '\n'.join(map(lambda x: self.__listrender(x, objtable), rows))

    def exists(self, obj):
        if not self.__cursor:
            click.echo(click.style('[SQLite] Database connection does not exist.', fg='red'))
            return False
        elif not obj:
            click.echo(click.style('[SQLite] Cannot find null object.', fg='red'))
        elif not obj.table in self.known:
            click.echo(click.style('[SQLite] Unknown object type.', fg='red'))
            return False
        else:
            self.__cursor.execute('SELECT uuid FROM {0} WHERE uuid={1}'.format(obj.table, str(obj.id)))
            row = self.__cursor.fetchone()
            return True if row else False

    def new(self, obj):
        if obj is None:
            click.echo(click.style('[SQLite] Cannot create null object.', fg='red'))
        #else:
            # We proceed case by case
         #   if type(obj) is Author:
