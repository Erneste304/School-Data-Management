import React, { useState, useEffect } from 'react';
import { HiCheckCircle, HiXCircle, HiExclamationCircle, HiSave } from 'react-icons/hi';

export default function AttendanceTracking() {
    const [classes, setClasses] = useState([]);
    const [selectedClass, setSelectedClass] = useState('');
    const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
    const [students, setStudents] = useState([]);
    const [attendanceRecords, setAttendanceRecords] = useState({});
    const [loading, setLoading] = useState(false);
    const [classesLoading, setClassesLoading] = useState(true);
    const [message, setMessage] = useState({ text: '', type: '' });

    useEffect(() => {
        fetchClasses();
    }, []);

    useEffect(() => {
        if (selectedClass) {
            fetchClassStudentsAndAttendance();
        } else {
            setStudents([]);
            setAttendanceRecords({});
        }
    }, [selectedClass, date]);

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
            setClassesLoading(false);
        }
    };

    const fetchClassStudentsAndAttendance = async () => {
        setLoading(true);
        setMessage({ text: '', type: '' });
        try {
            // 1. Fetch enrollments
            const enrollRes = await fetch(`/api/academics/enrollments/?class_id=${selectedClass}`);
            if (!enrollRes.ok) throw new Error('Failed to fetch enrollments');
            const enrollments = await enrollRes.json();

            // 2. Fetch today's attendance for this class
            const attRes = await fetch(`/api/academics/attendance/?class_id=${selectedClass}&date=${date}`);
            const existingAttendance = attRes.ok ? await attRes.json() : [];

            // Map enrollment ID to attendance object
            const attMap = {};
            existingAttendance.forEach(a => {
                attMap[a.enrollment] = a;
            });

            // Initialize local attendance state
            const initialAttendance = {};
            enrollments.forEach(e => {
                const existing = attMap[e.id];
                initialAttendance[e.id] = {
                    enrollment_id: e.id,
                    status: existing ? existing.status : 'Present',
                    is_late: existing ? existing.is_late : false,
                    lateness_minutes: existing ? existing.lateness_minutes : 0
                };
            });

            setStudents(enrollments);
            setAttendanceRecords(initialAttendance);
        } catch (err) {
            console.error('Error loading attendance tracking data:', err);
            setMessage({ text: 'Error loading data. Please try again.', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleStatusChange = (enrollmentId, status) => {
        setAttendanceRecords(prev => ({
            ...prev,
            [enrollmentId]: {
                ...prev[enrollmentId],
                status
            }
        }));
    };

    const handleLateToggle = (enrollmentId, isLate) => {
        setAttendanceRecords(prev => ({
            ...prev,
            [enrollmentId]: {
                ...prev[enrollmentId],
                is_late: isLate,
                lateness_minutes: isLate ? 10 : 0
            }
        }));
    };

    const handleLatenessChange = (enrollmentId, minutes) => {
        setAttendanceRecords(prev => ({
            ...prev,
            [enrollmentId]: {
                ...prev[enrollmentId],
                lateness_minutes: parseInt(minutes) || 0
            }
        }));
    };

    const handleSave = async () => {
        setLoading(true);
        setMessage({ text: '', type: '' });
        try {
            const recordsList = Object.values(attendanceRecords);
            const res = await fetch('/api/academics/bulk-attendance/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    class_id: parseInt(selectedClass),
                    date,
                    records: recordsList
                })
            });

            const data = await res.json();
            if (res.ok) {
                setMessage({ text: data.detail || 'Attendance saved successfully!', type: 'success' });
            } else {
                setMessage({ text: data.detail || 'Failed to save attendance.', type: 'error' });
            }
        } catch (err) {
            setMessage({ text: 'Server connection error. Please try again.', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    if (classesLoading) {
        return <div className="flex justify-center py-10"><span className="loader-blue"></span></div>;
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Daily Attendance Tracking</h2>
                <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Take class attendance, mark lates and absents for students</p>
            </div>

            {/* Selection Bar */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4 flex flex-col sm:flex-row gap-4 items-center justify-between">
                <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
                    <div className="flex flex-col">
                        <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Select Class</label>
                        <select
                            className="border border-gray-300 dark:border-gray-700 rounded-lg p-2 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-white text-sm w-full sm:w-48"
                            value={selectedClass}
                            onChange={(e) => setSelectedClass(e.target.value)}
                        >
                            <option value="">Choose Class...</option>
                            {classes.map((c) => (
                                <option key={c.id} value={c.id}>{c.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="flex flex-col">
                        <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Select Date</label>
                        <input
                            type="date"
                            className="border border-gray-300 dark:border-gray-700 rounded-lg p-2 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-white text-sm w-full sm:w-48"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                        />
                    </div>
                </div>

                {students.length > 0 && (
                    <button
                        onClick={handleSave}
                        disabled={loading}
                        className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-5 py-2.5 rounded-lg transition duration-200 text-sm font-semibold shadow-md w-full sm:w-auto"
                    >
                        <HiSave className="w-5 h-5" />
                        Save Attendance
                    </button>
                )}
            </div>

            {message.text && (
                <div className={`p-4 rounded-lg text-sm font-medium border-l-4 ${
                    message.type === 'success' 
                        ? 'bg-green-50 text-green-700 border-green-500' 
                        : 'bg-red-50 text-red-700 border-red-500'
                }`}>
                    {message.text}
                </div>
            )}

            {/* Attendance Sheet */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
                {loading && students.length === 0 ? (
                    <div className="flex justify-center py-10"><span className="loader-blue"></span></div>
                ) : students.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-300 text-xs font-semibold uppercase border-b border-gray-200 dark:border-gray-700">
                                    <th className="p-4">Student ID</th>
                                    <th className="p-4">Name</th>
                                    <th className="p-4">Lateness</th>
                                    <th className="p-4 text-center">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                {students.map((student) => {
                                    const record = attendanceRecords[student.id] || { status: 'Present', is_late: false, lateness_minutes: 0 };
                                    return (
                                        <tr key={student.id} className="hover:bg-gray-50 dark:hover:bg-gray-750 transition duration-150 text-sm">
                                            <td className="p-4 font-semibold text-gray-500">{student.student_name.split(' (')[1]?.replace(')', '') || `STUD0${student.id}`}</td>
                                            <td className="p-4 font-medium text-gray-800 dark:text-white">{student.student_name.split(' (')[0]}</td>
                                            <td className="p-4">
                                                <div className="flex items-center gap-3">
                                                    <label className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400 cursor-pointer">
                                                        <input
                                                            type="checkbox"
                                                            checked={record.is_late}
                                                            onChange={(e) => handleLateToggle(student.id, e.target.checked)}
                                                            className="rounded text-blue-500 focus:ring-blue-400 w-4 h-4"
                                                        />
                                                        Is Late
                                                    </label>
                                                    {record.is_late && (
                                                        <div className="flex items-center gap-1">
                                                            <input
                                                                type="number"
                                                                className="border border-gray-300 dark:border-gray-750 rounded p-1 w-16 text-center text-xs dark:bg-gray-900 text-gray-800 dark:text-white"
                                                                value={record.lateness_minutes}
                                                                min="1"
                                                                onChange={(e) => handleLatenessChange(student.id, e.target.value)}
                                                            />
                                                            <span className="text-xs text-gray-400 font-medium">mins</span>
                                                        </div>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="p-4">
                                                <div className="flex items-center justify-center gap-2">
                                                    <button
                                                        type="button"
                                                        onClick={() => handleStatusChange(student.id, 'Present')}
                                                        className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                                                            record.status === 'Present'
                                                                ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300 ring-2 ring-green-400'
                                                                : 'bg-gray-50 text-gray-400 dark:bg-gray-700 dark:text-gray-300 hover:bg-green-50 hover:text-green-600'
                                                        }`}
                                                    >
                                                        <HiCheckCircle className="w-4 h-4" />
                                                        Present
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => handleStatusChange(student.id, 'Absent')}
                                                        className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                                                            record.status === 'Absent'
                                                                ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300 ring-2 ring-red-400'
                                                                : 'bg-gray-50 text-gray-400 dark:bg-gray-700 dark:text-gray-300 hover:bg-red-50 hover:text-red-600'
                                                        }`}
                                                    >
                                                        <HiXCircle className="w-4 h-4" />
                                                        Absent
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => handleStatusChange(student.id, 'Excused')}
                                                        className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                                                            record.status === 'Excused'
                                                                ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300 ring-2 ring-yellow-400'
                                                                : 'bg-gray-50 text-gray-400 dark:bg-gray-700 dark:text-gray-300 hover:bg-yellow-50 hover:text-yellow-600'
                                                        }`}
                                                    >
                                                        <HiExclamationCircle className="w-4 h-4" />
                                                        Excused
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <p className="text-gray-500 text-center py-10">No students enrolled in this class.</p>
                )}
            </div>
        </div>
    );
}
