import argparse
import ast
import itertools
from itertools import permutations
from sys import maxsize

import numpy as np
from pyproj import Proj
from shapely.geometry import LineString, MultiLineString, Point

points = [
    {"latitude": 37.1726668, "longitude": -3.5996359},
    {"latitude": 37.178399, "longitude": -3.599734},
    {"latitude": 37.170009, "longitude": -3.599067},
    {"latitude": 37.173849, "longitude": -3.60304},
    {"latitude": 37.1743, "longitude": -3.602934},
    {"latitude": 37.174385, "longitude": -3.603439},
    {"latitude": 37.174771, "longitude": -3.606839},
    {"latitude": 37.177224, "longitude": -3.603417},
]

avoid_points = [
    {"latitude": 37.175918, "longitude": -3.605083},
    {"latitude": 37.175180, "longitude": -3.598421},
    {"latitude": 37.180668, "longitude": -3.599708},
]

# implementation of traveling Salesman Problem
def travellingSalesmanProblem(graph, s):

    # store all vertex apart from source vertex
    vertex = []
    for i in range(graph.shape[0]):
        if i != s:
            vertex.append(i)

    # store minimum weight Hamiltonian Cycle
    min_path = maxsize
    next_permutation = permutations(vertex)
    for i in next_permutation:

        # store current Path weight(cost)
        current_pathweight = 0

        # compute current path weight
        k = s
        for j in i:
            current_pathweight += graph[k][j]
            k = j
        current_pathweight += graph[k][s]

        # update minimum
        if current_pathweight < min_path:
            path = str(i)
        min_path = min(min_path, current_pathweight)

    return min_path, path


# Driver Code
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start", default=0, help="Point where the problem starts", type=int
    )
    args = parser.parse_args()
    start = args.start

    p = Proj(proj="utm", zone=10, ellps="WGS84", units="m")

    points_good = [p(point["longitude"], point["latitude"]) for point in points]
    points_good = [Point(point) for point in points_good]
    points_bad = [p(point["longitude"], point["latitude"]) for point in avoid_points]
    # avoid points are created with a radius of 200 meters,
    points_bad = [Point(point).buffer(200) for point in points_bad]

    # create distance matrix, avoiding forbidden areas. Connections that
    # go though avoid zones are set to ~inf
    distance_matrix = np.zeros((len(points), len(points)))
    for ix1, ix2 in itertools.combinations(np.arange(len(points)), 2):
        point1 = points_good[ix1]
        point2 = points_good[ix2]
        line = LineString([point1, point2])
        emptiness = []
        for point_bad in points_bad:
            emptiness.append(point_bad.intersection(line).is_empty)
        if all(emptiness):
            distance_matrix[ix1, ix2] = line.length
            distance_matrix[ix2, ix1] = line.length
        else:
            distance_matrix[ix1, ix2] = 999999999
            distance_matrix[ix2, ix1] = 999999999

    min_dist, min_path = travellingSalesmanProblem(distance_matrix, start)
    x = list(ast.literal_eval(min_path))
    x.insert(0, start)
    print("Distance travelled on shortest path: ", min_dist)
    print("Shortest path: ", x)
