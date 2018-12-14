# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
import uuid


class Attachment:

    def __init__(self, objid: uuid.UUID, objcls:str, content):
        self.__objid = objid
        self.__objcls = objcls
        self.__content = content
        self.__id = str(uuid.uuid3(uuid.NAMESPACE_OID, self.stringify()))

    @property
    def id(self):
        return self.__id

    @property
    def objid(self):
        return self.__objid

    @property
    def objcls(self):
        return self.__objcls

    @property
    def content(self):
        return self.__content

