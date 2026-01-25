import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Spline from '@splinetool/react-spline';
import { Explore } from './Explore';
import './index.css';
import './Desktop.css';

const navItems = [
  { label: "Home", path: "/" },
  { label: "Explore", path: "/explore" },
  { label: "About", path: "/about" },
];

// Navbar component
const Navbar = () => {
  const location = useLocation();
  
  return (
    <header className="navbar">
      <Link to="/" className="navbar-logo">
        Compass
      </Link>

      <nav className="navbar-nav animate-fade-in animate-delay">
        {navItems.map((item, index) => (
          <Link 
            key={index} 
            to={item.path} 
            className={`navbar-link ${location.pathname === item.path ? 'active' : ''}`}
          >
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="navbar-buttons animate-fade-in animate-delay">
        <Link to="/login" className="btn btn-outline">
          Log In
        </Link>
        <Link to="/signup" className="btn btn-primary">
          Sign Up
        </Link>
      </div>
    </header>
  );
};

// Home component
const Home = () => (
  <>
    {/* Hero Badge Card */}
    <section className="hero">
      <div className="hero-badge-container animate-fade-in animate-delay">
        <div className="hero-badge">
          <img
            className="hero-badge-icon"
            alt="Group"
            src="https://c.animaapp.com/mijkxqh6XSKe3B/img/group-2.png"
          />
          <div className="hero-badge-text">
            Trusted by +5000 Users and Brands
          </div>
        </div>
      </div>
    </section>

    {/* Spline Scene */}
    <div
      id="home"
      style={{ width: '100vw', height: '100vh', marginTop: '-100px' }}
    >
      <div style={{ width: '100vw', height: '100vh' }}>
        <Spline scene="https://prod.spline.design/Go96WFMIdS85XHjq/scene.splinecode" />
      </div>
    </div>
    
    {/* Desktop Component Content */}
    <div className="desktop-container">
      <div className="how-it-works-badge">
        <div className="badge-icon-wrapper">
          <img
            className="badge-icon"
            alt="Steps"
            src="https://c.animaapp.com/mkpswtn2QinJKt/img/material-symbols-step.svg"
          />
        </div>
        <span className="badge-text">HOW IT WORKS</span>
      </div>

      <h1 className="main-heading">
        Start In Four Steps And Grow With <br />
        Personalized, AI Backed Career Recommendations
      </h1>

      <div className="steps-image-container">
        <img 
          src="/assets/Frame 31.svg" 
          alt="Four Steps Process" 
          className="steps-image"
        />
      </div>

      <footer className="footer">
        <div className="footer-follow-text">Follow Us On</div>
        <div className="footer-copyright">©2026 compass.org</div>

        <img
          className="footer-social-icons"
          alt="Social"
          src="https://c.animaapp.com/mkpswtn2QinJKt/img/group-6.png"
        />

        <a href="#contact" className="footer-contact-link">
          <span>Contact Us</span>
        </a>
      </footer>
    </div>
  </>
);

// Main App component with routing
export default function App() {
  return (
    <Router>
      <div style={{ margin: 0, padding: 0, width: '100%', minHeight: '100vh' }}>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/explore" element={<Explore />} />
          <Route path="/about" element={<div>About Page - Coming Soon</div>} />
          <Route path="/login" element={<div>Login Page - Coming Soon</div>} />
          <Route path="/signup" element={<div>Sign Up Page - Coming Soon</div>} />
        </Routes>
      </div>
    </Router>
  );
}