import React from "react";
import { Link, useLocation } from "react-router-dom";

const Navbar = () => {
  const location = useLocation();
  return (
    <>
      <nav className="navbar">
        <div className="navbar-content">
          <h1>EMS Lite</h1>
          <ul className="nav-links">
            <li>
              <Link
                to="/"
                className={location.pathname === "/" ? "active" : ""}
              >
                Dashboard
              </Link>
            </li>
            <li>
              <Link
                to="/employees"
                className={location.pathname === "/employees" ? "active" : ""}
              >
                Employees
              </Link>
            </li>
            <li>
              <Link
                to="/attendance"
                className={location.pathname === "/attendance" ? "active" : ""}
              >
                Attendance
              </Link>
            </li>
          </ul>
        </div>
      </nav>
    </>
  );
};

export default Navbar;
