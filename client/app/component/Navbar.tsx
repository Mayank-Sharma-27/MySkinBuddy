"use client";
import React, { useState } from "react";
import Link from "next/link";
import NavLink from "./NavLink"; // Assuming NavLink is an optimized link component for Next.js
import { Bars3Icon, XMarkIcon } from "@heroicons/react/24/solid";
import MenuOverlay from "./MenuOverlay";
import SchedulePickup from "./SchedulePickup";
import Image from "next/image";

const navLinks = [
  {
    title: "Products",
    path: "#products",
  },
  {
    title: "Ingrdients",
    path: "#pricing",
  },
  {
    title: "FAQ",
    path: "#faq",
  },
];

const Navbar = () => {
  const [navbarOpen, setNavbarOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-10 bg-[#faf4f4] bg-opacity-100">
      <nav className="flex container lg:py-0 flex-wrap items-center justify-between mx-auto px-4 py-0">
        <Link href="/">
          <div
            className="text-lg md:text-5xl font-semibold"
            style={{ cursor: "pointer" }}
          >
            <Image
              src="/images/logo.jpg"
              alt="Company Logo"
              width={100}
              height={1}
              style={{
                maxWidth: "100%",
                height: "auto",
                objectFit: "contain",
              }}
            />
          </div>
        </Link>
        <div className="mobile-menu block md:hidden">
          {!navbarOpen ? (
            <button
              onClick={() => setNavbarOpen(true)}
              className="flex items-center px-3 py-2 border rounded text-black hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              aria-expanded="false"
              aria-controls="mobile-menu"
              aria-label="Open main menu"
            >
              <Bars3Icon className="h-5 w-5" />
            </button>
          ) : (
            <button
              onClick={() => setNavbarOpen(false)}
              className="flex items-center px-3 py-2 border rounded text-black hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              aria-expanded="true"
              aria-controls="mobile-menu"
              aria-label="Close main menu"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          )}
        </div>
        <div className="menu hidden md:block md:w-auto" id="navbar">
          <ul className="flex p-4 md:p-0 sm:flex-row md:space-x-8 mt-0 list-none">
            {navLinks.map((link, index) => (
              <li key={index}>
                <NavLink href={link.path} title={link.title} />
              </li>
            ))}
            <li></li>
          </ul>
        </div>
      </nav>
      {navbarOpen && <MenuOverlay links={navLinks} />}
    </header>
  );
};

export default Navbar;
