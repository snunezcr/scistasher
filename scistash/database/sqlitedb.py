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
from scistash.database.memorydb import MemoryDBHandler
from sqlite3 import Error
import sqlite3
import pathlib
import click
import uuid


class SQLiteHandler:
    # Functions to convert from tuples to simple objects (no nesting)
    # We define these first to have the function maps ready
    @staticmethod
    def __tupletoauthor(tp):
        lid, fn, ln = tp
        return Author(fn, ln)

    @staticmethod
    def __tupletoarticle(tp):
        lid, rk, yy, tt, jj, vl, nm, ps, pe, rt = tp
        return Article(rk, None, tt, yy, jj, vl, nm, (ps, pe), rt)

    @staticmethod
    def __tupletoannotation(tp):
        lid, oid, ocls, sm, ifo = tp
        return Annotation(oid, ocls, sm, ifo)

    @staticmethod
    def __tupletotag(tp):
        lid, oid, ocls, cnt = tp
        return Tag(oid, ocls, cnt)

    # This includes the blob
    # TODO: in future versions, depending on the size of objects, a total memory quota is needed as a macro parameter
    @staticmethod
    def __tupletofile(tp):
        lid, oid, ocls, fn, ft, ds, fs, cn = tp
        RefFile(oid, fn, ft, ds, fs, cn)

    @staticmethod
    def __tupletoref(tp):
        lid, oid, ocls, rid = tp
        Reference(oid, ocls, rid)

    # Type-to-tuple-function mapping to recover from database
    __typetupleobjfunction = {
        Author: __tupletoauthor,
        Article: __tupletoarticle,
        Annotation: __tupletoannotation,
        Tag: __tupletotag,
        RefFile: __tupletofile,
        Reference: __tupletoref
    }

    # Helper function to remove tags, files and references
    def __deletedecorators(self, did: uuid.UUID):
        self.__cursor.execute(f'DELETE FROM tags WHERE objuuid={did}')
        self.__cursor.execute(f'DELETE FROM files WHERE objuuid={did}')
        self.__cursor.execute(f'DELETE FROM refs WHERE objuuid={did}')

    def __deleteauthor(self, did: uuid.UUID):
        if did is None:
            click.echo(click.style('[SQLite] Cannot delete null author id.', fg='red'))
        else:
            if not self.exists_fetch(did, Author):
                click.echo(click.style(f'[SQLite] Author { did } does not exist.', fg='magenta'))
            else:
                if click.confirm('Do you wish to delete referenced objects for this author? ', default=False):
                    # Find all annotations and delete their decorators
                    self.__cursor.execute(f'SELECT uuid FROM annotations WHERE objuuid={did}')
                    annots = self.__cursor.fetchall()
                    # This takes care of all decorators with first degree of indirection
                    for aid in annots:
                        self.__deletedecorators(aid)
                    # Delete all the author's decorators
                    self.__deletedecorators(did)
                    # Delete the author-article association

                if click.confirm('Do you wish to remove the association to existing articles?', default=False):
                    self.__cursor.execute(f'DELETE FROM authorsperarticle WHERE authuuid={did}')

                # Finally, delete the author
                self.__cursor.execute(f'DELETE FROM authors where uuid={did}')

    def __deletearticle(self, did: uuid.UUID):
        if did is None:
            click.echo(click.style('[SQLite] Cannot delete null article id.', fg='red'))
        else:
            if not self.exists_fetch(did, Article):
                click.echo(click.style(f'[SQLite] Article { did } does not exist.', fg='magenta'))
            else:
                if click.confirm('Do you wish to delete referenced objects for this article? ', default=False):
                    # Find all annotations and delete their decorators
                    self.__cursor.execute(f'SELECT uuid FROM annotations WHERE objuuid={did}')
                    annots = self.__cursor.fetchall()
                    # This takes care of all decorators with first degree of indirection
                    for aid in annots:
                        self.__deletedecorators(aid)
                    # We also need to take care of refuuids in references
                    self.__cursor.execute(f'DELETE FROM refs WHERE refuuid={did}')
                    # Delete all the author's decorators
                    self.__deletedecorators(did)
                    # Delete the author-article association

                if click.confirm('Do you wish to remove the association to existing authors?', default=False):
                    self.__cursor.execute(f'DELETE FROM authorsperarticle WHERE artuuid={did}')

                # Finally, delete the author
                self.__cursor.execute(f'DELETE FROM articles where uuid={did}')

    def __deleteannotation(self, did: uuid.UUID):
        if did is None:
            click.echo(click.style('[SQLite] Cannot delete null annotation id.', fg='red'))
        else:
            if not self.exists_fetch(did, Annotation):
                click.echo(click.style(f'[SQLite] Annotation { did } does not exist.', fg='magenta'))
            else:
                if click.confirm('Do you wish to delete referenced objects for this annotation? ', default=False):
                    self.__deletedecorators(did)
                    # Delete the author-article association

                # Finally, delete the annotation
                self.__cursor.execute(f'DELETE FROM annotations where uuid={did}')

    def __deletetag(self, did: uuid.UUID=None):
        if did is None:
            click.echo(click.style('[SQLite] Cannot delete null tag id.', fg='red'))
        else:
            self.__cursor.execute(f'DELETE FROM tags WHERE uuid={did}')

    def __deletefile(self, did: uuid.UUID=None):
        if id is None:
            click.echo(click.style('[SQLite] Cannot delete null file id.', fg='red'))
        else:
            self.__cursor.execute(f'DELETE FROM files WHERE uuid={did}')

    def __deleteref(self, did: uuid.UUID=None):
        if id is None:
            click.echo(click.style('[SQLite] Cannot delete null reference id.', fg='red'))
        else:
            self.__cursor.execute(f'DELETE FROM refs WHERE uuid={did}')

    # Type-to-insert from object to database
    __objecttodeletefunction = {
        Author: __deleteauthor,
        Article: __deletearticle,
        Annotation: __deleteannotation,
        Tag: __deletetag,
        RefFile: __deletefile,
        Reference: __deleteref
    }

    # We use these functions to both create or edit database records
    def __authortorow(self, obj: Author, prior: uuid.UUID=None):
        if prior is not None:
            # Delete the prior id before modification, insert the new one
            self.__objecttodeletefunction[Author](prior)
            # Update existing annotations and decorators
            self.__cursor.execute(f'UPDATE annotations SET objid={obj.id} WHERE objid={prior}')
            self.__cursor.execute(f'UPDATE tags SET objid={obj.id} WHERE objid={prior}')
            self.__cursor.execute(f'UPDATE files SET objid={obj.id} WHERE objid={prior}')
            self.__cursor.execute(f'UPDATE refs SET objid={obj.id} WHERE objid={prior}')


        # Only insert the new row
        self.__cursor.execute(f'INSERT INTO authors ({obj.id}, {obj.firstname}, {obj.lastname})')

    def __articletorow(self, obj: Article, prior: uuid.UUID = None):
        if prior is not None:
            # Delete the prior id before modification, including author-article ties, insert the new one
            self.__objecttodeletefunction[Article](prior)
            self.__cursor.execute(f'DELETE FROM authorsperarticle WHERE artuuid={prior}')
            # Update existing annotations and decorators
            self.__cursor.execute(f'UPDATE annotations SET objid={obj.id} WHERE objid={prior}')
            self.__cursor.execute(f'UPDATE tags SET objid={obj.id} WHERE objid={prior}')
            self.__cursor.execute(f'UPDATE files SET objid={obj.id} WHERE objid={prior}')
            self.__cursor.execute(f'UPDATE refs SET objid={obj.id} WHERE objid={prior}')

        # Insert one row per article
        self.__cursor.execute(f'INSERT INTO articles ({obj.id}, {obj.refkey}, {obj.title}, {obj.journal}, ' +
                              f'{obj.volume}, {obj.number}, {obj.pages[0]}, {obj.pages[1]}, {obj.retracted})')

        # Insert authors and update article-authors references if new
        for auth in obj.authors:
            if not self.exists(auth):
                self.__authortorow(auth)
            self.__cursor.execute(f'INSERT INTO authorsperarticle ({obj.id}, {auth.id})')

    def __annotationtorow(self, obj: Annotation, prior: uuid.UUID = None):
        if prior is not None:
            # Delete the prior id before modification, including annotation-object ties, insert the new one
            self.__objecttodeletefunction[Annotation](prior)
            self.__cursor.execute(f'DELETE FROM annotations WHERE artuuid={prior}')
            # Update existing decorators
            self.__cursor.execute(f'UPDATE tags SET objid={obj.id} WHERE objid={prior}')
            self.__cursor.execute(f'UPDATE files SET objid={obj.id} WHERE objid={prior}')
            self.__cursor.execute(f'UPDATE refs SET objid={obj.id} WHERE objid={prior}')


        # Insert one row per annotation
        self.__cursor.execute(f'INSERT INTO annotations ({obj.id}, {obj.objuuid}, {obj.objcls}, {obj.summary}, {obj.info})')

    def __tagtorow(self, obj: Tag, prior = None):
        self.__cursor.execute(f'INSERT INTO tags ({obj.id}, {obj.objid}, {obj.objcls}, {obj.content})')

    def __filetorow(self, obj: RefFile, prior = None):
        self.__cursor.execute(f'INSERT INTO tags ({obj.id}, {obj.objid}, {obj.objcls}, {obj.fname}, {obj.ftype}, {obj.desc}, {obj.desc}, {obj.fsize}, {sqlite3.Binary(obj.content)})')

    def __reftorow(self, obj: Reference, prior = None):
        self.__cursor.execute(f'INSERT INTO refs ({obj.id}, {obj.objid}, {obj.objcls}, {obj.content})')

    # Type-to-insert from object to database
    __objecttoinsertfunction = {
        Author: __authortorow,
        Article: __articletorow,
        Annotation: __annotationtorow,
        Tag: __tagtorow,
        RefFile: __filetorow,
        Reference: __reftorow
    }

    # Type-to-table mapping
    __typetotablemap = {
        Author: 'authors',
        Article: 'articles',
        Annotation: 'annotations',
        Tag: 'tags',
        RefFile: 'files',
        Reference: 'refs'
    }

    # Table-to-type mapping (no elegant and efficient way to obtain from Python's dictionary
    __tabletotypemapper = {
        'authors': Author,
        'articles': Article,
        'annotations': Annotation,
        'tags': Tag,
        'files': RefFile,
        'refs': Reference
    }

    # SQL statements for all tables
    # Given that we will take care of all operations, foreign keys have been forgone. This may not be the best
    # practice, but preserves generality.
    __authorstable = """
    CREATE TABLE IF NOT EXISTS authors (
        uuid text PRIMARY KEY,
        firstname text NOT NULL,
        lastname text NOT NULL
    )
    """

    __articlestable = """
    CREATE TABLE IF NOT EXISTS articles (
        uuid text PRIMARY KEY,
        refkey text NOT NULL UNIQUE,
        year int NOT NULL,
        title text NOT NULL,
        journal text NOT NULL,
        volume int NOT NULL,
        numb int not NULL,
        pagstart int NOT NULL,
        pagend int NOT NULL,
        retracted int not NULL
    )
    """

    __annotationstable = """
   CREATE TABLE IF NOT EXISTS annotations (
        uuid text PRIMARY KEY,
        objuuid text NOT NULL,
        objclass text NOT NULL,
        summary text NOT NULL,
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
            descr text NOT NULL,
            fsize int NOT NULL,
            content blob NOT NULL
        )
        """

    __refstable = """
     CREATE TABLE IF NOT EXISTS refs (
         uuid PRIMARY KEY,
         objuuid text NOT NULL,
         objclass text NOT NULL,
         refuuid text NOT NULL
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
            self.__conn.commit()
            self.__conn.close()

    # Data management commands
    #
    # All commands here are constructive blocks later to be used by the dispatch function. Almost all operations
    # should be mirrored in the

    # TODO: this needs to be refactored properly
    def __listrendertuple(self, tuple, objtype):
        # Authors can be rendered easily
        if objtype == 'authors':
            iid, fn, ln = tuple
            return '\t[{0}]\t\t{2}, {1}'.format(iid, fn, ln)
        # For an article tuple, find all authors. If no authors exist, raise error. Otherwise, list last names.
        elif objtype == 'articles':
            iid, rk, yy, tt, jn, vm, nm, ps, pe, rt = tuple
            query = f'''
            SELECT * FROM authors 
            INNER JOIN authorsperarticle ON authors.id = authorsperarticle.authuuid 
            WHERE authorsperarticle.artuuid={iid}\
            '''
            self.__cursor.execute(query)

            auths = self.__cursor.fetchall()

            if not auths:
                click.echo(click.style('[SQLite] Article {0} contains no authors.'.format(iid), fg='red'))
                return None
            else:
                lnames = []
                for t in auths:
                    _, _, auln = t
                    lnames.append(auln)

            return '\t{0}\t{8}\t{1}. {2}. {3}. {4}({5}: {6}--{7})'.format(iid, yy, ' ,'.join(lnames),
                                                                           tt, vm, nm, ps, pe, '!' if rt else ' ')
        # For annotations, retrieve a simplified version of the object
        elif objtype == 'annotations':
            iid, oid, cls, inf = tuple

            if cls == 'author':
                self.__cursor.execute(f'SELECT firstname, lastname FROM authors WHERE id={oid}')
                data = self.__cursor.fetchone()

                if not data:
                    click.echo(click.style('[SQLite] Annotation {0} refers to no author.'.format(iid),
                                           fg='red'))
                    return None
                else:
                    fn, ln = data
                    return '\t{0}\t\t{3}\t<{2},{1}>\t{5}, {4}'.format(iid, oid, cls, inf, fn, ln)
            elif cls == 'article':
                self.__cursor.execute(f'SELECT year, title, journal FROM articles WHERE id={oid}')
                data = self.__cursor.fetchone()

                if not data:
                    click.echo(click.style('[SQLite] Annotation {0} refers to no author.'.format(iid),
                                           fg='red'))
                    return None
                else:
                    yy, tt, jj = data
                    return '\t{0}\t\t{3}\t<{2},{1}>\t{4}.{5}.{6}. '.format(iid, oid, cls, inf, yy, tt, jj)
            else:
                return None
        # Tags
        elif objtype == 'tags':
            iid, oid, cls, cnt = tuple

            if cls == 'author':
                self.__cursor.execute(f'SELECT firstname, lastname FROM authors WHERE id={oid}')
                data = self.__cursor.fetchone()

                if not data:
                    click.echo(click.style('[SQLite] Tag {0} belongs to no author.'.format(iid),
                                           fg='red'))
                    return None
                else:
                    fn, ln = data
                    return '\t{0}\t\t{3}\t<{2},{1}>\t{5},{4}'.format(iid, oid, cls, cnt, fn, ln)
            elif cls == 'article':
                self.__cursor.execute(f'SELECT year, title, journal FROM articles WHERE id={oid}')
                data = self.__cursor.fetchone()

                if not data:
                    click.echo(click.style('[SQLite] Tag {0} belongs to no article.'.format(iid), fg='red'))
                    return None
                else:
                    yy, tt, jj = data
                    return '\t{0}\t\t{3}\t<{2},{1}>\t{4}.{5}.{6}. '.format(iid, oid, cls, cnt, yy, tt, jj)
            elif cls == 'annotations':
                self.__cursor.execute(f'SELECT objuuid, objclass, summary FROM annotations WHERE id={oid}')
                data = self.__cursor.fetchone()

                if not data:
                    click.echo(click.style('[SQLite] Tag {0} belongs to no annotation.'.format(iid),fg='red'))
                    return None
                else:
                    rid, roid, sm = data
                    return '\t{0}\t\t{3}\t<{2},{1}>\t{4} <<{6},{5}>> '.format(iid, oid, cls, cnt, sm, rid, roid)
            else:
                return None
        # Files
        elif objtype == 'files':
            iid, oid, cls, fnm, fty, dsc, fsz = tuple

            if cls == 'author':
                self.__cursor.execute(f'SELECT firstname, lastname FROM authors WHERE id={oid}')
                data = self.__cursor.fetchone()

                if not data:
                    click.echo(click.style('[SQLite] Tag {0} belongs to no author.'.format(iid), fg='red'))
                    return None
                else:
                    fn, ln = data
                    return '\t{0}\t\t{3} [{4}, {8} bytes] {5}\t<{2},{1}>\t{7}, {6}'.format(iid, oid, cls, fnm,
                                                                                  fty, dsc, fn, ln, fsz)
            elif cls == 'article':
                self.__cursor.execute(f'SELECT year, title, journal FROM articles WHERE id={oid}')
                data = self.__cursor.fetchone()

                if not data:
                    click.echo(click.style('[SQLite] Tag {0} belongs to no article.'.format(iid),
                                           fg='red'))
                    return None
                else:
                    yy, tt, jj = data
                    return '\t{0}\t\t{3} [{4}] {5}\t<{2},{1}>\t{6}.{7}.{8}.'.format(iid, oid, cls, fnm,
                                                                                      fty, dsc, yy, tt, jj)
            elif cls == 'annotations':
                self.__cursor.execute(f'SELECT objuuid, objclass, summary FROM annotations WHERE id={oid}')
                data = self.__cursor.fetchone()

                if not data:
                    click.echo(click.style('[SQLite] Tag {0} belongs to no annotation.'.format(iid), fg='red'))
                    return None
                else:
                    rid, roid, sm = data
                    return '\t{0}\t\t{3} [{4}] {5}\t<{2},{1}>\t <<{6},{7}>>'.format(iid, oid, cls, fnm,
                                                                                      fty, dsc, rid, roid)
            else:
                return None
        # References
        elif objtype == 'refs':
            iid, oid, cls, rid = tuple

            self.__cursor.execute(f'SELECT year, title, journal FROM articles WHERE id={rid}')
            rdata = self.__cursor.fetchone()

            if not rdata:
                click.echo(click.style('[SQLite] Reference {0} points to no stash article.'.format(iid), fg='red'))
                return None
            else:
                ryy, rtt, rjj = rdata

                if cls == 'author':
                    self.__cursor.execute(f'SELECT firstname, lastname FROM authors WHERE id={oid}')
                    data = self.__cursor.fetchone()

                    if not data:
                        click.echo(click.style('[SQLite] Reference {0} belongs to no author.'.format(iid),
                                               fg='red'))
                        return None
                    else:
                        fn, ln = data
                        return '\t{0}\t\t<{2},{1}> {4}, {3} ----> [5] {6}.{7}.{8}.'.format(iid, oid, cls, fn, ln,
                                                                                             rid, ryy, rtt, rjj)
                elif cls == 'article':
                    self.__cursor.execute('SELECT year, title, journal FROM articles WHERE id={0}'.format(oid))
                    data = self.__cursor.fetchone()

                    if not data:
                        click.echo(click.style('[SQLite] Reference {0} belongs to no article.'.format(iid),
                                               fg='red'))
                    else:
                        yy, tt, jj = data
                        return '\t{0}\t\t<{2},{1}> {3}.{4}.{5}. ----> [6] {7}.{8}.{9}.'.format(iid, oid, cls, yy, tt,
                                                                                                 jj, rid, ryy, rtt, rjj)
                elif cls == 'annotations':
                    self.__cursor.execute(f'SELECT objuuid, objclass, summary FROM annotations WHERE id={oid}')
                    data = self.__cursor.fetchone()

                    if not data:
                        click.echo(click.style('[SQLite] Reference {0} belongs to no annotation.'.format(iid),fg='red'))
                    else:
                        rfid, rfobc, sm = data
                        return '\t{0}\t\t<{2},{1}> {3} <<{5},{4}>> ----> [5] {6}.{7}.{8}.'.format(iid, oid, cls, sm,
                                                                                                    rfid, rfobc, ryy,
                                                                                                    rtt, rjj)
                else:
                    return None
        else:
            return None

    # List objects in the database
    def list(self, objtable):
        if not self.__cursor:
            click.echo(click.style('[SQLite] Database connection does not exist.', fg='red'))
            return None
        elif not objtable:
            click.echo(click.style('[SQLite] Cannot list unknown object type.', fg='red'))
            return None
        else:
            if objtable not in ['authors', 'articles', 'annotations', 'tags', 'files', 'refs']:
                click.echo(click.style('[SQLite] Unknown object type.', fg='red'))
                return None
            else:
                # Files require special treatment to avoid pulling blobs
                if objtable != 'files':
                    self.__cursor.execute(f'SELECT * FROM {objtable}')
                else:
                    self.__cursor.execute(f'SELECT uuid, objuuid, objclass, fname, ftype, descr, fsize FROM {objtable}')

                rows = self.__cursor.fetchall()

            if not rows:
                click.echo(click.style('[SQLite] Database contains no {0}.'.format(objtable), fg='magenta'))
                return None
            else:
                return '\n'.join(map(lambda x: self.__listrendertuple(x, objtable), rows))

    def exists_fetch(self, oid: uuid.UUID, otype):
        if not otype in self.__typetotablemap.keys():
            click.echo(click.style('[SQLite] Unknown object type.', fg='red'))
            return False
        else:
            self.__cursor.execute(f'SELECT uuid FROM {self.__typetotablemap[otype]} WHERE uuid={str(oid)}')
            return True if self.__cursor.fetchone() else False

    def exists(self, obj):
        if not self.__cursor:
            click.echo(click.style('[SQLite] Database connection does not exist.', fg='red'))
            return False
        elif not obj:
            click.echo(click.style('[SQLite] Cannot find null object.', fg='red'))
            return False
        else:
            return self.exists_fetch(obj.id, type(obj))

    def fetch(self, oid: uuid.UUID, otype):
        if not self.exists_fetch(oid, otype):
            click.echo(click.style('[SQLite] Object not present in stash.', fg='magenta'))
            return None
        else:
            self.__cursor.execute(f'SELECT * FROM {self.__typetotablemap[otype]}')
            data = self.__cursor.fetchone()

            if data:
                return self.__typetupleobjfunction[otype](data)
            else:
                return None

    def checkout(self, oid: uuid.UUID, fhash: dict):
        if oid not in fhash.keys():
            click.echo(click.style('[FetchH] Object not present across the complete stash.', fg='magenta'))
            return None

        otype = fhash[oid]
        return self.fetch(oid, otype)

    def save(self, obj, prior: uuid.UUID, fhash: dict):
        if obj is None:
            click.echo(click.style('[SQLite] Cannot save null object.', fg='red'))
        elif obj.id == prior:
            click.echo(click.style('[SQLite] Ignoring saving for same object.', fg='magenta'))
        else:
            if self.exists(obj):
                click.echo(click.style('[SQLite] the object already exists.', fg='red'))
            else:
                self.__objecttoinsertfunction[type(obj)](obj, prior)
                fhash[obj.id] = type(obj)

    def delete(self, did: uuid.UUID, fhash: dict):
        if did not in fhash.keys():
            click.echo(click.style('[FetchH] Object not present across the complete stash.', fg='magenta'))
        else:
            self.__objecttodeletefunction[fhash[did]](did)
            fhash.pop(did, None)

    def buildfetchhash(self):
        click.echo('[SQLite] Attempting to construct a fetch hash...')

        if self.__cursor is None:
            click.echo(click.style('[SQLite] Fetch hash construction failed.', fg='red'))
            return None
        else:
            fhash = {}

            for table in list(self.__typetotablemap.values()):
                self.__cursor.execute(f'SELECT DISTINCT uuid FROM {table}')

                for t in self.__cursor.fetchall():
                    fhash[uuid.UUID(t)] = self.__tabletotypemapper[table]

            click.echo('[SQLite] Fetch hash constructed.')
            return fhash

    def buildcontexthash(self):
        click.echo('[SQLite] Attempting to construct a context hash...')

        if not self.__cursor:
            click.echo(click.style('[SQLite] Database connection does not exist.', fg='red'))
            return None
        else:
            chash = {}

            for table in list(self.__typetotablemap.values()):
                if table == 'files':
                    self.__cursor.execute(f'SELECT uuid, objuuid, objclass, fname, ftype, descr, fsize FROM {table}')
                else:
                    self.__cursor.execute(f'SELECT * FROM {table}')

                for t in self.__cursor.fetchall():
                    chash[uuid.UUID(t[0])] = self.__listrendertuple(t, table)

            click.echo('[SQLite] Context hash constructed.')
            return chash
