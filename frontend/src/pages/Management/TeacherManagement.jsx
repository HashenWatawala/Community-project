import React, { useState } from "react";
import { Search, Plus, Edit2, Trash2, X } from "lucide-react";
import Button from "../../components/Button";
import Navbar from "../../components/Navbar";
import Sidebar from "../../components/Sidebar";

const TeacherManagement = () => {
  const [teachers, setTeachers] = useState([
   
  ]);

  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [editingTeacher, setEditingTeacher] = useState(null);
  const [formData, setFormData] = useState({
    nameWithInitial: "",
    nicNo: "",
    contactNumber: "",
    email: "",
    hasAssignClass: "no",
    subjects: [
      { name: "", grades: [] },
    ],
  });

  const availableGrades = [
    "6",
    "7",
    "8",
    "9",
    "10",
    "11"
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleRadioChange = (value) => {
    setFormData((prev) => ({ ...prev, hasAssignClass: value }));
  };

 const toggleGrade = (subjectIndex, grade) => {
  setFormData(prev => {
    const updatedSubjects = [...prev.subjects];
    const gradeList = updatedSubjects[subjectIndex].grades;

    if (gradeList.includes(grade)) {
      updatedSubjects[subjectIndex].grades = gradeList.filter(g => g !== grade);
    } else {
      updatedSubjects[subjectIndex].grades = [...gradeList, grade];
    }

    return { ...prev, subjects: updatedSubjects };
  });
};

  const removeGrade = (subjectIndex, grade) => {
  setFormData(prev => {
    const updatedSubjects = [...prev.subjects];
    updatedSubjects[subjectIndex].grades = updatedSubjects[subjectIndex].grades.filter(
      g => g !== grade
    );
    return { ...prev, subjects: updatedSubjects };
  });
};


  const handleAddTeacher = () => {
    setEditingTeacher(null);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingTeacher(null);
    setFormData({
      nameWithInitial: "",
      nicNo: "",
      contactNumber: "",
      email: "",
      hasAssignClass: "no",
      subjects: [
      {name:"", grades:[]}
      ],
    
    });
  };

  const handleSaveTeacher = () => {
    const assignedSubjects = formData.subjects.filter(
      (s) => s.name && s.grades.length > 0
    );

    if (editingTeacher) {
      // existing teacher
      const updatedTeachers = teachers.map((t) =>
        t.id === editingTeacher.id
          ? {
              ...t,
              name: formData.nameWithInitial || "Unnamed Teacher",
              subjects: assignedSubjects.map((s) => ({
                name: s.name,
                grades: s.grades,
              })),
            }
          : t
      );
      setTeachers(updatedTeachers);
    } else {
      // ADD new teacher
      const newTeacher = {
        id: teachers.length + 1,
        name: formData.nameWithInitial || "Unnamed Teacher",
        subjects:
          assignedSubjects.length > 0
            ? assignedSubjects.map((s) => ({
                name: s.name,
                grades: s.grades,
              }))
            : [],
      };
      setTeachers([...teachers, newTeacher]);
    }

    handleCloseModal();
  };

  const handleEditTeacher = (teacher) => {
    setEditingTeacher(teacher);
    setShowModal(true);

    setFormData({
      nameWithInitial: teacher.name,
      nicNo: "",
      contactNumber: "",
      email: "",
      hasAssignClass: "no",
      subjects: teacher.subjects.length > 0 
      ? teacher.subjects.map(s => ({ name: s.name, grades: s.grades }))
      : [{ name: "", grades: [] }]
  });
};
  

  const handleDeleteTeacher = (id) => {
    if (window.confirm("Are you sure you want to delete this teacher?")) {
      setTeachers((prev) => prev.filter((t) => t.id !== id));
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />

        <div className="flex-1 p-6 overflow-auto">
          <div className="mb-6 flex items-center justify-between">
            <h3 className="text-2xl font-semibold mb-6 text-gray-800">Teacher Details</h3>
            <div className="flex gap-4">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-3 pr-10 py-2 border border-gray-300 rounded-md w-64"
                />
                <Search className="absolute right-3 top-2.5 w-5 h-5 text-gray-400" />
              </div>
              <Button
                onClick={handleAddTeacher}
                className="bg-slate-800 text-white px-4 py-2 rounded-md flex items-center gap-2 hover:bg-slate-700"
              >
                <Plus className="w-4 h-4" />
                Add New Teacher
              </Button>
            </div>
          </div>

          {/* Add/Edit Modal */}
        {showModal && (
  <div className="fixed inset-0 left-80 z-50 flex items-start justify-center overflow-auto bg-black/30 p-6">
    <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-4xl mx-6 mt-18">
      <h2 className="text-2xl font-bold text-slate-900 mb-6">
        {editingTeacher ? "Edit Teacher" : "Add New Teacher"}
      </h2>
  
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <input
                  type="text"
                  name="nameWithInitial"
                  placeholder="Name with initial"
                  value={formData.nameWithInitial}
                  onChange={handleInputChange}
                  className="border border-gray-300 rounded px-3 py-2"
                />
                <input
                  type="text"
                  name="nicNo"
                  placeholder="NIC no"
                  value={formData.nicNo}
                  onChange={handleInputChange}
                  className="border border-gray-300 rounded px-3 py-2"
                />
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <input
                  type="text"
                  name="contactNumber"
                  placeholder="Contact Number"
                  value={formData.contactNumber}
                  onChange={handleInputChange}
                  className="border border-gray-300 rounded px-3 py-2"
                />
                <input
                  type="email"
                  name="email"
                  placeholder="E-mail"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="border border-gray-300 rounded px-3 py-2"
                />
              </div>

           {/* Assign Class */}
<div className="mb-6">
  <label className="block mb-2">Have an Assigned Class?</label>
  <div className="flex gap-4">
    <label className="flex items-center gap-2">
      <input
        type="radio"
        name="hasAssignClass"
        checked={formData.hasAssignClass === "yes"}
        onChange={() => handleRadioChange("yes")}
        style={{ accentColor: '#1e293b' }}
        className="cursor-pointer"
      />
      Yes
    </label>

    <label className="flex items-center gap-2">
      <input
        type="radio"
        name="hasAssignClass"
        checked={formData.hasAssignClass === "no"}
        onChange={() => handleRadioChange("no")}
        style={{ accentColor: '#1e293b' }}
        className="cursor-pointer"
      />
      No
    </label>
  </div>
</div>
              {/* Subject Details */}
{/* Subject Details */}
<div>
  <h2 className="text-lg font-semibold text-slate-800 mb-4">
    Subject Details
  </h2>
  <div className="grid grid-cols-2 gap-4 mb-3 text-sm font-medium text-slate-700 tracking-wide">
    <div className="text-slate-900"> Subject Name</div>
    <div className="text-slate-900">Assign Grade</div>
  </div>

  {formData.subjects.map((subject, subjectIndex) => (
    <div key={subjectIndex}>
      <div className="grid grid-cols-2 gap-4 py-4 items-start">
        <div className="relative">
          {/* Dropdown to select subject */}
          <select
            className="border border-gray-300 rounded px-3 py-2 pr-8 w-full cursor-pointer appearance-none bg-white"
            value={subject.name || ""}
            onChange={(e) => {
              const selectedSubject = e.target.value;
              setFormData(prev => {
                const updatedSubjects = [...prev.subjects];
                updatedSubjects[subjectIndex].name = selectedSubject;
                return { ...prev, subjects: updatedSubjects };
              });
            }}
          >
            <option value="" disabled hidden>
              Select Subject
            </option>
            {["Sinhala", "Maths", "Science", "English", "P.T.S", "Religion","History","Geography","C.T.E","Health Science","Dancing","Art","Tamil","ICT","Home Science","Library"].map((subj) => (
              <option key={subj} value={subj}>
                {subj}
              </option>
            ))}
          </select>
        </div>

        <div className="relative">
          {/* Selected Grades as Chips */}
          <div className="flex flex-wrap gap-2 mb-2 min-h-[32px] bg-gray-50 p-2 rounded">
            {subject.grades.length > 0 ? (
              subject.grades.map((grade) => (
                <span
                  key={grade}
                  className="bg-slate-800 hover:bg-slate-700 text-white px-3 py-1 rounded-full text-sm flex items-center gap-2 shadow-md transition"
                >
                  Grade {grade}
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      // Remove grade
                      setFormData(prev => {
                        const updatedSubjects = prev.subjects.map((subj, idx) => {
                          if (idx === subjectIndex) {
                            return {
                              ...subj,
                              grades: subj.grades.filter(g => g !== grade)
                            };
                          }
                          return subj;
                        });
                        return { ...prev, subjects: updatedSubjects };
                      });
                    }}
                    className="hover:bg-slate-800 rounded-full p-0.5 flex items-center justify-center transition"
                    type="button"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))
            ) : (
              <span className="text-gray-400 text-sm">No grades selected</span>
            )}
          </div>

          {/* Dropdown to add grades */}
          <select
            className="border border-gray-300 rounded px-3 py-2 pr-8 w-full cursor-pointer appearance-none bg-white"
            defaultValue=""
            onChange={(e) => {
              const selectedGrade = e.target.value;
              if (!selectedGrade) return;

              setFormData(prev => {
                const updatedSubjects = prev.subjects.map((subj, idx) => {
                  if (idx === subjectIndex) {
                    const grades = subj.grades.includes(selectedGrade)
                      ? subj.grades
                      : [...subj.grades, selectedGrade];
                    return { ...subj, grades };
                  }
                  return subj;
                });
                return { ...prev, subjects: updatedSubjects };
              });

              e.target.value = ""; // reset dropdown
            }}
          >
            <option value="" disabled hidden>
              Select Grade
            </option>
            {availableGrades.map((grade) => (
              <option key={grade} value={grade}>
                Grade {grade}
              </option>
            ))}
          </select>
        </div>
      </div>

      {subjectIndex < formData.subjects.length - 1 && (
        <div className="border-b border-gray-200"></div>
      )}
    </div>
  ))}
</div>
{/* Add Another Subject Button */}
<button
  type="button"
  onClick={() => {
    setFormData(prev => ({
      ...prev,
      subjects: [...prev.subjects, { name: "", grades: [] }]
    }));
  }}
  className="
    mt-4 w-full
    bg-slate-800 text-white
    font-medium
    px-6 py-3 rounded-lg
    shadow-sm hover:shadow-md
    hover:bg-slate-500
    transition-colors duration-200
    flex items-center justify-center gap-2 "
>
  <Plus className="w-5 h-5" />
  Add Another Subject
</button>

              <div className="flex justify-end gap-3 mt-6">
                <Button
                  onClick={handleCloseModal}
                  variant="outline"
                  size="md"
                  className="!bg-white !text-black !border-gray-300 hover:!bg-slate-800 hover:!text-white hover:!border-slate-800"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleSaveTeacher}
                  size="md"
                  className="!bg-slate-800 !text-white hover:!bg-slate-700"
                >
                  {editingTeacher ? "Update" : "Save"}
                </Button>
              </div>
            </div>
            </div>
          
          )}

          {/* Teachers Table */}
          {!showModal && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4">Teacher Name</th>
                      <th className="text-left py-3 px-4">
                        Assigned Grades & Subjects
                      </th>
                      <th className="text-left py-3 px-4">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {teachers.map((teacher) => (
                      <tr key={teacher.id} className="border-b">
                        <td className="py-4 px-4">{teacher.name}</td>
                        <td className="py-4 px-4">
                          {teacher.subjects.map((subject, idx) => (
                            <div key={idx} className="flex flex-wrap gap-2 mb-2">
                              {subject.grades.length>0? (
                              subject.grades.map((grade) => (
                                <span
                                  key={grade}
                                  className="bg-slate-800 text-white px-3 py-1 rounded text-sm"
                                >
                                  {grade}-{subject.name}
                                </span>
                              ))
                            ):(
                              <span className="text-gray-400 text-sm">No grades assigned</span>
                            )}
                              </div>
                          ))}
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex gap-2">
                            <button
                              className="p-2 hover:bg-gray-100 rounded"
                              onClick={() => handleEditTeacher(teacher)}
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              className="p-2 hover:bg-gray-100 rounded"
                              onClick={() => handleDeleteTeacher(teacher.id)}
                            >
                              <Trash2 className="w-4 h-4 text-red-500" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeacherManagement;