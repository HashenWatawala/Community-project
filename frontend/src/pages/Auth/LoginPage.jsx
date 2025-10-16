import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../../utils/auth";

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    // Example static login (replace with backend call later)
    if (username === "admin" && password === "1234") {
      loginUser({ username, role: "admin" }); // Save login to localStorage
      navigate("/dashboard"); // Redirect to a protected page
    } else {
      alert("Invalid credentials");
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-gray-100">
      <form
        onSubmit={handleLogin}
        className="bg-white shadow-lg rounded-lg p-8 w-96"
      >
        <h2 className="text-2xl font-semibold text-center mb-6">Login</h2>

        <input
          type="text"
          placeholder="Username"
          className="w-full border border-gray-300 rounded-lg p-2 mb-4"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full border border-gray-300 rounded-lg p-2 mb-6"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg"
        >
          Sign In
        </button>
      </form>
    </div>
  );
};

export default LoginPage;
