import React from "react";
import { LogOut, UserRound } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { logoutUser } from "../utils/auth";

function Navbar() {
  const navigate = useNavigate();

  // Function to handle logout
  const handleLogout = () => {
    logoutUser();
    navigate("/login", { replace: true });
  };

  return (
    <div className="w-full h-[100px] bg-white border-b border-gray-300 flex items-center justify-between pl-12 pr-16">
      {/* Header content */}
      {/* Left side - Admin info */}
      <div className="flex items-center gap-4 py-[21px]">
        <div className="w-[50px] h-[50px] bg-white rounded-full border-2 border-gray-800 flex items-center justify-center">
          <UserRound className="w-7 h-7 text-gray-800" />
        </div>
        <div className="leading-none">
          <h2 className="text-lg font-bold text-gray-800 my-0">ADMIN NAME</h2>
          <p className="text-lg text-gray-500 italic">role</p>
        </div>
      </div>

      {/* Right side - Logout */}
      <button
        type="button"
        onClick={handleLogout}
        className="flex items-center gap-2 text-gray-800 hover:text-blue-900 transition-colors cursor-pointer"
      >
        <span className="text-xl font-medium">Log out</span>
        <LogOut className="w-5 h-5" />
      </button>
    </div>
  );
}
export default Navbar;
