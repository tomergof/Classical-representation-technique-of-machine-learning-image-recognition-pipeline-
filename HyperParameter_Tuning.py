#Hyperparameters Tuning
import time
import os
import math
import numpy as np
from matplotlib import pyplot as plt
import cv2
import sklearn
from os import listdir
from PIL import Image
from random import shuffle
from sklearn.svm import LinearSVC
from sklearn.cluster import KMeans
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

# While tuning uor hypermaremeters, we used a Cross-Validation method, spliting the train images to 5 sets.
# As you can see in the following code, we tuned 5 hyperparameters for the linear SVM, and 6 for RBF kernel SVM
# We tuned part of the parameters simultaneously, to achieve the best results.

# We first tuned simultaneously the following 3 hyperparameters:
# Image size; Batch Size for extracting the sifts; Step size between keypoint in the image.

tuning_indices = [20,21,22,23,24,25,26,27,28,29] # classes used for tuning the hyperparameters
image_batch_step_sizes = []
image_size =[50, 100, 150, 200, 250, 300, 350, 400]
batch_size = [4,6,8,12,16]
step_size = [4, 7, 10, 13, 16, 19]

for im_size in image_size:
    tuning_data, tuning_labels, color_data = load_data(data_path, tuning_indices,(im_size,im_size))
    tuning_train_x, tuning_train_y, tuning_test_x, tuning_test_y = split_data(tuning_data,tuning_labels)
    for b_size in batch_size:
        for st_size in step_size:
            model_svm = LinearSVC(C = 1, multi_class = 'ovr') #C=1 for inital tuning, arbitrary - using linear SVM
            res = CV(tuning_train_x, tuning_train_y, 5, model_svm, st_size, b_size, 300) #From the paper
            image_batch_step_sizes.append([im_size, b_size,st_size, res])


# When we saw that the best results where achieved with 50 or 100 image size, we run this tuning code again, with image_size = 75.
# This led us to the best results, with the following hyperparameters: image_size = 75, batch_size = 8, step_size = 7

# Now we moved to tune the K - number of clusters in the Kmeans algorihtm:
# Possible K's: (100,1100,100)

tuning_data, tuning_labels,color_data= load_data(data_path, tuning_indices,(75,75))
tuning_train_x, tuning_train_y, tuning_test_x, tuning_test_y = split_data(tuning_data,tuning_labels)
num_of_clusters = [x for x in range(100,1100, 100)]
Kmeans_results=[]
for k in num_of_clusters:
    model_svm = LinearSVC(C = 1, multi_class = 'ovr') #C=1 for inital tuning, arbitrary - using linear SVM
    res = CV(tuning_train_x, tuning_train_y, 5, model_svm, 7, 8, k)
    Kmeans_results.append([k, res])

# The best resulst was achieved with K = 900. We chose this K and moved to tuning linearSVM  - chosing the C hyperparameter:
# Possible C - [2^^-3, 2^^-2,...2^^15]

results_linear_svm=[]
C_for_LinearSvm = [2**x for x in range(-3,16)]

for c in C_for_LinearSvm:
    model_svm = LinearSVC(C = c, multi_class = 'ovr')
    res = CV(tuning_train_x, tuning_train_y, 5, model_svm,  7, 8, 900)
    results_linear_svm.append([c, res])


# In order to determine if the linear kernel is the best one, we trained model with RBF kernel SVM, in which
# we tuned both the C hypperparameter and the gamma hyperparameter
# Possible C - [2^^-3, 2^^-2,..., 2^^15]
# Possible gamma - []

results_RBF_svm_C=[]
C_for_RBFsvm = [2**x for x in range(-3,16)]
for c in C_for_RBFsvm:
    model_RBF_svm = sklearn.svm.SVC(C=c, kernel = 'rbf', decision_function_shape = 'ovr') # gamma default value =  1 / (n_features * X.var())
    res = CV(tuning_train_x, tuning_train_y, 5, model_RBF_svm,  7, 8, 900)
    results_RBF_svm_C.append([c, res])

# The chosen C for rbf SVM was: C = 2**0 = 1
# We tuned the gamma with the chosen C.
# possible gamma - [2^^-15, 2^^-14, ..., 2^^3]

results_RBF_svm_gamma=[]
gamma_values = [2**x for x in range(-15,4)]
for gamma in gamma_values:
    model_RBF_svm = sklearn.svm.SVC(C=1, kernel = 'rbf', gamma = gamma, decision_function_shape = 'ovr')
    res = CV(tuning_train_x, tuning_train_y, 5, model_RBF_svm,  7, 8, 900)
    results_RBF_svm_gamma.append([gamma, res])
