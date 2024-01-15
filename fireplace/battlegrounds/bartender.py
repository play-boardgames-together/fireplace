from typing import TYPE_CHECKING

from fireplace.dsl.selector import FRIENDLY_MINIONS

from ..cards.utils import Freeze
from ..player import Player


if TYPE_CHECKING:
    from .game import BGS_Game
    from .player import RecruitPlayer


class Bartender(Player):

    """
    | Tavern Tier | The number of minions offered |
    | - | - |
    | 1 | 3 |
    | 2 | 4 |
    | 3 | 4 |
    | 4 | 5 |
    | 5 | 5 |
    | 6 | 6 |
    """
    MINION_OFFERED = {
        0: 0,
        1: 3,
        2: 4,
        3: 4,
        4: 5,
        5: 5,
        6: 6,
    }

    """
    | Tavern Tier | Base Cost |
    | - | - |
    | 2 | 5 |
    | 3 | 7 |
    | 4 | 8 |
    | 5 | 11 |
    | 6 | 10 |
    """
    UPGRADE_BASE_COST = {
        0: 0,
        1: 0,
        2: 5,
        3: 7,
        4: 8,
        5: 11,
        6: 10,
    }

    def __init__(self, player):
        super().__init__("Bartender Bob", None, "DALA_BOSS_99h")
        self.player: RecruitPlayer = player
        self.game: BGS_Game = player.game
        self.tavern_tier = 0
        self._upgrade_cost = 0
        self.freeze_times = 0

    @property
    def upgrade_cost(self):
        return self._upgrade_cost

    @upgrade_cost.setter
    def upgrade_cost(self, value):
        self._upgrade_cost = max(value, 0)

    def _recruit_one(self):
        return self.game.minion_pool.pop(tavern_tier=list(range(self.tavern_tier + 1)))

    def recruit(self):
        while len(self.field) < self.MINION_OFFERED[self.tavern_tier]:
            self.summon(self._recruit_one)

    def refresh(self):
        self.player.pay_cost(1)
        for card in self.field[:]:
            card.frozen = False
            card.remove()
            self.game.minion_pool.append(card)
        self.recruit()

    def can_refresh(self):
        if not self.can_refresh():
            return
        return self.can_pay_cost(1)

    def upgrade(self):
        if not self.can_upgrade():
            return
        self.player.pay_cost(self.upgrade_cost)
        self.tavern_tier += 1
        self.upgrade_cost = self.UPGRADE_BASE_COST[self.tavern_tier]

    def can_upgrade(self):
        return self.player.can_pay_cost(self.upgrade_cost)

    def freeze(self):
        if not self.can_freeze():
            return
        self.player.pay_cost(0)
        self.freeze_times -= 1
        if self.field.filter(frozon=False):
            for card in self.field:
                card.frozon = True
        else:
            for card in self.field:
                card.frozon = False
        for card in self.field:
            card.frozen = True

    def can_freeze(self):
        return self.freeze_times > 0

    def setup(self):
        super().prepare_for_game()
        self.upgrade()
        self.recruit()

    def begin_turn(self):
        for card in self.field.filter(frozon=False):
            card.remove()
            self.game.minion_pool.append(card)
        for card in self.field:
            card.frozne = False
        self.recruit()
        self.upgrade_cost -= 1
        self.freeze_times = 5
