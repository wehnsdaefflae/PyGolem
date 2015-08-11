from __future__ import division

import numpy
import matplotlib.pyplot as plt

from miscellaneous.various_stuff import doubledict_to_string


class HeatMap(dict):
    def __init__(self, name=None, *args, **kw_args):
        super(HeatMap, self).__init__(*args, **kw_args)
        if name is None:
            self.name = self.__repr__()
        else:
            self.name = name

    def __repr__(self):
        return type(self).__name__ + str(id(self))

    def __str__(self):
        return doubledict_to_string(self, title=self.name)

    def normalize(self):
        total = 0
        for each_sub_dict in self.values():
            total += sum(each_sub_dict.values())

        if total < 1:
            normalized_map = HeatMap(self)
            normalized_map.name = "n" + self.name
            return normalized_map

        normalized_map = HeatMap(name="n" + self.name)
        for each_key, each_sub_dict in self.items():
            if each_key in normalized_map:
                sub_dict = normalized_map[each_key]
            else:
                sub_dict = dict()
                normalized_map[each_key] = sub_dict
            for k, v in each_sub_dict.items():
                sub_dict[k] = v / total
        return normalized_map

    def update_value(self, x, y):
        if x in self:
            sub_dict = self[x]
        else:
            sub_dict = dict()
            self[x] = sub_dict

        sub_dict[y] = sub_dict.get(y, 0) + 1

    def save_plot(self, directory=None, name=None):
        if len(self) < 1:
            return

        x_max = max(self.keys())
        y_max = max(y for sub_dict in self.values() for y in sub_dict.keys())
        m = [[.0] * (y_max + 1) for _ in xrange(x_max + 1)]

        for x_key, sub_dict in self.items():
            for y_key, value in sub_dict.items():
                m[x_max - x_key][y_key] = value

        if name is None:
            name = self.name

        if directory is None:
            directory = ""
        elif not directory[-1] == "/":
            directory += "/"

        z = numpy.array(m)

        plt.subplot(1, 1, 1)
        plt.pcolor(z, cmap=plt.get_cmap("hot"))
        plt.title(name)

        plt.savefig(directory + name + ".png")


class HeatMapPolicyMixin(object):
    def __init__(self):
        self.heat_map = HeatMap(name="hmap" + self.__repr__())

    def warm(self, x, y):
        self.heat_map.update_value(x, y)