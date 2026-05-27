import React, { useState, useEffect } from 'react';
import { HiUser, HiAcademicCap, HiCalendar, HiChartBar, HiClipboardList } from 'react-icons/hi';

export default function MyChildrenDashboard() {
    const [children, setChildren] = useState([]);
    const [selectedChild, setSelectedChild] = useState(null);
    const [grades, setGrades] = useState([]);
    const [attendance, setAttendance] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadingDetails, setLoadingDetails] = useState(false);

    useEffect(() => {
        fetchChildren();
    }, []);

    const fetchChildren = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/accounts/children/');
            if (res.ok) {
                const data = await res.json();
                setChildren(data);
                if (data.length > 0) {
                    setSelectedChild(data[0]);
                    fetchChildDetails(data[0].user); // user is the user ID of the child
                }
            }
        } catch (err) {
            console.error('Error fetching children:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchChildDetails = async (studentUserId) => {
        setLoadingDetails(true);
        try {
            const [gradesRes, attendanceRes] = await Promise.all([
                fetch(`/api/academics/grades/?student_id=${studentUserId}`),
                fetch(`/api/academics/attendance/?student_id=${studentUserId}`)
            ]);

            if (gradesRes.ok) setGrades(await gradesRes.json());
            if (attendanceRes.ok) setAttendance(await attendanceRes.json());
        } catch (err) {
            console.error('Error fetching details:', err);
        } finally {
            setLoadingDetails(false);
        }
    };

    const handleChildSelect = (child) => {
        setSelectedChild(child);
        fetchChildDetails(child.user);
    };

    if (loading) {
        return <div className="flex justify-center py-16"><span className="loader-blue"></span></div>;
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Academic Progress Tracker</h2>
                <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Review profiles, grades, and attendance metrics for children</p>
            </div>

            {children.length > 0 ? (
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Left profile selection column */}
                    <div className="lg:col-span-1 space-y-4">
                        <h3 className="text-base font-bold text-gray-700 dark:text-gray-300">My Children</h3>
                        <div className="space-y-3">
                            {children.map(child => (
                                <button
                                    key={child.student_id}
                                    onClick={() => handleChildSelect(child)}
                                    className={`w-full text-left p-4 rounded-xl shadow-sm border transition flex flex-col ${
                                        selectedChild?.student_id === child.student_id
                                            ? 'bg-blue-600 border-blue-600 text-white'
                                            : 'bg-white dark:bg-gray-800 border-gray-150 dark:border-gray-700 text-gray-800 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                                    }`}
                                >
                                    <div className="flex items-center gap-2.5">
                                        <HiUser className="w-5 h-5" />
                                        <span className="font-bold text-sm">{child.full_name}</span>
                                    </div>
                                    <p className="text-xs mt-1.5 opacity-80">Classroom: {child.class_name || 'Not Enrolled'}</p>
                                    <p className="text-[10px] font-mono mt-1 opacity-70">ID: {child.student_id}</p>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Right details progress panel */}
                    <div className="lg:col-span-3 space-y-6">
                        {selectedChild && (
                            <>
                                {/* Profile metrics top cards */}
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                    <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 flex items-center gap-3">
                                        <div className="p-2.5 bg-blue-50 dark:bg-blue-950/20 text-blue-500 rounded-lg"><HiAcademicCap className="w-6 h-6" /></div>
                                        <div>
                                            <p className="text-xs text-gray-400">Current Classroom</p>
                                            <p className="text-base font-bold text-gray-800 dark:text-white">{selectedChild.class_name || 'Not Enrolled'}</p>
                                        </div>
                                    </div>
                                    <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 flex items-center gap-3">
                                        <div className="p-2.5 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-500 rounded-lg"><HiCalendar className="w-6 h-6" /></div>
                                        <div>
                                            <p className="text-xs text-gray-400">Attendance Rate</p>
                                            <p className="text-base font-bold text-gray-800 dark:text-white">{selectedChild.attendance_rate || '100'}%</p>
                                        </div>
                                    </div>
                                    <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 flex items-center gap-3">
                                        <div className="p-2.5 bg-indigo-50 dark:bg-indigo-950/20 text-indigo-500 rounded-lg"><HiChartBar className="w-6 h-6" /></div>
                                        <div>
                                            <p className="text-xs text-gray-400">Cumulative GPA</p>
                                            <p className="text-base font-bold text-gray-800 dark:text-white">{selectedChild.gpa || 'N/A'}</p>
                                        </div>
                                    </div>
                                </div>

                                {loadingDetails ? (
                                    <div className="flex justify-center py-10"><span className="loader-blue"></span></div>
                                ) : (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {/* Grades list */}
                                        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border dark:border-gray-700 space-y-4">
                                            <h3 className="text-base font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                                                <HiChartBar className="text-blue-500 w-5 h-5" /> Recent Assignment Marks
                                            </h3>
                                            {grades.length > 0 ? (
                                                <div className="divide-y dark:divide-gray-750">
                                                    {grades.map(grade => (
                                                        <div key={grade.id} className="py-3 flex justify-between items-center text-sm">
                                                            <div>
                                                                <h4 className="font-semibold text-gray-800 dark:text-white">{grade.assignment_name || 'Assignment Task'}</h4>
                                                                <p className="text-xs text-gray-400 mt-0.5">Recorded: {grade.date_recorded}</p>
                                                            </div>
                                                            <span className="font-bold text-indigo-650 bg-indigo-50 dark:bg-indigo-950/30 px-3 py-1 rounded text-xs">
                                                                Score: {parseFloat(grade.score)}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <p className="text-xs text-gray-400 italic">No grading marks posted yet.</p>
                                            )}
                                        </div>

                                        {/* Attendance history */}
                                        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border dark:border-gray-700 space-y-4">
                                            <h3 className="text-base font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                                                <HiClipboardList className="text-emerald-500 w-5 h-5" /> Daily Attendance Logs
                                            </h3>
                                            {attendance.length > 0 ? (
                                                <div className="divide-y dark:divide-gray-750">
                                                    {attendance.map(att => (
                                                        <div key={att.id} className="py-3 flex justify-between items-center text-sm">
                                                            <div>
                                                                <h4 className="font-semibold text-gray-855 dark:text-white">{att.date}</h4>
                                                                {att.is_late && <p className="text-[10px] text-red-500 font-bold">Late by {att.lateness_minutes} mins</p>}
                                                            </div>
                                                            <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                                                                att.status === 'Present'
                                                                    ? 'bg-green-100 text-green-800'
                                                                    : att.status === 'Excused'
                                                                    ? 'bg-blue-100 text-blue-800'
                                                                    : 'bg-red-100 text-red-800'
                                                            }`}>
                                                                {att.status}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <p className="text-xs text-gray-400 italic">No attendance marked yet.</p>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </div>
            ) : (
                <div className="text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-xl shadow border">
                    <span className="text-4xl mb-2 block">👨‍👩‍👧‍👦</span>
                    No linked child profiles found under this parent user.
                </div>
            )}
        </div>
    );
}
