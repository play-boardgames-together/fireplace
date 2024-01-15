from typing import TYPE_CHECKING

from hearthstone.enums import Zone

from ..cards import db
from ..player import Player
from ..utils import CardList
from .bartender import Bartender
from .minion import BGS_Minion


if TYPE_CHECKING:
    from .game import BGS_Game


class RecruitPlayer(Player):
    def __init__(self, name):
        self.game: BGS_Game
        super().__init__(name, None, None)
        self.bartender = Bartender()

    def setup(self):
        self.prepare_for_game()
        self.max_mana = 3
        self.bartender.setup()

    def draw(self, count=1):
        pass

    def begin_turn(self):
        self.opponent = self.bartender
        self.bartender.begin_turn()

    def can_attack(self):
        for minion in self.field:
            if minion.atk and minion.attack_targets:
                return True
        return False

    def prepare_combat(self):
        self.temp_field = self.field
        self.field: list[BGS_Minion] = CardList()
        for temp_minion in self.temp_field:
            minion = BGS_Minion(db[temp_minion.id])
            minion.controller = self
            minion.zone_position = Zone.PLAY
            for buff in temp_minion.buffs:
                # Recreate the buff stack
                new_buff = self.card(buff.id)
                new_buff.source = buff.source
                attributes = ["atk", "max_health", "_xatk", "_xhealth", "_xcost", "store_card"]
                for attribute in attributes:
                    if hasattr(buff, attribute):
                        setattr(new_buff, attribute, getattr(buff, attribute))
                new_buff.apply(minion)
                if buff in self.game.active_aura_buffs:
                    new_buff.tick = buff.tick
                    self.game.active_aura_buffs.append(new_buff)
            for k in temp_minion.silenceable_attributes:
                v = getattr(temp_minion, k)
                setattr(minion, k, v)
            minion.silenced = temp_minion.silenced
            minion.damage = temp_minion.damage
        self.combat_iter = iter(self.combats)

    def clear_combat(self):
        self.field = self.temp_field
        self.temp_field = None
        self.combat_iter = None

    @property
    def combats(self):
        if len(self.field) == 0:
            return
        self.combat = None
        while len(self.field) > 0:
            if self.combat is self.field[-1] or self.combat is None:
                self.combat = self.field[0]
            else:
                self.combat = self.combat.right
            if self.combat:
                yield self.combat

    def get_combat_damage(self):
        return sum(minion.tech_level for minion in self.field) + self.bartender.tavern_tier
