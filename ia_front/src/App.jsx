import { useState } from 'react';
// Imports des composants principaux
import Sidebar from './components/Sidebar';
import Login from './pages/Login'; 
import Inscription from './pages/Inscription'; 
import Employes from './pages/Employes';
import Dashboard from './pages/Dashboard';
import Cameras from './pages/Cameras';
import Absences from './pages/Absences';
import DepartementForm from './pages/DepartementForm'; 
import { LogOut, User } from 'lucide-react';

function App() {
  // --- STATE (الذاكرة) ---
  const [activePage, setActivePage] = useState('Dashboard');
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  // NOTE: Dans une application réelle, isLoggedIn devrait être initialisé 
  // en vérifiant si un token valide existe déjà dans le localStorage.
  const [isLoggedIn, setIsLoggedIn] = useState(false); 
  const [authMode, setAuthMode] = useState('login'); 

  // --- NOUVELLE FONCTION: Gérer la déconnexion de manière sécurisée ---
  const handleLogout = () => {
    // 1. Supprimer le token d'accès stocké (ESSENTIEL pour la sécurité)
    localStorage.removeItem('accessToken'); 
    // 2. Mettre à jour l'état de connexion pour afficher la page de Login
    setIsLoggedIn(false);
    // 3. Fermer le menu profil
    setIsProfileOpen(false); 
    // 4. Réinitialiser la page active au Dashboard (pour la prochaine connexion)
    setActivePage('Dashboard');
  };
  
  // دالة لعرض محتوى الصفحات
  const renderContent = () => {
    switch (activePage) {
      case 'Dashboard': return <Dashboard />;
      case 'Gestion des Employés': return <Employes />;
      case 'Gestion des Caméras': return <Cameras />;
      case 'Gestion des Absences': return <Absences />;
      case 'Ajouter Département': return <DepartementForm />;
      default: return <Dashboard />;
    }
  };
  
  // 1. المنطق الأمني: Si non connecté, afficher Login/Register
  if (!isLoggedIn) {
    if (authMode === 'register') {
      return <Inscription setAuthMode={setAuthMode} />;
    }
    // الوضع الافتراضي: صفحة تسجيل الدخول
    return <Login onLoginSuccess={setIsLoggedIn} setAuthMode={setAuthMode} />;
  }

  // 2. الواجهة الرئيسية (Main Dashboard)
  return (
    <div className="flex bg-[#F8F9FA] min-h-screen font-sans">
      
      {/* Sidebar (80px) */}
      <Sidebar activePage={activePage} setActivePage={setActivePage} />
      
      {/* المحتوى الرئيسي (ml-80 لتفادي Sidebar) */}
      <main className="flex-1 ml-80 p-8 transition-all duration-300">
        
        {/* Header */}
        <header className="flex justify-end items-center mb-8">
          <div className="relative">
             <button 
               onClick={() => setIsProfileOpen(!isProfileOpen)}
               className="flex items-center gap-3 hover:bg-gray-100 p-1 pr-3 rounded-full transition"
             >
               <div className="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-white border-2 border-white shadow-sm"><User size={20} /></div>
             </button>

             {/* Dropdown Menu */}
             {isProfileOpen && (
               <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-gray-100 z-50 overflow-hidden">
                 
                 <div className="p-4 border-b border-gray-100 bg-gray-50">
                   <p className="text-gray-900 font-bold text-base">Admin</p>
                   <p className="text-[#00C4CC] text-xs font-medium uppercase tracking-wider">Administrateur</p>
                 </div>
                 
                 <div className="p-2">
                   {/* Bouton de Déconnexion qui appelle la nouvelle fonction handleLogout */}
                   <button 
                     onClick={handleLogout} 
                     className="w-full flex items-center gap-3 px-3 py-2 text-red-500 hover:bg-red-50 rounded-lg transition font-medium text-sm"
                   >
                     <LogOut size={18} />
                     Déconnexion
                   </button>
                 </div>
               </div>
             )}
          </div>
        </header>

        {/* عرض المحتوى حسب الصفحة المختارة */}
        {renderContent()}

      </main>
    </div>
  );
}

export default App;