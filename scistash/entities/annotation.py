# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
import uuid


class Annotation:

    def __init__(self, refuuid: uuid.UUID, sm: str, info: str):
        self.__refuuid = refuuid
        self.__summary = sm
        self.__info = info
        self.__id = uuid.uuid3(uuid.NAMESPACE_OID, str(self.__refuuid) + self.__summary + self.__info)

    @property
    def id(self):
        return self.__id

    @property
    def refuuid(self):
        return self.__refuuid

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
        self.__id = uuid.uuid3(uuid.NAMESPACE_OID, self.stringify())

    def stringify(self):
        return str(self.__refuuid) + self.__summary + self.__info

    def __str__(self):
        return '==> Annotation: {3}\n\tSummary: {0}\n\tInformation {1}\n\tBelongs to: {2}'.format(self.summary,
                                                                                                  self.info,
                                                                                                  self.refuuid,
                                                                                                  self.id)
