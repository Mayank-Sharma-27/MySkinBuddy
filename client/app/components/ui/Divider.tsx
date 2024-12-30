"use client";

import { HTMLAttributes } from "react";
import { twMerge } from "tailwind-merge";

interface DividerProps extends HTMLAttributes<HTMLDivElement> {
  text?: string;
}

export function Divider({ text, className, ...props }: DividerProps) {
  const baseStyles = "relative";
  const classes = twMerge(baseStyles, className);

  if (!text) {
    return <hr className="border-t border-gray-300" {...props} />;
  }

  return (
    <div className={classes} {...props}>
      <div className="absolute inset-0 flex items-center">
        <div className="w-full border-t border-gray-300" />
      </div>
      <div className="relative flex justify-center text-sm">
        <span className="px-2 bg-white text-gray-500">{text}</span>
      </div>
    </div>
  );
}
