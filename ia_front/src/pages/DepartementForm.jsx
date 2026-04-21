import { useState } from 'react';
import axios from 'axios';
import { Building, Save } from 'lucide-react';

const API_URL = "http://localhost:8000/departements/"; 

const getToken = () => localStorage.getItem('accessToken');

const DepartementForm = () => {
    // --- STATE ---
    const [nom, setNom] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');
        
        const token = getToken();

        if (!token) {
            setError("Erreur d'authentification. Veuillez vous reconnecter.");
            return;
        }

        try {
            const dataToSend = { nom };
            
            const response = await axios.post(
                API_URL, 
                dataToSend, 
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            setMessage(`Département "${response.data.nom}" ajouté avec succès!`);
            setNom('');
            
        } catch (err) {
            const errorMessage = err.response?.data?.detail || "Erreur de création du département.";
            setError(errorMessage);
        }
    };

    return (
        <div className="font-sans">
            <h1 className="text-3xl font-normal text-gray-800 mb-6 border-b pb-3">Ajouter un Nouveau Département</h1>
            
            <div className="flex justify-center">
            
                <div className="w-full max-w-2xl bg-white p-8 rounded-xl shadow-lg border border-gray-200">
                    
                    {message && (<div className="bg-green-100 text-green-700 p-3 rounded-lg text-sm mb-4 border border-green-200 font-medium">{message}</div>)}
                    {error && (<div className="bg-red-100 text-red-700 p-3 rounded-lg text-sm mb-4 border border-red-200 font-medium">{error}</div>)}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Nom du Département</label>
                            <div className="relative">
                                <Building size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                                <input 
                                    type="text" 
                                    value={nom} 
                                    onChange={(e) => setNom(e.target.value)} 
                                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00C4CC] outline-none"
                                    placeholder="Ex: Informatique, Marketing..."
                                    required
                                />
                            </div>
                        </div>

                        <button 
                            type="submit" 
                            className="w-full bg-[#00C4CC] text-white py-3 rounded-lg font-bold hover:bg-[#00A0A6] transition shadow-md flex items-center justify-center gap-2"
                        >
                            <Save size={20} /> Enregistrer
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default DepartementForm;