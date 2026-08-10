import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";
import axios from "axios";
import React, { useState, useEffect } from "react";
import { API } from "../../utils/auth";

const ViewTimetable = () => {
  const [selectedClass, setSelectedClass] = useState("6A");
  const [selectedGrade, setSelectedGrade] = useState(6);
  const [gradeMap, setGradeMap] = useState({});
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

  const fetchTimetableDoc = async () => {
    try {
      const res = await axios.get(`${API}/api/timetable`);
      const timetableDoc = res.data?.timetable || res.data || {};

      // Build grade -> classes map from timetable keys like '6A', '7B'
      const map = {};
      Object.keys(timetableDoc).forEach((className) => {
        // extract leading digits as grade
        const match = className.match(/^(\d+)/);
        const grade = match ? Number(match[0]) : null;
        if (grade) {
          map[grade] = map[grade] || [];
          map[grade].push(className);
        }
      });

      setGradeMap(map);

      // If no selectedClass set from map, pick first available
      if (!selectedClass) {
        const firstGrade = Object.keys(map)[0];
        if (firstGrade && map[firstGrade]?.length > 0) {
          setSelectedGrade(Number(firstGrade));
          setSelectedClass(map[firstGrade][0]);
        }
      }
    } catch (err) {
      console.log(err);
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
    fetchTimetableDoc();

    if (selectedClass) {
      fetchTimetable();
    }
  }, [selectedClass]);

  // derive available grades from gradeMap or fallback to 6-11
  const availableGrades =
    Object.keys(gradeMap).length > 0
      ? Object.keys(gradeMap).map((g) => Number(g)).sort((a, b) => a - b)
      : [6, 7, 8, 9, 10, 11];

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
      time: "9:30 - 10:10",
    },
    {
      number: 5,
      time: "10:10 - 10:30 (Interval)",
    },
    {
      number: 6,
      time: "10:30 - 11:15",
    },
    {
      number: 7,
      time: "12:00 - 12:45",
    },
    {
      number: 8,
      time: "12:45 - 1:30",
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
                value={selectedGrade}
                onChange={(e) => {
                  const g = Number(e.target.value);
                  setSelectedGrade(g);
                  // pick first class in this grade if available
                  const classes = gradeMap[g] || [];
                  if (classes.length > 0) setSelectedClass(classes[0]);
                }}
                className="border px-4 py-2 rounded"
              >
                {availableGrades.map((grade) => (
                  <option key={grade} value={grade}>
                    {grade}
                  </option>
                ))}
              </select>

              {/* class selector if multiple classes per grade */}
              {gradeMap[selectedGrade] && (
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                  className="border px-4 py-2 rounded"
                >
                  {gradeMap[selectedGrade].map((cls) => (
                    <option key={cls} value={cls}>
                      {cls}
                    </option>
                  ))}
                </select>
              )}
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

                        const found = dayData?.find((item) => item.period === p.number);
                        return (
                          subjectNameById[found?.subjectId] ||
                          found?.subjectName ||
                          found?.subjectId ||
                          ""
                        );
                      };

                      return (
                        <React.Fragment key={p.number}>
                          <tr>
                            <td className="border px-4 py-3 text-center">{p.number}</td>
                            <td className="border px-4 py-3 text-center">{p.time}</td>
                            <td className="border px-4 py-3 text-center">{getSubject("Monday")}</td>
                            <td className="border px-4 py-3 text-center">{getSubject("Tuesday")}</td>
                            <td className="border px-4 py-3 text-center">{getSubject("Wednesday")}</td>
                            <td className="border px-4 py-3 text-center">{getSubject("Thursday")}</td>
                            <td className="border px-4 py-3 text-center">{getSubject("Friday")}</td>
                          </tr>

                          {/* Insert interval row visually after period 4 */}
                          {p.number === 4 && (
                            <tr>
                              <td className="border px-4 py-3 text-center">—</td>
                              <td className="border px-4 py-3 text-center font-semibold">10:10 - 10:30 (Interval)</td>
                              <td className="border px-4 py-3 text-center">Interval</td>
                              <td className="border px-4 py-3 text-center">Interval</td>
                              <td className="border px-4 py-3 text-center">Interval</td>
                              <td className="border px-4 py-3 text-center">Interval</td>
                              <td className="border px-4 py-3 text-center">Interval</td>
                            </tr>
                          )}
                        </React.Fragment>
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
