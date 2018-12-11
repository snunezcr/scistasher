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
    table = 'files'

    def __init__(self, objid, path: Path, ftyp: str, desc: str):
        self.__fname = path.name
        self.__fsize = path.stat().st_size
        self.__ftype = ftyp
        self.__desc = desc
        super().__init__(objid, path.read_bytes())

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
        return str(self.id) + str(self.objid) + self.__fname + self.__ftype + self.__desc + str(self.content)

    def __str__(self):
        return super(Attachment, self).__str__() + \
               '==> Reference file: {0}\n\tReferee: {1}\n\tName: {2}\n\tSize: {3}\n\tType: {4}\n\tDescription: {5}\n'.format(
                   self.id,
                   self.objid,
                   self.__fname,
                   str(self.__fsize),
                   self.__ftype,
                   self.__desc)
