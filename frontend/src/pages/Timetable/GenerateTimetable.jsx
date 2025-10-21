import React, { useState } from "react";
import Navbar from "../../components/Navbar";
import Sidebar from "../../components/Sidebar";

const GenerateTimetable = () => {
  const [selectedGrades, setSelectedGrades] = useState([]);
  const [isGenerated, setIsGenerated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const grades = [
    "Grade 6",
    "Grade 7",
    "Grade 8",
    "Grade 9",
    "Grade 10",
    "Grade 11",
    "All Teachers Timetable",
  ];

  const handleCheckboxChange = (grade) => {
    setSelectedGrades((prev) =>
      prev.includes(grade) ? prev.filter((g) => g !== grade) : [...prev, grade]
    );
  };

  const handleSelectAll = () => {
    if (selectedGrades.length === grades.length) {
      setSelectedGrades([]);
    } else {
      setSelectedGrades([...grades]);
    }
  };

  const handleGenerate = async () => {
    if (selectedGrades.length === 0) {
      alert("Please select at least one class.");
      return;
    }


    try {
      setIsLoading(true);
      // await axios.post("/api/generate-timetable", { selectedGrades });
      // simulate network
      await new Promise((res) => setTimeout(res, 800));
      setIsGenerated(true);
    } catch (err) {
      console.error(err);
      alert("Failed to generate timetable.");
    } finally {
      setIsLoading(false);
    }
  };

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
            Generate Timetable
          </h3>

          <div className="flex flex-col lg:flex-row gap-6">
            {/* Selection card (narrow left) */}
            <div className="bg-white rounded-xl shadow-md w-full lg:w-80 p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h5 className="text-2xl text-blue-900 font-semibold mb-1 text-center">Select Classes</h5>
                  <p className="text-sm text-gray-500">
                    Choose which classes to include in the timetable
                  </p>
                </div>

                {/* optional select all */}
              </div>

              <div className="mt-4 space-y-3">
                {grades.map((grade, idx) => (
                  <label
                    key={idx}
                    className="flex items-center justify-between gap-4 cursor-pointer select-none"
                  >
                    {/* grade text (left) */}
                    <span className="text-gray-700">{grade}</span>

                    {/* checkbox (right) */}
                    <input
                      type="checkbox"
                      value={grade}
                      checked={selectedGrades.includes(grade)}
                      onChange={() => handleCheckboxChange(grade)}
                      className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                  </label>
                ))}
              </div>

              <button
                onClick={handleGenerate}
                className={`mt-6 w-full py-2 rounded-lg text-white font-semibold transition ${
                  isLoading ? "bg-blue-500 cursor-wait" : "bg-blue-950 hover:bg-blue-800"
                }`}
                disabled={isLoading}
              >
                {isLoading ? "Generating..." : "Generate Timetable"}
              </button>
            </div>

            {/* Timetable display (right, larger) */}
            <div className="flex-1 bg-white rounded-xl shadow-md p-10 flex items-center justify-center min-h-[240px]">
              {isGenerated ? (
                <div className="text-center">
                  <div className="text-blue-600 mb-3">
                    <i className="fa-solid fa-calendar-check text-5xl" />
                  </div>
                  <h4 className="text-xl font-semibold text-gray-800">Timetable Generated</h4>
                  <p className="text-gray-500 mt-2">New timetable has been generated successfully!</p>

                  {/* preview / download / view buttons placeholders */}
                  <div className="mt-5 flex justify-center gap-3">
                    <button className="px-4 py-2 bg-white border rounded-md text-sm">View</button>
                    <button className="px-4 py-2 bg-blue-700 text-white rounded-md text-sm">Download</button>
                  </div>
                </div>
              ) : (
                <div className="text-center">
                  <div className="text-blue-600 mb-3">
                    <i className="fa-solid fa-calendar-plus text-5xl" />
                  </div>
                  <h4 className="text-xl font-semibold text-gray-800">Empty</h4>
                  <p className="text-gray-500 mt-2">Generate New Timetable</p>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default GenerateTimetable;
