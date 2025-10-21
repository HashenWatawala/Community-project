export const loginUser = (userData) => {
  localStorage.setItem("user", JSON.stringify(userData));
};

export const logoutUser = () => {
  localStorage.removeItem("user");
};

export const getUser = () => {
  const data = localStorage.getItem("user");
  return data ? JSON.parse(data) : null;
};

export const isAuthenticated = () => {
  return !!localStorage.getItem("user");
};