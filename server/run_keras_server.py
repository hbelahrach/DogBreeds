# USAGE
# Start the server:
# 	python run_keras_server.py
# Submit a request via cURL:
# 	curl -X POST -F image=@dog.jpg 'http://localhost:5000/predict'
# Submita a request via Python:
#	python simple_request.py

# import the necessary packages
from keras.applications import ResNet50
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from keras.layers import GlobalAveragePooling2D
from keras.layers import Dropout, Flatten, Dense
from keras.models import Sequential
from keras.applications.vgg19 import VGG19, preprocess_input
from glob import glob
from PIL import Image
import numpy as np
import cv2
import flask
import io

# initialize our Flask application and the Keras model
app = flask.Flask(__name__)
vgg_model = None
model = None
dog_names = []


def load_model():
    # load the pre-trained Keras model (here we are using a model
    # pre-trained on ImageNet and provided by Keras, but you can
    # substitute in your own networks just as easily)
    global model
    global vgg_model
    vgg_model = VGG19(weights='imagenet', include_top=False)
    model = Sequential()
    model.add(GlobalAveragePooling2D(input_shape=(7, 7, 512)))
    model.add(Dense(70, activation='relu'))
    model.add(Dense(133, activation='softmax'))
    model.compile(optimizer='rmsprop',
                  loss='categorical_crossentropy', metrics=['accuracy'])
    model.load_weights('saved_models/weights.best.VGG19.hdf5')

    # load list of dog names
    global dog_names
    file = open("dogNames.txt", "r")
    dog_names = file.read().splitlines()


def prepare_image(image, target):
    # if the image mode is not RGB, convert it
    if image.mode != "RGB":
        image = image.convert("RGB")

    # resize the input image and preprocess it
    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)

    # return the processed image
    return image


@app.route("/predict", methods=["POST"])
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"success": False}
    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            # read the image in PIL format
            image = flask.request.files["image"].read()
            print flask.request.files["image"]
            image = Image.open(io.BytesIO(image))

            # preprocess the image and prepare it for classification
            image = prepare_image(image, target=(224, 224))
            # classify the input image and then initialize the list
            # of predictions to return to the client
            vgg_pred = vgg_model.predict(image)
            preds = model.predict(vgg_pred)
            name = dog_names[np.argmax(preds)]
            data["prediction"] = name

            # indicate that the request was a success
            data["success"] = True

    # return the data dictionary as a JSON response
    return flask.jsonify(data)


# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server..."
           "please wait until server has fully started"))
    load_model()
    app.run()
