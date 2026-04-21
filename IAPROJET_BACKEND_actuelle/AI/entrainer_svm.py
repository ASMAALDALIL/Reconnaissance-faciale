import os

#permet de corrigés les chemin des image pour qu'ils soit accépter par opencv
os.system('python converti_le_nom.py')

from re import X
import cv2 as cv
import tensorflow as tf
import matplotlib.pyplot as plt
from mtcnn import MTCNN
import numpy as np
from PIL import Image
from keras_facenet import FaceNet
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import pickle

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class FACELOADING:
    def __init__(self, directory):
        self.directory = directory
        self.target_size = (160, 160)
        self.X = []
        self.Y = []
        self.detector = MTCNN()

    def extract_face(self, filename):
        img = cv.imread(filename)
        if img is None:
            print(f"Error: Could not read image {filename}")
            return None

        img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        detections = self.detector.detect_faces(img_rgb)

        if len(detections) == 0:
            return None

        x, y, w, h = detections[0]['box']
        x, y = abs(x), abs(y)
        face = img_rgb[y:y + h, x:x + w]
        face_arr = cv.resize(face, self.target_size)
        return face_arr

    def load_faces(self, dir):
        FACES = []
        for im_name in os.listdir(dir):
            path = os.path.join(dir, im_name)
            single_face = self.extract_face(path)
            if single_face is not None:
                FACES.append(single_face)
        return FACES

    def load_classes(self):
        for sub_dir in os.listdir(self.directory):
            path = os.path.join(self.directory, sub_dir)
            if not os.path.isdir(path):
                continue
            FACES = self.load_faces(path)
            labels = [sub_dir for _ in range(len(FACES))]
            print(f"LOADED SUCCESSFULLY: {len(labels)} images from {sub_dir}")
            self.X.extend(FACES)
            self.Y.extend(labels)
        return np.asarray(self.X), np.asarray(self.Y)

    def save_faces(self, output_dir="testr"):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Dossier créé: {output_dir}")

        for i, face_array in enumerate(self.X):
            label = self.Y[i]
            label_dir = os.path.join(output_dir, label)
            if not os.path.exists(label_dir):
                os.makedirs(label_dir)
            img = Image.fromarray(face_array, 'RGB')
            img_path = os.path.join(label_dir, f"image_{i:03d}.jpg")
            img.save(img_path)
        print(f"\n{len(self.X)} visages enregistrés dans le dossier '{output_dir}'.")


# tester la classe il faut mettre le code en dessous active :

dataset_path = r"C:\IA project\dataset"
faceloading = FACELOADING(dataset_path)
X, Y = faceloading.load_classes()

if len(X) > 0:
    print(f"Total images loaded: {len(X)}")
    faceloading.save_faces(output_dir="testr")
else:
    print("Aucune donnée chargée. Vérifiez le chemin de votre dataset et les images.")

embedder = FaceNet()

def get_embedding(face_img):
    face_img = face_img.astype(np.float32)
    face_img = np.expand_dims(face_img, axis=0)
    yhat = embedder.embeddings(face_img)
    return yhat

EMBEDDER_X = []
for img in X:
    EMBEDDER_X.append(get_embedding(img))
EMBEDDER_X = np.asarray(EMBEDDER_X)
if len(EMBEDDER_X.shape) > 2:
    EMBEDDER_X = EMBEDDER_X.reshape(EMBEDDER_X.shape[0], -1)

#Enregistrer les vecteur trouver dans un fichier compresse dans le dossier testr
output_filename = r"model/visages_embeddings_comprimes.npz"
np.savez_compressed(output_filename, X=X, Y=Y, EMBEDDINGS=EMBEDDER_X)

encoder = LabelEncoder()
encoder.fit(Y)
Y = encoder.transform(Y)

X_train, X_test, Y_train, Y_test = train_test_split(EMBEDDER_X, Y, shuffle=True, random_state=17)

model = SVC(kernel='linear', probability=True)
model.fit(X_train, Y_train)

ypreds_train = model.predict(X_train)
ypreds_test = model.predict(X_test)

accuracy_score(Y_train, ypreds_train)
accuracy_score(Y_test, ypreds_test)

#hada bach ncréew fichier entrainer dyal model svm
output_path = os.path.join('testr', 'svm_model_160x160.pkl')
with open(output_path, 'wb') as f:
    pickle.dump(model, f)


#hada code dyal test dyal hadchi walakin ghir bimage.
'''
print("-" * 50)
print("TEST DE RECONNAISSANCE FACIALE")


def reconnaitre_visage(image_path):
    # 1. Lecture de l'image
    img = cv.imread(image_path)
    if img is None:
        print(f"Erreur : Impossible de lire l'image {image_path}")
        return

    img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    detections = faceloading.detector.detect_faces(img_rgb)

    if len(detections) == 0:
        print("Aucun visage détecté dans cette image.")
        return

    x, y, w, h = detections[0]['box']
    x, y = abs(x), abs(y)

    face = img_rgb[y:y + h, x:x + w]
    face_resized = cv.resize(face, (160, 160))

    face_pixel = face_resized.astype(np.float32)
    face_pixel = np.expand_dims(face_pixel, axis=0)

    embedding = embedder.embeddings(face_pixel)

    prediction_index = model.predict(embedding)
    prediction_proba = model.predict_proba(embedding)

    class_index = prediction_index[0]
    class_name = encoder.inverse_transform([class_index])[0]
    confidence = prediction_proba[0][class_index] * 100

    print(f"\nRésultat : C'est {class_name} avec une confiance de {confidence:.2f}%")

    cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    text = f"{class_name} ({confidence:.1f}%)"
    cv.putText(img, text, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv.imshow("Resultat de la reconnaissance", img)
    cv.waitKey(0)
    cv.destroyAllWindows()


# --- Zone de test ---
image_path_to_test = r"C:\achraf.jpg"
reconnaitre_visage(image_path_to_test)'''