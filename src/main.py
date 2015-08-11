import time
import datetime

from interaction.miscellaneous.various_stuff import create_dir
from interaction.model.model import Model
from interaction.agents.agent import NewAgent as Agent
from interaction.miscellaneous.environment import Labyrinth

#random.seed(618916)

print("started")
agent = Agent(lrn_rate=.1, dsc_rate=.5, min_likelihood=1.)

env = Labyrinth()
env.set_agent(agent)

for x in range(100000):
    #print env
    if x % 1000 == 0:
        print str(agent.get_structure())
    env.tick()

print str(agent)

out_dir = "../res/" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "/"
create_dir(out_dir)

with open(out_dir + "agent.txt", 'w') as out_file:
    out_file.write(Model.__str__(agent))

with open(out_dir + "heat_maps.txt", 'w') as out_file:
    for each_heat_map in agent.parent.get_heat_maps_recursively():
        out_file.write(str(each_heat_map.normalize()) + "\n")

mark = agent.parent
while mark is not None:
    level_dir = out_dir + "plots%02d/" % (mark.get_level(),)
    create_dir(level_dir)
    for each_heat_map in mark.get_heat_maps():
        each_heat_map.save_plot(directory=level_dir)
    mark = mark.parent


while True:
    print env
    env.tick()
    time.sleep(.1)