# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
from scistash.entities.identifiable import IdentifiableEntity
import uuid


class CitableEntity(IdentifiableEntity):
    def __init__(self, refkey='', authors=None, title='', year=0):
        super().__init__()
        self.__refkey = refkey
        if authors is None:
            self.__authors = []
        else:
            self.__authors = authors
        self.__title = title
        self.__year = year

    @property
    def refkey(self):
        return self.__refkey

    @property
    def authors(self):
        return self.__authors

    @property
    def title(self):
        return self.__title

    @property
    def year(self):
        return self.__year

    @refkey.setter
    def refkey(self, val):
        self.__key = val
        self.id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    @authors.setter
    def authors(self, val):
        self.__authors = val
        self.id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    @title.setter
    def title(self, val):
        self.__title = val
        self.id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    @year.setter
    def year(self, val):
        self.__year = str(val)
        self.id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    def __str__(self):
        authstr = '; '.join(self.authors[:-1])+' and ' + self.authors[-1]
        return '==> Entity: {3}\n\tYear: {2}\n\tAuthors: {0}\n\tTitle: {1}'.format(authstr, self.title, self.year, self.id)
