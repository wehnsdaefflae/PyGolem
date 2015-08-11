# -*- coding: utf-8 -*-
"""
averages the full prediction data into segments of length "sampling_steps"
and
averages a segment "clipping" of the prediction data
into segments of length "clipping_ssteps"
as csv file
"""
from __future__ import division
import os
from collections import defaultdict
import math

directory = "peter"
sampling_steps = 192            # single_sequence length

#directory = "numbers"
#sampling_steps = 2500           # single_sequence length

#directory = "lang_nat"
#sampling_steps = 1000           # single_sequence length

#directory = "calls"
#sampling_steps = 1205           # single_sequence length

n = 0                           # get n-th sequence iteration
clipping = (n * sampling_steps, (n+1) * sampling_steps)
clipping_ssteps = (sampling_steps + 1) // 20 # average over 20 segments

comp_dirs = os.walk(directory).next()[1]
for each_comp in comp_dirs:
    full_comp_dir = directory + "/" + each_comp
    all_onlp_vals = defaultdict(lambda:[])
    clipping_vals = defaultdict(lambda:[])
    
    for each_runfile in os.listdir(full_comp_dir):
        file_data = open(full_comp_dir + "/" + each_runfile, 'r').readlines()[1:]
        
        succ_sum_abs = 0
        succ_sum_clp = 0
        for each_line in file_data:
            split_line = each_line[:-1].split("\t")
            each_it = int(split_line[0])
            each_suc = float(split_line[1])
            succ_sum_abs += each_suc
            succ_sum_clp += each_suc
            
            if (clipping[1] > each_it >= clipping[0]) and (each_it % clipping_ssteps == 0):
                clipping_vals[each_it].append(round(succ_sum_clp / clipping_ssteps, 4))
                succ_sum_clp = 0
                
            if each_it % sampling_steps == 0:
                all_onlp_vals[each_it].append(round(succ_sum_abs / sampling_steps, 4))
                succ_sum_abs = 0

    avrg_onlp = dict()
    for each_it, each_lst in all_onlp_vals.items():
        avrg_val = sum(each_lst) / len(each_lst)
        error = 0
        for each_val in each_lst:
            error += math.pow(each_val - avrg_val, 2)
        error /= len(each_lst) - 1
        error = math.sqrt(error)
        avrg_onlp[each_it] = (round(avrg_val, 4), round(error, 4))
    
    avrg_onlp_data = open(full_comp_dir+"/results_avrg.csv", 'w')
    avrg_onlp_data.writelines("iteration\tsuccess\terror\n")
    for i in sorted(avrg_onlp.keys()):
        values = avrg_onlp[i]
        avrg_onlp_data.writelines(str(i)+"\t"+"\t".join([str(x) for x in values])+"\n")
    avrg_onlp_data.close()
    
    avrg_clip = dict()
    for each_it, each_lst in clipping_vals.items():
        avrg_val = sum(each_lst) / len(each_lst)
        error = 0
        for each_val in each_lst:
            error += math.pow(each_val - avrg_val, 2)
        error /= len(each_lst) - 1
        error = math.sqrt(error)
        avrg_clip[each_it] = (round(avrg_val, 4), round(error, 4))
    
    avrg_clip_data = open(full_comp_dir+"/results_clip.csv", 'w')
    avrg_clip_data.writelines("iteration\tsuccess\terror\n")
    for i in sorted(avrg_clip.keys()):
        values = avrg_clip[i]
        avrg_clip_data.writelines(str(i)+"\t"+"\t".join([str(x) for x in values])+"\n")
    avrg_clip_data.close()
    
print
print "done"
