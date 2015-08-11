import random

from interaction.model.model import HeatMappedModel
from interaction.miscellaneous.environment import AgentClass
from interaction.miscellaneous.various_stuff import multi_max


__author__ = 'wernsdorfer'


class NewAgent(AgentClass, HeatMappedModel):
    def __init__(self,
                 epsilon=.1, eps_decay=1.,
                 lrn_rate=.1, dsc_rate=.5,
                 min_likelihood=1.):
        AgentClass.__init__(self, epsilon, eps_decay)
        HeatMappedModel.__init__(self, lrn_rate, dsc_rate, min_likelihood)
        self.parent = self._new_layer()

    def __str__(self):
        return HeatMappedModel.__str__(self)

    def _get_next_motor(self, state):
        candidates, _ = multi_max([(state, a) for a in self.actions], key=self.template_policy.get_value)
        _, motor = random.choice(candidates)
        return motor

    def _react(self, state, reward):
        self.all_states.add(state)

        if self.last_pair is None:
            motor = random.choice(self.actions)
            pair = (state, motor)

        else:
            if random.random() < self.epsilon:
                motor = random.choice(self.actions)
            else:
                motor = self._get_next_motor(state)

            pair = (state, motor)
            value = self.caching_policy.get_value(pair)

            if self.last_observation is not None:
                if self._is_breakdown(state):
                    value = self._recursion(state, self.cdr)
                    self.cdr = 0

            self.caching_policy.frequency_integrate(self.last_pair, state)
            #self.caching_policy.update_value(self.last_pair, reward, value)

            self.last_observation = (self.last_pair, state)

        self.last_pair = pair
        self.cdr = self.dsc_rate * self.cdr + reward
        return motor