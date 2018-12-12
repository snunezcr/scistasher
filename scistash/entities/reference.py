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

    def __init__(self, objid, refkey: uuid.UUID):
        super().__init__(objid, refkey)

    def __str__(self):
        return '==> Tag: {2}\n\t{0} {1}'.format(self.objid, self.content, self.id)

    def stringify(self):
        return str(self.objid)+str(self.content)
