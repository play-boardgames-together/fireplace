from typing import TYPE_CHECKING

from hearthstone.enums import Zone

from ..card import Minion


if TYPE_CHECKING:
    from .player import RecruitPlayer


class BGS_Minion(Minion):
    cannot_attack_heroes = True
    def __init__(self, data):
        self.controller: RecruitPlayer
        super().__init__(data)

    @property
    def left(self):
        if self.zone_position == 1:
            return None
        return self.controller.field[self.zone_position - 2]

    @property
    def right(self):
        if self.zone_position == len(self.controller.field):
            return None
        return self.controller.field[self.zone_position]

    def _set_zone(self, value):
        if self is self.controller.combat and value != Zone.PLAY:
            self.controller.combat = self.left
        return super()._set_zone(value)
