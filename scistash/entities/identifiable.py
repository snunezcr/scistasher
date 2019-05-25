# Copyright @ 2019
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
import uuid

class IdentifiableEntity:
    def __init__(self):
        self.__id = None
        self.__priorid = None
        self.__fromDB = False

    @property
    def id(self):
        return self.__id

    @property
    def priorid(self):
        return self.__priorid

    @id.setter
    def id(self, val):
        self.__priorid = self.__id
        self.__id = val

    @property
    def fromDB(self):
        return self.__fromDB

    @fromDB.setter
    def fromDB(self, val: bool):
        self.__fromDB = val
