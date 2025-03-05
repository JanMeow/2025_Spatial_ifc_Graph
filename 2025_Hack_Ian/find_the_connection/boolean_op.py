import numpy as np
import collision
"""
This module contains the boolean operations that are used for merging collision shapes
or touching shapes
# Task 
# Install conda, meshplot,libigl,PolyFem, 

1. Architect inputs IFC good/bad its not production ready anyways
2. Create product classes for the production companies 
3. Corner type menu, 
4. Component Matching Semi Touching the same type on the same floor, knowing floor thickness
5. (Here we are also not asking what if the type is not declared) minimal inner core, edge cases 
like range betweeen 100-150 then persay 300 wall can never be reached


Task for the week:
1. Get all touching wall type in a group
2. Perform boolean operation using the libraty

"""
def boolean_union(shape1, shape2):
    if collision.intersect(shape1, shape2):
        return np.vstack((shape1, shape2))
    print("Shapes are not intersecting")
    return
