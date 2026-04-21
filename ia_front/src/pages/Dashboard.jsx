import { useState, useEffect } from 'react';
import axios from 'axios';
import { UserX, Phone, Building } from 'lucide-react';
import { API_BASE_URL } from '../config';

const ABSENTS_URL = API_BASE_URL + "/presence/absents"; // nouvel endpoint unifié
const DEPT_URL = API_BASE_URL + "/departements";

const Dashboard = () => {
    const prenomAdmin = localStorage.getItem("adminPrenom") || "";
    const nomAdmin = localStorage.getItem("adminNom") || "";

    const dateDuJour = new Intl.DateTimeFormat('fr-FR', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    }).format(new Date());

    const [stats, setStats] = useState({ absents: [] });
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            setLoading(false);
            return;
        }

        try {
            const config = { headers: { 'Authorization': `Bearer ${token}` } };
            
            // 🔹 Date du jour au format YYYY-MM-DD
            const todayStr = new Date().toISOString().split('T')[0];

            // 🔹 Requête vers le nouvel endpoint unifié
            const [absentsRes, deptRes] = await Promise.all([
                axios.get(`${ABSENTS_URL}?mode=day&target_date=${todayStr}`, config),
                axios.get(DEPT_URL, config)
            ]);

            const deptMap = new Map(deptRes.data.map(d => [d.id, d.nom]));

            const mappedAbsents = absentsRes.data.map(emp => ({
                id: emp.id,
                nom_complet: emp.nom_complet,
                numero: emp.numero,
                dept: deptMap.get(emp.departement_id) || "Non assigné",
            }));

            setStats({ absents: mappedAbsents });

        } catch (error) {
            console.error("Erreur API Dashboard:", error);
            setStats({ absents: [] });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const Loader = () => (
        <div role="status" className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#00C4CC]"></div>
        </div>
    );

    const AbsentCard = ({ emp }) => (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition gap-4">
            <div className="flex flex-col gap-1">
                <h4 className="text-lg font-bold text-gray-800 capitalize">{emp.nom_complet}</h4>
                <div className="flex items-center gap-1.5 text-sm text-gray-500">
                    <Building size={14} />
                    <span>{emp.dept}</span>
                </div>
            </div>
            <div className="flex items-center gap-2 text-sm font-medium text-[#00C4CC] bg-cyan-50 px-3 py-2 rounded-lg w-fit">
                <Phone size={16} />
                <span>{emp.numero}</span>
            </div>
        </div>
    );

    return (
        <div className="font-sans p-6">
            <div className="mb-10">
                <h2 className="text-4xl font-light text-gray-800">
                    Bonjour,{" "}
                    <span className="font-medium text-[#00C4CC]">{prenomAdmin} {nomAdmin}</span>
                </h2>
                <p className="text-gray-500 mt-1 first-letter:capitalize">{dateDuJour}</p>
            </div>

            <div className="flex justify-center">
                <div className="bg-white rounded-xl shadow-lg border border-gray-100 w-full max-w-4xl">
                    <div className="p-6 border-b border-[#00C4CC]/20 flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-cyan-50 rounded-lg">
                                <UserX className="text-[#00C4CC]" size={24} />
                            </div>
                            <h3 className="text-xl font-medium text-gray-700">Employés Absents</h3>
                        </div>
                        <span className="bg-[#00C4CC] text-white px-3 py-1 rounded-full text-sm font-bold shadow-sm">
                            {stats.absents.length}
                        </span>
                    </div>

                    <div className="p-6 flex flex-col gap-3">
                        {loading ? (
                            <Loader />
                        ) : stats.absents.length === 0 ? (
                            <div className="text-center py-8 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                                <p className="text-gray-500 font-medium">Tout le monde est présent aujourd'hui ! 🎉</p>
                            </div>
                        ) : (
                            stats.absents.map(emp => <AbsentCard key={emp.id} emp={emp} />)
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
