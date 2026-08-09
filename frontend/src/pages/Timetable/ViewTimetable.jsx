import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";
import axios from "axios";
import React, { useState, useEffect } from "react";
import { API } from "../../utils/auth";

const ViewTimetable = () => {
  const [selectedClass, setSelectedClass] = useState("6A");
  const [currentTimetable, setCurrentTimetable] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const subjectNameById = subjects.reduce((lookup, subject) => {
    lookup[subject.id] = subject.subjectName;
    return lookup;
  }, {});

  const fetchSubjects = async () => {
    try {
      const response = await axios.get(`${API}/api/subjects/`);
      setSubjects(response.data || []);
    } catch (err) {
      console.log(err);
      setSubjects([]);
    }
  };

  const fetchTimetable = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await axios.get(`${API}/api/timetable`, {
        params: {
          className: selectedClass,
        },
      });

      setCurrentTimetable(response.data);
    } catch (error) {
      console.log(error);

      setError("No timetable found.");
      setCurrentTimetable(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubjects();

    if (selectedClass) {
      fetchTimetable();
    }
  }, [selectedClass]);

  const grades = ["6A", "7A", "8A", "9A", "10A", "11A"];

  const periods = [
    {
      number: 1,
      time: "7:30 - 8:10",
    },
    {
      number: 2,
      time: "8:10 - 8:50",
    },
    {
      number: 3,
      time: "8:50 - 9:30",
    },
    {
      number: 4,
      time: "9:45 - 10:25",
    },
    {
      number: 5,
      time: "10:25 - 11:05",
    },
    {
      number: 6,
      time: "11:05 - 11:45",
    },
    {
      number: 7,
      time: "11:45 - 12:25",
    },
    {
      number: 8,
      time: "12:25 - 1:05",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      <header>
        <Navbar />
      </header>

      <div className="flex">
        <aside className="hidden md:block">
          <Sidebar />
        </aside>

        <main className="flex-1 p-6">
          <h3 className="text-2xl font-semibold mb-6 text-gray-800">
            View Timetable
          </h3>

          <div className="bg-white rounded-xl shadow-md p-6 mb-6">
            <div className="flex items-center gap-4">
              <label className="font-semibold">Grade</label>

              <select
                value={selectedClass}
                onChange={(e) => setSelectedClass(e.target.value)}
                className="border px-4 py-2 rounded"
              >
                {grades.map((grade) => (
                  <option key={grade} value={grade}>
                    {grade}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {loading && <p>Loading timetable...</p>}

          {error && <p className="text-red-500">{error}</p>}

          {currentTimetable && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h4 className="text-lg font-semibold text-center mb-5">
                Timetable - {selectedClass}
              </h4>

              <div className="overflow-x-auto">
                <table className="min-w-full border border-gray-400">
                  <thead>
                    <tr>
                      <th className="border px-4 py-3">Period</th>

                      <th className="border px-4 py-3">Time</th>

                      <th className="border px-4 py-3">Monday</th>

                      <th className="border px-4 py-3">Tuesday</th>

                      <th className="border px-4 py-3">Wednesday</th>

                      <th className="border px-4 py-3">Thursday</th>

                      <th className="border px-4 py-3">Friday</th>
                    </tr>
                  </thead>

                  <tbody>
                    {periods.map((p) => {
                      const getSubject = (day) => {
                        const dayData = currentTimetable?.[day];

                        const found = dayData?.find(
                          (item) => item.period === p.number,
                        );

                        return (
                          subjectNameById[found?.subjectId] ||
                          found?.subjectName ||
                          found?.subjectId ||
                          ""
                        );
                      };

                      return (
                        <tr key={p.number}>
                          <td className="border px-4 py-3 text-center">
                            {p.number}
                          </td>

                          <td className="border px-4 py-3 text-center">
                            {p.time}
                          </td>

                          <td className="border px-4 py-3 text-center">
                            {getSubject("Monday")}
                          </td>

                          <td className="border px-4 py-3 text-center">
                            {getSubject("Tuesday")}
                          </td>

                          <td className="border px-4 py-3 text-center">
                            {getSubject("Wednesday")}
                          </td>

                          <td className="border px-4 py-3 text-center">
                            {getSubject("Thursday")}
                          </td>

                          <td className="border px-4 py-3 text-center">
                            {getSubject("Friday")}
                          </td>
                        </tr>
                      );
                    })}
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
