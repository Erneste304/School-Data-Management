import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  const navigate = useNavigate();
  const [announcements, setAnnouncements] = useState([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userRole, setUserRole] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role');
    
    if (token && role) {
      setIsLoggedIn(true);
      setUserRole(role);
    }
    
    // Fetch announcements
    fetchAnnouncements();
  }, []);

  const fetchAnnouncements = async () => {
    try {
      const response = await fetch('/api/announcements/published/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        }
      });
      if (response.ok) {
        const data = await response.json();
        setAnnouncements(data.slice(0, 3)); // Show only 3 latest
      }
    } catch (error) {
      console.error('Error fetching announcements:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNavigateToDashboard = () => {
    navigate('/dashboard');
  };

  const handleLoginClick = () => {
    navigate('/login');
  };

  const handleVisitorAccess = () => {
    navigate('/dashboard?visitor=true');
  };

  return (
    <div className="home-page">
      {/* Navigation Bar */}
      <nav className="navbar">
        <div className="container">
          <div className="navbar-brand">
            <h1 className="school-name">School Data Management System</h1>
            <p className="tagline">Excellence in Education Management</p>
          </div>
          <div className="navbar-actions">
            {isLoggedIn ? (
              <>
                <Link to="/dashboard" className="btn btn-primary">Dashboard</Link>
                <button className="btn btn-secondary" onClick={() => {
                  localStorage.clear();
                  window.location.href = '/';
                }}>Logout</button>
              </>
            ) : (
              <>
                <button className="btn btn-primary" onClick={handleLoginClick}>Login</button>
                <button className="btn btn-outline" onClick={handleVisitorAccess}>Visitor Access</button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1>Welcome to Our School</h1>
          <p>Empowering education through intelligent data management</p>
          {!isLoggedIn && (
            <div className="hero-buttons">
              <button className="btn btn-large btn-primary" onClick={handleLoginClick}>
                Get Started
              </button>
              <button className="btn btn-large btn-outline" onClick={handleVisitorAccess}>
                Learn More
              </button>
            </div>
          )}
        </div>
        <div className="hero-image">
          <div className="placeholder-image">
            📚 School Logo
          </div>
        </div>
      </section>

      {/* Quick Stats */}
      <section className="stats-section">
        <div className="container">
          <h2>Our System at a Glance</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">👥</div>
              <h3>Student Management</h3>
              <p>Comprehensive tracking of student data, profiles, and progress</p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <h3>Academic Records</h3>
              <p>Grades, attendance, and performance analysis</p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">💰</div>
              <h3>Finance Module</h3>
              <p>Manage fees, transactions, and financial reports</p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📋</div>
              <h3>Discipline Tracking</h3>
              <p>Record and manage student discipline cases</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <h2>Key Features</h2>
          <div className="features-grid">
            <div className="feature-card">
              <h3>Multi-Role Dashboard</h3>
              <p>Customized dashboards for Admin, Teachers, Students, Parents, and more. Each role gets relevant information and tools.</p>
              <ul>
                <li>✓ Admin - System oversight</li>
                <li>✓ Teachers - Class management</li>
                <li>✓ Students - Academic tracking</li>
                <li>✓ Parents - Child progress</li>
              </ul>
            </div>

            <div className="feature-card">
              <h3>Student Management</h3>
              <p>Complete student profiles organized by age group and educational stage.</p>
              <ul>
                <li>✓ Age-based grouping (0-5, 6-10, 11-16, 17-25+)</li>
                <li>✓ Educational stages (Nursery, Primary, Secondary, TVET)</li>
                <li>✓ Guardian information</li>
                <li>✓ Emergency contacts</li>
              </ul>
            </div>

            <div className="feature-card">
              <h3>Academic Excellence</h3>
              <p>Track grades, attendance, and student performance with ease.</p>
              <ul>
                <li>✓ Grade management</li>
                <li>✓ Attendance tracking</li>
                <li>✓ Performance analytics</li>
                <li>✓ Progress reports</li>
              </ul>
            </div>

            <div className="feature-card">
              <h3>Announcements & Reports</h3>
              <p>Secretary module for official communications and documentation.</p>
              <ul>
                <li>✓ System announcements</li>
                <li>✓ Academic reports</li>
                <li>✓ Analysis & insights</li>
                <li>✓ Newsletters</li>
              </ul>
            </div>

            <div className="feature-card">
              <h3>Financial Management</h3>
              <p>Complete fee management and financial tracking system.</p>
              <ul>
                <li>✓ Fee structures</li>
                <li>✓ Payment tracking</li>
                <li>✓ Financial reports</li>
                <li>✓ Budget management</li>
              </ul>
            </div>

            <div className="feature-card">
              <h3>Discipline Management</h3>
              <p>Professional discipline case handling and student welfare tracking.</p>
              <ul>
                <li>✓ Case reporting</li>
                <li>✓ Investigation tracking</li>
                <li>✓ Welfare monitoring</li>
                <li>✓ Behavior records</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Announcements Section */}
      {!loading && announcements.length > 0 && (
        <section className="announcements-section">
          <div className="container">
            <h2>Latest Announcements</h2>
            <div className="announcements-grid">
              {announcements.map((announcement) => (
                <div key={announcement.id} className="announcement-card">
                  {announcement.featured_image && (
                    <img src={announcement.featured_image} alt={announcement.title} className="announcement-image" />
                  )}
                  <h3>{announcement.title}</h3>
                  <p className="announcement-summary">{announcement.summary || announcement.content.substring(0, 150)}...</p>
                  <div className="announcement-meta">
                    <span className={`priority ${announcement.priority}`}>
                      {announcement.priority.toUpperCase()}
                    </span>
                    <span className="date">{new Date(announcement.published_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </div>
            {isLoggedIn && (
              <div className="view-all">
                <Link to="/announcements" className="btn btn-outline">View All Announcements</Link>
              </div>
            )}
          </div>
        </section>
      )}

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <h2>Ready to Get Started?</h2>
          <p>Join our system to manage school operations efficiently</p>
          {!isLoggedIn ? (
            <div className="cta-buttons">
              <button className="btn btn-large btn-primary" onClick={handleLoginClick}>
                Login to Your Account
              </button>
              <button className="btn btn-large btn-outline" onClick={handleVisitorAccess}>
                Browse as Visitor
              </button>
            </div>
          ) : (
            <button className="btn btn-large btn-primary" onClick={handleNavigateToDashboard}>
              Go to Dashboard
            </button>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h4>About Us</h4>
              <p>School Data Management System - Excellence in Education</p>
            </div>
            <div className="footer-section">
              <h4>Quick Links</h4>
              <ul>
                <li><a href="#features">Features</a></li>
                <li><a href="#announcements">Announcements</a></li>
                <li><a href="#contact">Contact</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Contact</h4>
              <p>Email: info@school.edu</p>
              <p>Phone: +1-234-567-8900</p>
            </div>
            <div className="footer-section">
              <h4>Follow Us</h4>
              <div className="social-links">
                <a href="#facebook">Facebook</a>
                <a href="#twitter">Twitter</a>
                <a href="#instagram">Instagram</a>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 School Data Management System. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
