import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './RegisterPage.css';

const RegisterPage = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        role: 'student',
        phone: '',
        password: '',
        password2: ''
    });
    const [error, setError] = useState('');
    const [successMsg, setSuccessMsg] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const { username, email, first_name, last_name, role, phone, password, password2 } = formData;

    const onChange = e => setFormData({ ...formData, [e.target.name]: e.target.value });

    const onSubmit = async e => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccessMsg('');

        if (password !== password2) {
            setError("Passwords do not match.");
            setLoading(false);
            return;
        }

        try {
            const response = await fetch('/api/accounts/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(formData),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccessMsg("Registration successful! Redirecting to login...");
                setTimeout(() => {
                    navigate('/login');
                }, 2000);
            } else {
                // If there are validation errors from DRF, show them
                if (data.password2) {
                    setError(data.password2);
                } else if (data.email) {
                    setError(`Email error: ${data.email.join(', ')}`);
                } else if (data.username) {
                    setError(`Username error: ${data.username.join(', ')}`);
                } else {
                    setError(data.detail || 'Registration failed. Please verify your details.');
                }
            }
        } catch (err) {
            setError('Server connection error. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="register-container">
            <div className="register-card">
                <div className="register-header">
                    <div className="logo-placeholder">🏫</div>
                    <h1>Create Account</h1>
                    <p>Join the Rutabo School Management System</p>
                </div>

                {error && <div className="error-banner">{error}</div>}
                {successMsg && <div className="success-banner">{successMsg}</div>}

                <form onSubmit={onSubmit} className="register-form">
                    <div className="form-grid">
                        <div className="form-group">
                            <label htmlFor="username">Username</label>
                            <input
                                type="text"
                                id="username"
                                name="username"
                                placeholder="johndoe"
                                value={username}
                                onChange={onChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="email">Email Address</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                placeholder="john.doe@school.com"
                                value={email}
                                onChange={onChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="first_name">First Name</label>
                            <input
                                type="text"
                                id="first_name"
                                name="first_name"
                                placeholder="John"
                                value={first_name}
                                onChange={onChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="last_name">Last Name</label>
                            <input
                                type="text"
                                id="last_name"
                                name="last_name"
                                placeholder="Doe"
                                value={last_name}
                                onChange={onChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="role">Your Role</label>
                            <select
                                id="role"
                                name="role"
                                value={role}
                                onChange={onChange}
                                className="form-select"
                                required
                            >
                                <option value="student">Student</option>
                                <option value="teacher">Teacher</option>
                                <option value="parent">Parent</option>
                                <option value="animateur">Animateur</option>
                                <option value="animatrice">Animatrice</option>
                                <option value="accountant">Accountant</option>
                                <option value="admin">System Admin</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label htmlFor="phone">Phone Number</label>
                            <input
                                type="text"
                                id="phone"
                                name="phone"
                                placeholder="+250 788 123 456"
                                value={phone}
                                onChange={onChange}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <input
                                type="password"
                                id="password"
                                name="password"
                                placeholder="••••••••"
                                value={password}
                                onChange={onChange}
                                required
                                minLength={8}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password2">Confirm Password</label>
                            <input
                                type="password"
                                id="password2"
                                name="password2"
                                placeholder="••••••••"
                                value={password2}
                                onChange={onChange}
                                required
                                minLength={8}
                            />
                        </div>
                    </div>

                    <button type="submit" className="register-button" disabled={loading}>
                        {loading ? (
                            <span className="loader"></span>
                        ) : (
                            'Sign Up'
                        )}
                    </button>
                </form>

                <div className="register-footer">
                    <p>Already have an account? <Link to="/login" className="login-link">Sign In</Link></p>
                    <Link to="/" className="back-link">Return to Home</Link>
                </div>
            </div>
        </div>
    );
};

export default RegisterPage;
