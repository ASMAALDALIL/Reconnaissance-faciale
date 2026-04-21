import cv2
import numpy as np
import requests
from mtcnn import MTCNN
from keras_facenet import FaceNet
import pickle
from sklearn.preprocessing import LabelEncoder
from datetime import date

# ------------ CONFIGURATION -----------------
BACKEND_URL = "http://127.0.0.1:8000/presence/"
GET_EMPLOYEE_URL = "http://127.0.0.1:8000/employees/by-name/"
CAMERA_ID = "c39742e9-ac03-4656-a761-2820e764be77"  # mets l'ID réel

CONFIDENCE_THRESHOLD = 0.7  # seuil pour considérer une prédiction fiable

# ------------ CHARGEMENT DES MODELS -----------------
detector = MTCNN()
embedder = FaceNet()

with open("AI/model/svm_model_160x160.pkl", "rb") as f:
    svm_model = pickle.load(f)

data = np.load("AI/model/visages_embeddings_comprimes.npz")
Y = data["Y"]

label_encoder = LabelEncoder()
label_encoder.fit(Y)

# ------------ CACHE POUR ÉVITER LES DOUBLONS -----------------
today_cache = set()  # stocke employee_id déjà enregistrés aujourd'hui

# ------------ FONCTIONS IA -----------------
def extract_faces(img):
    """Retourne une liste de faces détectées et redimensionnées"""
    detections = detector.detect_faces(img)
    faces = []
    for det in detections:
        x, y, w, h = det["box"]
        x, y = abs(x), abs(y)
        face = img[y:y + h, x:x + w]
        face = cv2.resize(face, (160, 160))
        faces.append(face)
    return faces if faces else None

def get_embedding(face):
    """Retourne l'embedding 512-dimensionnel pour une face"""
    face = face.astype(np.float32)
    face = np.expand_dims(face, axis=0)
    return embedder.embeddings(face)

def enregistrer_presence(employee_id):
    """Enregistre la présence si elle n'a pas déjà été enregistrée aujourd'hui"""
    if employee_id in today_cache:
        return  # déjà enregistré aujourd'hui

    payload = {
        "employee_id": employee_id,
        "camera_id": CAMERA_ID
    }

    try:
        res = requests.post(BACKEND_URL, json=payload)
        if res.status_code == 200:
            print(f"🎯 Présence enregistrée pour {employee_id}")
            today_cache.add(employee_id)
        else:
            print(f"⚠️ Erreur backend pour {employee_id} : {res.text}")
    except requests.RequestException as e:
        print(f"⚠️ Erreur réseau lors de l'enregistrement : {e}")

# ------------ BOUCLE DE RECONNAISSANCE -----------------
def start_camera():
    cap = cv2.VideoCapture(0)
    print("📸 Caméra démarrée…")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = extract_faces(rgb)

        if faces:
            for face in faces:
                embedding = get_embedding(face)
                
                # prédiction SVM
                probabilities = svm_model.predict_proba(embedding)[0]
                prediction_index = np.argmax(probabilities)
                confidence = probabilities[prediction_index]

                if confidence < CONFIDENCE_THRESHOLD:
                    name = "Inconnu"
                    employee_id = None
                else:
                    name = label_encoder.inverse_transform([prediction_index])[0]

                    try:
                        r = requests.get(GET_EMPLOYEE_URL + name)
                        r.raise_for_status()
                        employee_id = r.json()["id"]
                    except requests.RequestException as e:
                        print(f"⚠️ Impossible de récupérer l'employee_id pour {name} : {e}")
                        employee_id = None

                print("Nom détecté par l'AI :", name)

                # enregistrer la présence uniquement si l'employee_id est défini et non déjà enregistré
                if employee_id and employee_id not in today_cache:
                    enregistrer_presence(employee_id)

                # affichage sur la vidéo
                color = (0, 255, 0) if name != "Inconnu" else (0, 0, 255)
                cv2.putText(frame, name, (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow("AI Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_camera()
