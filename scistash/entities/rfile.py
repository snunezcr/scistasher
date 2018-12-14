# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
from scistash.entities.attachment import Attachment
from pathlib import Path


class RefFile(Attachment):

    def __init__(self, objid, objcls, path: Path, ftyp: str, desc: str, fsz=0, cnt=None):
        self.__fname = path.name
        self.__ftype = ftyp
        self.__desc = desc

        if cnt is None:
            # Creating from file
            self.__fsize = path.stat().st_size
            super().__init__(objid, objcls, path.read_bytes())
        else:
            self.__fsize = fsz
            # Creating from db
            super().__init__(objid, objcls, cnt)

    @property
    def fname(self):
        return self.__fname


    @property
    def ftype(self):
        return self.__ftype

    @property
    def fsize(self):
        return self.__fsize

    @property
    def desc(self):
        return self.desc

    @fname.setter
    def fname(self, val):
        self.__fname = val

    @ftype.setter
    def ftype(self, val):
        self.__ftype = val

    @desc.setter
    def desc(self, val):
        self.desc = type

    def stringify(self):
        # Note: if the file is large, this will be expensive
        # TODO: the current limit in sqlite is 10^9 bytes (1 GB). Larger files require other DB managers
        #       (PostgreSQL's TOAST data type). This may be ideal if this software becomes implemented in the context
        #       of large research facilities, and is extended to include other objects beyond papers (e.g. sensor data).
        return str(self.id) + str(self.objid) + self.objcls + self.__fname + self.__ftype + self.__desc + str(self.content)

    def __str__(self):
        return '==> Reference file: {0}\n\tReferee: <{1},{2}>\n\tName: {3}\n\tSize: {4}\n\tType: {5}\n\tDescription: {6}\n'.format(
                   self.id,
                   self.objid,
                   self.objcls,
                   self.__fname,
                   str(self.__fsize),
                   self.__ftype,
                   self.__desc)
