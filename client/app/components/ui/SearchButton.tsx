"use client";

import { ButtonHTMLAttributes } from "react";
import { twMerge } from "tailwind-merge";

interface SearchButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  className?: string;
}

export function SearchButton({
  children,
  className,
  ...props
}: SearchButtonProps) {
  const baseStyles = twMerge(
    "px-8 py-3.5 rounded-2xl font-medium text-white whitespace-nowrap",
    "bg-gradient-to-r from-[#B75CFF] to-[#FF7373]",
    "hover:from-[#A346FF] hover:to-[#FF5C5C]",
    "transition-all duration-200 shadow-sm",
    "hover:shadow-md hover:-translate-y-0.5",
    "active:translate-y-0",
    className
  );

  return (
    <button className={baseStyles} {...props}>
      {children}
    </button>
  );
}
