# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
import uuid


class Author:
    table = 'authors'

    def __init__(self, first='', last=''):
        self.__firstname = first
        self.__lastname = last
        self.__id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    @property
    def id(self):
        return self.__id

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
        self.__id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    @lastname.setter
    def lastname(self, val):
        self.__lastname = val
        self.__id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    def stringify(self):
        return self.firstname+self.lastname

    def formalref(self):
        return '{1}, {0}'.format(self.firstname, self.lastname, self.id)

    def __str__(self):
        return '==> Author: {2}\n\t{1}, {0}'.format(self.firstname, self.lastname, self.id)
