import React from "react"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import GetStarted from "./pages/GetStarted";
import GenerateTimetable from "./pages/Timetable/GenerateTimetable";
import ViewTimetable from "./pages/Timetable/ViewTimetable";
import LoginPage from "./pages/Auth/LoginPage";
import Dashboard from "./pages/Dashboard/DashBoard";
import ClassManagement from "./pages/Management/ClassManagement";
import RegisterPage  from "./pages/Auth/RegisterPage";
import TeacherManagement from "./pages/Management/TeacherManagement";
import SubjectManagement from "./pages/Management/SubjectManagement";


import ProtectedRoute from "./routes/ProtectedRoute";

function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<GetStarted />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />

        <Route path="/class-management" element={
          <ProtectedRoute>
            <ClassManagement />
          </ProtectedRoute>
        } />

        <Route path="/teacher-management" element={
          <ProtectedRoute>
            <TeacherManagement />
          </ProtectedRoute>
        } />

        <Route path="/subject-management" element={
          <ProtectedRoute>
            <SubjectManagement />
          </ProtectedRoute>
        } />

        <Route path="/generate-timetable" element={
          <ProtectedRoute>
            <GenerateTimetable />
          </ProtectedRoute>
        } />

        <Route path="/view-timetable" element={
          <ProtectedRoute>
            <ViewTimetable />
          </ProtectedRoute>
        } />

      </Routes>
    </Router>
  )
}

export default App
