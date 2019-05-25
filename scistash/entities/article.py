# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
from scistash.entities.citable import CitableEntity
import uuid


class Article(CitableEntity):

    def __init__(self, refkey='', authors=None, title='', year=0, journal='', volume=0,
                 number=0, pages=(0, 0), retracted=False, fdb=False):
        super().__init__(refkey, authors, title, year)
        self.__journal = journal
        self.__volume = volume
        self.__number = number
        self.__pages = pages
        self.__retracted = retracted
        self.__id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())
        self.fromDB = fdb

    @property
    def journal(self):
        return self.__journal

    @property
    def volume(self):
        return self.__volume

    @property
    def number(self):
        return self.__number

    @property
    def pages(self):
        return self.__pages

    @property
    def retracted(self):
        return self.__retracted

    @property
    def mayhavetags(self):
        return True

    @property
    def mayhavereferences(self):
        return True

    @property
    def mayhavefiles(self):
        return True

    @journal.setter
    def journal(self, val):
        self.__journal = val
        super().id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    @volume.setter
    def volume(self, val):
        self.__volume = val
        super().id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    @number.setter
    def number(self, val):
        self.__number = val
        super().id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    @pages.setter
    def pages(self, val):
        self.__pages = val
        super().id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    def stringify(self):
        return ''.join([
            self.refkey,
            ''.join(self.authors),
            self.title,
            str(self.year),
            self.journal,
            str(self.volume),
            str(self.number),
            ''.join(map(str, self.pages)),
            str(self.retracted)
        ])

    def __str__(self):
        pstart, pend = self.pages
        retraction = 'yes' if self.retracted else 'no'
        return super(Article, self).__str__() + \
               '\n\tJournal: {0}\n\tVolume: {1}\n\tNumber: {2}\n\tPages: {3}--{4}\n\tRetracted: {5}\n'.format(
                   self.journal,
                   self.volume,
                   self.number,
                   pstart,
                   pend,
                   retraction)
