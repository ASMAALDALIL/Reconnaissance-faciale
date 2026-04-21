import os

# Lancement du script converti_le_nom.py au début
os.system('python converti_le_nom.py')

import cv2 as cv
import numpy as np
import tensorflow as tf
import pickle
from mtcnn import MTCNN
from keras_facenet import FaceNet
from sklearn.preprocessing import LabelEncoder

os.environ['CUDA_VISIBLE_DEVICES'] = '2'

facenet = FaceNet()
detector = MTCNN()

faces_embeddings = np.load('model/visages_embeddings_comprimes.npz')
Y = faces_embeddings['Y']
encoder = LabelEncoder()
encoder.fit(Y)

model = pickle.load(open('model/svm_model_160x160.pkl', 'rb'))

# fhad cap ila drna 0 donc rah ghadi nkhdmo b les caméra locaux dyal les pc dyalna sinon wa7d il a bina ndiro chi caméra externe
cap = cv.VideoCapture(0)

while cap.isOpened():
    _, frame = cap.read()
    rgb_img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    detections = detector.detect_faces(rgb_img)

    for face in detections:
        x, y, w, h = face['box']
        x, y = abs(x), abs(y)

        img = rgb_img[y:y + h, x:x + w]

        if img.shape[0] == 0 or img.shape[1] == 0:
            continue

        img = cv.resize(img, (160, 160))
        img = np.expand_dims(img, axis=0)

        ypred = facenet.embeddings(img)

        # had lcode li ja mn b3d bax ila kan système mamt2kdx mn la personne bli rah employe au moins b 50%  ghadi i3tina erreur
        probability = model.predict_proba(ypred)
        confidence = np.max(probability)
        best_class_index = np.argmax(probability)

        if confidence > 0.5:
            face_name = encoder.inverse_transform([best_class_index])[0]
            final_name = f"{face_name} ({confidence * 100:.0f}%)"
            color = (0, 255, 0)
        else:
            final_name = "Inconnu"
            color = (0, 0, 255)

        cv.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv.putText(frame, str(final_name), (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv.LINE_AA)

    cv.imshow("Face Recognition", frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()