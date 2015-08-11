from __future__ import division
import random

from miscellaneous.various_stuff import multi_max
from stochastic_process.processes import MarkovProcess


class Hierarchy(object):
    def __init__(self, lrn_rate, dsc_rate, min_likelihood, level=0):
        self.lrn_rate = lrn_rate
        self.dsc_rate = dsc_rate
        self.min_likelihood = min_likelihood
        self.level = level

        self.last_pair = None
        self.last_observation = None
        self.template_policy = MarkovProcess(lrn_rate, dsc_rate)
        self.all_states = set()
        self.caching_policy = MarkovProcess(lrn_rate, dsc_rate)
        self.cdr = 0.
        self.parent = None

    def __str__(self):
        out_str = "Structure: %s\n\n" % (self.get_structure())
        pivot = self
        level = 0
        while pivot is not None:
            out_str += "LEVEL %s\n" % (level, )
            for each_state in pivot.all_states:
                out_str += str(each_state) + "\n"
            out_str += "\n"
            pivot = pivot.parent
            level += 1
        return out_str

    def get_level(self):
        return self.level

    def get_structure(self):
        structure = []
        tagged = self
        while tagged is not None:
            structure.append(len(tagged.all_states))
            tagged = tagged.parent
        return structure

    def get_total_frequency(self, pair, state):
        return self.template_policy.get_frequency(pair, state) + self.caching_policy.get_frequency(pair, state)

    def get_total_likelihood(self, pair, state):
        total_sum = 0

        caching_value = 0
        if pair in self.caching_policy.transitions:
            sub_dict = self.caching_policy.transitions[pair]
            if state in sub_dict:
                caching_value = sub_dict[state]
                total_sum += sum(sub_dict.values())

        template_value = 0
        if pair in self.template_policy.transitions:
            sub_dict = self.template_policy.transitions[pair]
            if state in sub_dict:
                template_value = sub_dict[state]
                total_sum += sum(sub_dict.values())

        if total_sum < 1:
            return 1.

        return (caching_value + template_value) / total_sum

    def _get_next_state(self, pair, sub_pair, sub_state):
        key_func = lambda x: self.get_total_likelihood(pair, x) * x.get_transition_likelihood(sub_pair, sub_state)
        candidates, _ = multi_max(self.all_states, key=key_func)
        return random.choice(candidates)

    def _new_layer(self):
        return Hierarchy(self.lrn_rate, self.dsc_rate, self.min_likelihood, level=self.level+1)

    def _is_breakdown(self, state):
        value = 0
        sum_of_max = 0

        if self.last_pair in self.caching_policy.transitions:
            sub_dict = self.caching_policy.transitions[self.last_pair]
            value += sub_dict.get(state, 0)
            sum_of_max += max(sub_dict.values())

        if self.last_pair in self.template_policy.transitions:
            sub_dict = self.template_policy.transitions[self.last_pair]
            value += sub_dict.get(state, 0)
            sum_of_max += max(sub_dict.values())

        return value < sum_of_max

    def _get_abstract_state(self, abstract_instance):
        if self.template_policy.get_process_likelihood(abstract_instance) >= self.min_likelihood:
            self.template_policy.process_integrate(abstract_instance)
            return self.template_policy

        candidates, likelihood = multi_max(self.parent.all_states, key=abstract_instance.get_process_likelihood)
        if likelihood >= self.min_likelihood:
            abstract_state = random.choice(candidates)
            abstract_state.process_integrate(abstract_instance)
            return abstract_state

        return abstract_instance

    def _recursion(self, state, reward):
        if self.parent is None:
            self.parent = self._new_layer()

        abstract_state = self._get_abstract_state(self.caching_policy)
        last_last_pair = self.last_observation[0]
        self.template_policy = self.parent.predict(abstract_state, last_last_pair, reward, self.last_pair, state)
        self.caching_policy = MarkovProcess(self.lrn_rate, self.dsc_rate)

        abstract_pair = abstract_state, last_last_pair

        return self.parent.template_policy.get_value(abstract_pair)

    def predict(self, state, action, reward, sub_pair, sub_state):
        self.all_states.add(state)

        pair = (state, action)
        if self.last_pair is None:
            next_state = state

        else:
            value = self.caching_policy.get_value(pair)
            if self.last_observation is not None:
                if self._is_breakdown(state):
                    value = self._recursion(state, self.cdr)
                    self.cdr = 0

            self.caching_policy.frequency_integrate(self.last_pair, state)
            #self.caching_policy.update_value(self.last_pair, reward, value)

            next_state = self._get_next_state(pair, sub_pair, sub_state)
            self.last_observation = (self.last_pair, state)

        self.last_pair = pair
        self.cdr = self.dsc_rate * self.cdr + reward
        return next_state


class HeatMappedHierarchy(Hierarchy):
    def __init__(self, lrn_rate, dsc_rate, min_likelihood, level=0):
        Hierarchy.__init__(self, lrn_rate, dsc_rate, min_likelihood, level=level)

    def _new_layer(self):
        return HeatMappedHierarchy(self.lrn_rate, self.dsc_rate, .0 ** (self.level + 1), level=self.level+1)

    def populate_heat_maps(self, x, y):
        self.template_policy.warm(x, y)
        if self.parent is not None:
            self.parent.populate_heat_maps(x, y)

    def get_heat_maps(self):
        return [x.heat_map for x in self.all_states]

    def get_heat_maps_recursively(self):
        all_heat_maps = list()
        mark = self
        while mark is not None:
            all_heat_maps += mark.get_heat_maps()
            mark = mark.parent
        return all_heat_maps
