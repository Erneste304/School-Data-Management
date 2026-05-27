import React, { useState, useEffect } from 'react';
import { HiSearch, HiUserAdd, HiTrash, HiFilter, HiAcademicCap } from 'react-icons/hi';

export default function StudentManagement() {
    const [students, setStudents] = useState([]);
    const [classes, setClasses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedClass, setSelectedClass] = useState('');
    const [showAddModal, setShowAddModal] = useState(false);
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        student_id: '',
        current_class: '',
        phone: '',
        password: 'password123'
    });
    const [error, setError] = useState('');

    useEffect(() => {
        fetchClasses();
        fetchStudents();
    }, [selectedClass]);

    const fetchClasses = async () => {
        try {
            const res = await fetch('/api/academics/classes/');
            if (res.ok) {
                const data = await res.json();
                setClasses(data);
            }
        } catch (err) {
            console.error('Error fetching classes:', err);
        }
    };

    const fetchStudents = async () => {
        setLoading(true);
        try {
            let url = '/api/academics/students/';
            const params = [];
            if (selectedClass) params.push(`class_id=${selectedClass}`);
            if (searchQuery) params.push(`search=${searchQuery}`);
            if (params.length > 0) {
                url += `?${params.join('&')}`;
            }

            const res = await fetch(url);
            if (res.ok) {
                const data = await res.json();
                setStudents(data);
            }
        } catch (err) {
            console.error('Error fetching students:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        fetchStudents();
    };

    const handleAddStudent = async (e) => {
        e.preventDefault();
        setError('');
        try {
            // 1. Create User
            const userRes = await fetch('/api/accounts/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: formData.username,
                    email: formData.email,
                    first_name: formData.first_name,
                    last_name: formData.last_name,
                    role: 'student',
                    phone: formData.phone,
                    password: formData.password,
                    password2: formData.password
                })
            });

            const userData = await userRes.json();
            if (!userRes.ok) {
                setError(userData.detail || 'Failed to create student user accounts.');
                return;
            }

            // 2. Create Student Profile
            const studentRes = await fetch('/api/academics/students/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user: userData.user.id,
                    student_id: formData.student_id,
                    enrollment_date: new Date().toISOString().split('T')[0],
                    current_class: formData.current_class ? parseInt(formData.current_class) : null,
                    is_active: true
                })
            });

            if (studentRes.ok) {
                // 3. Create enrollment
                if (formData.current_class) {
                    await fetch('/api/academics/enrollments/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            student: userData.user.id,
                            enrolled_class: parseInt(formData.current_class),
                            academic_year: '2025-2026'
                        })
                    });
                }

                setShowAddModal(false);
                setFormData({
                    username: '',
                    email: '',
                    first_name: '',
                    last_name: '',
                    student_id: '',
                    current_class: '',
                    phone: '',
                    password: 'password123'
                });
                fetchStudents();
            } else {
                const sData = await studentRes.json();
                setError(sData.detail || 'Failed to create student profile.');
            }
        } catch (err) {
            setError('Server connection error. Please try again.');
        }
    };

    const handleDeleteStudent = async (id) => {
        if (!confirm('Are you sure you want to deactivate this student?')) return;
        try {
            const res = await fetch(`/api/academics/students/${id}/`, {
                method: 'DELETE'
            });
            if (res.ok) {
                fetchStudents();
            }
        } catch (err) {
            console.error('Error deleting student:', err);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Student Management</h2>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">View, search, filter and manage student accounts</p>
                </div>
                <button
                    onClick={() => setShowAddModal(true)}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200 text-sm font-semibold shadow-md self-start sm:self-center"
                >
                    <HiUserAdd className="w-5 h-5" />
                    Add Student
                </button>
            </div>

            {/* Filter and Search Bar */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4 flex flex-col md:flex-row gap-4 items-center justify-between">
                <form onSubmit={handleSearchSubmit} className="relative w-full md:max-w-md">
                    <input
                        type="text"
                        placeholder="Search by name or student ID..."
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-white text-sm"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    <button type="submit" className="absolute left-3 top-2.5 text-gray-400 hover:text-blue-500">
                        <HiSearch className="w-5 h-5" />
                    </button>
                </form>

                <div className="flex items-center gap-3 w-full md:w-auto">
                    <HiFilter className="text-gray-400" />
                    <select
                        className="border border-gray-300 dark:border-gray-700 rounded-lg p-2 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-white text-sm w-full md:w-48"
                        value={selectedClass}
                        onChange={(e) => setSelectedClass(e.target.value)}
                    >
                        <option value="">All Classes</option>
                        {classes.map((c) => (
                            <option key={c.id} value={c.id}>{c.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Student Table */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
                {loading ? (
                    <div className="flex justify-center py-10"><span className="loader-blue"></span></div>
                ) : students.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-300 text-xs font-semibold uppercase border-b border-gray-200 dark:border-gray-700">
                                    <th className="p-4">Student ID</th>
                                    <th className="p-4">Name</th>
                                    <th className="p-4">Class</th>
                                    <th className="p-4">GPA</th>
                                    <th className="p-4">Attendance Rate</th>
                                    <th className="p-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                {students.map((student) => (
                                    <tr key={student.user} className="hover:bg-gray-50 dark:hover:bg-gray-750 transition duration-150 text-sm">
                                        <td className="p-4 font-semibold text-blue-600 dark:text-blue-400">{student.student_id}</td>
                                        <td className="p-4 font-medium text-gray-800 dark:text-white">{student.full_name}</td>
                                        <td className="p-4 text-gray-500 dark:text-gray-400">{student.class_name || 'N/A'}</td>
                                        <td className="p-4">
                                            <span className="px-2.5 py-1 bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 rounded-full font-semibold text-xs">
                                                {student.gpa || '0.00'}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            <span className="px-2.5 py-1 bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300 rounded-full font-semibold text-xs">
                                                {student.attendance_rate !== undefined ? `${student.attendance_rate}%` : '0%'}
                                            </span>
                                        </td>
                                        <td className="p-4 text-right">
                                            <button
                                                onClick={() => handleDeleteStudent(student.user)}
                                                className="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 dark:hover:bg-red-950 transition duration-150"
                                            >
                                                <HiTrash className="w-5 h-5" />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <p className="text-gray-500 text-center py-10">No students found.</p>
                )}
            </div>

            {/* Add Student Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-lg w-full p-6 space-y-4">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Add New Student</h3>
                            <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        {error && <div className="p-3 bg-red-50 text-red-600 rounded text-xs">{error}</div>}
                        <form onSubmit={handleAddStudent} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Username</label>
                                <input
                                    type="text" required
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm"
                                    value={formData.username}
                                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Email</label>
                                <input
                                    type="email" required
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">First Name</label>
                                <input
                                    type="text" required
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm"
                                    value={formData.first_name}
                                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Last Name</label>
                                <input
                                    type="text" required
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm"
                                    value={formData.last_name}
                                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Student ID</label>
                                <input
                                    type="text" required
                                    placeholder="e.g. STUD004"
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm"
                                    value={formData.student_id}
                                    onChange={(e) => setFormData({ ...formData, student_id: e.target.value })}
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Assign Class</label>
                                <select
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm"
                                    value={formData.current_class}
                                    onChange={(e) => setFormData({ ...formData, current_class: e.target.value })}
                                >
                                    <option value="">No Class</option>
                                    {classes.map((c) => (
                                        <option key={c.id} value={c.id}>{c.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Phone</label>
                                <input
                                    type="text"
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm"
                                    value={formData.phone}
                                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Password</label>
                                <input
                                    type="password" required
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                />
                            </div>
                            <div className="col-span-1 sm:col-span-2 flex justify-end gap-3 pt-3 border-t dark:border-gray-700">
                                <button type="button" onClick={() => setShowAddModal(false)} className="px-4 py-2 border rounded text-gray-500 text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition">Save Student</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
