# service/camera_service.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import cv2
import asyncio
from datetime import datetime
import base64
from uuid import UUID

from models.Camera import Camera
from models.Employe import Employee
from models.Departement import Departement
from schemas.camera import CameraCreate, CameraResponse
from service.ai_camera_service import ai_camera_service


class CameraService:
    """Service de gestion des caméras avec streaming et reconnaissance IA"""
    
    # Dictionnaire des streams actifs {camera_id: VideoCapture}
    active_streams = {}
    
    @staticmethod
    def create_camera(db: Session, data: CameraCreate):
        """Créer une nouvelle caméra"""
        camera = Camera(
            numero=data.numero,
            rtsp_url=data.rtsp_url,
            departement_id=data.departement_id,
            is_entry_camera=data.is_entry_camera
        )
        db.add(camera)
        db.commit()
        db.refresh(camera)
        return camera
    
    @staticmethod
    def get_all_cameras(db: Session) -> List[Dict]:
        """Récupère toutes les caméras avec leurs départements"""
        cameras = db.query(Camera).join(Departement).all()
        
        result = []
        for camera in cameras:
            result.append({
                'id': str(camera.id),
                'numero': camera.numero,
                'rtsp_url': camera.rtsp_url,
                'is_entry_camera': camera.is_entry_camera,
                'departement': {
                    'id': str(camera.departement.id),
                    'nom': camera.departement.nom
                },
                'is_streaming': str(camera.id) in CameraService.active_streams
            })
        
        return result
    
    @staticmethod
    def get_camera_by_id(db: Session, camera_id: UUID) -> Optional[Dict]:
        """Récupère une caméra par ID"""
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        
        if not camera:
            return None
        
        return {
            'id': str(camera.id),
            'numero': camera.numero,
            'rtsp_url': camera.rtsp_url,
            'is_entry_camera': camera.is_entry_camera,
            'departement': {
                'id': str(camera.departement.id),
                'nom': camera.departement.nom
            } if camera.departement else None,
            'is_streaming': str(camera.id) in CameraService.active_streams
        }
    
    @staticmethod
    def delete_camera(db: Session, camera_id: UUID):
        """Supprime une caméra"""
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if camera:
            # Arrêter le stream si actif
            if str(camera.id) in CameraService.active_streams:
                asyncio.create_task(CameraService.stop_camera_stream(str(camera.id)))
            
            db.delete(camera)
            db.commit()
        return camera
    
    @staticmethod
    async def start_camera_stream(camera_id: str, rtsp_url: str):
        """
        Démarre le stream d'une caméra
        
        Args:
            camera_id: UUID de la caméra (en string)
            rtsp_url: URL RTSP ou numéro de webcam (0, 1, etc.)
        """
        if camera_id in CameraService.active_streams:
            print(f"Stream déjà actif pour camera {camera_id}")
            return
        
        try:
            # Détecter si c'est une webcam locale ou une URL RTSP
            if rtsp_url and rtsp_url.isdigit():
                source = int(rtsp_url)
            elif rtsp_url:
                source = rtsp_url
            else:
                source = 0  # Webcam par défaut
            
            cap = cv2.VideoCapture(source)
            
            # Configuration optimale
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Réduire le buffer
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            if not cap.isOpened():
                raise Exception(f"Impossible d'ouvrir le flux: {rtsp_url}")
            
            CameraService.active_streams[camera_id] = cap
            print(f"Stream démarré pour camera {camera_id} (source: {source})")
            
        except Exception as e:
            print(f" Erreur démarrage stream camera {camera_id}: {e}")
            raise
    
    @staticmethod
    async def stop_camera_stream(camera_id: str):
        """Arrête le stream d'une caméra"""
        if camera_id in CameraService.active_streams:
            cap = CameraService.active_streams[camera_id]
            cap.release()
            del CameraService.active_streams[camera_id]
            print(f" Stream arrêté pour camera {camera_id}")
    
    @staticmethod
    async def get_frame(camera_id: str, annotate: bool = True) -> Optional[bytes]:
        """
        Récupère une frame de la caméra
        
        Args:
            camera_id: UUID de la caméra (string)
            annotate: Annoter avec détections AI
        
        Returns:
            Frame encodée en JPEG ou None
        """
        if camera_id not in CameraService.active_streams:
            return None
        
        cap = CameraService.active_streams[camera_id]
        ret, frame = cap.read()
        
        if not ret or frame is None:
            return None
        
        # Annoter avec l'IA
        if annotate:
            detected_faces = ai_camera_service.detect_faces_in_frame(frame)
            if detected_faces:
                frame = ai_camera_service.annotate_frame(frame, detected_faces)
        
        # Encoder en JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        if not ret:
            return None
        
        return buffer.tobytes()
    
    @staticmethod
    async def search_employee_in_camera(
        db: Session,
        camera_id: str, 
        employee_name: str
    ) -> Dict:
        """
        Recherche un employé dans le flux d'une caméra
        
        Args:
            db: Session database
            camera_id: UUID de la caméra (string)
            employee_name: Nom complet de l'employé
        
        Returns:
            Résultat de recherche avec frames et coordonnées
        """
        # Vérifier que le stream est actif
        if camera_id not in CameraService.active_streams:
            return {
                'success': False,
                'error': 'Stream non actif',
                'message': 'Veuillez d\'abord démarrer le flux de la caméra'
            }
        
        # Vérifier que l'employé existe
        employee = db.query(Employee).filter(
            Employee.nom_complet.ilike(f"%{employee_name}%")
        ).first()
        
        if not employee:
            return {
                'success': False,
                'error': 'Employé non trouvé',
                'message': f'Aucun employé trouvé avec le nom "{employee_name}"'
            }
        
        # Rechercher dans plusieurs frames
        max_attempts = 15
        found = False
        result = None
        
        for attempt in range(max_attempts):
            cap = CameraService.active_streams[camera_id]
            ret, frame = cap.read()
            
            if not ret or frame is None:
                await asyncio.sleep(0.1)
                continue
            
            # Rechercher l'employé avec l'IA
            search_result = ai_camera_service.search_employee_in_frame(
                frame, 
                employee.nom_complet
            )
            
            if search_result and search_result['found']:
                found = True
                
                # Extraire la zone zoomée
                zoom_bbox = search_result['zoom_bbox']
                x, y, w, h = zoom_bbox['x'], zoom_bbox['y'], zoom_bbox['w'], zoom_bbox['h']
                
                # S'assurer que le bbox est dans les limites
                frame_h, frame_w = frame.shape[:2]
                x = max(0, min(x, frame_w - 1))
                y = max(0, min(y, frame_h - 1))
                w = min(w, frame_w - x)
                h = min(h, frame_h - y)
                
                zoomed_frame = frame[y:y+h, x:x+w]
                
                # Annoter la frame complète
                annotated_frame = ai_camera_service.annotate_frame(
                    frame, 
                    [search_result['employee']],
                    highlight_employee=employee.nom_complet
                )
                
                # Encoder les frames
                _, full_buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                _, zoom_buffer = cv2.imencode('.jpg', zoomed_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                
                result = {
                    'success': True,
                    'employee': {
                        'id': str(employee.id),
                        'nom_complet': employee.nom_complet,
                        'numero': employee.numero,
                        'departement_id': str(employee.departement_id)
                    },
                    'detection': {
                        'confidence': search_result['employee']['recognition_confidence'],
                        'mtcnn_confidence': search_result['employee']['mtcnn_confidence'],
                        'bbox': search_result['employee']['bbox'],
                        'zoom_bbox': zoom_bbox,
                        'center': search_result['center']
                    },
                    'frames': {
                        'full': base64.b64encode(full_buffer).decode('utf-8'),
                        'zoomed': base64.b64encode(zoom_buffer).decode('utf-8')
                    },
                    'message': f'Employé {employee.nom_complet} détecté avec {search_result["employee"]["recognition_confidence"]:.1%} de confiance'
                }
                break
            
            await asyncio.sleep(0.1)
        
        if not found:
            result = {
                'success': False,
                'error': 'Employé non détecté',
                'message': f'L\'employé {employee.nom_complet} n\'a pas été détecté dans le champ de la caméra ({max_attempts} tentatives)',
                'employee': {
                    'id': str(employee.id),
                    'nom_complet': employee.nom_complet,
                    'numero': employee.numero
                }
            }
        
        return result
    
    @staticmethod
    def get_active_streams_count() -> int:
        """Retourne le nombre de streams actifs"""
        return len(CameraService.active_streams)
    
    @staticmethod
    def get_active_streams_ids() -> List[str]:
        """Retourne la liste des IDs des streams actifs"""
        return list(CameraService.active_streams.keys())


# Instance singleton
camera_service = CameraService()