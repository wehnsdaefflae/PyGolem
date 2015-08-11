import time
import datetime

from miscellaneous.various_stuff import create_dir
from hierarchy.hierarchy import Hierarchy

__author__ = 'wernsdorfer'


from agent import NewAgent as Agent


class Labyrinth(object):
    def __init__(self):
        self.agent = Agent({'n', 'e', 's', 'w'}, lrn_rate=.1, dsc_rate=.5, min_likelihood=1.)

        self.start_pos = (0, 1)
        self.grid_map = [['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                         ['.', '.', '.', '.', 'x', '.', 'x', '.', '.', '.', 'x'],
                         ['x', 'x', 'x', '.', 'x', '.', 'x', '.', 'x', '.', 'x'],
                         ['x', '.', '.', '.', 'x', '.', '.', '.', 'x', '.', 'x'],
                         ['x', '.', 'x', 'x', 'x', '.', 'x', '.', 'x', '.', 'x'],
                         ['x', '.', '.', '.', '.', '.', 'x', '.', 'x', '.', 'x'],
                         ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', '.', 'x'],
                         ['x', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'x'],
                         ['x', '.', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                         ['x', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'g'],
                         ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]

        self.agent_pos = self.start_pos
        self.height = len(self.grid_map)
        self.width = len(self.grid_map[0])

        self.this_reward = 0

        self.this_sensor = self.__get_sensors__()
        self.intended_action = None

    def __str__(self):
        full_str_lst = ["\t " + " ".join([str(x) for x in range(self.width)])]

        for y in range(len(self.grid_map)):
            each_line = self.grid_map[y]
            line_lst = [str(y) + "\t"]
            for x in range(len(each_line)):
                if (x, y) == self.agent_pos:
                    line_lst.append("#")
                else:
                    line_lst.append(str(each_line[x]))

            full_str_lst.append(" ".join(line_lst))

        full_str_lst.append("\n")
        full_str_lst.append("\t".join(["perception:", str(self.this_sensor)]))
        full_str_lst.append("\t".join(["intention:", str(self.intended_action)]))
        full_str_lst.append("\t\t".join(["reward:", str(self.this_reward)]))
        full_str_lst.append("\t".join(["iteration:", str(self.agent.iteration)]))
        full_str_lst.append("\n")

        return "\n".join(full_str_lst)

    def __get_sensors__(self):
        agent_x, agent_y = self.agent_pos
        n = not self.grid_map[(agent_y-1) % self.height][agent_x] == 'x'
        e = not self.grid_map[agent_y][(agent_x+1) % self.width] == 'x'
        s = not self.grid_map[(agent_y+1) % self.height][agent_x] == 'x'
        w = not self.grid_map[agent_y][(agent_x-1) % self.width] == 'x'
        return n, e, s, w

    def _get_sensors__(self):
        return self.agent_pos

    def tick(self):
        agent_x, agent_y = self.agent_pos

        self.agent.populate_heat_maps(agent_y, agent_x)

        if self.intended_action == "n":
            agent_y = (agent_y - 1) % (self.height - 1)
        elif self.intended_action == "e":
            agent_x = (agent_x + 1) % (self.width - 1)
        elif self.intended_action == "s":
            agent_y = (agent_y + 1) % (self.height - 1)
        elif self.intended_action == "w":
            agent_x = (agent_x - 1) % (self.width - 1)

        target_cell = self.grid_map[agent_y][agent_x]
        last_x = self.agent_pos[0]

        self.this_reward = 0
        if target_cell == "x":
            self.this_reward = -5

        elif target_cell == "g":
            self.this_reward = 10
            self.agent_pos = self.start_pos

        elif target_cell == "d":
            self.this_reward = -10
            self.agent_pos = self.start_pos

        else:
            this_x = self.agent_pos[0]
            #self.this_reward = (this_x - (last_x + 1)) % -(self.width-1)
            self.this_reward = 0
            self.agent_pos = (agent_x, agent_y)

        self.this_sensor = self.__get_sensors__()
        self.intended_action = self.agent.get_motor(self.this_sensor, self.this_reward)


if __name__ == "__main__":
    w = Labyrinth()

    for x in range(100000):
        #print env
        if x % 1000 == 0:
            print str(w.agent.get_structure())
        w.tick()

    print str(w.agent)

    out_dir = "../res/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "/"
    create_dir(out_dir)

    with open(out_dir + "agent.txt", 'w') as out_file:
        out_file.write(Hierarchy.__str__(w.agent))

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
