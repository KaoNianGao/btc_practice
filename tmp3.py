# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 20:55:33 2023


"""

from def_class import FieldElement,Point,S256Point,G,N,hash256


e = int.from_bytes(hash256(b'my secret'), 'big')
z = int.from_bytes(hash256(b'my message'), 'big')

k = 1234567890

r = (k*G).x.num