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

    def __init__(self):
        click.echo('[IMemDB] Initializing in memory stash...')
        self.__authors = []
        self.__articles = []
        self.__annotations = []
        self.__tags = []
        self.__files = []
        self.__refs = []
        click.echo('[IMemDB] In-memory stash initialized.')

    def exists(self, obj):
        if not obj:
            click.echo(click.style('[IMemDB] Cannot find null object.', fg='red'))
        else:
            if type(obj) is Author:
                rows = list(filter(lambda x: x.id == obj.id, self.__authors))
            elif type(obj) is Article:
                rows = list(filter(lambda x: x.id == obj.id, self.__articles))
            elif type(obj) is Annotation:
                rows = list(filter(lambda x: x.id == obj.id, self.__annotations))
            elif type(obj) is Tag:
                rows = list(filter(lambda x: x.id == obj.id, self.__tags))
            elif type(obj) is RefFile:
                rows = list(filter(lambda x: x.id == obj.id, self.__files))
            elif type(obj) is Reference:
                rows = list(filter(lambda x: x.id == obj.id, self.__refs))
            else:
                rows = []

            return True if rows else False

    def scratchall(self):
        if click.confirm(click.style('[IMemDB] Irrecoverably scratch all unsaved stash objects?', bold=True, fg='magenta')):
            self.__authors = []
            self.__articles = []
            self.__annotations = []
            self.__tags = []
            self.__files = []
            self.__refs = []
            click.echo('[IMemDB] All in-memory stash objects have been scratched.')
