const Sidebar = ({ activePage, setActivePage }) => {
  // حيدنا icons من هنا
  const menuItems = [
    { name: 'Dashboard' },
    { name: 'Gestion des Employés' },
    { name: 'Gestion des Caméras' },
    { name: 'Gestion des Absences' },
    { name: 'Ajouter Département' },
  ];

  return (
    <div className="w-80 bg-white border-r border-gray-200 h-screen p-5 flex flex-col fixed left-0 top-0">
      
      <div className="mb-10 mt-4 px-2">
        <h1 className="text-2xl font-semibold text-[#00C4CC] whitespace-nowrap">
          Admin Dashboard
        </h1>
      </div>

      <div className="flex flex-col gap-2">
        {menuItems.map((item) => (
          <button
            key={item.name}
            onClick={() => setActivePage(item.name)}
            className={`flex items-center p-4 rounded-lg transition-all duration-200 text-left text-base ${
              activePage === item.name
                // الستايل الجديد: خلفية خفيفة + خط فاليمن + لون سماوي
                ? 'bg-[#00C4CC]/10 text-[#00C4CC] font-bold border-r-4 border-[#00C4CC]' 
                : 'text-gray-500 hover:bg-cyan-50 hover:text-[#00C4CC] font-normal'
            }`}
          >
            {/* حيدنا span ديال الأيقونة */}
            {item.name}
          </button>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;