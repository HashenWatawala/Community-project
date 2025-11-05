import React, { useState } from "react";
import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";

const ViewTimetable = () => {
  const [selectedGrade, setSelectedGrade] = useState("Grade 10");
  const [selectedTeacher, setSelectedTeacher] = useState("");

  const grades = [
    "Grade 6",
    "Grade 7",
    "Grade 8",
    "Grade 9",
    "Grade 10",
    "Grade 11",
  ];

  const teachers = [
    "A.P Gunadasa",
    "M.N.F",
    "A.S.T",
    "M.M",
    "S.V",
    "J.A.D.H",
    "M.R.P",
    "H.A.S",
  ];

  const timetableData = {
    "Grade 10": {
      name: "Grade 10",
      data: [
        {
          period: 1,
          time: "7.45 - 8.25",
          monday: "English(M.N.F)",
          tuesday: "English(M.N.F)",
          wednesday: "English(M.N.F)",
          thursday: "English(M.N.F)",
          friday: "English(M.N.F)",
        },
        {
          period: "Break",
          time: "8.25 - 8.30",
          tuesday: "Register Marking Time",
          monday: "Register Marking Time",
          wednesday: "Register Marking Time",
          thursday: "Register Marking Time",
          friday: "Register Marking Time",
          isBreak: true,
        },
        {
          period: 2,
          time: "8.30 - 9.10",
          monday: "Sinhala(M.R.P)",
          tuesday: "Science(A.S.T)",
          wednesday: "Science(A.S.T)",
          thursday: "Maths(A.P.)",
          friday: "C.T.E (S.V)",
        },
        {
          period: 3,
          time: "9.10 - 9.50",
          monday: "C.T.E (S.V)",
          tuesday: "Art/Dancing(J.A.D.H.)",
          wednesday: "Sinhala (M.R.P)",
          thursday: "Science(A.S.T)",
          friday: "Science(A.S.T)",
        },
        {
          period: 4,
          time: "9.50 - 10.50",
          monday: "C.T.E (S.V)",
          tuesday: "Art/Dancing(J.A.D.H.)",
          wednesday: "Health Science(H.A.S)",
          thursday: "Religion (M.M)",
          friday: "Science(A.S.T)",
        },
        {
          period: "Interval",
          time: "10.30 - 10.50",
          monday: "Interval",
          tuesday: "Interval",
          wednesday: "Interval",
          thursday: "Interval",
          friday: "Interval",
          isBreak: true,
        },
        {
          period: 5,
          time: "10.50 - 11.30",
          monday: "Health Science(H.A.S)",
          tuesday: "Maths(A.P.)",
          wednesday: "Sinhala (M.R.P)",
          thursday: "Health Science(H.A.S)",
          friday: "Health Science(H.A.S)",
        },
        {
          period: 6,
          time: "11.30 - 12.10",
          monday: "Dancing(J.A.D.H.)",
          tuesday: "Maths(A.P.)",
          wednesday: "Maths(A.P.)",
          thursday: "Maths(A.P.)",
          friday: "Maths(A.P.)",
        },
        {
          period: 7,
          time: "12.10 - 12.50",
          monday: "Science(A.S.T)",
          tuesday: "Religion (M.M)",
          wednesday: "History (S.V)",
          thursday: "Health Science(H.A.S)",
          friday: "Maths(A.P.)",
        },
        {
          period: 8,
          time: "12.50 - 1.30",
          monday: "Maths(A.P.)",
          tuesday: "Sinhala (M.R.P)",
          wednesday: "Maths(A.P.)",
          thursday: "Science(A.S.T)",
          friday: "Library(M.M)",
        },
      ],
    },
    "A.P Gunadasa": {
      name: "Mr. A.P Gunadasa",
      data: [
        {
          period: 1,
          time: "7.45 - 8.25",
          monday: "-",
          tuesday: "9-Maths",
          wednesday: "9-Maths",
          thursday: "9-Maths",
          friday: "9-Maths",
        },
        {
          period: "Break",
          time: "8.25 - 8.30",
          monday: "Register Making Time",
          tuesday: "Register Making Time",
          wednesday: "Register Making Time",
          thursday: "Register Making Time",
          friday: "Register Making Time",
          isBreak: true,
        },
        {
          period: 2,
          time: "8.30 - 9.10",
          monday: "11-Maths",
          tuesday: "11-Maths",
          wednesday: "7-Maths",
          thursday: "10-Maths",
          friday: "11-Maths",
        },
        {
          period: 3,
          time: "9.10 - 9.50",
          monday: "9-Maths",
          tuesday: "11-Maths",
          wednesday: "7-Maths",
          thursday: "11-Maths",
          friday: "11-Maths",
        },
        {
          period: 4,
          time: "9.50 - 10.50",
          monday: "7-Maths",
          tuesday: "-",
          wednesday: "-",
          thursday: "8-Maths",
          friday: "6-Maths",
        },
        {
          period: "Interval",
          time: "10.30 - 10.50",
          monday: "Interval",
          tuesday: "Interval",
          wednesday: "Interval",
          thursday: "Interval",
          friday: "Interval",
          isBreak: true,
        },
        {
          period: 5,
          time: "10.50 - 11.30",
          monday: "8-Maths",
          tuesday: "10-Maths",
          wednesday: "6-Maths",
          thursday: "-",
          friday: "8-Maths",
        },
        {
          period: 6,
          time: "11.30 - 12.10",
          monday: "9-Maths",
          tuesday: "10-Maths",
          wednesday: "10-Maths",
          thursday: "6-Maths",
          friday: "7-Maths",
        },
        {
          period: 7,
          time: "12.10 - 12.50",
          monday: "-",
          tuesday: "8-Maths",
          wednesday: "11-Maths",
          thursday: "7-Maths",
          friday: "10-Maths",
        },
        {
          period: 8,
          time: "12.50 - 1.30",
          monday: "10-Maths",
          tuesday: "6-Maths",
          wednesday: "10-Maths",
          thursday: "-",
          friday: "8-Maths",
        },
      ],
    },
  };

  const currentTimetable = selectedTeacher
    ? timetableData[selectedTeacher]
    : timetableData[selectedGrade];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Top navbar */}
      <header>
        <Navbar />
      </header>

      <div className="flex">
        {/* Sidebar (left) */}
        <aside className="hidden md:block">
          <Sidebar />
        </aside>

        {/* Main content */}
        <main className="flex-1 p-6">
          <h3 className="text-2xl font-semibold mb-6 text-gray-800">
            View Timetable
          </h3>

          {/* Filter Section */}
          <div className="bg-white rounded-xl shadow-md p-6 mb-6 border border-gray-200">
            <div className="flex flex-col sm:flex-row gap-6 items-start sm:items-center">
              <div className="flex items-center gap-3">
                <label
                  htmlFor="grade-select"
                  className="text-gray-700 font-semibold text-base whitespace-nowrap"
                >
                  Grade
                </label>
                <select
                  id="grade-select"
                  className="block px-4 py-2 border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm font-medium cursor-pointer hover:border-gray-400 transition"
                  value={selectedGrade}
                  onChange={(e) => {
                    setSelectedGrade(e.target.value);
                    setSelectedTeacher("");
                  }}
                >
                  {grades.map((grade) => (
                    <option key={grade} value={grade}>
                      {grade}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-3">
                <label
                  htmlFor="teacher-select"
                  className="text-gray-700 font-semibold text-base whitespace-nowrap"
                >
                  Teacher
                </label>
                <select
                  id="teacher-select"
                  className="block px-4 py-2 border-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm font-medium cursor-pointer hover:border-gray-400 transition"
                  value={selectedTeacher}
                  onChange={(e) => {
                    setSelectedTeacher(e.target.value);
                    setSelectedGrade("");
                  }}
                >
                  <option value="">Select Teacher</option>
                  {teachers.map((teacher) => (
                    <option key={teacher} value={teacher}>
                      {teacher}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Timetable Section */}
          {currentTimetable && (
            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
              <h4 className="text-lg font-semibold mb-6 text-gray-800 text-center">
                Time Table -2024
                <br />
                {currentTimetable.name}
              </h4>

              <div className="overflow-x-auto">
                <table className="min-w-full border-collapse border border-gray-400">
                  <thead>
                    <tr className="bg-white border-b-2 border-gray-400">
                      <th className="border border-gray-400 px-4 py-3 text-left text-sm font-bold text-gray-900">
                        No. of Period
                      </th>
                      <th className="border border-gray-400 px-4 py-3 text-left text-sm font-bold text-gray-900">
                        Time
                      </th>
                      <th className="border border-gray-400 px-4 py-3 text-center text-sm font-bold text-gray-900">
                        Monday
                      </th>
                      <th className="border border-gray-400 px-4 py-3 text-center text-sm font-bold text-gray-900">
                        Tuesday
                      </th>
                      <th className="border border-gray-400 px-4 py-3 text-center text-sm font-bold text-gray-900">
                        Wednesday
                      </th>
                      <th className="border border-gray-400 px-4 py-3 text-center text-sm font-bold text-gray-900">
                        Thursday
                      </th>
                      <th className="border border-gray-400 px-4 py-3 text-center text-sm font-bold text-gray-900">
                        Friday
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentTimetable.data.map((row, idx) => (
                      <tr
                        key={idx}
                        className={`${
                          row.isBreak
                            ? "bg-gray-100"
                            : idx % 2 === 0
                            ? "bg-white"
                            : "bg-gray-50"
                        } hover:bg-gray-100 transition`}
                      >
                        <td className="border border-gray-400 px-4 py-3 text-sm font-semibold text-gray-900">
                          {row.period}
                        </td>
                        <td className="border border-gray-400 px-4 py-3 text-sm text-gray-700">
                          {row.time}
                        </td>
                        <td className="border border-gray-400 px-4 py-3 text-sm text-gray-700 text-center">
                          {row.monday}
                        </td>
                        <td className="border border-gray-400 px-4 py-3 text-sm text-gray-700 text-center">
                          {row.tuesday}
                        </td>
                        <td className="border border-gray-400 px-4 py-3 text-sm text-gray-700 text-center">
                          {row.wednesday}
                        </td>
                        <td className="border border-gray-400 px-4 py-3 text-sm text-gray-700 text-center">
                          {row.thursday}
                        </td>
                        <td className="border border-gray-400 px-4 py-3 text-sm text-gray-700 text-center">
                          {row.friday}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default ViewTimetable;
