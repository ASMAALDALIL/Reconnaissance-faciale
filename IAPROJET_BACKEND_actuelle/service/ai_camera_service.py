# service/ai_camera_service.py
import cv2
import numpy as np
from typing import Optional, Dict, List
import pickle
from pathlib import Path
from mtcnn import MTCNN
from keras_facenet import FaceNet
from sklearn.preprocessing import LabelEncoder

class AICameraService:
    """Service d'intégration de l'IA avec MTCNN + FaceNet pour la reconnaissance faciale"""
    
    def __init__(self):
        # Chemins vers les modèles
        self.model_path = Path("AI/model/svm_model_160x160.pkl")
        self.embeddings_path = Path("AI/model/visages_embeddings_comprimes.npz")
        
        # Charger les modèles
        self.load_models()
        
        print("✅ AICameraService initialisé avec MTCNN + FaceNet")
    
    def load_models(self):
        """Charge les modèles MTCNN, FaceNet et SVM"""
        try:
            # Détecteur MTCNN
            self.detector = MTCNN()
            
            # Embedder FaceNet
            self.embedder = FaceNet()
            
            # Modèle SVM
            with open(self.model_path, "rb") as f:
                self.svm_model = pickle.load(f)
            
            # Charger les labels
            data = np.load(self.embeddings_path)
            Y = data["Y"]
            
            # Encoder les labels
            self.label_encoder = LabelEncoder()
            self.label_encoder.fit(Y)
            
            print(f"✅ Modèles chargés: {len(Y)} employés")
        except Exception as e:
            print(f"❌ Erreur chargement modèles: {e}")
            self.detector = None
            self.svm_model = None
    
    def extract_face(self, img: np.ndarray) -> Optional[np.ndarray]:
        """
        Extrait un visage d'une image avec MTCNN
        
        Returns:
            Face 160x160 ou None si aucun visage détecté
        """
        if self.detector is None:
            return None
        
        detections = self.detector.detect_faces(img)
        if len(detections) == 0:
            return None

        # Prendre le premier visage détecté
        x, y, w, h = detections[0]["box"]
        x, y = abs(x), abs(y)

        face = img[y:y + h, x:x + w]
        face = cv2.resize(face, (160, 160))

        return face
    
    def get_embedding(self, face: np.ndarray) -> np.ndarray:
        """Extrait l'embedding d'un visage avec FaceNet"""
        face = face.astype(np.float32)
        face = np.expand_dims(face, axis=0)
        return self.embedder.embeddings(face)
    
    def detect_faces_in_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Détecte tous les visages dans une frame et les identifie
        
        Returns:
            Liste des visages détectés avec infos
        """
        if frame is None or self.detector is None:
            return []
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detections = self.detector.detect_faces(rgb)
        
        detected_faces = []
        for detection in detections:
            x, y, w, h = detection["box"]
            x, y = abs(x), abs(y)
            confidence = detection["confidence"]
            
            # Extraire le visage
            face = rgb[y:y + h, x:x + w]
            face_resized = cv2.resize(face, (160, 160))
            
            # Obtenir l'embedding
            embedding = self.get_embedding(face_resized)
            
            # Identifier l'employé
            employee_info = self.identify_employee(embedding)
            
            detected_faces.append({
                'bbox': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
                'mtcnn_confidence': float(confidence),
                'employee_name': employee_info['name'] if employee_info else "Inconnu",
                'recognition_confidence': float(employee_info['confidence']) if employee_info else 0.0,
                'embedding': embedding
            })
        
        return detected_faces
    
    def identify_employee(self, embedding: np.ndarray) -> Optional[Dict]:
        """
        Identifie un employé à partir de son embedding
        
        Returns:
            Dict avec name et confidence ou None
        """
        if self.svm_model is None or embedding is None:
            return None
        
        try:
            # Prédiction avec SVM
            prediction_index = self.svm_model.predict(embedding)[0]
            
            # Obtenir les probabilités (si disponible)
            if hasattr(self.svm_model, 'predict_proba'):
                proba = self.svm_model.predict_proba(embedding)
                confidence = float(np.max(proba))
            else:
                # Si pas de predict_proba, utiliser decision_function
                decision = self.svm_model.decision_function(embedding)
                confidence = float(1.0 / (1.0 + np.exp(-np.max(decision))))  # Sigmoid
            
            # Récupérer le nom
            name = self.label_encoder.inverse_transform([prediction_index])[0]
            
            # Seuil de confiance
            if confidence < 0.5:
                return None
            
            return {
                'name': name,
                'confidence': confidence
            }
        except Exception as e:
            print(f"❌ Erreur identification: {e}")
            return None
    
    def search_employee_in_frame(
        self, 
        frame: np.ndarray, 
        employee_name: str
    ) -> Optional[Dict]:
        """
        Recherche un employé spécifique dans une frame
        
        Args:
            frame: Image de la caméra (BGR)
            employee_name: Nom complet de l'employé
        
        Returns:
            Dict avec bbox et infos de zoom ou None
        """
        # Détecter tous les visages
        detected_faces = self.detect_faces_in_frame(frame)
        
        # Normaliser le nom recherché (enlever accents, espaces multiples, etc.)
        search_name = employee_name.strip().lower()
        
        # Chercher l'employé
        for face in detected_faces:
            face_name = face['employee_name'].strip().lower()
            
            # Correspondance exacte ou partielle
            if search_name in face_name or face_name in search_name:
                x, y, w, h = face['bbox']['x'], face['bbox']['y'], face['bbox']['w'], face['bbox']['h']
                margin = int(max(w, h) * 0.3)  # 30% de marge
                
                return {
                    'found': True,
                    'employee': face,
                    'zoom_bbox': {
                        'x': max(0, x - margin),
                        'y': max(0, y - margin),
                        'w': w + 2 * margin,
                        'h': h + 2 * margin
                    },
                    'center': {
                        'x': x + w // 2,
                        'y': y + h // 2
                    }
                }
        
        return None
    
    def annotate_frame(
        self, 
        frame: np.ndarray, 
        detected_faces: List[Dict],
        highlight_employee: Optional[str] = None
    ) -> np.ndarray:
        """
        Annote une frame avec les détections
        
        Args:
            frame: Image originale (BGR)
            detected_faces: Liste des visages détectés
            highlight_employee: Nom de l'employé à mettre en surbrillance
        
        Returns:
            Frame annotée
        """
        annotated = frame.copy()
        
        for face in detected_faces:
            x, y, w, h = face['bbox']['x'], face['bbox']['y'], face['bbox']['w'], face['bbox']['h']
            name = face['employee_name']
            confidence = face['recognition_confidence']
            
            # Vérifier si c'est l'employé recherché
            is_highlighted = False
            if highlight_employee:
                if highlight_employee.strip().lower() in name.strip().lower():
                    is_highlighted = True
            
            # Couleur selon si highlight
            color = (0, 255, 0) if is_highlighted else (0, 0, 255)  # Vert si highlight, Rouge sinon
            thickness = 3 if is_highlighted else 2
            
            # Rectangle autour du visage
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, thickness)
            
            # Nom + confiance
            label = f"{name} ({confidence:.2%})"
            
            # Fond noir pour le texte
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated, (x, y - text_h - 10), (x + text_w, y), color, -1)
            
            cv2.putText(
                annotated, 
                label, 
                (x, y - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, 
                (255, 255, 255),  # Texte blanc
                2
            )
            
            # Si highlight, ajouter indicateur
            if is_highlighted:
                cv2.putText(
                    annotated,
                    ">>> TROUVE <<<",
                    (x, y + h + 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )
        
        return annotated


# Instance singleton
ai_camera_service = AICameraService()