import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Plus, Pencil, Trash2, X, Building, Phone, MapPin, Image as ImageIcon, User } from 'lucide-react';

const API_URL = "http://localhost:8000/employees";
const DEPT_API_URL = "http://localhost:8000/departements";

const Employes = () => {
  // --- STATE ---
  const [employes, setEmployes] = useState([]);
  const [departements, setDepartements] = useState([]);

  const [searchTerm, setSearchTerm] = useState("");

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentEmployee, setCurrentEmployee] = useState(null);

  // Modification : On utilise 'nom_complet' directement
  const [formData, setFormData] = useState({
    nom_complet: "", 
    adresse: "",
    tel: "",
    path_dossier_images: "",
    departement_id: ""
  });

  // --- 1. CHARGEMENT DES DONNÉES ---
  const fetchData = async () => {
    const token = localStorage.getItem("accessToken");
    if (!token) return;

    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };

      const [empRes, deptRes] = await Promise.all([
        axios.get(API_URL, config),
        axios.get(DEPT_API_URL, config),
      ]);

      const deptList = deptRes.data;
      setDepartements(deptList);
      const deptMap = new Map(deptList.map((d) => [d.id, d.nom]));

      const mappedEmployes = empRes.data.map((emp) => {
        return {
          ...emp,
          // Plus besoin de découper le nom/prénom pour l'affichage
          departement_nom: deptMap.get(emp.departement_id) || "Non assigné",
        };
      });

      setEmployes(mappedEmployes);
    } catch (error) {
      console.error("Erreur chargement:", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // --- 2. GESTION DU FORMULAIRE ---
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const openAddModal = () => {
    setIsEditing(false);
    setCurrentEmployee(null);
    setFormData({
      nom_complet: "", // Champ unique
      adresse: "",
      tel: "",
      path_dossier_images: "",
      departement_id: departements.length > 0 ? departements[0].id : "",
    });
    setIsFormOpen(true);
  };

  const openEditModal = (employee) => {
    setIsEditing(true);
    setCurrentEmployee(employee);
    setFormData({
      nom_complet: employee.nom_complet, // On récupère le nom complet direct
      adresse: employee.adresse,
      tel: employee.numero,
      path_dossier_images: employee.path_dossier_images || "",
      departement_id: employee.departement_id,
    });
    setIsFormOpen(true);
  };

  // --- 3. SAUVEGARDE ---
  const handleSave = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("accessToken");
    
    const config = {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    };

    const payload = {
      nom_complet: formData.nom_complet, // Envoi direct sans concaténation
      adresse: formData.adresse,
      numero: formData.tel,
      departement_id: formData.departement_id,
      path_dossier_images: formData.path_dossier_images
    };

    try {
      if (isEditing && currentEmployee) {
        await axios.put(`${API_URL}/${currentEmployee.id}`, payload, config);
      } else {
        await axios.post(API_URL, payload, config);
      }

      setIsFormOpen(false);
      fetchData();
    } catch (error) {
      console.error("Erreur sauvegarde:", error.response || error);
      alert("Erreur lors de l'enregistrement.");
    }
  };

  // --- 4. SUPPRESSION ---
  const handleDelete = async (id) => {
    if (!window.confirm("Voulez-vous vraiment supprimer cet employé ?")) return;
    const token = localStorage.getItem("accessToken");
    try {
      await axios.delete(`${API_URL}/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchData();
    } catch (error) {
      alert("Erreur suppression.");
    }
  };

  // --- 5. RECHERCHE ---
  const filteredEmployes = employes.filter((emp) => {
    const search = searchTerm.toLowerCase();
    return (
      emp.nom_complet.toLowerCase().includes(search) ||
      emp.departement_nom.toLowerCase().includes(search)
    );
  });

  return (
    <div className="p-6 font-sans bg-gray-50 min-h-screen">
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
        <h1 className="text-3xl font-light text-gray-800">Gestion des Employés</h1>
        <button
          onClick={openAddModal}
          className="bg-[#00C4CC] hover:bg-[#00A0A6] text-white px-6 py-2.5 rounded-lg font-bold shadow-md transition flex items-center gap-2"
        >
          <Plus size={20} /> Ajouter Employé
        </button>
      </div>

      {/* TABLEAU */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {/* Barre de recherche */}
        <div className="p-5 border-b border-gray-100 bg-gray-50/50">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher (Nom, Département)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00C4CC]/50 transition"
            />
          </div>
        </div>

        {/* Table - Colonne Image Supprimée */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#EAFBFC] text-gray-600 text-sm uppercase tracking-wider">
                {/* Colonne Image supprimée ici */}
                <th className="p-4 font-semibold">Nom Complet</th>
                <th className="p-4 font-semibold">Département</th>
                <th className="p-4 font-semibold">Adresse</th>
                <th className="p-4 font-semibold">Téléphone</th>
                <th className="p-4 font-semibold text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredEmployes.map((emp) => (
                <tr key={emp.id} className="hover:bg-gray-50 transition">
                   {/* Cellule Image supprimée ici */}
                  <td className="p-4 text-gray-700 font-medium">{emp.nom_complet}</td>
                  <td className="p-4">
                    <span className="px-3 py-1 rounded-full text-xs font-semibold bg-cyan-100 text-cyan-700">
                      {emp.departement_nom}
                    </span>
                  </td>
                  <td className="p-4 text-gray-500 text-sm max-w-xs truncate" title={emp.adresse}>{emp.adresse}</td>
                  <td className="p-4 text-gray-500 text-sm">{emp.numero}</td>
                  <td className="p-4">
                    <div className="flex items-center justify-center gap-2">
                      <button onClick={() => openEditModal(emp)} className="p-1.5 text-cyan-500 hover:bg-cyan-50 rounded-md transition">
                        <Pencil size={18} />
                      </button>
                      <button onClick={() => handleDelete(emp.id)} className="p-1.5 text-red-400 hover:bg-red-50 rounded-md transition">
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredEmployes.length === 0 && (
                <tr><td colSpan="5" className="p-8 text-center text-gray-400">Aucun employé trouvé.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* MODAL FORMULAIRE */}
      {isFormOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
            <div className="bg-[#00C4CC] p-6 flex justify-between items-center text-white">
              <h2 className="text-xl font-bold">{isEditing ? "Modifier l'Employé" : "Nouvel Employé"}</h2>
              <button onClick={() => setIsFormOpen(false)} className="hover:bg-white/20 p-1 rounded-full transition"><X size={24} /></button>
            </div>

            <form onSubmit={handleSave} className="p-6 space-y-4">
              
              {/* Nom Complet (Champ Unique) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nom Complet</label>
                <div className="relative">
                    <User size={18} className="absolute left-3 top-3 text-gray-400" />
                    <input 
                        name="nom_complet" 
                        required 
                        value={formData.nom_complet} 
                        onChange={handleChange} 
                        placeholder="Ex: Jean Dupont"
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00C4CC] outline-none transition" 
                    />
                </div>
              </div>

              {/* Chemin de l'image (Texte) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Chemin de l'image (URL/Path)</label>
                <div className="relative">
                    <ImageIcon size={18} className="absolute left-3 top-3 text-gray-400" />
                    <input 
                        name="path_dossier_images" 
                        value={formData.path_dossier_images} 
                        onChange={handleChange} 
                        placeholder="Ex: http://monsite.com/photo.jpg"
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00C4CC] outline-none transition" 
                    />
                </div>
              </div>

              {/* Département */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Département</label>
                <div className="relative">
                   <Building size={18} className="absolute left-3 top-3 text-gray-400" />
                   <select name="departement_id" value={formData.departement_id} onChange={handleChange} required className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00C4CC] outline-none bg-white transition">
                       <option value="">-- Sélectionner --</option>
                       {departements.map(dept => (<option key={dept.id} value={dept.id}>{dept.nom}</option>))}
                   </select>
                </div>
              </div>

              {/* Adresse */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Adresse</label>
                <div className="relative">
                    <MapPin size={18} className="absolute left-3 top-3 text-gray-400" />
                    <input name="adresse" required value={formData.adresse} onChange={handleChange} className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00C4CC] outline-none transition" />
                </div>
              </div>

              {/* Téléphone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Téléphone</label>
                <div className="relative">
                    <Phone size={18} className="absolute left-3 top-3 text-gray-400" />
                    <input name="tel" required value={formData.tel} onChange={handleChange} className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00C4CC] outline-none transition" />
                </div>
              </div>

              {/* Boutons */}
              <div className="flex justify-end space-x-3 pt-6 border-t mt-2">
                <button type="button" onClick={() => setIsFormOpen(false)} className="px-5 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition">Annuler</button>
                <button type="submit" className="px-6 py-2 text-sm font-medium text-white bg-[#00C4CC] rounded-lg hover:bg-[#00A0A6] shadow-md transition transform active:scale-95">
                  {isEditing ? "Enregistrer" : "Ajouter"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Employes;