import React from "react";

const NavLink = ({ href, title }) => {
  const handleClick = (e) => {
    e.preventDefault();
    const target = document.querySelector(href);
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <a
      href={href}
      onClick={handleClick}
      className="block py-2 pl-3 pr-4 text-black sm:text-xl rounded md:p-0 mt-2.5"
    >
      {title}
    </a>
  );
};

export default NavLink;
