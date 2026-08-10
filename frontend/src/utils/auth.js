export const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const loginUser = async (username, password) => {
  const resp = await fetch(`${API}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await resp.json();
  if (!resp.ok) {
    throw new Error(data.detail || data.message || "Login failed");
  }
  // store token and user
  localStorage.setItem(
    "user",
    JSON.stringify({ token: data.access_token, user: data.user }),
  );
  return data;
};

export const registerUser = async (payload) => {
  const resp = await fetch(`${API}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await resp.json();
  if (!resp.ok) {
    throw new Error(data.detail || data.message || "Register failed");
  }
  return data;
};

export const logoutUser = () => {
  localStorage.removeItem("user");
};

export const getUser = () => {
  const data = localStorage.getItem("user");
  return data ? JSON.parse(data) : null;
};

export const isAuthenticated = () => {
  const u = getUser();
  return !!(u && u.token);
};
