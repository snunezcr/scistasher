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
