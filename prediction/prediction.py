# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 13:17:25 2014

@author: mark
"""
from __future__ import division
import random

from libraries.various_stuff import multi_max


SOT = "<"
EOT = ">"


class Mesh(object):
    def __init__(self):
        self.matrix = dict()
        
    def __str__(self):
        return "".join(self.to_trajectory())
    
    def to_trajectory(self, start=SOT):
        trajectory = [start]
        while trajectory[-1] in self.matrix.keys():
            trajectory.append(self.next_state(trajectory[-1]))
        
        return [str(x) for x in trajectory]
    
    def integrate(self, trajectory):
        for pos in range(len(trajectory)-1):
            from_state, to_state = trajectory[pos:pos+2]
            if from_state in self.matrix.keys():
                sub_dict = self.matrix[from_state]
                if to_state in sub_dict.keys():
                    sub_dict[to_state] += 1
                else:
                    sub_dict[to_state] = 1
            else:
                sub_dict = dict()
                sub_dict[to_state] = 1
                self.matrix[from_state] = sub_dict
    
    def compatibility(self, trajectory):
        matches = 0
        max_values = 0
        for pos in range(len(trajectory)-1):
            from_state, to_state = trajectory[pos:pos+2]
            if from_state in self.matrix.keys():
                sub_dict = self.matrix[from_state]
                if to_state in sub_dict.keys():
                    matches += sub_dict[to_state]
                max_values += max(sub_dict.values())
        
        comp = 1
        if max_values >= 1:
            comp = matches / max_values
        return comp
    
    def next_state(self, state):
        n = state
        if state in self.matrix.keys():
            sub_dict = self.matrix[state]
            max_keys, value = multi_max(sub_dict.keys(), key=lambda x: sub_dict[x])
            n = random.choice(max_keys)
        return n


class Predictor(object):
    def __init__(self, min_comp=1.):
        self.this_mesh = Mesh()
        self.next_mesh = self.this_mesh
        self.meshes = {self.this_mesh}
        self.trajectory = [SOT]
        self.parent = None
        self.min_comp = min_comp
        
    def __str__(self):
        return "\n\n".join({"\n".join([str(id(mesh)), str(mesh.to_trajectory(SOT))]) for mesh in self.meshes})
    
    def height(self):
        h = 1
        this_layer = self
        while not this_layer.parent is None:
            this_layer = this_layer.parent
            h += 1
        return h
        
    def no_all_meshes(self):
        this_layer = self
        r = [len(this_layer.meshes)]
        while not this_layer.parent is None:
            this_layer = this_layer.parent
            r.append(len(this_layer.meshes))
        return r
        
    def tot_no_meshes(self):
        return sum(self.no_all_meshes())
    
    def all_layers(self):
        this_layer = self
        this_level = 0
        r = ["level\t#meshes", "\t".join([str(this_level), str(len(this_layer.meshes))])]
        while not this_layer.parent is None:
            this_layer = this_layer.parent
            this_level += 1
            r.append("\t".join([str(this_level), str(len(this_layer.meshes))]))
        return "\n".join(r)

    def get_mesh(self, trajectory, adapt, comp_thresh):
        best_mesh = self.next_mesh
        max_meshes, max_comp = multi_max(self.meshes, key=lambda x: x.compatibility(trajectory))
        if not self.next_mesh in max_meshes:  # bias towards predicted mesh
            best_mesh = random.choice(max_meshes)

        if adapt:
            if max_comp < comp_thresh:
                best_mesh = Mesh()
                self.meshes.add(best_mesh)

            best_mesh.integrate(trajectory)
        return best_mesh

    def next_state(self, state):
        next_state = self.this_mesh.next_state(state)
        if next_state == EOT:
            next_state = self.next_mesh.next_state(SOT)
        return next_state
    
    def tick(self, state, adapt=True):
        if state in self.trajectory:
            self.trajectory.append(EOT)

            self.next_mesh = self.get_mesh(self.trajectory, adapt, self.min_comp)
            
            if self.parent is None and adapt and not self.next_mesh is self.this_mesh:
                self.parent = Predictor()
            
            if not self.parent is None:
                self.this_mesh = self.parent.tick(self.next_mesh, adapt=adapt)
                self.next_mesh = self.parent.next_state(self.this_mesh)
            
            self.trajectory = [SOT]
        
        self.trajectory.append(state)  # condition AND consequence

        return self.next_state(state)
    

if __name__ == "__main__":  
    pred = Predictor(min_comp=.5)
    sequence = "peter piper picked a peck of pickled peppers " \
               "a peck of pickled peppers peter piper picked " \
               "if peter piper picked a peck of pickled peppers " \
               "wheres the peck of pickled peppers peter piper picked "
    
    #sequence = "abracadabra"

    #sequence_data = open("sequences/anon_calls.txt", 'r')
    #sequence = [int(x[:-1]) for x in sequence_data.readlines()]
    #sequence = sequence[:1000]*5

    #sequence_data = open("sequences/charles_dexter_ward.txt", 'r')
    #sequence = sequence_data.read()[:1000]

    # diversity * tolerance / length
    
    reps = 100
    correct_preds = 0
    
    print "learning:"
    print "iteration\t#totmeshes\tprecision"

    prediction = []
    for i in range(reps):
        for j in range(len(sequence)):
            c = sequence[j]
            pc = pred.tick(c)
            prediction.append(pc)
            correct_preds += int(pc == sequence[(j+1) % len(sequence)])
         
        no_meshes = pred.tot_no_meshes()
        precision = round(correct_preds / len(sequence), 4)
        print "\t".join([str(i), str(no_meshes), str(precision)])
        correct_preds = 0
    print
    
    """
    print "original:"
    print sequence
    print
    
    print "online learning and generation:"
    print prediction[-len(sequence):]
    print
    
    print "online generation:"    
    prediction = []
    for i in range(reps):
        for j in range(len(sequence)):
            prediction.append(pred.tick(sequence[j], adapt=False))
            
    print prediction[-len(sequence):]
    print
    
    print "offline generation:"
    prediction = []
    c = sequence[0]
    for i in range(reps):
        for j in range(len(sequence)):
            prediction.append(c)
            c = pred.tick(c, adapt=False)
            
    print prediction[-len(sequence):]
    print
    """    
    
    print "structure:"
    print pred.no_all_meshes()
    print
