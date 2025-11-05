import React, { useState } from "react";
import { Search, X, Plus, Edit2, Trash2 } from "lucide-react";
import Button from "../../components/Button.jsx";
import Sidebar from "../../components/Sidebar.jsx";
import Navbar from "../../components/Navbar.jsx";

// OVERLAY MODAL COMPONENT
const Modal = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      ></div>
      <div className="relative bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {children}
      </div>
    </div>
  );
};

// ADD/EDIT SUBJECT FORM COMPONENT
const SubjectForm = ({ onClose, onSave, editData = null, teachers, grade }) => {
  const [formData, setFormData] = useState({
    subjectName: editData?.subjectName || "",
    periodsPerWeek: editData?.periodsPerWeek || "",
    assignedTeacher: editData?.assignedTeacher || "",
  });

  const handleSubmit = () => {
    if (
      formData.subjectName &&
      formData.periodsPerWeek &&
      formData.assignedTeacher
    ) {
      onSave({ ...formData, grade });
      onClose();
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">
          {editData ? "Edit Subject" : "Add New Subject"}
        </h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X size={24} />
        </button>
      </div>

      <div>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <input
              type="text"
              placeholder="Subject Name"
              value={formData.subjectName}
              onChange={(e) =>
                setFormData({ ...formData, subjectName: e.target.value })
              }
              className="w-full px-4 py-2.5 border border-gray-300 rounded focus:outline-none focus:border-[#1e3a5f] bg-gray-50"
            />
          </div>
          <div>
            <input
              type="number"
              placeholder="Number of period per week"
              value={formData.periodsPerWeek}
              onChange={(e) =>
                setFormData({ ...formData, periodsPerWeek: e.target.value })
              }
              className="w-full px-4 py-2.5 border border-gray-300 rounded focus:outline-none focus:border-[#1e3a5f] bg-gray-50"
              min="1"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <input
              type="text"
              placeholder="Assign Teacher"
              value={formData.assignedTeacher}
              onChange={(e) =>
                setFormData({ ...formData, assignedTeacher: e.target.value })
              }
              className="w-full px-4 py-2.5 border border-gray-300 rounded focus:outline-none focus:border-[#1e3a5f] bg-gray-50"
            />
          </div>
        </div>

        <div className="flex gap-4">
          <Button onClick={handleSubmit} variant="primary">
            {editData ? "Update Subject" : "Add Subject"}
          </Button>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
        </div>
      </div>
    </div>
  );
};

// SUBJECT TABLE COMPONENT
const SubjectTable = ({ grade, subjects, onEdit, onDelete, onAdd }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-2xl font-semibold">Grade {grade}</h3>
        <Button
          onClick={() => onAdd(grade)}
          variant="primary"
          className="flex items-center gap-2 bg-[#1e3a5f] text-white px-4 py-2 rounded hover:bg-[#2a4a6d]"
        >
          <Plus size={20} />
          Add New Subject
        </Button>
      </div>

      <table className="w-full">
        <thead>
          <tr className="border-b-2 border-gray-200">
            <th className="text-left py-3 px-4 font-semibold text-gray-600">
              Subject Name
            </th>
            <th className="text-left py-3 px-4 font-semibold text-gray-600">
              Number of period per week
            </th>
            <th className="text-left py-3 px-4 font-semibold text-gray-600">
              Assigned Teacher
            </th>
            <th className="text-left py-3 px-4 font-semibold text-gray-600">
              Action
            </th>
          </tr>
        </thead>
        <tbody>
          {subjects.length === 0 ? (
            <tr>
              <td colSpan="4" className="text-center py-8 text-gray-400">
                No subjects added yet
              </td>
            </tr>
          ) : (
            subjects.map((subject) => (
              <tr
                key={subject.id}
                className="border-b border-gray-100 hover:bg-gray-50"
              >
                <td className="py-4 px-4">{subject.subjectName}</td>
                <td className="py-4 px-4">{subject.periodsPerWeek}</td>
                <td className="py-4 px-4">{subject.assignedTeacher}</td>
                <td className="py-4 px-4">
                  <div className="flex gap-3">
                    <button
                      onClick={() => onEdit(subject)}
                      className="text-gray-600 hover:text-[#1e3a5f]"
                    >
                      <Edit2 size={18} />
                    </button>
                    <button
                      onClick={() => onDelete(subject.id)}
                      className="text-gray-600 hover:text-red-600"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

// MAIN SUBJECT MANAGEMENT COMPONENT
const SubjectManagement = () => {
  const [subjects, setSubjects] = useState([
    {
      id: 1,
      grade: 6,
      subjectName: "History",
      periodsPerWeek: 6,
      assignedTeacher: "Mr.ABC Perera",
    },
    {
      id: 2,
      grade: 6,
      subjectName: "English",
      periodsPerWeek: 6,
      assignedTeacher: "Mr.ABC Silva",
    },
    {
      id: 3,
      grade: 7,
      subjectName: "History",
      periodsPerWeek: 6,
      assignedTeacher: "Mr.ABC Perera",
    },
    {
      id: 4,
      grade: 7,
      subjectName: "English",
      periodsPerWeek: 6,
      assignedTeacher: "Mr.ABC Silva",
    },
    {
      id: 5,
      grade: 8,
      subjectName: "Mathematics",
      periodsPerWeek: 7,
      assignedTeacher: "Ms.XYZ Fernando",
    },
    {
      id: 6,
      grade: 9,
      subjectName: "Science",
      periodsPerWeek: 6,
      assignedTeacher: "Dr.John Doe",
    },
    {
      id: 7,
      grade: 10,
      subjectName: "Chemistry",
      periodsPerWeek: 5,
      assignedTeacher: "Mr.ABC Perera",
    },
    {
      id: 8,
      grade: 11,
      subjectName: "Physics",
      periodsPerWeek: 6,
      assignedTeacher: "Mr.ABC Silva",
    },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSubject, setEditingSubject] = useState(null);
  const [selectedGrade, setSelectedGrade] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Mock teachers list - replace with your actual teachers data
  const teachers = [
    "Mr.ABC Perera",
    "Mr.ABC Silva",
    "Ms.XYZ Fernando",
    "Dr.John Doe",
  ];

  // Get unique grades from subjects
  const grades = [...new Set(subjects.map((s) => s.grade))].sort(
    (a, b) => a - b
  );

  // Filter grades based on search
  const filteredGrades = searchQuery
    ? grades.filter((grade) => grade.toString().includes(searchQuery))
    : grades;

  const handleAddSubject = (grade) => {
    setSelectedGrade(grade);
    setEditingSubject(null);
    setIsModalOpen(true);
  };

  const handleEditSubject = (subject) => {
    setEditingSubject(subject);
    setSelectedGrade(subject.grade);
    setIsModalOpen(true);
  };

  const handleSaveSubject = (formData) => {
    if (editingSubject) {
      // Update existing subject
      setSubjects(
        subjects.map((s) =>
          s.id === editingSubject.id ? { ...s, ...formData } : s
        )
      );
    } else {
      // Add new subject
      const newSubject = {
        id: Date.now(),
        ...formData,
      };
      setSubjects([...subjects, newSubject]);
    }
  };

  const handleDeleteSubject = (id) => {
    if (window.confirm("Are you sure you want to delete this subject?")) {
      setSubjects(subjects.filter((s) => s.id !== id));
    }
  };

  const getSubjectsByGrade = (grade) => {
    return subjects.filter((s) => s.grade === grade);
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />

        <div className="pt-20 px-8">
          <div className="p-8">
            <div className="flex justify-between items-center mb-8">
              <h1 className="text-3xl font-bold">Subject Details</h1>
              <div className="relative w-72">
                <input
                  type="text"
                  placeholder="Search by grade..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 pr-10 border border-gray-300 rounded focus:outline-none focus:border-[#1e3a5f]"
                />
                <Search
                  className="absolute right-3 top-2.5 text-gray-400"
                  size={20}
                />
              </div>
            </div>

            {filteredGrades.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                No grades found matching your search
              </div>
            ) : (
              filteredGrades.map((grade) => (
                <SubjectTable
                  key={grade}
                  grade={grade}
                  subjects={getSubjectsByGrade(grade)}
                  onEdit={handleEditSubject}
                  onDelete={handleDeleteSubject}
                  onAdd={handleAddSubject}
                />
              ))
            )}
          </div>
        </div>

        <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
          <SubjectForm
            onClose={() => setIsModalOpen(false)}
            onSave={handleSaveSubject}
            editData={editingSubject}
            teachers={teachers}
            grade={selectedGrade}
          />
        </Modal>
      </div>
    </div>
  );
};

export default SubjectManagement;
