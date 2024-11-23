import React from "react";
import Image from "next/image";

const HeroSection = () => {
  return (
    <div className="flex flex-col items-center justify-center text-center bg-[#faf4f4] py-20">
      <div className="mb-6">
        <Image
          src="/images/tubes.png"
          alt="Decorative tubes"
          width={450}
          height={200}
          layout="intrinsic"
        />
      </div>
      <h1 className="text-5xl text-[#a984b2] font-extrabold mb-6 tracking-tight">
        decode ingredient lists{" "}
        <span className="text-[#6d6875]">like a pro</span>
      </h1>
      <p className="mb-6 text-lg md:text-xl max-w-xl mx-auto">
        * Type to search for products or ingredients
      </p>
      <div className="flex justify-center items-center w-full px-4">
        <input
          type="text"
          placeholder="Search..."
          className="border-2 border-gray-300 p-4 w-full max-w-lg rounded-l-lg"
        />
        <button className="bg-[#6d6875] text-white px-8 rounded-r-lg">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M8 4v16m8-16v16M4 8h16m-16 8h16"
            />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default HeroSection;
