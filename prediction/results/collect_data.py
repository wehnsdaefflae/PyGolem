# -*- coding: utf-8 -*-
"""
generates full prediction data on various sequences
as csv file
"""
from __future__ import division
import prediction
import os
import time
import languagefromgrammar as lfg

target_dir = "peter" # len = 192
single_seq = "peter piper picked a peck of pickled peppers a peck of pickled peppers peter piper picked if peter piper picked a peck of pickled peppers wheres the peck of pickled peppers peter piper picked "

#target_dir = "numbers" # len = 2500
#single_seq = "0"
#tmp_seq = ""
#num_dict = {"0": "4431", "1": "1012", "2": "2323", "3": "4021", "4": "0310"}
#for i in range(5):
#    for c in single_seq:
#        tmp_seq += num_dict[c]
#    single_seq = tmp_seq

#target_dir = "lang_nat" # len = 1000
#lang_data = open("sequences/charles_dexter_ward.txt", 'r')
#single_seq = lang_data.read()[:1000]
#lang_data.close()

#target_dir = "calls" # len = 1205
#call_data = open("sequences/anon_calls.txt", 'r')
#call_data_lines = call_data.readlines()
#call_data.close()
#single_seq = [int(x[:-1]) for x in call_data_lines]

#target_dir = "lang_art"
#single_seq = ""
#rules = {('S', 'A'), ('S', 'B'), ('A', 'anC'), ('C', 'nC'), ('C', 'b'), ('B', 'cnD'), ('D', 'nD'), ('D', 'd')}
#for word in lfg.make_no_words(1000, rules):
#    single_seq += word
    
#target_dir = "test"
#single_seq = "a"*1000

repetitions = 20
sequence = single_seq * repetitions

runs = 10
comp_steps = [2*x/10 for x in range(6)]

print target_dir

for this_comp in comp_steps:
    print " ".join([str(this_comp), "in", str(comp_steps)])

    directory = target_dir + "/comp_"+str(this_comp)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for r in range(runs):
        print "\t"+" ".join([str(r), "of", str(runs), "runs"])
        
        pred = prediction.Predictor(min_comp=this_comp)

        start_time = time.clock()
        
        lines = ["iteration\tsuccess\tmeshes\n"]
        p = None
        for i in range(len(sequence)+1):
            line_info = [i, int(p == sequence[i % len(sequence)])]
            line_info.extend(pred.no_all_meshes())
            line = "\t".join([str(entry) for entry in line_info])
            lines.append(line + "\n")

            p = pred.tick(sequence[i % len(sequence)])
            if time.clock() - start_time >= 5:
                print "\t\t"+str(round(i * 100 / len(sequence), 4))
                start_time = time.clock()
            
        tmp_str = "%0" + str(len(str(runs-1))) + "d"
        r_str = str(tmp_str % (r,))
        data_file = open(directory+"/run"+r_str+"_full.csv", 'w')
        data_file.writelines(lines)
        data_file.close()
