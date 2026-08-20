import React, { useState, useEffect } from "react";
import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";
import { fetchTeachersCount, fetchClassesCount } from "../../utils/dashboard";

const Dashboard = () => {
  const [teachersCount, setTeachersCount] = useState(0);
  const [classesCount, setClassesCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCounts = async () => {
      setLoading(true);
      const teachersData = await fetchTeachersCount();
      const classesData = await fetchClassesCount();

      // Animate teachers count
      const teachersIncrement = teachersData / 50;
      let teachersCurrent = 0;

      const teachersInterval = setInterval(() => {
        teachersCurrent += teachersIncrement;
        if (teachersCurrent >= teachersData) {
          setTeachersCount(teachersData);
          clearInterval(teachersInterval);
        } else {
          setTeachersCount(Math.floor(teachersCurrent));
        }
      }, 30);

      // Animate classes count
      const classesIncrement = classesData / 50;
      let classesCurrent = 0;

      const classesInterval = setInterval(() => {
        classesCurrent += classesIncrement;
        if (classesCurrent >= classesData) {
          setClassesCount(classesData);
          clearInterval(classesInterval);
          setLoading(false);
        } else {
          setClassesCount(Math.floor(classesCurrent));
        }
      }, 30);

      return () => {
        clearInterval(teachersInterval);
        clearInterval(classesInterval);
      };
    };

    fetchCounts();
  }, []);

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-8 bg-gray-100 min-h-screen">
          {/* Header */}
          <div className="flex justify-end mb-8">
            <button
              className="bg-blue-950 hover:bg-blue-900 text-white rounded-md text-md font-medium transition-colors"
              style={{ width: '282px', height: '65px' }}
            >
              Generate time table
            </button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 gap-8 max-w-4xl">
            {/* Teachers Card */}
            <div className="bg-white rounded-lg shadow p-10">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-700 text-base mb-4">
                    Total Registered Teachers
                  </p>
                  <p className="text-6xl font-bold text-gray-900">
                    {loading ? "-" : teachersCount}
                  </p>
                </div>
                <div className="text-7xl">
                  👩‍🏫
                </div>
              </div>
            </div>

            {/* Grades Card */}
            <div className="bg-white rounded-lg shadow p-10">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-700 text-base mb-4">
                    Total Registered Classes
                  </p>
                  <p className="text-6xl font-bold text-gray-900">
                    {loading ? "-" : classesCount}
                  </p>
                </div>
                <div className="text-7xl">
                  👥
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;