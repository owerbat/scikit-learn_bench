#===============================================================================
# Copyright 2020-2021 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bench
import numpy as np
from sklearn.metrics import accuracy_score

parser = argparse.ArgumentParser(
    description='scikit-learn kNN classifier benchmark')

parser.add_argument('--task', default='classification', type=str,
                    choices=('search', 'classification'),
                    help='kNN task: search or classification')
parser.add_argument('--n-neighbors', default=5, type=int,
                    help='Number of neighbors to use')
parser.add_argument('--weights', type=str, default='uniform',
                    help='Weight function used in prediction')
parser.add_argument('--method', type=str, default='brute',
                    choices=('brute', 'kd_tree', 'ball_tree', 'auto'),
                    help='Algorithm used to compute the nearest neighbors')
parser.add_argument('--metric', type=str, default='euclidean',
                    help='Distance metric to use')
params = bench.parse_args(parser)

from sklearn.neighbors import KNeighborsClassifier

# Load generated data
X_train, X_test, y_train, y_test = bench.load_data(params)
params.n_classes = len(np.unique(y_train))

# Create classification object
knn_clsf = KNeighborsClassifier(n_neighbors=params.n_neighbors,
                                weights=params.weights,
                                algorithm=params.method,
                                metric=params.metric,
                                n_jobs=params.n_jobs)

# Measure time and accuracy on fitting
train_time, _ = bench.measure_function_time(knn_clsf.fit, X_train, y_train, params=params)
if params.task == 'classification':
    y_pred = knn_clsf.predict(X_train)
    train_acc = 100 * accuracy_score(y_pred, y_train)

# Measure time and accuracy on prediction
if params.task == 'classification':
    predict_time, yp = bench.measure_function_time(knn_clsf.predict, X_test,
                                                   params=params)
    test_acc = 100 * accuracy_score(yp, y_test)
else:
    predict_time, _ = bench.measure_function_time(knn_clsf.kneighbors, X_test,
                                                  params=params)

if params.task == 'classification':
    bench.print_output(library='sklearn',
                       algorithm=knn_clsf._fit_method + '_knn_classification',
                       stages=['training', 'prediction'], params=params,
                       functions=['knn_clsf.fit', 'knn_clsf.predict'],
                       times=[train_time, predict_time],
                       accuracies=[train_acc, test_acc], accuracy_type='accuracy[%]',
                       data=[X_train, X_test], alg_instance=knn_clsf)
else:
    bench.print_output(library='sklearn',
                       algorithm=knn_clsf._fit_method + '_knn_search',
                       stages=['training', 'search'], params=params,
                       functions=['knn_clsf.fit', 'knn_clsf.kneighbors'],
                       times=[train_time, predict_time],
                       data=[X_train, X_test], alg_instance=knn_clsf)
