# Implementing Machine Learning Image Recognition Pipeline 📷
In this task I implemented a Sift -> Kmeans -> SVM pipeline, for classifying images between 10 different classes.
<br>

## Installation 🔗
The projects requires installing and importing the foolowing libraries and packages:
  ```bash
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
  ```
Go to "Data" folder to find the link for downloading the images.

## Usage 🤔
To import the data, first download it to your computer. Choose arbitrary 10 indexes (will be used for training the model):
  ```bash
  data_path = ""
  class_indices = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]

  if __name__ == "__main__":
      main(data_path, class_indices)
  ```
  
The code above, after changing the data_path variable to the folder on your computer, and changing the class_indices as you wish, will activate the pipeline.
<br>
## Pipeline - Explained In Detail 🕵️‍♀️
The methodology is to extract 128 dimensional vectors called SIFTs, each one represents a part of an image. Doing so for an entire image for multiple images from different classes, allows us to have a uniform representation of different parts of all the images.
Later, by training a K-Means model for clustering those SIFT vectors, I am able to represent similar SIFTs (which means similar parts of images) by one unique ‘prototype’.
Now, by comparing all SIFT vectors from each image to all of the prototypes, each image can be represented as a histogram of prototypes (or more accurately, represent each SIFT in the image by its cluster). The idea is that same classed images should have similar histogram representation.
At the end of the procces, a SVM model was used for classifying images by their histogram representation.
<br>
## Code Implementation 👩‍💻
The code runs by an activation of a ‘main’ function which takes data path (data location in the computer) and train/test class indices.
The ‘main’ function holds ‘hard coded’ tuned hyper-parameters values, and calls the data preprocessing functions; K-Means model training function; ‘image to histogram representation’ function; SVM model training function; test data predictions and final result printing function.
While building a list of SIFT vectors for clustering, I adjusted the code to randomly select up to 500 SIFTs from each image. Therefore, when training on about 250 images I had no more than 125,000 vectors for the K-Means model to cluster.
<br>
## Test Results 🏆
For the best hyper parameter tuning results and when choosing the most accurate model, **I obtained an accuracy rate of 63.9% on the test set.**
<br>
In order to examine the most interesting errors in our model, we produced the following confusion matrix:

![image](https://user-images.githubusercontent.com/61631269/123091559-2d655100-d432-11eb-8acb-b9323404688f.png)
<br>
It’s easy to notice by the dark blue color on the diagonal, that most of the classes are well predicted. Nonetheless, there is a substantial amount of error and in each class. Many images labeled as ‘hedgehog’ were classified as ‘hawksbill’ which are different animals to a human eye, though both are ‘round’ looking, what may explain the error. In addition, I notice from showing the error images that many of the misclassifications occurred in images with messy background and other objects in the image. In order to perform better results on the test class, I think that taking more “clean” images can be useful. In contrast, using same images but with different SIFT extraction method can be useful – extracting SIFTs only from the main part of the image instead of using dense SIFTs extraction.
