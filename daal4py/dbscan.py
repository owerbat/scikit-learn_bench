# Copyright (C) 2020 Intel Corporation
#
# SPDX-License-Identifier: MIT

import argparse
from bench import parse_args, time_mean_min, load_data, print_output
from daal4py import dbscan
from daal4py.sklearn.utils import getFPType

parser = argparse.ArgumentParser(description='daal4py DBSCAN clustering '
                                             'benchmark')
parser.add_argument('-e', '--eps', '--epsilon', type=float, default=10.,
                    help='Radius of neighborhood of a point')
parser.add_argument('-m', '--min-samples', default=5, type=int,
                    help='The minimum number of samples required in a '
                    'neighborhood to consider a point a core point')
params = parse_args(parser, prefix='daal4py')

# Load generated data
X, _, _, _ = load_data(params, add_dtype=True)


# Define functions to time
def test_dbscan(X):
    algorithm = dbscan(
        fptype=getFPType(X),
        epsilon=params.eps,
        minObservations=params.min_samples,
        resultsToCompute='computeCoreIndices'
    )
    return algorithm.compute(X)


columns = ('batch', 'arch', 'prefix', 'function', 'threads', 'dtype', 'size',
           'n_clusters', 'time')

# Time clustering
time, result = time_mean_min(test_dbscan, X,
                             outer_loops=params.outer_loops,
                             inner_loops=params.inner_loops,
                             goal_outer_loops=params.goal,
                             time_limit=params.time_limit,
                             verbose=params.verbose)
params.n_clusters = int(result.nClusters[0, 0])

print_output(library='daal4py', algorithm='dbscan', stages=['training'],
             columns=columns, params=params, functions=['DBSCAN'],
             times=[time], accuracies=[None], accuracy_type=None, data=[X])
