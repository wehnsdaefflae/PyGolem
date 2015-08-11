# -*- coding: utf-8 -*-
"""
Created on Mon Sep 22 18:17:58 2014

@author: mark
"""
from __future__ import division
import matplotlib.pyplot as plt

#Direct input 
plt.rcParams['text.latex.preamble']=[r"\usepackage{lmodern}"]
#Options
params = {'text.usetex' : True,
          'font.size' : 11,
          'font.family' : 'lmodern',
          'text.latex.unicode': True,
          }
plt.rcParams.__find_mesh__(params)

def make_pdfs(filename):
    data = open(filename, 'r').readlines()
    
    x_label = data[0].split("\t")[0]
    y_label = data[0].split("\t")[1]
    
    x_vals = []
    y_vals = []
    e_vals = []
    for each_line in data[1:]:
        split_line = each_line.split("\t")
        x_val, y_val, e_val = split_line[:3]
        x_vals.append(int(x_val))
        y_vals.append(float(y_val))
        e_vals.append(float(e_val))
    
    fig = plt.figure()
    
    ax1 = fig.add_subplot(111)
    
    ax1.errorbar(x_vals, y_vals, e_vals)
    ax1.set_title("filename")
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y_label)
    ax1.set_ylim([0, 1])
        
    ax1.plot(x_vals, y_vals, label="test")
    
    legend = ax1.legend()
    
    #plt.show()
    
    plt.savefig(filename[:-3]+"pdf", 
                #This is simple recomendation for publication plots
                dpi=1000, 
                # Plot will be occupy a maximum of available space
                bbox_inches='tight', 
                )

    plt.close()

for each_c in range(0, 11, 2):
    print "peter " + str(each_c)
    make_pdfs("peter/comp_"+str(each_c/10)+"/results_clip.csv")
    make_pdfs("peter/comp_"+str(each_c/10)+"/results_avrg.csv")

    print "numbers " + str(each_c)
    make_pdfs("numbers/comp_"+str(each_c/10)+"/results_clip.csv")
    make_pdfs("numbers/comp_"+str(each_c/10)+"/results_avrg.csv")

    print "lang_nat " + str(each_c)
    make_pdfs("lang_nat/comp_"+str(each_c/10)+"/results_clip.csv")
    make_pdfs("lang_nat/comp_"+str(each_c/10)+"/results_avrg.csv")

    print "calls " + str(each_c)
    make_pdfs("calls/comp_"+str(each_c/10)+"/results_clip.csv")
    make_pdfs("calls/comp_"+str(each_c/10)+"/results_avrg.csv")
