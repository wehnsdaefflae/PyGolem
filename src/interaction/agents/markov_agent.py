import random

from interaction.miscellaneous.environment import AgentClass
from interaction.model.processes import MarkovProcess
from miscellaneous.various_stuff import multi_max


class Agent(AgentClass):
    def __init__(self, epsilon=.1, eps_decay=1, lrn_rate=.1, dsc_rate=.5, on_policy=True):
        AgentClass.__init__(self, epsilon, eps_decay)
        self.caching_policy = MarkovProcess(lrn_rate, dsc_rate)
        self.on_policy = on_policy
        self.last_pair = None

    def __str__(self):
        return str(self.caching_policy.__repr__())

    def _get_best_motor(self, state):
        candidates, _ = multi_max([(state, a) for a in self.actions], key=self.caching_policy.get_value)
        _, motor = random.choice(candidates)
        return motor

    def _react(self, state, reward):
        if self.last_pair is None:
            motor = random.choice(self.actions)
            pair = (state, motor)

        else:
            if random.random() < self.epsilon:
                motor = random.choice(self.actions)
                pair = (state, motor)
                if self.on_policy:
                    value = self.caching_policy.get_value(pair)
                else:
                    tmp_pair = (state, self._get_best_motor(state))
                    value = self.caching_policy.get_value(tmp_pair)
            else:
                motor = self._get_best_motor(state)
                pair = (state, motor)
                value = self.caching_policy.get_value(pair)

            self.caching_policy.update_value(self.last_pair, reward, value)

        self.last_pair = pair
        return motor