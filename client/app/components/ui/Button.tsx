"use client";

import { ButtonHTMLAttributes } from "react";
import { twMerge } from "tailwind-merge";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "gradient";
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
}

export function Button({
  children,
  className,
  variant = "primary",
  size = "md",
  fullWidth = false,
  ...props
}: ButtonProps) {
  const baseStyles =
    "font-medium rounded-lg shadow-sm transition-all duration-200 active:scale-95";

  const variants = {
    primary:
      "text-white bg-primary-500 hover:bg-primary-600 focus:ring-2 focus:ring-primary-500/50",
    secondary:
      "text-white bg-secondary-500 hover:bg-secondary-600 focus:ring-2 focus:ring-secondary-500/50",
    outline:
      "text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 focus:ring-2 focus:ring-primary-500/50",
    gradient:
      "text-white bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 focus:ring-2 focus:ring-primary-500/50",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base",
  };

  const classes = twMerge(
    baseStyles,
    variants[variant],
    sizes[size],
    fullWidth ? "w-full" : "",
    className
  );

  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
}
