# Implementing Machine Learning Image Recognition Pipeline 📷
In this task I implemented a Sift -> Kmeans -> SVM pipeline, for classifying images between 10 different classes.
<br>
## Pipeline - Explained In Detail 🕵️‍♀️
The methodology is to extract 128 dimensional vectors called SIFTs, each one represents a part of an image. Doing so for an entire image for multiple images from different classes, allows us to have a uniform representation of different parts of all the images.
Later, by training a K-Means model for clustering those SIFT vectors, I am able to represent similar SIFTs (which means similar parts of images) by one unique ‘prototype’.
Now, by comparing all SIFT vectors from each image to all of the prototypes, each image can be represented as a histogram of prototypes (or more accurately, represent each SIFT in the image by its cluster). The idea is that same classed images should have similar histogram representation.
At the end of the procces, a SVM model was used for classifying images by their histogram representation.
<br>
## Code Implementation
The code runs by an activation of a ‘main’ function which takes data path (data location in the computer) and train/test class indices.
The ‘main’ function holds ‘hard coded’ tuned hyper-parameters values, and calls the data preprocessing functions; K-Means model training function; ‘image to histogram representation’ function; SVM model training function; test data predictions and final result printing function.
While building a list of SIFT vectors for clustering, I adjusted the code to randomly select up to 500 SIFTs from each image. Therefore, when training on about 250 images I had no more than 125,000 vectors for the K-Means model to cluster.
<br>
## Test Results
For the best hyper parameter tuning results and when choosing the most accurate model, I obtained an accuracy rate of 63.9% on the test set.
<br>
## Files in the Repository 
*Hyperparameter Tuning*
The full procces of chossing all the relevant hyperparameters in the algorithms.
*Function & Packages*
All the packages that needs to be installed.
All the function for activating the project's pipe.
*Main*
Calling the main function of the project.
