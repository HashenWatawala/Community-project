
import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";
import axios from "axios";
import { useState, useEffect } from "react";

const ViewTimetable = () => {
const [selectedGrade, setSelectedGrade] = useState("Grade 10");
const [selectedTeacher, setSelectedTeacher] = useState("");
const [currentTimetable, setCurrentTimetable] = useState(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState("");

const fetchTimetable = async () => {
  try {
    setLoading(true);
    setError("");

    let response;

    if (selectedTeacher) {
      response = await axios.get(
        `http://localhost:8000/api/timetable?teacherId=${selectedTeacher}`
      );
    } else {
      const gradeNumber = Number(
        selectedGrade.replace("Grade ", "")
      );

      response = await axios.get(
        `http://localhost:8000/api/timetable?grade=${gradeNumber}`
      );
    }

    setCurrentTimetable(response.data);
  } catch (err) {
    console.error(err);
    setError("No timetable found.");
    setCurrentTimetable(null);
  } finally {
    setLoading(false);
  }
};

useEffect(() => {
  fetchTimetable();
}, [selectedGrade, selectedTeacher]);

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

{currentTimetable?.timetable &&
  Object.entries(currentTimetable.timetable).map(
    ([className, schedule]) => (

      <React.Fragment key={className}>

        <tr>
          <td 
            colSpan="7"
            className="bg-blue-100 font-bold text-center py-3"
          >
            {className}
          </td>
        </tr>


        {Object.entries(schedule).map(
          ([day, periods]) => (

            periods.map((period, idx) => (

              <tr
                key={`${day}-${idx}`}
                className={`${
                  idx % 2 === 0
                    ? "bg-white"
                    : "bg-gray-50"
                } hover:bg-gray-100 transition`}
              >

                <td className="border border-gray-400 px-4 py-3 text-sm font-semibold text-gray-900">
                  {period.period}
                </td>


                <td className="border border-gray-400 px-4 py-3 text-sm text-gray-700">
                  {period.time}
                </td>


                <td className="border border-gray-400 px-4 py-3 text-sm text-center">
                  {day === "Monday" ? period.subject : ""}
                </td>


                <td className="border border-gray-400 px-4 py-3 text-sm text-center">
                  {day === "Tuesday" ? period.subject : ""}
                </td>


                <td className="border border-gray-400 px-4 py-3 text-sm text-center">
                  {day === "Wednesday" ? period.subject : ""}
                </td>


                <td className="border border-gray-400 px-4 py-3 text-sm text-center">
                  {day === "Thursday" ? period.subject : ""}
                </td>


                <td className="border border-gray-400 px-4 py-3 text-sm text-center">
                  {day === "Friday" ? period.subject : ""}
                </td>


              </tr>

            ))

          )
        )}

      </React.Fragment>

    )
  )}

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
