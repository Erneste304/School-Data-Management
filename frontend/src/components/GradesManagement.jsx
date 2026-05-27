import React, { useState, useEffect } from 'react';
import { HiPlusCircle, HiBookmark, HiAcademicCap, HiTrendingUp } from 'react-icons/hi';

export default function GradesManagement() {
    const [userRole, setUserRole] = useState(localStorage.getItem('userRole') || 'student');
    const [grades, setGrades] = useState([]);
    const [classes, setClasses] = useState([]);
    const [selectedClass, setSelectedClass] = useState('');
    const [students, setStudents] = useState([]);
    const [selectedStudent, setSelectedStudent] = useState('');
    const [loading, setLoading] = useState(true);
    const [showAddModal, setShowAddModal] = useState(false);
    const [newGrade, setNewGrade] = useState({
        enrollment: '',
        assignment_name: '',
        score: ''
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        if (userRole === 'student' || userRole === 'parent') {
            fetchStudentGrades();
        } else {
            fetchClasses();
        }
    }, [userRole]);

    useEffect(() => {
        if (selectedClass) {
            fetchClassStudents();
        } else {
            setStudents([]);
        }
    }, [selectedClass]);

    useEffect(() => {
        if (selectedStudent) {
            fetchSelectedStudentGrades();
        } else if (userRole !== 'student' && userRole !== 'parent') {
            setGrades([]);
        }
    }, [selectedStudent]);

    const fetchStudentGrades = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/academics/grades/');
            if (res.ok) {
                const data = await res.json();
                setGrades(data);
            }
        } catch (err) {
            console.error('Error fetching student grades:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchClasses = async () => {
        try {
            const res = await fetch('/api/academics/classes/');
            if (res.ok) {
                const data = await res.json();
                setClasses(data);
                if (data.length > 0) {
                    setSelectedClass(data[0].id.toString());
                }
            }
        } catch (err) {
            console.error('Error fetching classes:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchClassStudents = async () => {
        try {
            const res = await fetch(`/api/academics/enrollments/?class_id=${selectedClass}`);
            if (res.ok) {
                const data = await res.json();
                setStudents(data);
                if (data.length > 0) {
                    setSelectedStudent(data[0].student.toString());
                    setNewGrade(prev => ({ ...prev, enrollment: data[0].id.toString() }));
                } else {
                    setSelectedStudent('');
                    setGrades([]);
                }
            }
        } catch (err) {
            console.error('Error fetching class students:', err);
        }
    };

    const fetchSelectedStudentGrades = async () => {
        setLoading(true);
        try {
            const res = await fetch(`/api/academics/grades/?student_id=${selectedStudent}`);
            if (res.ok) {
                const data = await res.json();
                setGrades(data);
            }
        } catch (err) {
            console.error('Error fetching selected student grades:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAddGrade = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        // Find active enrollment ID for selected student
        const activeEnrollment = students.find(s => s.student.toString() === selectedStudent);
        if (!activeEnrollment) {
            setError('Student enrollment record not found.');
            return;
        }

        try {
            const res = await fetch('/api/academics/grades/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    enrollment: activeEnrollment.id,
                    assignment_name: newGrade.assignment_name,
                    score: parseFloat(newGrade.score)
                })
            });

            if (res.ok) {
                setSuccess('Grade recorded successfully!');
                setNewGrade({ enrollment: activeEnrollment.id.toString(), assignment_name: '', score: '' });
                setShowAddModal(false);
                fetchSelectedStudentGrades();
            } else {
                const data = await res.json();
                setError(data.detail || 'Failed to submit grade.');
            }
        } catch (err) {
            setError('Server connection error. Please try again.');
        }
    };

    // Calculate Grade average
    const totalScore = grades.reduce((acc, curr) => acc + parseFloat(curr.score), 0);
    const averageScore = grades.length > 0 ? (totalScore / grades.length).toFixed(1) : 'N/A';

    const getLetterGrade = (score) => {
        const val = parseFloat(score);
        if (val >= 90) return 'A';
        if (val >= 80) return 'B';
        if (val >= 70) return 'C';
        if (val >= 60) return 'D';
        return 'F';
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Academic Grades & Marks</h2>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
                        {userRole === 'student' || userRole === 'parent'
                            ? 'Monitor assignments, quiz results and overall academic averages'
                            : 'Manage class lists, grade assessments, and publish student scores'}
                    </p>
                </div>
                {(userRole === 'teacher' || userRole === 'admin') && students.length > 0 && (
                    <button
                        onClick={() => setShowAddModal(true)}
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200 text-sm font-semibold shadow-md self-start sm:self-center"
                    >
                        <HiPlusCircle className="w-5 h-5" />
                        Record Grade
                    </button>
                )}
            </div>

            {/* Main Selection Area for Admin/Teachers */}
            {(userRole === 'teacher' || userRole === 'admin') && (
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4 flex flex-col sm:flex-row gap-4 items-center">
                    <div className="flex flex-col w-full sm:w-48">
                        <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Select Class</label>
                        <select
                            className="border border-gray-300 dark:border-gray-700 rounded-lg p-2 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-white text-sm"
                            value={selectedClass}
                            onChange={(e) => setSelectedClass(e.target.value)}
                        >
                            {classes.map((c) => (
                                <option key={c.id} value={c.id}>{c.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="flex flex-col w-full sm:w-64">
                        <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Select Student</label>
                        <select
                            className="border border-gray-300 dark:border-gray-700 rounded-lg p-2 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-white text-sm"
                            value={selectedStudent}
                            onChange={(e) => setSelectedStudent(e.target.value)}
                            disabled={students.length === 0}
                        >
                            {students.length === 0 ? (
                                <option value="">No enrolled students</option>
                            ) : (
                                students.map((s) => (
                                    <option key={s.student} value={s.student}>{s.student_name}</option>
                                ))
                            )}
                        </select>
                    </div>
                </div>
            )}

            {/* Performance Overview Card */}
            {grades.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-5 shadow flex items-center gap-4 text-white">
                        <div className="p-3 bg-white/20 rounded-xl">
                            <HiAcademicCap className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-white/70 text-sm">Overall Average</p>
                            <p className="text-2xl font-bold">{averageScore}%</p>
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-emerald-500 to-emerald-700 rounded-2xl p-5 shadow flex items-center gap-4 text-white">
                        <div className="p-3 bg-white/20 rounded-xl">
                            <HiTrendingUp className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-white/70 text-sm">Equivalent Grade</p>
                            <p className="text-2xl font-bold">{getLetterGrade(averageScore)}</p>
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-violet-500 to-violet-700 rounded-2xl p-5 shadow flex items-center gap-4 text-white">
                        <div className="p-3 bg-white/20 rounded-xl">
                            <HiBookmark className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-white/70 text-sm">Assessments Taken</p>
                            <p className="text-2xl font-bold">{grades.length} Graded</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Grades Table */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
                {loading ? (
                    <div className="flex justify-center py-10"><span className="loader-blue"></span></div>
                ) : grades.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-300 text-xs font-semibold uppercase border-b border-gray-200 dark:border-gray-700">
                                    <th className="p-4">Assessment / Assignment</th>
                                    <th className="p-4">Date Recorded</th>
                                    <th className="p-4">Score</th>
                                    <th className="p-4">Letter Grade</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                {grades.map((grade) => (
                                    <tr key={grade.id} className="hover:bg-gray-50 dark:hover:bg-gray-755 transition text-sm">
                                        <td className="p-4 font-semibold text-gray-800 dark:text-white">{grade.assignment_name}</td>
                                        <td className="p-4 text-gray-500 dark:text-gray-400">{grade.date_recorded}</td>
                                        <td className="p-4">
                                            <span className="font-bold text-gray-800 dark:text-white">{grade.score}%</span>
                                        </td>
                                        <td className="p-4">
                                            <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                                                getLetterGrade(grade.score) === 'A' 
                                                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' 
                                                    : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                                            }`}>
                                                {getLetterGrade(grade.score)}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="text-center py-12 text-gray-500">
                        <span className="text-4xl mb-2 block">📚</span>
                        No academic grades found for this student.
                    </div>
                )}
            </div>

            {/* Record Grade Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Record Student Assessment</h3>
                            <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        {error && <div className="p-3 bg-red-50 text-red-600 rounded text-xs">{error}</div>}
                        <form onSubmit={handleAddGrade} className="space-y-4">
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Assessment Name</label>
                                <input
                                    type="text" required
                                    placeholder="e.g. Midterm Physics, Algebra Quiz 1"
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newGrade.assignment_name}
                                    onChange={(e) => setNewGrade({ ...newGrade, assignment_name: e.target.value })}
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Score Percentage (%)</label>
                                <input
                                    type="number" required min="0" max="100" step="0.1"
                                    placeholder="e.g. 87.5"
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newGrade.score}
                                    onChange={(e) => setNewGrade({ ...newGrade, score: e.target.value })}
                                />
                            </div>
                            <div className="flex justify-end gap-3 pt-3 border-t dark:border-gray-700">
                                <button type="button" onClick={() => setShowAddModal(false)} className="px-4 py-2 border rounded text-gray-500 text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition">Save Mark</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
