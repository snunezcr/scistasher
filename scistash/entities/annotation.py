# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
from scistash.entities.identifiable import IdentifiableEntity
import uuid


class Annotation(IdentifiableEntity):

    def __init__(self, objuuid: uuid.UUID, objcls: type, sm: str, info: str, fdb: bool):
        super().__init__()
        self.__objuuid = objuuid
        self.__objcls = objcls
        self.__summary = sm
        self.__info = info
        self.__id = uuid.uuid3(uuid.NAMESPACE_OID, str(self.__objuuid) + self.__summary + self.__info)
        self.fromDB = fdb

    @property
    def id(self):
        return self.__id

    @property
    def objuuid(self):
        return self.__objuuid

    @property
    def objcls(self):
        return self.__objcls

    @property
    def summary(self):
        return self.__summary

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

    @summary.setter
    def summary(self, val):
        self.__summary = val

    @info.setter
    def info(self, val):
        self.__info = val
        super().id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    def stringify(self):
        return str(self.__objuuid) + self.__summary + self.__info

    def __str__(self):
        return f'==> Annotation: {self.id}\n\tSummary: {self.summary}\n\tInformation {self.info}\n\tBelongs to: <{self.objuuid},{self.objcls}>'
