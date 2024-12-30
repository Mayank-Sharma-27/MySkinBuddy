"use client";

import { HTMLAttributes } from "react";
import { twMerge } from "tailwind-merge";

interface ContainerProps extends HTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg" | "xl";
}

export function Container({
  children,
  className,
  size = "lg",
  ...props
}: ContainerProps) {
  const baseStyles = "mx-auto px-4 sm:px-6";

  const sizes = {
    sm: "max-w-3xl",
    md: "max-w-5xl",
    lg: "max-w-7xl",
    xl: "max-w-[96rem]",
  };

  const classes = twMerge(baseStyles, sizes[size], className);

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
}
