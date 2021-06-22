# Implementing Machine Learning Image Recognition Pipeline
In this task I implemented a Sift -> Kmeans -> SVM pipeline, for classifying images between 10 different classes.
<br>
## Pipeline - Explained In Detail
The methodology is to extract 128 dimensional vectors called SIFTs, each one represents a part of an image. Doing so for an entire image for multiple images from different classes, allows us to have a uniform representation of different parts of all the images.
Later, by training a K-Means model for clustering those SIFT vectors, I am able to represent similar SIFTs (which means similar parts of images) by one unique ‘prototype’.
Now, by comparing all SIFT vectors from each image to all of the prototypes, each image can be represented as a histogram of prototypes (or more accurately, represent each SIFT in the image by its cluster). The idea is that same classed images should have similar histogram representation.
At the end of the procces, a SVM model was used for classifying images by their histogram representation.
