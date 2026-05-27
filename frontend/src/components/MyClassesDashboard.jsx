import React, { useState, useEffect } from 'react';
import { HiAcademicCap, HiSearch, HiUsers, HiUser, HiChartBar, HiCheckCircle } from 'react-icons/hi';

export default function MyClassesDashboard() {
    const [classes, setClasses] = useState([]);
    const [selectedClass, setSelectedClass] = useState(null);
    const [students, setStudents] = useState([]);
    const [loadingClasses, setLoadingClasses] = useState(true);
    const [loadingStudents, setLoadingStudents] = useState(false);
    const [search, setSearch] = useState('');

    useEffect(() => {
        fetchClasses();
    }, []);

    const fetchClasses = async () => {
        setLoadingClasses(true);
        try {
            const res = await fetch('/api/academics/classes/');
            if (res.ok) {
                setClasses(await res.json());
            }
        } catch (err) {
            console.error('Error fetching classes:', err);
        } finally {
            setLoadingClasses(false);
        }
    };

    const fetchStudentsForClass = async (classId) => {
        setLoadingStudents(true);
        try {
            const res = await fetch(`/api/academics/students/?class_id=${classId}`);
            if (res.ok) {
                setStudents(await res.json());
            }
        } catch (err) {
            console.error('Error fetching class students:', err);
        } finally {
            setLoadingStudents(false);
        }
    };

    const handleClassClick = (cls) => {
        setSelectedClass(cls);
        fetchStudentsForClass(cls.id);
    };

    const filteredStudents = students.filter(s => {
        if (!search) return true;
        const q = search.toLowerCase();
        return (
            s.full_name?.toLowerCase().includes(q) ||
            s.student_id?.toLowerCase().includes(q)
        );
    });

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Classrooms & Rosters</h2>
                <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Manage classrooms, tutor assignments, and view student lists</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Class list (left col) */}
                <div className="lg:col-span-1 space-y-4">
                    <h3 className="text-base font-bold text-gray-700 dark:text-gray-300">Available Classrooms</h3>
                    {loadingClasses ? (
                        <div className="flex justify-center py-8"><span className="loader-blue"></span></div>
                    ) : classes.length > 0 ? (
                        <div className="space-y-3">
                            {classes.map(cls => (
                                <button
                                    key={cls.id}
                                    onClick={() => handleClassClick(cls)}
                                    className={`w-full text-left p-4 rounded-xl shadow-sm border transition flex flex-col justify-between ${
                                        selectedClass?.id === cls.id
                                            ? 'bg-blue-600 border-blue-600 text-white'
                                            : 'bg-white dark:bg-gray-800 border-gray-100 dark:border-gray-700 text-gray-855 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                                    }`}
                                >
                                    <div className="flex items-center gap-2.5">
                                        <HiAcademicCap className={`w-6 h-6 ${selectedClass?.id === cls.id ? 'text-white' : 'text-blue-500'}`} />
                                        <span className="font-bold text-base">{cls.name}</span>
                                    </div>
                                    <div className="mt-3 flex items-center justify-between text-xs opacity-80">
                                        <span className="truncate">Tutor: {cls.class_tutor_name || 'Unassigned'}</span>
                                        <span className="flex items-center gap-1"><HiUsers className="w-3.5 h-3.5" /> {cls.student_count} registered</span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-10 text-gray-500 bg-white dark:bg-gray-800 rounded-xl">No classes found.</div>
                    )}
                </div>

                {/* Students list (right col) */}
                <div className="lg:col-span-2 space-y-4">
                    {selectedClass ? (
                        <>
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                                <div>
                                    <h3 className="text-lg font-bold text-gray-800 dark:text-white">Roster: {selectedClass.name}</h3>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">Class Level: {selectedClass.level}</p>
                                </div>
                                <div className="flex items-center gap-2 bg-white dark:bg-gray-800 rounded-lg px-3 py-1.5 border dark:border-gray-700">
                                    <HiSearch className="text-gray-400 w-4 h-4" />
                                    <input
                                        type="text"
                                        placeholder="Search students..."
                                        className="bg-transparent outline-none text-xs w-full text-gray-800 dark:text-white"
                                        value={search}
                                        onChange={(e) => setSearch(e.target.value)}
                                    />
                                </div>
                            </div>

                            {loadingStudents ? (
                                <div className="flex justify-center py-12"><span className="loader-blue"></span></div>
                            ) : filteredStudents.length > 0 ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {filteredStudents.map(student => (
                                        <div key={student.student_id} className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-150 dark:border-gray-700 flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 flex items-center justify-center font-bold text-sm">
                                                    {student.full_name?.[0]}
                                                </div>
                                                <div>
                                                    <h4 className="font-bold text-sm text-gray-800 dark:text-white leading-tight">{student.full_name}</h4>
                                                    <p className="text-xs text-gray-400 font-mono mt-0.5">{student.student_id}</p>
                                                </div>
                                            </div>
                                            <div className="text-right space-y-1">
                                                <div className="flex items-center gap-1 justify-end text-xs font-semibold text-emerald-600">
                                                    <HiCheckCircle className="w-4 h-4" />
                                                    <span>{student.attendance_rate || '100'}% Att.</span>
                                                </div>
                                                <div className="flex items-center gap-1 justify-end text-xs font-semibold text-indigo-650">
                                                    <HiChartBar className="w-4 h-4" />
                                                    <span>GPA: {student.gpa || 'N/A'}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-xl border">
                                    No students enrolled in this classroom.
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-64 text-center bg-white dark:bg-gray-800 rounded-xl border dark:border-gray-700">
                            <span className="text-5xl mb-3">🏫</span>
                            <h3 className="font-bold text-gray-705 dark:text-gray-300">No Classroom Selected</h3>
                            <p className="text-xs text-gray-400 mt-1">Select a classroom from the list to view its active roster.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
