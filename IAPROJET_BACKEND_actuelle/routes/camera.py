# routes/camera.py
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import asyncio

from database import get_db
from service.camera_service import camera_service
from schemas.camera import CameraCreate, CameraResponse
from core.security import get_current_admin

router = APIRouter(prefix="/camera", tags=["Camera"])


# ========== ROUTES CRUD DE BASE ==========

@router.post("/", response_model=CameraResponse)
def add_camera(
    data: CameraCreate, 
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Créer une nouvelle caméra"""
    return camera_service.create_camera(db, data)


@router.get("/", response_model=List[dict])
def list_cameras(db: Session = Depends(get_db)):
    """
    📋 Liste toutes les caméras avec leurs départements
    
    Retourne:
        - Liste des caméras
        - Statut de streaming (actif/inactif)
        - Infos département
    """
    return camera_service.get_all_cameras(db)


@router.get("/{camera_id}", response_model=dict)
def get_camera(camera_id: UUID, db: Session = Depends(get_db)):
    """Récupère les détails d'une caméra"""
    cam = camera_service.get_camera_by_id(db, camera_id)
    if not cam:
        raise HTTPException(404, "Camera not found")
    return cam


@router.delete("/{camera_id}")
def delete(
    camera_id: UUID, 
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """Supprime une caméra (arrête le stream si actif)"""
    cam = camera_service.delete_camera(db, camera_id)
    if not cam:
        raise HTTPException(404, "Camera not found")
    return {"message": "Camera deleted"}


# ========== ROUTES STREAMING ==========

@router.post("/{camera_id}/start")
async def start_camera(
    camera_id: UUID,
    db: Session = Depends(get_db)
):
    """
    ▶️ Démarre le stream d'une caméra
    
    Lance le flux vidéo RTSP/webcam en arrière-plan.
    Appelez cette route AVANT d'ouvrir le WebSocket.
    """
    camera = camera_service.get_camera_by_id(db, camera_id)
    
    if not camera:
        raise HTTPException(404, "Camera not found")
    
    try:
        camera_id_str = str(camera_id)
        await camera_service.start_camera_stream(camera_id_str, camera['rtsp_url'])
        
        return {
            "success": True,
            "message": f"Stream démarré pour caméra {camera['numero']}",
            "camera_id": camera_id_str
        }
    except Exception as e:
        raise HTTPException(500, f"Erreur démarrage stream: {str(e)}")


@router.post("/{camera_id}/stop")
async def stop_camera(camera_id: UUID):
    """🛑 Arrête le stream d'une caméra"""
    try:
        camera_id_str = str(camera_id)
        await camera_service.stop_camera_stream(camera_id_str)
        
        return {
            "success": True,
            "message": f"Stream arrêté pour caméra {camera_id_str}"
        }
    except Exception as e:
        raise HTTPException(500, f"Erreur arrêt stream: {str(e)}")


@router.get("/{camera_id}/status")
async def get_stream_status(camera_id: UUID):
    """📊 Vérifie si une caméra est en streaming"""
    camera_id_str = str(camera_id)
    is_active = camera_id_str in camera_service.active_streams
    
    return {
        "camera_id": camera_id_str,
        "is_streaming": is_active,
        "active_streams_count": camera_service.get_active_streams_count()
    }


# ========== ROUTE RECHERCHE EMPLOYÉ (CŒUR DU DASHBOARD) ==========

@router.post("/{camera_id}/search-employee")
async def search_employee(
    camera_id: UUID,
    employee_name: str = Query(..., description="Nom complet de l'employé"),
    db: Session = Depends(get_db)
):
    """
    🔍 ROUTE PRINCIPALE : Recherche un employé dans le flux caméra
    
    Cette route :
    1. Vérifie que le stream est actif
    2. Vérifie que l'employé existe en DB
    3. Utilise l'IA (MTCNN + FaceNet) pour détecter les visages
    4. Compare avec le modèle SVM
    5. Retourne les frames annotées + zoom
    
    Args:
        camera_id: UUID de la caméra
        employee_name: Nom complet à rechercher (ex: "Jean Dupont")
    
    Returns:
        {
            "success": bool,
            "employee": {...},  # Infos employé
            "detection": {...},  # Coordonnées bbox, confidence
            "frames": {
                "full": "base64...",  # Frame complète annotée
                "zoomed": "base64..."  # Zoom sur l'employé
            },
            "message": str
        }
    
    Exemple d'utilisation:
        POST /camera/{uuid}/search-employee?employee_name=Jean%20Dupont
    """
    try:
        camera_id_str = str(camera_id)
        
        result = await camera_service.search_employee_in_camera(
            db=db,
            camera_id=camera_id_str,
            employee_name=employee_name
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(500, f"Erreur recherche employé: {str(e)}")


# ========== WEBSOCKET STREAMING VIDÉO ==========

@router.websocket("/ws/{camera_id}/stream")
async def websocket_camera_stream(
    websocket: WebSocket,
    camera_id: UUID,
    annotate: bool = Query(True, description="Annoter avec détections AI")
):
    """
    🎬 WebSocket pour streaming vidéo en temps réel
    
    Le WebSocket envoie des frames JPEG au format binaire.
    
    Usage Python:
    ```python
    import websockets
    import asyncio
    
    async def stream():
        uri = f"ws://localhost:8000/camera/ws/{camera_id}/stream?annotate=true"
        async with websockets.connect(uri) as ws:
            while True:
                frame_bytes = await ws.recv()
                # Traiter la frame...
    
    asyncio.run(stream())
    ```
    
    Usage JavaScript:
    ```javascript
    const ws = new WebSocket(`ws://localhost:8000/camera/ws/${cameraId}/stream?annotate=true`);
    ws.binaryType = 'arraybuffer';
    
    ws.onmessage = (event) => {
        const blob = new Blob([event.data], { type: 'image/jpeg' });
        const url = URL.createObjectURL(blob);
        imageElement.src = url;
    };
    ```
    
    Args:
        camera_id: UUID de la caméra
        annotate: Si true, annotations AI sur les frames
    """
    await websocket.accept()
    camera_id_str = str(camera_id)
    
    try:
        # Vérifier que le stream est actif
        if camera_id_str not in camera_service.active_streams:
            await websocket.send_json({
                "error": "Stream non actif",
                "message": f"Appelez d'abord POST /camera/{camera_id}/start"
            })
            await websocket.close()
            return
        
        print(f"✅ WebSocket connecté pour camera {camera_id_str}")
        
        # Boucle de streaming
        frame_count = 0
        while True:
            try:
                # Récupérer une frame
                frame_bytes = await camera_service.get_frame(camera_id_str, annotate=annotate)
                
                if frame_bytes is None:
                    await asyncio.sleep(0.033)  # ~30 FPS
                    continue
                
                # Envoyer au client
                await websocket.send_bytes(frame_bytes)
                
                frame_count += 1
                if frame_count % 300 == 0:  # Log toutes les 10 secondes
                    print(f"📹 Camera {camera_id_str}: {frame_count} frames envoyées")
                
                # Contrôler le framerate (~30 FPS)
                await asyncio.sleep(0.033)
                
            except WebSocketDisconnect:
                print(f"🔌 Client déconnecté pour camera {camera_id_str}")
                break
            except Exception as e:
                print(f"❌ Erreur streaming camera {camera_id_str}: {e}")
                await asyncio.sleep(0.1)
                
    except Exception as e:
        print(f"❌ Erreur WebSocket camera {camera_id_str}: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass
        print(f"🔒 WebSocket fermé pour camera {camera_id_str}")


@router.websocket("/ws/{camera_id}/detections")
async def websocket_detections(
    websocket: WebSocket,
    camera_id: UUID
):
    """
    🎯 WebSocket pour détections en temps réel (métadonnées seulement)
    
    Plus léger que le streaming vidéo complet.
    Envoie uniquement les infos de détection (noms, bbox, confidence).
    
    Usage:
    ```python
    async with websockets.connect(uri) as ws:
        while True:
            data = await ws.recv()
            detections = json.loads(data)
            print(detections['detections'])  # Liste des visages détectés
    ```
    
    Retourne:
    ```json
    {
        "timestamp": 1234567890.123,
        "camera_id": "uuid...",
        "detections": [
            {
                "employee_name": "Jean Dupont",
                "confidence": 0.95,
                "bbox": {"x": 100, "y": 200, "w": 80, "h": 100}
            }
        ],
        "count": 1
    }
    ```
    """
    await websocket.accept()
    camera_id_str = str(camera_id)
    
    try:
        if camera_id_str not in camera_service.active_streams:
            await websocket.send_json({
                "error": "Stream non actif"
            })
            await websocket.close()
            return
        
        print(f"✅ WebSocket détections connecté pour camera {camera_id_str}")
        
        from service.ai_camera_service import ai_camera_service
        
        while True:
            try:
                # Récupérer une frame brute
                cap = camera_service.active_streams[camera_id_str]
                ret, frame = cap.read()
                
                if not ret or frame is None:
                    await asyncio.sleep(0.2)
                    continue
                
                # Détecter les visages
                detections = ai_camera_service.detect_faces_in_frame(frame)
                
                # Envoyer les métadonnées (sans embedding)
                lightweight_detections = [
                    {
                        'employee_name': d['employee_name'],
                        'recognition_confidence': d['recognition_confidence'],
                        'mtcnn_confidence': d['mtcnn_confidence'],
                        'bbox': d['bbox']
                    }
                    for d in detections
                ]
                
                await websocket.send_json({
                    'timestamp': asyncio.get_event_loop().time(),
                    'camera_id': camera_id_str,
                    'detections': lightweight_detections,
                    'count': len(lightweight_detections)
                })
                
                # Envoyer toutes les 500ms
                await asyncio.sleep(0.5)
                
            except WebSocketDisconnect:
                print(f"🔌 WebSocket détections déconnecté pour camera {camera_id_str}")
                break
            except Exception as e:
                print(f"❌ Erreur détections camera {camera_id_str}: {e}")
                await asyncio.sleep(0.2)
                
    except Exception as e:
        print(f"❌ Erreur WebSocket détections: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass


# ========== ROUTE DEBUG ==========

@router.get("/debug/active-streams")
async def get_active_streams():
    """🔧 Debug: Liste les streams actifs"""
    return {
        "count": camera_service.get_active_streams_count(),
        "camera_ids": camera_service.get_active_streams_ids()
    }