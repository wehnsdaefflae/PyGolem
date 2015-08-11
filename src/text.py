import time
import datetime

from miscellaneous.various_stuff import create_dir
from hierarchy.hierarchy import Hierarchy

__author__ = 'wernsdorfer'


from agent import NewAgent as Agent


class Labyrinth(object):
    def __init__(self):
        self.agent = Agent({True}, lrn_rate=.1, dsc_rate=.5, min_likelihood=1.)

        self.start_pos = 0
        self.text = "peter piper picked a peck of pickled peppers a peck of pickled peppers peter piper picked if peter piper picked a peck of pickled peppers wheres the peck of pickled peppers peter piper picked "
        self.agent_pos = self.start_pos
        self.length = len(self.text)

        self.this_sensor = self.__get_sensors__()
        self.intended_action = None

    def __get_sensors__(self):
        return self.text[self.agent_pos]

    def tick(self):
        if self.intended_action:
            self.agent_pos = (self.agent_pos + 1) % self.length
        else:
            self.agent_pos = (self.agent_pos - 1) % self.length

        self.this_sensor = self.__get_sensors__()
        self.intended_action = self.agent.get_motor(self.this_sensor, 0)


if __name__ == "__main__":
    w = Labyrinth()

    for x in range(100000):
        #print env
        if x % 1000 == 0:
            print str(w.agent.get_structure())
        w.tick()

    #print str(w.agent)

    out_dir = "../res/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "/"
    create_dir(out_dir)

    with open(out_dir + "agent.txt", 'w') as out_file:
        out_file.write(Hierarchy.__str__(w.agent))

    exit()

    with open(out_dir + "heat_maps.txt", 'w') as out_file:
        for each_heat_map in w.agent.parent.get_heat_maps_recursively():
            out_file.write(str(each_heat_map.normalize()) + "\n")

    mark = w.agent.parent
    while mark is not None:
        level_dir = out_dir + "plots%02d/" % (mark.get_level(),)
        create_dir(level_dir)
        for each_heat_map in mark.get_heat_maps():
            each_heat_map.save_plot(directory=level_dir)
        mark = mark.parent

    while True:
        print w
        w.tick()
        time.sleep(.1)
