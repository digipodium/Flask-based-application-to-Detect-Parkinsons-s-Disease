from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix
from skimage import feature
from imutils import build_montages
from imutils import paths
import numpy as np
import argparse
import cv2
import pickle
import os


def quantify_image(image):
	# compute the histogram of oriented gradients feature vector for
	# the input image
	features = feature.hog(image, orientations=9,
		pixels_per_cell=(10, 10), cells_per_block=(2, 2),
		transform_sqrt=True, block_norm="L1")

	# return the feature vector
	return features

def load_split(path):
	# grab the list of images in the input directory, then initialize
	# the list of data (i.e., images) and class labels
	imagePaths = list(paths.list_images(path))
	data = []
	labels = []

	# loop over the image paths
	for imagePath in imagePaths:
		# extract the class label from the filename
		label = imagePath.split(os.path.sep)[-2]

		# load the input image, convert it to grayscale, and resize
		# it to 200x200 pixels, ignoring aspect ratio
		image = cv2.imread(imagePath)
		image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		image = cv2.resize(image, (200, 200))

		# threshold the image such that the drawing appears as white
		# on a black background
		image = cv2.threshold(image, 0, 255,
			cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

		# quantify the image
		features = quantify_image(image)

		# update the data and labels lists, respectively
		data.append(features)
		labels.append(label)

	# return the data and labels
	return (np.array(data), np.array(labels))



def predict(spiralpath,wavepath):
    testingPaths=[spiralpath,wavepath]
    le=LabelEncoder()
    idxs = np.arange(0, len(testingPaths))  
    images = []
    # loop over the testing samples
    for i in idxs:
        # load the testing image, clone it, and resize it
        print(testingPaths[i].split(os.path.sep))
        if "spiral" in testingPaths[i].split(os.path.sep)[-1].lower():
            model=pickle.load(open("app/model/spiral.h5",'rb'))
            le.classes_=np.load('app/model/spiral.npy')
            image = cv2.imread(testingPaths[i])
            output = image.copy()
            output = cv2.resize(output, (500, 500))

            # pre-process the image in the same manner we did earlier
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = cv2.resize(image, (200, 200))
            image = cv2.threshold(image, 0, 255,
                cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

            # quantify the image and make predictions based on the extracted
            # features using the last trained Random Forest
            features = quantify_image(image)
            preds = model.predict([features])
            label = le.inverse_transform(preds)[0]

            # draw the colored class label on the output image and add it to
            # the set of output images
            color = (0, 255, 0) if label == "Healthy" else (0, 0, 255)
            cv2.putText(output, label, (15, 55), cv2.FONT_HERSHEY_SIMPLEX,2,
                color, 6)
            print(os.path.join(os.path.dirname(testingPaths[i]),"predspiral"+os.path.splitext(testingPaths[i])[1]))
            cv2.imwrite(os.path.join(os.path.dirname(testingPaths[i]),"predspiral"+os.path.splitext(testingPaths[i])[1]),output)
            spath=os.path.join(os.path.dirname(testingPaths[i]).split('/',1)[1],"predspiral"+os.path.splitext(testingPaths[i])[1])

        elif "wave" in testingPaths[i].split(os.path.sep)[-1].lower():
            model=pickle.load(open("app/model/wave.h5",'rb'))
            le.classes_=np.load('app/model/wave.npy')
            image = cv2.imread(testingPaths[i])
            output = image.copy()
            output = cv2.resize(output, (500,500))

            # pre-process the image in the same manner we did earlier
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = cv2.resize(image, (200, 200))
            image = cv2.threshold(image, 0, 255,
                cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

            # quantify the image and make predictions based on the extracted
            # features using the last trained Random Forest
            features = quantify_image(image)
            preds = model.predict([features])
            label = le.inverse_transform(preds)[0]

            # draw the colored class label on the output image and add it to
            # the set of output images
            color = (0, 255, 0) if label == "Healthy" else (0, 0, 255)
            cv2.putText(output, label, (15,55), cv2.FONT_HERSHEY_SIMPLEX,2,
                color, 6)
            cv2.imwrite(os.path.join(os.path.dirname(testingPaths[i]),"predwave"+os.path.splitext(testingPaths[i])[1]),output)
            wpath=os.path.join(os.path.dirname(testingPaths[i]).split('/',1)[1],"predwave"+os.path.splitext(testingPaths[i])[1])
        
    return(spath,wpath)

# base=os.getcwd()
# spiralpath=os.path.realpath(os.path.join(base,"static/data/spiral/spiral.png"))
# print(os.path.exists(spiralpath))
# wavepath=os.path.realpath(os.path.join(base,'static/data/wave/wave.png'))
# print(os.path.exists(wavepath))

# predict(spiralpath,wavepath)