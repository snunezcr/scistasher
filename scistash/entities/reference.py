# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
from scistash.entities.attachment import Attachment
import uuid


class Reference(Attachment):

    def __init__(self, objid, objcls, refkey: uuid.UUID, fdb: bool):
        super().__init__(objid, objcls, refkey)
        self.fromDB = fdb

    def __str__(self):
        return '==> Tag: {3}\n\t<{0},{1}> {2}'.format(self.objid, self.objcls, self.content, self.id)

    def stringify(self):
        return str(self.objid)+self.objcls+str(self.content)
