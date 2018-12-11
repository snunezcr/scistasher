# Copyright @ 2018
#
# Santiago Nunez-Corrales <snunezcr@gmail.com>
# A Scientific Reference Stasher (SciStash)
#
# This software is intended for personal use and does not imply any guarantees
# in functionality or performance.
from scistash.entities.attachment import Attachment


class Tag(Attachment):
    table = 'tags'

    def __init__(self, objid, text: str):
        super().__init__(objid, text)

    def __str__(self):
        return '==> Tag: {2}\n\t{0} {1}'.format(self.objid, self.content, self.id)

    def stringify(self):
        return str(self.objid)+self.content
