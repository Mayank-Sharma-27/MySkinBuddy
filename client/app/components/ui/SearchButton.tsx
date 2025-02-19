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
    "absolute right-2 inset-y-2",
    "rounded-xl text-white aspect-square",
    "bg-gradient-to-r from-[#B75CFF] to-[#FF7373]",
    "hover:from-[#A346FF] hover:to-[#FF5C5C]",
    "transition-all duration-200",
    "hover:scale-105",
    "active:scale-95",
    "flex items-center justify-center",
    className
  );

  return (
    <button className={baseStyles} {...props}>
      <span className="sr-only">Search</span>
      <svg
        className="h-5 w-5"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2.5}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
    </button>
  );
}
