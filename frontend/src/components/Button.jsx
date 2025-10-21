import React from "react";
import PropTypes from "prop-types";

const baseStyles ="inline-flex w-fit items-center justify-center font-medium rounded-2xl transition-all duration-200 focus:outline-none";

const variants = {
  primary: "bg-blue-600 text-white hover:bg-blue-700",
  secondary: "bg-gray-200 text-gray-800 hover:bg-gray-300",
  danger: "bg-red-600 text-white hover:bg-red-700",
  outline: "border border-gray-400 text-gray-700 hover:bg-gray-100",
};

const sizes = {
  sm: "px-3 py-1 text-sm",
  md: "px-4 py-2 text-base",
  lg: "px-6 py-3 text-lg",
};

export default function Button({
  children,
  variant = "primary",
  size = "md",
  disabled = false,
  onClick,
  className = "",
  type = "button",
}) {
  const styles = `${baseStyles} ${variants[variant]} ${sizes[size]} ${
    disabled ? "opacity-50 cursor-not-allowed" : ""
  } ${className}`;

  return (
    <button type={type} className={styles} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(["primary", "secondary", "danger", "outline"]),
  size: PropTypes.oneOf(["sm", "md", "lg"]),
  disabled: PropTypes.bool,
  onClick: PropTypes.func,
  className: PropTypes.string,
  type: PropTypes.string,
};


// npm install prop-types