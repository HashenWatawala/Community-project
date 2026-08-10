import React from "react";
import PropTypes from "prop-types";

const baseStyles =
  "inline-flex items-center justify-center font-semibold rounded-lg focus:outline-none transition-colors duration-200";

const variants = {
  primary:
    "bg-[#0f2c4c] text-white hover:bg-[#163861] shadow-sm",
  secondary:
    "bg-gray-200 text-gray-800 hover:bg-gray-300",
  outline:
    "border border-[#0f2c4c] text-[#0f2c4c] hover:bg-[#0f2c4c] hover:text-white transition-all",
  danger:
    "bg-red-600 text-white hover:bg-red-700",
};

const sizes = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-5 py-2 text-base",
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
