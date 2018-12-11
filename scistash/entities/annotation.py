# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
import uuid


class Annotation:
    table = 'annotations'

    def __init__(self, refuuid: uuid.UUID, info: str):
        self.__refuuid = refuuid
        self.__info = info
        self.__id = uuid.uuid3(uuid.NAMESPACE_OID, str(self.__refuuid) + self.__info)

    @property
    def id(self):
        return self.__id

    @property
    def refkey(self):
        return self.__refuuid

    @property
    def info(self):
        return self.__info

    @property
    def mayhavetags(self):
        return True

    @property
    def mayhavereferences(self):
        return True

    @property
    def mayhavefiles(self):
        return True

    @info.setter
    def info(self, val):
        self.__info = val
        self.__id = uuid.uuid3(uuid.NAMESPACE_OID, str(self.__refuuid) + self.info)

    def __str__(self):
        return '==> Annotation: {2}\n\t{0} {1}'.format(self.refkey, self.info, self.id)
