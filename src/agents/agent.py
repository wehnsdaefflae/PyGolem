import os
import random

from model.hierarchy import HeatMappedHierarchy
from miscellaneous.various_stuff import multi_max

__author__ = 'wernsdorfer'


class NewAgent(HeatMappedHierarchy):
    def __init__(self, actions, epsilon=.1, eps_decay=1., lrn_rate=.1, dsc_rate=.5, min_likelihood=1.):
        HeatMappedHierarchy.__init__(self, lrn_rate, dsc_rate, min_likelihood)
        self.actions = actions
        self.epsilon = epsilon
        self.eps_decay = eps_decay
        self.iteration = 0
        self.episode = 0
        self.log_data = ["iteration\tepisode\treward\n"]
        self.parent = self._new_layer()

    def __repr__(self):
        return type(self).__name__ + str(id(self))

    def __str__(self):
        return HeatMappedHierarchy.__str__(self)

    def log(self, reward):
        this_line = (self.iteration, self.episode, reward)
        self.log_data.append("%s\t%s\t%s\n" % this_line)

    def store_results(self, directory, filename):
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(directory + filename, 'w') as logfile:
            logfile.writelines(self.log_data)

    def store_state(self, directory, filename):
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(directory + filename, 'w') as target_file:
            target_file.write(str(self))

    def episode_reset(self):
        self.episode += 1

    def get_motor(self, state, reward):
        motor = self._react(state, reward)
        self.log(reward)
        self.iteration += 1
        self.epsilon *= self.eps_decay
        return motor

    def _get_next_motor(self, state):
        candidates, _ = multi_max([(state, a) for a in self.actions], key=self.template_policy.get_value)
        _, motor = random.choice(candidates)
        return motor

    def _react(self, state, reward):
        self.all_states.add(state)

        if self.last_pair is None:
            motor, = random.sample(self.actions, 1)
            pair = (state, motor)

        else:
            if random.random() < self.epsilon:
                motor, = random.sample(self.actions, 1)
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
