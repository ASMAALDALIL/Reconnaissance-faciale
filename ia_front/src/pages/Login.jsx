// src/pages/Login.jsx

import { useState } from 'react';
import axios from 'axios';
import { User, Lock, LogIn } from 'lucide-react';
import { ADMIN_LOGIN_URL } from '../config';

const Login = ({ onLoginSuccess, setAuthMode }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await axios.post(
        ADMIN_LOGIN_URL,
        {
          nom: username,
          mot_de_passe: password
        },
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );

      const token = response.data.access_token;
      localStorage.setItem('accessToken', token);

      onLoginSuccess(true);

    } catch (err) {
      const errorMessage =
        err.response?.data?.detail ||
        'Erreur de connexion au serveur ou identifiants incorrects.';
      setError(errorMessage);
      console.error("Login Error:", err.response);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#F8F9FA] font-sans">
      <div className="w-full max-w-sm p-8 bg-white rounded-2xl shadow-[0_4px_30px_rgba(0,0,0,0.05)] border border-gray-100">
        <h2 className="text-3xl font-bold text-gray-800 mb-2 text-center">
          Bienvenue
        </h2>
        <p className="text-gray-500 text-center mb-8">
          Connectez-vous à votre compte Admin.
        </p>

        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm mb-4 border border-red-200 font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">

          {/* Champ Nom */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom (Identifiant)
            </label>
            <div className="relative">
              <User
                size={20}
                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00C4CC] outline-none"
                required
              />
            </div>
          </div>

          {/* Champ Mot de passe */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mot de passe
            </label>
            <div className="relative">
              <Lock
                size={20}
                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00C4CC] outline-none"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-[#00C4CC] text-white py-3 rounded-lg font-bold hover:bg-[#00A0A6] transition shadow-md flex items-center justify-center gap-2"
          >
            <LogIn size={20} /> Se connecter
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Pas encore de compte?
            <button
              type="button"
              onClick={() => setAuthMode('register')}
              className="text-[#00C4CC] font-semibold ml-1 hover:underline"
            >
              S'inscrire
            </button>
          </p>
        </div>

      </div>
    </div>
  );
};

export default Login;
