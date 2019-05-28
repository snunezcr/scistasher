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
from scistash.database.sqlitedb import SQLiteHandler
import click
import uuid


class MemoryDBHandler:

    def __init__(self, memquota=0):
        click.echo('[IMemDB] Initializing in-memory stash...')
        self.__memquota = memquota
        self.__data = {
            Author: [],
            Article: [],
            Annotation: [],
            Tag: [],
            RefFile: [],
            Reference: []
        }
        click.echo('[IMemDB] In-memory stash initialized.')

    # Most internal implementation
    def exists_fetch(self, oid, otype):
        rows = list(filter(lambda x: x.id == oid, self.__data[otype]))
        return True if rows else False

    # Implementation with entire object, not just ids and types
    def exists(self, obj):
        if not obj:
            click.echo(click.style('[IMemDB] Cannot find null object.', fg='red'))
            return False
        else:
            return self.exists_fetch(obj.id, type(obj))

    def put(self, obj, fhash: dict):
        if obj is None:
            return
        elif self.exists(obj):
            click.echo(click.style('[IMemDB] Object already exists in memory.', fg='magenta'))
        elif type(obj) not in self.__data.keys():
            click.echo(click.style('[IMemDB] Unknown object type.', fg='red'))
        else:
            fhash[obj.id] = type(obj)
            self.__data[type(obj)].append(obj)

    def __fetch(self, oid: uuid.UUID, otype):
        if otype not in self.__data.keys():
            click.echo(click.style('[IMemDB] Unknown object type.', fg='red'))
            return None
        else:
            for obj in self.__data[otype]:
                if obj.id == oid:
                    return obj

            return None

    def checkout_fetch(self, oid: uuid.UUID, otype, fhash: dict):
        if not self.exists_fetch(oid, otype):
            click.echo(click.style('[IMemDB] Object does not exist in memory.', fg='magenta'))
            return None

        else:
            click.echo(click.style('[IMemDB] Unknown object type.', fg='red'))
            data = self.__fetch(oid, otype)

            if data:
                # We only work with immutable data in memory
                self.scratch_fetch(oid, otype, fhash)

            return data

    def object_fetch(self, oid: uuid.UUID, otype):
        if not self.exists_fetch(oid, otype):
            click.echo(click.style('[IMemDB] Object does not exist in memory.', fg='magenta'))
            return None

        else:
            click.echo(click.style('[IMemDB] Unknown object type.', fg='red'))
            return self.__fetch(oid, otype)

    def scratch_fetch(self, oid: uuid.UUID, otype, fhash: dict):
        if otype not in self.__data.keys():
            click.echo(click.style('[IMemDB] Unknown object type.', fg='red'))
        elif not self.exists_fetch(oid, otype):
            click.echo(click.style('[IMemDB] Object does not exist in memory.', fg='magenta'))
        else:
            self.__data[otype] = list(filter(lambda x: x.id != oid, self.__data[otype]))
            fhash.pop(oid, None)
            click.echo(click.style('[IMemDB] Object has been scratched.', fg='green'))

    def scratchall(self, fhash: dict):
        if click.confirm(click.style('[IMemDB] Irrecoverably scratch all unsaved stash objects?', bold=True, fg='magenta')):
            # This removes the keys. At all times, if the object is in the database, it is not in memory and viceversa
            for tp in self.__data.keys():
                for obj in self.__data[tp]:
                    fhash.pop(obj.id, None)

            # And reset the data entities
            self.__data = {
                Author: [],
                Article: [],
                Annotation: [],
                Tag: [],
                RefFile: [],
                Reference: []
            }
            click.echo('[IMemDB] All in-memory stash objects have been scratched.')

    def testMemEmpty(self):
        return (not self.__data[Author]) & (not self.__data[Article]) & (not self.__data[Annotation]) & \
               (not self.__data[Tag]) & (not self.__data[RefFile]) & (not self.__data[Reference])

    def scratch(self, arg):
        if self.testMemEmpty():
            click.echo(click.style('[IMemDB] No pending entities in memory database', fg='blue'))
            click.echo('\n')
        else:
            if arg=='all':
                click.echo(click.style('[IMemDB] Scratching authors', fg='blue'))
                self.__data[Author] = []
                click.echo(click.style('[IMemDB] Scratching articles', fg='blue'))
                self.__data[Article] = []
                click.echo(click.style('[IMemDB] Scratching annotations', fg='blue'))
                self.__data[Annotation] = []
                click.echo(click.style('[IMemDB] Scratching tags', fg='blue'))
                self.__data[Tag] = []
                click.echo(click.style('[IMemDB] Scratching files', fg='blue'))
                self.__data[RefFile] = []
                click.echo(click.style('[IMemDB] Scratching references', fg='blue'))
                self.__data[Reference] = []
                click.echo('\n')
            elif arg in ['authors', 'articles', 'annotations', 'tags', 'files', 'refs']:
                __tabletotypemapper = {
                    'authors': Author,
                    'articles': Article,
                    'annotations': Annotation,
                    'tags': Tag,
                    'files': RefFile,
                    'refs': Reference
                }

                click.echo(click.style(f'[IMemDB] Scratching { arg }', fg='blue'))

                self.__data[__tabletotypemapper[arg]] = []
            else:
                click.echo(click.style(f'[IMemDB] Unrecognized entity \'{ arg }\'.', fg='magenta'))

    def show(self, arg):
        if self.testMemEmpty():
            click.echo(click.style('[IMemDB] No pending entities in memory database', fg='blue'))
            click.echo('\n')
        else:
            if arg=='all':
                click.echo(click.style('[IMemDB] Pending authors', fg='blue'))

                for author in self.__data[Author]:
                    click.echo(click.style(str(author), fg='blue'))

                click.echo('\n')

                click.echo(click.style('[IMemDB] Pending articles', fg='blue'))

                for article in self.__data[Article]:
                    click.echo(click.style(str(article), fg='blue'))

                click.echo('\n')

                click.echo(click.style('[IMemDB] Pending annotations', fg='blue'))

                for annotation in self.__data[Annotation]:
                    click.echo(click.style(str(annotation), fg='blue'))

                click.echo('\n')

                click.echo(click.style('[IMemDB] Pending tags', fg='blue'))

                for tag in self.__data[Tag]:
                    click.echo(click.style(str(tag), fg='blue'))

                click.echo('\n')

                click.echo(click.style('[IMemDB] Pending files', fg='blue'))

                for reffile in self.__data[RefFile]:
                    click.echo(click.style(str(reffile), fg='blue'))

                click.echo('\n')

                click.echo(click.style('[IMemDB] Pending references', fg='blue'))

                for reference in self.__data[Reference]:
                    click.echo(click.style(str(reference), fg='blue'))

                click.echo('\n')
            elif arg in ['authors', 'articles', 'annotations', 'tags', 'files', 'refs']:
                __tabletotypemapper = {
                    'authors': Author,
                    'articles': Article,
                    'annotations': Annotation,
                    'tags': Tag,
                    'files': RefFile,
                    'refs': Reference
                }

                click.echo(click.style(f'[IMemDB] Pending { arg }', fg='blue'))

                for entity in self.__data[__tabletotypemapper[arg]]:
                    click.echo(click.style(str(entity), fg='blue'))
            else:
                click.echo(click.style(f'[IMemDB] Unrecognized entity \'{ arg }\'.', fg='magenta'))

    def save(self, target, dbhandler: SQLiteHandler, fhash: dict):
        if self.testMemEmpty():
            click.echo(click.style('[IMemDB] No pending entities in memory database to be saved', fg='blue'))
            click.echo('\n')
        else:
            if target=='all':
                click.echo(click.style('[IMemDB] Saving pending authors', fg='blue'))
                for author in self.__data[Author]:
                    dbhandler.save(author, fhash)

                click.echo(click.style('[IMemDB] Saving pending articles', fg='blue'))
                for article in self.__data[Article]:
                    dbhandler.save(article, fhash)

                click.echo(click.style('[IMemDB] Saving pending annotations', fg='blue'))
                for annotation in self.__data[Annotation]:
                    dbhandler.save(annotation, fhash)

                click.echo(click.style('[IMemDB] Saving pending tags', fg='blue'))
                for tag in self.__data[Tag]:
                    dbhandler.save(tag, fhash)

                click.echo(click.style('[IMemDB] Saving pending files', fg='blue'))
                for reffile in self.__data[RefFile]:
                    dbhandler.save(reffile, fhash)

                click.echo(click.style('[IMemDB] Saving pending references', fg='blue'))
                for reference in self.__data[Reference]:
                    dbhandler.save(reference, fhash)
            elif target in ['authors', 'articles', 'annotations', 'tags', 'files', 'refs']:
                __tabletotypemapper = {
                    'authors': Author,
                    'articles': Article,
                    'annotations': Annotation,
                    'tags': Tag,
                    'files': RefFile,
                    'refs': Reference
                }

                click.echo(click.style(f'[IMemDB] Saving pending { target }', fg='blue'))

                for entity in self.__data[__tabletotypemapper[target]]:
                    dbhandler.save(entity, fhash)
            else:
                click.echo(click.style(f'[IMemDB] Unrecognized entity \'{ target }\'.', fg='magenta'))

