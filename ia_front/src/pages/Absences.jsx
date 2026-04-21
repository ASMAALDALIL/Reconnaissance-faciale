import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Calendar as CalendarIcon, Phone, UserX, CalendarDays } from 'lucide-react';

// IMPORTS POUR LE CALENDRIER
import DatePicker, { registerLocale } from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import fr from 'date-fns/locale/fr';

registerLocale('fr', fr);

const API_URL = "http://localhost:8000/presence/absents";
const DEPT_API_URL = "http://localhost:8000/departements";

const Absence = () => {

  const getLocalDate = () => {
    const d = new Date();
    const offset = d.getTimezoneOffset();
    const localDate = new Date(d.getTime() - (offset * 60 * 1000));
    return localDate.toISOString().split('T')[0];
  };

  const todayStr = getLocalDate();

  const [absences, setAbsences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('day');
  const [selectedDate, setSelectedDate] = useState(todayStr);
  const [searchTerm, setSearchTerm] = useState("");

  const fetchData = async () => {
    setLoading(true);
    const token = localStorage.getItem("accessToken");
    if (!token) return;

    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      const queryParams = `?target_date=${selectedDate}&mode=${viewMode}`;
      const absentsUrl = `${API_URL}${queryParams}`;

      const [deptRes, absRes] = await Promise.all([
        axios.get(DEPT_API_URL, config),
        axios.get(absentsUrl, config)
      ]);

      const deptMap = new Map(deptRes.data.map(d => [d.id, d.nom]));

      const mappedAbsences = absRes.data.map(emp => ({
        id: emp.id,
        nom_complet: emp.nom_complet,
        numero: emp.numero,
        departement_nom: deptMap.get(emp.departement_id) || "Non assigné",
        // Tente de récupérer la date de l'absence si fournie par le backend
        date_absence: emp.timestamp ? new Date(emp.timestamp).toLocaleDateString('fr-FR') : null
      }));

      setAbsences(mappedAbsences);

    } catch (error) {
      console.error("Erreur chargement absences:", error);
      setAbsences([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedDate, viewMode]);

  const getGroupedAbsences = () => {
    const filtered = absences.filter(emp =>
      emp.nom_complet.toLowerCase().includes(searchTerm.toLowerCase())
    );
    const grouped = filtered.reduce((acc, emp) => {
      const dept = emp.departement_nom;
      if (!acc[dept]) acc[dept] = [];
      acc[dept].push(emp);
      return acc;
    }, {});
    return grouped;
  };

  const groupedData = getGroupedAbsences();
  const sortedDepartments = Object.keys(groupedData).sort();

  return (
    <div className="p-6 font-sans bg-gray-50 min-h-screen">

      <h1 className="text-3xl font-light text-gray-800 mb-8">Gestion des Absences</h1>

      {/* BARRE DE CONTRÔLE */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 mb-6 flex flex-col md:flex-row justify-between items-center gap-4">

        {/* CALENDRIER */}
        <div className="flex items-center gap-4 w-full md:w-auto">
          <div className="relative">
            <CalendarIcon className={`absolute left-3 top-1/2 transform -translate-y-1/2 z-10 ${viewMode === 'day' ? 'text-[#00C4CC]' : 'text-gray-300'}`} size={18} />
            <DatePicker
              selected={new Date(selectedDate)}
              onChange={(date) => {
                const offset = date.getTimezoneOffset();
                const local = new Date(date.getTime() - (offset * 60 * 1000));
                setSelectedDate(local.toISOString().split('T')[0]);
              }}
              locale="fr"
              dateFormat="dd/MM/yyyy"
              maxDate={new Date()}
              disabled={viewMode !== 'day'}
              className={`pl-10 pr-4 py-2 border rounded-lg w-full outline-none transition font-medium cursor-pointer
                 ${viewMode !== 'day' ? 'bg-gray-50 text-gray-400 border-gray-100 cursor-not-allowed' : 'bg-white border-gray-200 text-gray-700 hover:border-[#00C4CC]'}`}
            />
          </div>

          {viewMode !== 'day' && (
            <span className="text-sm font-medium text-[#00C4CC] bg-cyan-50 px-3 py-1.5 rounded-md animate-in fade-in">
              {viewMode === 'week' ? '📅 Semaine Actuelle' : '📅 Mois Actuel'}
            </span>
          )}
        </div>

        {/* FILTRES */}
        <div className="flex bg-gray-100 p-1 rounded-lg">
          {['day', 'week', 'month'].map((mode) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all duration-200 ${viewMode === mode
                ? 'bg-[#00C4CC] text-white shadow-sm'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'
                }`}
            >
              {mode === 'day' ? 'Jour' : mode === 'week' ? 'Semaine' : 'Mois'}
            </button>
          ))}
        </div>
      </div>

      {/* RECHERCHE */}
      <div className="relative mb-8">
        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
        <input
          type="text"
          placeholder="Rechercher un employé par nom..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-12 pr-4 py-3 bg-white border border-gray-200 rounded-xl shadow-sm outline-none focus:ring-2 focus:ring-[#00C4CC]/30 transition"
        />
      </div>

      {/* LISTE DES ABSENCES */}
      {loading ? (
        <div className="flex justify-center items-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#00C4CC]"></div>
        </div>
      ) : sortedDepartments.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 bg-white rounded-xl border border-dashed border-gray-300">
          <UserX size={48} className="text-gray-200 mb-3" />
          <p className="text-gray-500 font-medium">Aucune absence trouvée pour cette période.</p>
        </div>
      ) : (
        <div className="space-y-8 pb-10">
          {sortedDepartments.map(deptName => (
            <div key={deptName} className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              
              {/* EN-TÊTE DÉPARTEMENT (Nettoyé: plus d'icône Building) */}
              <div className="flex items-center gap-3 mb-4 px-1 border-b border-gray-100 pb-2">
                <h3 className="text-lg font-bold text-gray-800">{deptName}</h3>
                <span className="bg-red-50 text-red-500 text-xs px-2.5 py-0.5 rounded-md font-bold">
                  {groupedData[deptName].length} Absents
                </span>
              </div>

              {/* GRILLE DES CARTES (Nettoyée: Nom en haut, Numéro en bas, Date si besoin) */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {groupedData[deptName].map(emp => (
                  <div key={emp.id} className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition flex flex-col justify-between gap-4 group">
                    
                    {/* HAUT : Nom + Date éventuelle */}
                    <div className="flex justify-between items-start">
                      <p className="font-bold text-gray-800 capitalize text-lg">{emp.nom_complet}</p>
                      
                      {/* Affichage de la date uniquement si mode Semaine ou Mois ET si la date existe */}
                      {viewMode !== 'day' && emp.date_absence && (
                        <div className="flex items-center gap-1 bg-orange-50 text-orange-600 px-2 py-1 rounded text-xs font-semibold whitespace-nowrap">
                            <CalendarDays size={12} />
                            <span>{emp.date_absence}</span>
                        </div>
                      )}
                    </div>

                    {/* BAS : Numéro de téléphone */}
                    <div className="flex items-center gap-2 text-sm text-[#00C4CC] font-medium bg-cyan-50 px-3 py-2 rounded-lg w-fit">
                      <Phone size={16} />
                      <span>{emp.numero}</span>
                    </div>

                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Absence;