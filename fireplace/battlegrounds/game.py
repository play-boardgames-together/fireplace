import random
from typing import TYPE_CHECKING

from hearthstone.enums import GameTag

from ..actions import Hit
from ..dsl.copy import ExactCopy
from ..dsl.selector import FRIENDLY_MINIONS
from ..game import BaseGame
from ..utils import CardList
from .phase import Phase
from .player import RecruitPlayer
from .minion import BGS_Minion


class BGS_Game(BaseGame):
    def __init__(self, players: list[RecruitPlayer]):
        self.players = players
        super().__init__(players)
        self.phase = Phase.INVALID
        """
        | Tavern Tier | Copies of each minion |
        | - | - |
        | 1 | 23 |
        | 2 | 38 |
        | 3 | 32 |
        | 4 | 38 |
        | 5 | 38 |
        | 6 | 27 |
        """
        self.hero_pool = CardList()
        self.minion_pool = CardList()

    def setup(self):
        pass

    def start(self):
        pass

    def begin_turn(self):
        self.phase = Phase.RECRUIT
        for player in self.players:
            player.bartender.begin_turn()

    def end_turn(self):
        self.combat()
        self.begin_turn()

    def combat(self):
        self.phase = Phase.COMBAT
        for player in self.players:
            player.prepare_combat()
        # TODO FIXME
        random.shuffle(self.players)
        for i in range(0, 4, 2):
            self._combat(self.players[i], self.players[i+1])
        for player in self.players:
            player.clear_combat()

    def _combat(self, player1: RecruitPlayer, player2: RecruitPlayer):
        if len(self.player1.field) > len(self.player2.field):
            player1, player2 = player2, player1

        self.current_player = player1
        player1.opponent = player2
        player2.opponent = player1

        while player1.can_attack() or player2.can_attack():
            minion: BGS_Minion = next(self.current_player.combat_iter)
            if minion is None:
                continue
            for _ in minion.max_attacks:
                if minion.atk > 0 and not minion.should_exit_combat and minion.attack_targets:
                    self.attack(minion, random.choice(minion.attack_targets))
            self.game.current_player = self.game.current_player.opponent

        if len(player1.field) == 0 and len(player2.field) > 0:
            self.queue_actions(player2, [Hit(player1, player2.get_combat_damage())])
        elif len(player1.field) > 0 and len(player2.field) == 0:
            self.queue_actions(player1, [Hit(player2, player1.get_combat_damage())])
