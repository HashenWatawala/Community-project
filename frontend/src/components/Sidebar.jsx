import React from "react";
import { NavLink } from "react-router-dom";
import { FaClipboardList } from "react-icons/fa";

const Sidebar = () => {
  const menuItems = [
    { name: "Dashboard", path: "/dashboard" },
    { name: "Teacher Management", path: "/teacher-management" },
    { name: "Subject Management", path: "/subject-management" },
    { name: "Generate Timetable", path: "/generate-timetable" },
    { name: "View Timetable", path: "/view-timetable" },
  ];

  return (
    <div className="w-64 md:w-72 lg:w-80 h-screen sticky top-0 bg-[#0b2948] text-white flex flex-col px-6 py-10 flex-shrink-0 overflow-y-auto">
      {/* Logo */}
      <div className="flex items-center gap-3 mb-16">
        <FaClipboardList size={36} />
        <h1 className="text-xl font-bold tracking-wide">CLASS PLANNER</h1>
      </div>

      {/* Menu */}
      <nav className="flex flex-col gap-4 w-full">
        {menuItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `block px-6 py-3 rounded-xl text-lg text-left font-medium transition-all duration-200 ${
                isActive
                  ? "bg-[#324b68] text-white"
                  : "text-gray-200 hover:bg-[#1e3b5c]"
              }`
            }
          >
            {item.name}
          </NavLink>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;
