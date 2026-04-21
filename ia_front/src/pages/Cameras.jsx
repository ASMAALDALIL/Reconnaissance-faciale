import { useState, useEffect , useRef } from 'react';
import axios from 'axios';
import { 
    Plus, Trash2, X, Video, Search, Camera, Clock, Building,
    Play, Square, AlertCircle, Loader, CheckCircle, XCircle, Zap
} from 'lucide-react'; // Retrait de 'Pencil', 'Eye', 'ChevronDown'

const API_URL = "http://localhost:8000/camera/";
const DEPT_API_URL = "http://localhost:8000/departements/"; 
const WS_URL = "ws://localhost:8000/camera/ws/";

const Cameras = () => {
  const [cameras, setCameras] = useState([]); 
  const [departements, setDepartements] = useState([]); 
  const [selectedCamera, setSelectedCamera] = useState(null); 
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [cameraToDelete, setCameraToDelete] = useState(null);

  const [formData, setFormData] = useState({ 
    numero: "", rtsp_url: "", departement_id: "", is_entry_camera: false 
  });
  
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState("");
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString('fr-FR'));
  const [isStreaming, setIsStreaming] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchResult, setSearchResult] = useState(null);
  const [streamError, setStreamError] = useState(null);

    const wsRef = useRef(null);
    const videoRef = useRef(null);
    const videoUrlRef = useRef(null);
  const getToken = () => localStorage.getItem('accessToken');

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString('fr-FR'));
    }, 1000);
    return () => clearInterval(timer);
  }, []);


  const fetchData = async () => {
    const token = getToken();
    if (!token) { return; }
    
    try {
      const config = { headers: { 'Authorization': `Bearer ${token}` } };
      
      const [camerasRes, deptRes] = await Promise.all([
          axios.get(API_URL, config), 
          axios.get(DEPT_API_URL, config) 
      ]);

      const deptMap = new Map(deptRes.data.map(d => [d.id, d.nom])); 

      const mappedCameras = camerasRes.data.map(cam => ({
          ...cam,
          departement_nom: cam.departement ? cam.departement.nom : deptMap.get(cam.departement_id) || "Non assigné", 
          is_entry_camera_text: cam.is_entry_camera ? "Entrée" : "Autre"
      }));
      
      setCameras(mappedCameras);
      setDepartements(deptRes.data); 
      
    } catch (error) {
      console.error("Erreur de l'API:", error.response);
      setError("Erreur lors du chargement des données.");
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (videoUrlRef.current) {
        URL.revokeObjectURL(videoUrlRef.current);
      }
    };
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({ 
        ...prev, 
        [name]: type === 'checkbox' ? checked : value 
    }));
  };

  const openAddModal = () => {
    setFormData({ 
        numero: "", rtsp_url: "", departement_id: departements.length > 0 ? departements[0].id : "", 
        is_entry_camera: false 
    });
    setIsFormOpen(true);
    setError('');
  };

  const handleSave = async (e) => {
    e.preventDefault();
    const token = getToken();
    setError('');

    const dataToSend = {
        numero: formData.numero,
        rtsp_url: formData.rtsp_url || null, 
        departement_id: formData.departement_id,
        is_entry_camera: formData.is_entry_camera,
    };

    try {
        const config = { headers: { 'Authorization': `Bearer ${token}` } };
        
        await axios.post(API_URL, dataToSend, config); 

        setIsFormOpen(false);
        fetchData();
    } catch (err) {
        const errorMessage = err.response?.data?.detail || "Erreur lors de l'ajout de la caméra.";
        setError(errorMessage);
        console.error("Save Error:", err.response);
    }
  };

  const openDeleteModal = (camera) => {
    setCameraToDelete(camera);
    setIsDeleteOpen(true);
  };

  const confirmDelete = async () => {
    const token = getToken();
    try {
      await axios.delete(`${API_URL}${cameraToDelete.id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
      });
      setIsDeleteOpen(false);
      fetchData();
    } catch (error) {
      alert("Erreur lors de la suppression.");
    }
  };
  
  const startStream = async (camera) => {
    const token = getToken();
    setStreamError(null);
    
    try {
      // 1. Démarrer le stream backend
      const response = await axios.post(
        `${API_URL}${camera.id}/start`,
        {},
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (!response.data.success) {
        throw new Error(response.data.message || "Échec démarrage stream");
      }


const ws = new WebSocket(`${WS_URL}${camera.id}/stream?annotate=true`);
      wsRef.current = ws;
      ws.binaryType = 'arraybuffer';

      ws.onopen = () => {
        console.log('WebSocket connecté');
        setIsStreaming(true);
      };

      ws.onmessage = (event) => {
        const blob = new Blob([event.data], { type: 'image/jpeg' });
        
        if (videoUrlRef.current) {
          URL.revokeObjectURL(videoUrlRef.current);
        }
        
        const url = URL.createObjectURL(blob);
        videoUrlRef.current = url;
        
        if (videoRef.current) {
          videoRef.current.src = url;
        }
      };

      ws.onerror = (error) => {
        console.error('Erreur WebSocket:', error);
        setStreamError('Erreur de connexion au flux vidéo');
        setIsStreaming(false);
      };

      ws.onclose = () => {
        console.log('WebSocket fermé');
        setIsStreaming(false);
      };

    } catch (error) {
      console.error(' Erreur démarrage stream:', error);
      setStreamError(error.response?.data?.detail || "Erreur lors du démarrage du stream");
      setIsStreaming(false);
    }
  };

  const stopStream = async () => {
    const token = getToken();
    
    try {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      if (videoUrlRef.current) {
        URL.revokeObjectURL(videoUrlRef.current);
        videoUrlRef.current = null;
      }

      if (videoRef.current) {
        videoRef.current.src = '';
      }

      if (selectedCamera) {
        await axios.post(
          `${API_URL}${selectedCamera.id}/stop`,
          {},
          { headers: { 'Authorization': `Bearer ${token}` } }
        );
      }

      setIsStreaming(false);
      setStreamError(null);
      
    } catch (error) {
      console.error(' Erreur arrêt stream:', error);
    }
  };


  const handleSearchEmployee = async (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim() || !selectedCamera) {
      return;
    }

    const token = getToken();
    setIsSearching(true);
    setSearchResult(null);
    setStreamError(null);

    try {
      const response = await axios.post(
        `${API_URL}${selectedCamera.id}/search-employee?employee_name=${encodeURIComponent(searchQuery)}`,
        {},
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      setSearchResult(response.data);

    } catch (error) {
      console.error(' Erreur recherche:', error);
      const errorMsg = error.response?.data?.detail || "Erreur lors de la recherche";
      setSearchResult({
        success: false,
        error: errorMsg,
        message: errorMsg
      });
    } finally {
      setIsSearching(false);
    }
  };
const openCameraModal = async (camera) => {
    setSelectedCamera(camera);
    setSearchQuery("");
    setSearchResult(null);
    setStreamError(null);
    
  
    await startStream(camera);
  };

  const closeCameraModal = async () => {
    await stopStream();
    setSelectedCamera(null);
    setSearchQuery("");
    setSearchResult(null);
  };


  return (
    <div className="font-sans relative">
      
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-normal text-gray-800">Gestion des Caméras</h1>
        <button onClick={openAddModal} className="bg-[#00C4CC] text-white px-6 py-2.5 rounded-lg font-bold shadow-sm hover:bg-[#00A0A6] transition flex items-center gap-2">
          <Plus size={20} /> Ajouter Caméra
        </button>
      </div>

      {/* Grid Caméras */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {cameras.length === 0 ? (
             <p className="col-span-4 text-center text-gray-500 py-10">
                Aucune caméra enregistrée.
            </p>
        ) : (
            cameras.map(cam => (
                <div 
                    key={cam.id} 
                    className="relative bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden group hover:shadow-xl transition duration-300 cursor-pointer"
                    onClick={() => openCameraModal(cam)}
                >
                    <div className="h-40 bg-gray-900 flex items-center justify-center relative">
                        <Camera size={48} className="text-[#00C4CC] opacity-60" />
                        
                        {cam.is_streaming && (
                          <div className="absolute top-2 left-2 flex items-center gap-1 bg-red-500 text-white text-xs px-2 py-1 rounded animate-pulse">
                            <div className="w-2 h-2 bg-white rounded-full"></div>
                            EN DIRECT
                          </div>
                        )}
                        
                        <div className="absolute top-2 right-2 flex items-center gap-1 bg-black/50 text-white text-xs px-2 py-1 rounded">
                            <Zap size={10} className={cam.is_entry_camera ? "text-green-400" : "text-gray-400"} />
                            {cam.is_entry_camera_text}
                        </div>
                    </div>

                    <div className="p-4">
                        <p className="text-sm text-gray-500 font-medium">{cam.departement_nom}</p>
                        <h3 className="text-lg font-bold text-gray-800 truncate mt-1">
                            Caméra N° {cam.numero}
                        </h3>
                        <p className="text-xs text-gray-400 truncate mt-1">
                          {cam.rtsp_url || "Pas d'URL"}
                        </p>
                    </div>

                    <div className="p-4 pt-0 flex justify-end gap-2">
                        <button 
                          onClick={(e) => { e.stopPropagation(); openDeleteModal(cam); }} 
                          className="p-2 text-red-500 hover:text-red-700 transition"
                        >
                            <Trash2 size={18} />
                        </button>
                    </div>
                </div>
            ))
        )}
      </div>

      {isFormOpen && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-xl shadow-2xl w-full max-w-lg">
              <h2 className="text-2xl font-bold mb-4 border-b pb-2">Ajouter une Nouvelle Caméra</h2>
              
              {error && (<div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm mb-4 border border-red-200 font-medium">{error}</div>)}
              
              <form onSubmit={handleSave} className="space-y-4">
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Numéro</label>
                  <input 
                      type="text" 
                      name="numero" 
                      value={formData.numero} 
                      onChange={handleChange} 
                      required
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-md shadow-sm mt-1"
                      placeholder="Ex: C001"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">URL RTSP (Optionnel)</label>
                  <input 
                      type="text" 
                      name="rtsp_url" 
                      value={formData.rtsp_url} 
                      onChange={handleChange} 
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-md shadow-sm mt-1"
                      placeholder="rtsp://user:pass@ip:port/stream"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Département</label>
                  <div className="relative mt-1">
                     <Building size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                     <select 
                         name="departement_id" 
                         value={formData.departement_id} 
                         onChange={handleChange} 
                         required
                         className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-md shadow-sm"
                     >
                         <option value="">Sélectionner un Département</option>
                         {departements.map(dept => (
                             <option key={dept.id} value={dept.id}>
                                 {dept.nom}
                             </option>
                         ))}
                     </select>
                  </div>
                </div>

                <div className="flex items-center pt-2">
                    <input
                        id="is_entry_camera"
                        name="is_entry_camera"
                        type="checkbox"
                        checked={formData.is_entry_camera}
                        onChange={handleChange}
                        className="h-4 w-4 text-[#00C4CC] border-gray-300 rounded focus:ring-[#00C4CC]"
                    />
                    <label htmlFor="is_entry_camera" className="ml-2 block text-sm text-gray-900">
                        Caméra d'entrée (pour l'enregistrement des présences)
                    </label>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button type="button" onClick={() => setIsFormOpen(false)} className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition">
                    Annuler
                  </button>
                  <button type="submit" className="px-4 py-2 text-sm font-medium text-white bg-[#00C4CC] rounded-lg hover:bg-[#00A0A6] transition">
                    Ajouter
                  </button>
                </div>
              </form>
            </div>
          </div>
      )}

      {isDeleteOpen && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-xl shadow-2xl w-full max-w-sm text-center">
              <X size={40} className="text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold mb-2">Confirmer la suppression</h2>
              <p className="text-gray-600 mb-6">Êtes-vous sûr de vouloir supprimer la caméra **N° {cameraToDelete?.numero}** ?</p>
              <div className="flex justify-center space-x-4">
                <button onClick={() => setIsDeleteOpen(false)} className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition">
                  Annuler
                </button>
                <button onClick={confirmDelete} className="px-4 py-2 text-sm font-medium text-white bg-red-500 rounded-lg hover:bg-red-700 transition">
                  Supprimer
                </button>
              </div>
            </div>
          </div>
      )}
      
      {selectedCamera && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center border-b pb-3 mb-4">
                <h2 className="text-2xl font-bold text-gray-800">Détails Caméra N° {selectedCamera.numero}</h2>
                <button onClick={() => setSelectedCamera(null)} className="text-gray-400 hover:text-gray-600">
                  <X size={24} />
                </button>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                 
                <div className="lg:col-span-2 bg-gray-900 rounded-lg p-6 flex items-center justify-center relative h-96">
                    <div className="text-center opacity-70">
                        <Video size={64} className="text-[#00C4CC] mx-auto mb-4" />
                        <p className="text-white text-sm">Flux vidéo en direct (Simulation)</p>
                        <p className="text-[#00C4CC] text-xs mt-1">{currentTime}</p>
                    </div>
                    
                    <div className="absolute top-4 left-4 bg-[#00C4CC] text-white text-xs px-2 py-0.5 rounded-md font-bold">
                        {selectedCamera.departement_nom}
                    </div>
                </div>

                <div className="lg:col-span-1 space-y-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                        <h3 className="text-base font-bold text-gray-800 mb-2">Informations Clés</h3>
                        <p className="text-sm text-gray-700 flex justify-between">
                            **Statut:** <span className={selectedCamera.is_entry_camera ? "text-green-600" : "text-gray-500"}>
                                {selectedCamera.is_entry_camera_text}
                            </span>
                        </p>
                        <p className="text-sm text-gray-700 flex justify-between">
                            **ID:** <span className="text-xs text-gray-500 truncate">{selectedCamera.id}</span>
                        </p>
                        <p className="text-sm text-gray-700 flex justify-between items-start pt-2">
                             **URL:** <span className="text-xs text-gray-500 w-2/3 break-all text-right">
                                {selectedCamera.rtsp_url || "N/A"}
                            </span>
                        </p>
                    </div>

                    <div className="bg-white p-4 border border-gray-200 rounded-lg">
                        <label className="block text-sm font-bold text-gray-700 mb-2">Rechercher un employé</label>
                        <form onSubmit={handleSearchEmployee} className="flex gap-3">
                          <input 
                              type="text" 
                              value={searchQuery} 
                              onChange={(e) => setSearchQuery(e.target.value)} 
                              placeholder="Nom/ID de l'employé..." 
                              className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg" 
                          />
                          <button type="submit" className="bg-[#00C4CC] text-white px-4 py-2.5 rounded-lg font-bold hover:bg-[#00A0A6] transition flex items-center">
                            <Search size={20} />
                          </button>
                        </form>
                    </div>
                </div>
              </div>
              
              <div className="flex justify-end pt-4">
                  <button onClick={() => setSelectedCamera(null)} className="px-6 py-2 text-sm font-medium text-white bg-gray-500 rounded-lg hover:bg-gray-700 transition">
                    Fermer
                  </button>
              </div>
            </div>
          </div>
      )}

    </div>
  );
};

export default Cameras;