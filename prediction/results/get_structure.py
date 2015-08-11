# -*- coding: utf-8 -*-
"""
generates a table of the structure of one exemplatory run
as csv file
"""

from collections import defaultdict

directory = "calls/comp_0.2"
file_name = "run0_full.csv"
data_in = open(directory + "/" + file_name, 'r')
lines = data_in.readlines()
data_in.close()

layer_dict = dict()
max_layer = -1

for each_line in lines[1:]:
    sep_line = each_line[:-1].split("\t")
    meshes_dict = defaultdict(lambda:0)
    len_line = len(sep_line)
    max_layer = max(max_layer, len_line - 2)
    for i in range(2, len_line):
        meshes_dict[i-2] = int(sep_line[i])
    it = int(sep_line[0])
    layer_dict[it] = meshes_dict

lines = []
line = ["iteration"]
line.extend(["l" + str(x) for x in range(max_layer)])
line = "\t".join(line)
line += "\n"
lines.append(line)

last_sub_dict = None
sorted_keys = sorted(layer_dict.keys())
for each_it in sorted_keys[:-1]:
    line = [str(each_it)]
    sub_dict = layer_dict[each_it]
    #print sub_dict
    for each_layer in range(max_layer):
        no_meshes = sub_dict[each_layer]
        line.append(str(no_meshes))
    line = "\t".join(line)
    line += "\n"
    if not sub_dict == last_sub_dict:
        lines.append(line)
    last_sub_dict = sub_dict

last_it = sorted_keys[-1]
line = [str(last_it)]
sub_dict = layer_dict[last_it]
for each_layer in layer_dict[last_it]:
    no_meshes = sub_dict[each_layer]
    line.append(str(no_meshes))
line = "\t".join(line)
line += "\n"
lines.append(line)

data_out = open(directory + "/" + file_name.split("_")[0] + "_structure.csv", 'w')
for each_line in lines:
    data_out.writelines(each_line)
data_out.close()

print
print "done"