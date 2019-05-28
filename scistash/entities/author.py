# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
from scistash.entities.identifiable import IdentifiableEntity
import uuid


class Author(IdentifiableEntity):

    def __init__(self, first: str, last: str, fdb: bool):
        super().__init__()
        self.__firstname = first
        self.__lastname = last
        self.__id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())
        self.fromDB = fdb

    @property
    def id(self):
        return self.id

    @property
    def firstname(self):
        return self.__firstname

    @property
    def lastname(self):
        return self.__lastname

    @property
    def mayhavetags(self):
        return True

    @property
    def mayhavereferences(self):
        return False

    @property
    def mayhavefiles(self):
        return True

    @firstname.setter
    def firstname(self, val):
        self.__firstname = val
        super().id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    @lastname.setter
    def lastname(self, val):
        self.__lastname = val
        super().id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    def stringify(self):
        return self.firstname+self.lastname

    def formalref(self):
        return '{1}, {0}'.format(self.firstname, self.lastname, self.id)

    def __str__(self):
        return '==> Author: {2}\n\t{1}, {0}'.format(self.firstname, self.lastname, self.id)

    def numberedref(self, seq: int):
        return f'\t[{ seq }] \t{ self.id } - {self.lastname}, {self.firstname}'

