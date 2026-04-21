// src/pages/Inscription.jsx

import { useState } from 'react';
import axios from 'axios';
import { User, Lock, Phone, Home, ArrowLeft } from 'lucide-react';
import { ADMIN_REGISTER_URL } from '../config';

const Inscription = ({ setAuthMode }) => {
    const [formData, setFormData] = useState({
        nom: '',
        prenom: '',
        adresse: '',
        numero: '',
        mot_de_passe: '',
        confirm_mot_de_passe: '',
    });

    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        // Vérification Mot de passe
        if (formData.mot_de_passe !== formData.confirm_mot_de_passe) {
            setError('Le mot de passe et la confirmation ne correspondent pas.');
            return;
        }

        try {
            const dataToSend = {
                nom: formData.nom,
                prenom: formData.prenom,
                adresse: formData.adresse,
                numero: formData.numero,
                mot_de_passe: formData.mot_de_passe,
            };

            const response = await axios.post(ADMIN_REGISTER_URL, dataToSend, {
                headers: { "Content-Type": "application/json" }
            });

            setSuccess('Inscription réussie ! Veuillez vous connecter.');
            
            // Redirection après 2-3 sec
            setTimeout(() => setAuthMode('login'), 2000);

        } catch (err) {
            // Récupérer message d’erreur backend
            const errorMessage =
                err.response?.data?.detail ||
                err.response?.data?.message ||
                'Erreur lors de l’inscription.';

            setError(errorMessage);
            console.error("Inscription Error:", err);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-[#F8F9FA] font-sans">
            <div className="w-full max-w-md p-8 bg-white rounded-2xl shadow-[0_4px_30px_rgba(0,0,0,0.05)] border border-gray-100">

                {/* Retour Login */}
                <button
                    onClick={() => setAuthMode('login')}
                    className="flex items-center text-sm font-medium text-gray-500 hover:text-[#00C4CC] transition mb-6"
                >
                    <ArrowLeft size={16} className="mr-1" />
                    Retour à la connexion
                </button>

                <h2 className="text-3xl font-bold text-gray-800 mb-2 text-center">
                    Créer un compte Admin
                </h2>

                {error && <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm mb-4 border">{error}</div>}
                {success && <div className="bg-green-50 text-green-700 p-3 rounded-lg text-sm mb-4 border">{success}</div>}

                <form onSubmit={handleSubmit} className="space-y-4">

                    <div className="grid grid-cols-2 gap-4">
                        <InputGroup icon={User} name="prenom" label="Prénom" value={formData.prenom} onChange={handleChange} />
                        <InputGroup icon={User} name="nom" label="Nom" value={formData.nom} onChange={handleChange} />
                    </div>

                    <InputGroup icon={Phone} name="numero" label="Numéro de Téléphone" value={formData.numero} onChange={handleChange} />
                    <InputGroup icon={Home} name="adresse" label="Adresse" value={formData.adresse} onChange={handleChange} />

                    <div className="grid grid-cols-2 gap-4">
                        <InputGroup icon={Lock} name="mot_de_passe" label="Mot de passe" type="password" value={formData.mot_de_passe} onChange={handleChange} />
                        <InputGroup icon={Lock} name="confirm_mot_de_passe" label="Confirmer mot de passe" type="password" value={formData.confirm_mot_de_passe} onChange={handleChange} />
                    </div>

                    <button type="submit" className="w-full bg-[#00C4CC] text-white py-3 rounded-lg font-bold hover:bg-[#00A0A6] transition shadow-md mt-6">
                        S'inscrire
                    </button>
                </form>
            </div>
        </div>
    );
};

const InputGroup = ({ icon: Icon, label, name, value, onChange, type = "text" }) => (
    <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
        <div className="relative">
            <Icon size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
                type={type}
                name={name}
                value={value}
                onChange={onChange}
                required
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00C4CC] outline-none"
            />
        </div>
    </div>
);

export default Inscription;
