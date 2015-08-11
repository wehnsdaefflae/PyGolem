from __future__ import division
from interaction.miscellaneous.various_stuff import doubledict_to_string, dict_to_string
from heatmap import HeatMapPolicyMixin


class AbstractProcess(object):
    def __repr__(self):
        raise NotImplementedError("Method must be implemented.")

    def __str__(self):
        raise NotImplementedError("Method must be implemented.")

    def get_no_frequencies(self):
        raise NotImplementedError("Method must be implemented.")

    def frequency_integrate(self, pair, state):
        raise NotImplementedError("Method must be implemented.")

    def get_frequency(self, pair, state):
        raise NotImplementedError("Method must be implemented.")

    def process_integrate(self, other):
        raise NotImplementedError("Method must be implemented.")

    def get_transition_likelihood(self, pair, state):
        raise NotImplementedError("Method must be implemented.")

    def get_process_likelihood(self, other):
        raise NotImplementedError("Method must be implemented.")

    def get_theoretical_distribution(self):
        raise NotImplementedError("Method must be implemented.")

    def get_cols(self):
        raise NotImplementedError("Method must be implemented.")

    def get_rows(self):
        raise NotImplementedError("Method must be implemented.")


class StochasticProcess(AbstractProcess):
    def __init__(self):
        self.transitions = dict()

    def __repr__(self):
        return type(self).__name__ + str(id(self))

    def __str__(self):
        if len(self.transitions) == 0:
            return self.__repr__() + "\n<no transitions>"
        else:
            return doubledict_to_string(self.transitions, title=self.__repr__())

    def get_no_frequencies(self):
        return sum(sum(sub_dict.values()) for sub_dict in self.transitions.values())

    def get_frequency(self, pair, state):
        if pair not in self.transitions:
            return 0
        sub_dict = self.transitions[pair]
        return sub_dict.get(state, 0)

    def frequency_integrate(self, pair, state):
        if pair in self.transitions:
            sub_dict = self.transitions[pair]
            sub_dict[state] = sub_dict.get(state, 0) + 1
        else:
            sub_dict = dict()
            sub_dict[state] = 1
            self.transitions[pair] = sub_dict

    def process_integrate(self, other):
        assert isinstance(other, StochasticProcess)
        for other_pair, other_sub_dict in other.transitions.items():
            if other_pair in self.transitions:
                self_sub_dict = self.transitions[other_pair]
            else:
                self_sub_dict = dict()
                self.transitions[other_pair] = self_sub_dict
            for other_state, other_value in other_sub_dict.items():
                self_sub_dict[other_state] = self_sub_dict.get(other_state, 0) + other_value

    def get_theoretical_distribution(self):
        normalized = StochasticProcess()
        for each_key, sub_dict in self.transitions.items():
            transition_sum = sum(sub_dict.values())
            norm_sub_dict = dict()
            for each_sub_key, each_value in sub_dict.items():
                norm_sub_dict[each_sub_key] = each_value / transition_sum
            normalized.transitions[each_key] = norm_sub_dict
        return normalized

    def get_transition_likelihood(self, pair, state):
        if pair not in self.transitions:
            return 1.
        sub_dict = self.transitions[pair]
        return sub_dict.get(state, 0) / sum(sub_dict.values())

    def get_process_likelihood(self, observed_process):
        likelihood = 1.
        for each_pair, sub_dict in observed_process.transitions.items():
            if each_pair not in self.transitions.keys():
                continue
            self_sub_dict = self.transitions[each_pair]
            trans_sum = sum(self_sub_dict.values())
            for each_state, each_trans in sub_dict.items():
                likelihood *= (self_sub_dict.get(each_state, 0) / trans_sum) ** each_trans
        return likelihood

    def get_cols(self):
        return {x for sub_dict in self.transitions.values() for x in sub_dict.keys()}

    def get_rows(self):
        return set(self.transitions.keys())


class AbstractMarkovProcess(object):
    def update_value(self, pair, reward, value):
        raise NotImplementedError("Method must be implemented.")

    def get_value(self, pair):
        raise NotImplementedError("Method must be implemented.")


class MarkovProcess(StochasticProcess, HeatMapPolicyMixin, AbstractMarkovProcess):
    def __init__(self, lrn_rate, dsc_rate):
        StochasticProcess.__init__(self)
        HeatMapPolicyMixin.__init__(self)
        self.values = dict()
        self.lrn_rate = lrn_rate
        self.dsc_rate = dsc_rate

    def __str__(self):
        if len(self.values) == 0:
            str_values = "<no values>"
        else:
            str_values = dict_to_string(self.values, sort_key=lambda x: x)
        return "%s\n%s" % (StochasticProcess.__str__(self), str_values)

    def update_value(self, pair, reward, value):
        old_val = self.get_value(pair)
        self.values[pair] = old_val + self.lrn_rate * (reward + self.dsc_rate * value - old_val)

    def get_value(self, pair):
        return self.values.get(pair, 0.)

    def process_integrate(self, other):
        StochasticProcess.process_integrate(self, other)
        for other_pair, other_value in other.values.items():
            self_weight = 0
            other_weight = 0
            if other_pair in self.transitions:
                sub_dict = self.transitions[other_pair]
                self_weight = sum(sub_dict.values())
            if other_pair in other.transitions:
                sub_dict = other.transitions[other_pair]
                other_weight = sum(sub_dict.values())
            weight_sum = self_weight + other_weight

            if weight_sum >= 1:
                new_value = (self.values.get(other_pair, .0) * self_weight + other_value * other_weight) / weight_sum
                self.values[other_pair] = new_value