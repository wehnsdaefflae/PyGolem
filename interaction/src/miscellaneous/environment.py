import os


class AgentClass(object):
    def __init__(self, epsilon, eps_decay):
        self.epsilon = epsilon
        self.eps_decay = eps_decay

        self.actions = None
        self.iteration = 0
        self.episode = 0
        self.log_data = ["iteration\tepisode\treward\n"]

    def __repr__(self):
        return type(self).__name__ + str(id(self))

    def __str__(self):
        raise NotImplementedError("Method must be implemented.")

    def _react(self, state, reward):
        raise NotImplementedError("Method must be implemented.")

    def get_motor(self, state, reward):
        motor = self._react(state, reward)
        self.log(reward)
        self.iteration += 1
        self.epsilon *= self.eps_decay
        return motor

    def _episode_reset(self):
        pass

    def episode_reset(self):
        self._episode_reset()
        self.episode += 1

    def set_motor_actions(self, actions):
        self.actions = actions

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


class Labyrinth(object):
    def __init__(self):
        # task
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

        #self.start_pos = (0, 3)
        #self.grid_map = [['x', 'x', 'x', 'x', 'x'],
        #                 ['x', 'x', 'x', '.', 'x'],
        #                 ['x', '.', '.', '.', 'x'],
        #                 ['.', '.', 'x', '.', '.'],
        #                 ['x', '.', 'x', 'x', 'x'],
        #                 ['x', 'x', 'x', 'x', 'x']]

        #self.start_pos = (1, 1)
        #self.grid_map = [['x', 'x', 'x', 'x', 'x', 'x'],
        #                 ['x', '.', '.', '.', '.', 'x'],
        #                 ['x', '.', '.', '.', '.', 'x'],
        #                 ['x', '.', '.', '.', '.', 'x'],
        #                 ['x', '.', '.', '.', '.', 'x'],
        #                 ['x', 'x', 'x', 'x', 'x', 'x']]

        self.agent_pos = self.start_pos
        self.actions = ['n', 'e', 's', 'w']
        self.height = len(self.grid_map)
        self.width = len(self.grid_map[0])

        self.this_reward = 0

        self.agent = None
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

    def set_agent(self, agent):
        if not isinstance(agent, AgentClass):
            raise TypeError("Class of agent must be inherited from tasks.AgentClass."
                            "Is %s instead." % (str(type(agent), )))
        self.agent = agent
        self.agent.set_motor_actions(self.actions)
        self.intended_action = self.agent.get_motor(self.this_sensor, self.this_reward)

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