# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 10:57:45 2018

@author: Porosos

% given an input vector v (numpy array or list), a value "value" and a string kp (that has to be the word 'larger' or 'lower'), the function returns another vector with all components equal to the input vector except those that are lower or larger (depending on the input string) than value; those elements are assigned the value "value".

% example: v = [1, 2, 4, 2]
% keep(v, 3, 'larger') returns [3, 3, 4, 3]
% keep(v, 3, 'lower') returns [1, 2, 3, 2]

"""

def keep(v, value = 0, kp = 'larger'):
    r = []
    if kp == 'larger':    
        for s in v:
            if s > value:
                r.append(s)
            else:
                r.append(value)
    if kp == 'lower':
        for s in v:
            if s < value:
                r.append(s)
            else:
                r.append(value)
    
    return r
