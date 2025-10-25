import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const RegisterPage = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    fullName: "",
    username: "",
    nic: "",
    email: "",
    role: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (form.password !== form.confirmPassword) {
      alert("Passwords do not match");
      return;
    }
    // TODO: Hook up to your API
    console.log("Register payload:", form);
    navigate("/login");
  };

  return (
    <div className="h-screen w-full flex items-center justify-center bg-[var(--color-primary)] px-4">
      <div className="w-full max-w-5xl bg-white rounded-lg shadow-2xl p-6 md:p-10">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-8">
          Create an Account
        </h1>

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Full Name */}
            <div>
              <input
                type="text"
                name="fullName"
                placeholder="Full Name"
                value={form.fullName}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                required
              />
            </div>

            {/* User name */}
            <div>
              <input
                type="text"
                name="username"
                placeholder="User name"
                value={form.username}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                required
              />
            </div>

            {/* NIC Number */}
            <div>
              <input
                type="text"
                name="nic"
                placeholder="NIC Number"
                value={form.nic}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                required
              />
            </div>

            {/* Password */}
            <div>
              <input
                type="password"
                name="password"
                placeholder="Password"
                value={form.password}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                required
              />
            </div>

            {/* Email */}
            <div>
              <input
                type="email"
                name="email"
                placeholder="e-mail"
                value={form.email}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                required
              />
            </div>

            {/* Re-entry Password */}
            <div>
              <input
                type="password"
                name="confirmPassword"
                placeholder="Re-entry Password"
                value={form.confirmPassword}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                required
              />
            </div>

            {/* Role Select */}
            <div className="md:col-span-1">
              <select
                name="role"
                value={form.role}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                required
              >
                <option value="" disabled>
                  Select your role
                </option>
                <option value="admin">Admin</option>
                <option value="principal">Principal</option>
                <option value="teacher">Teacher</option>
                <option value="clerk">Clerk</option>
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-10 flex justify-end gap-4">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="inline-flex items-center justify-center w-44 px-6 py-3 rounded-md bg-gray-400 text-white font-medium hover:opacity-90"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex items-center justify-center w-44 px-6 py-3 rounded-md bg-[var(--color-primary)] text-white font-semibold hover:opacity-90"
            >
              Create Account
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterPage;
