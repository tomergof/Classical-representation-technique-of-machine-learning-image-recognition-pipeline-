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


def main(data_path, class_indices):
    """ Main
    This function is used for the whole flow:
    Loading the data; Splitting to train-test; training a model with the chosen tuned hyper parameters; Testing to the train set.

    Input:
    data_path - folder where data is located
    class_indices - indices of images labels used for the train & test

    Output:
    results
    """
    data, labels, color_data = load_data(data_path, class_indices, (75, 75))  # Fixed tuned image size = 75*75
    train_x, train_y, test_x, test_y = split_data(data, labels)  # calls a function that splits the train and test
    train_x_color, train_y_color, test_x_color, test_y_color = split_data(color_data, labels)
    # Creating SIFTS for Kmeans:
    sifts = []
    print("Extracting SIFTs...")
    for image in train_x:
        sifts.append(SIFT(image, step_size=7, batch_size=8, build_dict=True))  # Fixed tuned step-size 7, batch-size 8
    sifts = np.array(sifts)
    sifts = np.reshape(sifts, (sifts.shape[0] * sifts.shape[1], sifts.shape[2]))  # reshape for building the dictionary
    print("Training K-Means model...")
    kmeans_model = kmeans(sifts, 900)  # Fixed tuned dictionary size 900 bins.
    images_hist_train = []
    images_hist_test = []
    print("Preparing images histograms...")
    for image in train_x:
        images_hist_train.append(build_hist(image, kmeans_model, step_size=7, batch_size=8))  # build train histogram of words
    for image in test_x:
        images_hist_test.append(build_hist(image, kmeans_model, step_size=7, batch_size=8))  # build test histogram of words
    print("Training SVM model...")
    SVM_model = linearSVM(images_hist_train, train_y, 16384)  # fixed tuned SVM - linear SVM, with fixed tuned C = 2^^14
    accuracy = SVM_model.score(images_hist_test,test_y)
    pred_test_y = SVM_model.predict(images_hist_test)
    miss_classified = {}
    labels_order = label_indices(test_y)
    for prediction, label, hist, i in zip(pred_test_y, test_y, images_hist_test, range(len(test_y))):
        if prediction != label:
            hist = np.array(hist)
            hist = hist.reshape(1,-1)
            difference = max(SVM_model.decision_function(hist)[0]) - SVM_model.decision_function(hist)[0][labels_order[label]]
            miss_classified = add_val_to_dic(miss_classified, label, [i, difference])
    print_output(train_y, test_y, pred_test_y, accuracy, miss_classified, test_x_color)


def label_indices(labels):
    '''
    This functions returns the indexes for labels as a dictionary in the first order they appear in a given list.
    '''
    indices = {}
    idx = 0
    for label in labels:
        if label not in indices:
            indices[label] = idx
            idx = idx + 1
    return indices


def CV(x, y, folds, SVMmodel, step_size, batch_size, dict_size):
    """ CV - Cross Validation
    This function was used only in the hyper parameters tuning.
    In this function, the train set was split 5 times to train-validation sets.

    Input:
    x - train_x; y - train_y; SVMmodel; step_size; batch_size; dict_size - number of clusters K in kmeans.
    Output:
    Average result of the model.
    """
    kf = KFold(n_splits=folds, shuffle=True)
    results = []
    for train_index, validation_index in kf.split(x):
        X_train, X_Validation = [x[idx] for idx in train_index], [x[idx] for idx in validation_index]
        y_train, y_Validation = [y[idx] for idx in train_index], [y[idx] for idx in validation_index]
        sifts = []
        for image in X_train:
            sifts.append(SIFT(image, step_size, batch_size, build_dict=True))
        sifts = np.array(sifts)
        sifts = np.reshape(sifts, (sifts.shape[0] * sifts.shape[1], sifts.shape[2]))
        kmeans_model = kmeans(sifts, dict_size)
        images_hist = []
        for image in X_train:
            images_hist.append(build_hist(image, kmeans_model, step_size, batch_size))
        SVMmodel.fit(images_hist, y_train)
        images_hist_val = []
        for image in X_Validation:
            images_hist_val.append(build_hist(image, kmeans_model, step_size, batch_size))
        results.append(accuracy_score(y_Validation, SVMmodel.predict(images_hist_val)) * 100)
    return sum(results) / len(results)


def kmeans(vectors, num_of_clusters):
    """Kmeans algorithm
    Input:
    vectors - Vectors of Sifts; num_of_clusters.
    Output:
    Kmeans model
    """
    model = KMeans(n_clusters=num_of_clusters, random_state=0)
    model.fit(vectors)
    return model


def load_data(path, indices, image_size):
    """Loading the images
    Input:
    path - Location of folders; indices - indices of relevant folders; dim - image size (for quadratic image)
    Output:
    Images + labels of images (Y)
    """
    data = []
    colored_images = []
    labels = []
    folders = os.listdir(path)
    folders.sort()
    indices_folders = []
    for idx in indices:
        indices_folders.append(folders[idx])  # get relevant folders
    for folder in indices_folders:
        sub_folder = path + "/" + folder
        sub_path = os.listdir(sub_folder)
        for image_name in sub_path:
            labels.append(folder)  # append lables to lable vector
            image_path = sub_folder + "/" + image_name
            colored_image = cv2.imread(image_path)
            image = cv2.cvtColor(colored_image, cv2.COLOR_BGR2GRAY)  # Used instead of rgb2gray
            image = cv2.resize(image, image_size)
            data.append(image)  # append image to data S X S X N array
            colored_images.append(colored_image)
    return data, labels, colored_images



def add_val_to_dic(dictionary, key, value):
    """Adding value to dictionary key
    A generic function to help us adding a certain value to a key, in a dictionary
    """
    if key not in dictionary:
        dictionary[key] = [value]
    elif type(dictionary[key]) == list:
        dictionary[key].append(value)
    else:
        dictionary[key] = [dictionary[key], value]
    return dictionary


def get_indices_of_labels(data, labels):
    """Getting indices of labels in the data
    This function used when splitting the data for train-test
    """
    indices_dict = {}
    for idx in range(len(labels)):
        key = labels[idx]
        val = idx
        indices_dict = add_val_to_dic(indices_dict, key, val)
    return indices_dict


def split_data(data, labels):
    """Split Data
    Used for splitting the relevant images folders data to train-test
    If folders contains 50 images or more, than 25 for training and 25 for test
    Else, half rounded up for train, half rounded down for test

    Input:
    data - images; labels - Y labels
    Output:
    train & test split to x-y
    """
    indices_list = get_indices_of_labels(data, labels)  # dictionary: key = label, value = image indexes
    train_x = []
    train_y = []
    test_x = []
    test_y = []
    for label in indices_list:
        indices = indices_list[label]
        start = indices[0]
        end = indices[-1]
        num_of_pictures = len(indices)
        if num_of_pictures >= 50:
            for idx in range(start, start + 25):
                train_x.append(data[idx])
                train_y.append(label)
            for idx in range(start + 25, start + 50):
                test_x.append(data[idx])
                test_y.append(label)
        else:
            middle = math.ceil(num_of_pictures / 2)
            for idx in range(start, start + middle):
                train_x.append(data[idx])
                train_y.append(label)
            for idx in range(start + middle, end + 1):
                test_x.append(data[idx])
                test_y.append(label)
    return train_x, train_y, test_x, test_y


def print_output(class_train_y, class_test_y, pred_test_y, accuracy, miss_classifications, color_data):
    """Printing the output
    As required in our work, we are printing the following information:
    Class names and number of images (train & test); Final test error
    """
    print("Classes names & number of images:")
    labels = label_indices(class_test_y)
    train_images = {}
    test_images = {}
    for image_train in class_train_y:
        train_images[image_train] = train_images.get(image_train, 0) + 1
    for image_test in class_test_y:
        test_images[image_test] = test_images.get(image_test, 0) + 1
    for cls in labels:
        print("Class Name: " + cls)
        print("Number of train images: " + str(train_images.get(cls)))
        print("Number of test images: " + str(test_images.get(cls)))
        print()
    print("Now Liel, it's time to see the results...")
    for i in range(5, 0, -1):
        print(i)
        time.sleep(1)
    print("The test error is: " + str(round((1-accuracy)*100, 3)))
    print("The test score is: " + str(round(accuracy*100, 3)))
    print()
    print("Confusion matrix:")
    print(confusion_matrix(class_test_y, pred_test_y))
    miss_classifications_images = check_two_maxs(miss_classifications)
    for label in miss_classifications_images:
        if len(miss_classifications_images[label][0]) == 0:
            print("There are no errors from class " + str(label))
        else:
            print("Largest error images of class " + str(label) + ":")
            for image_index in miss_classifications_images[label][0]:
                image = color_data[image_index]
                #For pltting the misclassyfied images:
                print_images(image)


def print_images(image):
    im2 = image.copy()
    im2[:, :, 0] = image[:, :, 2]
    im2[:, :, 2] = image[:, :, 0]
    plt.imshow(im2)


def build_hist(image, model, step_size, batch_size):
    """Building histogram of sifts
    Used for building an histogram for each image
    Input:
    image; model - Kmeans; step_size & batch_size - for Sifts extraction.
    Output:
    Histogram
    """
    clusters = model.cluster_centers_
    hist = [0] * len(clusters)
    sifts = SIFT(image, step_size, batch_size)
    sifts_as_prototypes = model.predict(sifts)
    for prototype in sifts_as_prototypes:
        hist[prototype] = hist[prototype] + 1
    hist = [x / sum(hist) for x in hist]
    return hist



def SIFT(image, step_size=5, batch_size=5, build_dict=False):
    """ SIFT
    This function gets a gray image and preforms a SIFT extraction based on given step size and batch size.

    Input;
    image; step_size; batch_size; build_dict - boolean parameter. Equals true if we call this function
    while building dictionary for Kmeans, and false otherwise.
    The purpose of this parameters is to chose a smaller amount of sifts from the image then building the dictionary.

    Output:
    Sifts.
    """
    limit = 500  # hardcoded limit of sifts from image to use while building the hist (500 sifts from 200 train photos = 100,000 sifts)
    image = np.array(image)
    sift = cv2.xfeatures2d.SIFT_create()
    kp = [cv2.KeyPoint(x, y, batch_size) for y in range(0, image.shape[0], step_size)
          for x in range(0, image.shape[1], step_size)]
    dense_feat = sift.compute(image, kp)
    sifts = dense_feat[1]
    if (build_dict):
        np.random.seed(0)
        np.random.shuffle(sifts)
        if limit < len(sifts):
            sifts = sifts[:limit]
    sifts = [normalize(x) for x in sifts]
    return sifts


def normalize(vector):
    """Normalizing Sifts
    Normalizing the way we learned in class
    1. Normalize
    2. Turn everything that is higher than 0.2 to be 0.2
    3. Normalize again

    Input:
    Vector for normalization
    Output:
    Normalized vector
    """
    norma_1 = np.linalg.norm(vector)
    if norma_1 == 0:  # Only zero vectors have norma equal zero.
        return vector
    norm_1 = vector / np.linalg.norm(vector)
    norm_1 = np.array(norm_1)
    max_02 = norm_1.clip(max=0.2)
    norm_2 = max_02 / np.linalg.norm(max_02)
    return norm_2


def linearSVM(x, y, c):
    """ linearSVM
    Fits linear SVM with chosen C and returns the model
    """
    model = LinearSVC(C=c, multi_class='ovr', max_iter=10000)
    model.fit(x, y)
    return model


def nonlinearSVM(x, y, c, kernel='rbf', gamma='auto'):
    """ nonlinearSVM
    Fits RBF kernel SVM with chosen C and gamma, and returns the model
    """
    model = sklearn.svm.SVC(C=c, kernel=kernel, gamma=gamma, decision_function_shape='ovr')
    model.fit(x, y)
    return model


def check_two_maxs(dict):
    '''
    This function return a dictionary of two or one maximum values per key of a given dictionary.
    '''
    images_to_print ={}
    for key in dict:
        max = 0
        max_index = dict[key][0][0]
        if len(dict[key]) == 1:
            images_to_print = add_val_to_dic(images_to_print, key, max_index)
        else:
            second_max = 0
            for margin in dict[key]:
                if margin[1] > max:
                    second_max = max
                    second_max_index = max_index
                    max = margin[1]
                    max_index = margin[0]

                elif max > margin[1] > second_max:
                    second_max = margin[1]
                    second_max_index = margin[0]
            images_to_print = add_val_to_dic(images_to_print, key, [max_index, second_max_index])
    return images_to_print

data_path = "/Users/danboguslavsky/Desktop/School/Computer Vision/First assignment/101_ObjectCategories/101_ObjectCategories"
class_indices = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]


if __name__ == "__main__":
    main(data_path, class_indices)

