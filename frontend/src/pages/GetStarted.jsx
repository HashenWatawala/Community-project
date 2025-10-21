import React from "react";
import { useNavigate } from "react-router-dom";

const GetStarted = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate("/login");
  };

  return (
    <div className="h-screen w-full flex items-center justify-center bg-gradient-to-b from-gray-100 via-gray-200 to-[var(--color-primary)]">
      <div className="max-w-4xl mx-auto px-6 text-center">
        {/* Main Heading */}
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-[var(--color-primary)] mb-6 leading-tight">
          EFFORTLESS TIMETABLE
          <br />
          MANAGEMENT SYSTEM
        </h1>

        {/* Tagline */}
        <p className="text-base md:text-lg text-gray-700 mb-10 max-w-4xl mx-auto leading-relaxed font-semibold">
          "Automate scheduling, reduce conflicts, and save time with our easy-to-use system designed for government schools"
        </p>

        {/* CTA Button */}
        <button
          onClick={handleGetStarted}
          className="bg-[var(--color-primary)] text-white px-12 py-4 rounded-md text-lg font-semibold hover:opacity-90 transition-opacity shadow-lg"
        >
          Get Started
        </button>
      </div>
    </div>
  );
};

export default GetStarted;
