import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../../utils/auth";
import logo from "../../assets/logo.png";

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    // login logic here
    try {
      const result = await loginUser(username, password);
      if (result.success) {
        navigate("/dashboard");
      }
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  return (
    <div className="h-screen w-full flex items-center justify-center bg-gray-100">
      {/* Main container for both sections */}
      <div className="flex flex-col md:flex-row shadow-2xl rounded-lg overflow-hidden max-w-4xl w-full mx-4">
        {/* Left section - Logo */}
        <div className="bg-[var(--color-primary)] w-full md:w-1/2 flex items-center justify-center p-8 md:p-12">
          <img
            src={logo}
            alt="Class Planner logo"
            className="w-56 md:w-64 lg:w-72 h-auto object-contain"
            loading="eager"
            fetchpriority="high"
          />
        </div>

        {/* Right section - Login Form */}
        <div className="bg-white w-full md:w-1/2 p-8 md:p-12 flex flex-col justify-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-8">Sign In</h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username Input */}
            <div className="flex justify-center">
              <input
                type="text"
                placeholder="User name"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-[90%] mx-auto px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition-all"
                required
              />
            </div>

            {/* Password Input */}
            <div className="flex justify-center">
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-[90%] mx-auto px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition-all"
                required
              />
            </div>

            {/* Sign In Button */}
            <button
              type="submit"
              className="w-[60%] mx-auto flex justify-center bg-[var(--color-primary)] text-white py-3 rounded-md font-semibold hover:opacity-90 transition-opacity"
            >
              Sign in
            </button>
          </form>

          {/* Register Link */}
          <div className="mt-6 text-center text-sm text-gray-600">
            Don't have account?{" "}
            <a
              href="/register"
              onClick={(e) => {
                e.preventDefault();
                navigate("/register");
              }}
              className="text-[var(--color-primary)] font-semibold hover:underline"
            >
              Register Now
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
