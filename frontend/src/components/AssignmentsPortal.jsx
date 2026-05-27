import React, { useState, useEffect } from 'react';
import { HiPlusCircle, HiClipboardList, HiPaperAirplane, HiCheckCircle, HiCalendar } from 'react-icons/hi';

export default function AssignmentsPortal() {
    const [userRole, setUserRole] = useState(localStorage.getItem('userRole') || 'student');
    const [assignments, setAssignments] = useState([]);
    const [submissions, setSubmissions] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [classes, setClasses] = useState([]);
    const [students, setStudents] = useState([]);
    const [selectedStudentEnrollment, setSelectedStudentEnrollment] = useState('');
    const [loading, setLoading] = useState(true);
    const [showAddAssignmentModal, setShowAddAssignmentModal] = useState(false);
    const [showSubmitModal, setShowSubmitModal] = useState(false);
    const [showSubmissionsPanel, setShowSubmissionsPanel] = useState(false);
    const [selectedAssignment, setSelectedAssignment] = useState(null);
    const [assignmentSubmissions, setAssignmentSubmissions] = useState([]);
    
    // Forms
    const [newAssignment, setNewAssignment] = useState({
        subject: '',
        title: '',
        description: '',
        due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] // default 7 days due
    });
    const [submissionContent, setSubmissionContent] = useState('');
    const [gradingInfo, setGradingInfo] = useState({ submissionId: '', grade: '' });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        fetchInitialData();
    }, [userRole]);

    const fetchInitialData = async () => {
        setLoading(true);
        try {
            // Fetch assignments
            const assignRes = await fetch('/api/academics/assignments/');
            if (assignRes.ok) {
                const assignData = await assignRes.json();
                setAssignments(assignData);
            }

            if (userRole === 'student' || userRole === 'parent') {
                // Fetch student submissions
                const subRes = await fetch('/api/academics/submissions/');
                if (subRes.ok) {
                    const subData = await subRes.json();
                    setSubmissions(subData);
                }

                // Fetch student profile to get enrollment ID
                const profileRes = await fetch('/api/academics/my-profile/');
                if (profileRes.ok) {
                    const profileData = await profileRes.json();
                    // Get enrollment by student's class
                    if (profileData.student) {
                        const enrollRes = await fetch(`/api/academics/enrollments/?student_id=${profileData.id}`);
                        if (enrollRes.ok) {
                            const enrollData = await enrollRes.json();
                            if (enrollData.length > 0) {
                                setSelectedStudentEnrollment(enrollData[0].id.toString());
                            }
                        }
                    }
                }
            } else {
                // Fetch subjects (for creating assignments)
                const subRes = await fetch('/api/academics/subjects/');
                if (subRes.ok) {
                    const subData = await subRes.json();
                    setSubjects(subData);
                    if (subData.length > 0) {
                        setNewAssignment(prev => ({ ...prev, subject: subData[0].id.toString() }));
                    }
                }
            }
        } catch (err) {
            console.error('Error fetching initial assignments data:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateAssignment = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        try {
            const res = await fetch('/api/academics/assignments/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    subject: parseInt(newAssignment.subject),
                    title: newAssignment.title,
                    description: newAssignment.description,
                    due_date: newAssignment.due_date
                })
            });

            if (res.ok) {
                setSuccess('Assignment posted successfully!');
                setShowAddAssignmentModal(false);
                setNewAssignment({
                    subject: subjects.length > 0 ? subjects[0].id.toString() : '',
                    title: '',
                    description: '',
                    due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
                });
                fetchInitialData();
            } else {
                const data = await res.json();
                setError(data.detail || 'Failed to create assignment.');
            }
        } catch (err) {
            setError('Server connection error. Please try again.');
        }
    };

    const handleOpenSubmitModal = (assignment) => {
        setSelectedAssignment(assignment);
        setSubmissionContent('');
        setError('');
        setSuccess('');
        setShowSubmitModal(true);
    };

    const handleSubmitHomework = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        if (!selectedStudentEnrollment) {
            setError('Student enrollment record not found. Cannot submit homework.');
            return;
        }

        try {
            const res = await fetch('/api/academics/submissions/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    assignment: selectedAssignment.id,
                    enrollment: parseInt(selectedStudentEnrollment),
                    content: submissionContent
                })
            });

            if (res.ok) {
                setSuccess('Homework submitted successfully!');
                setShowSubmitModal(false);
                fetchInitialData();
            } else {
                const data = await res.json();
                setError(data.detail || 'Failed to submit homework.');
            }
        } catch (err) {
            setError('Server connection error. Please try again.');
        }
    };

    const handleViewSubmissions = async (assignment) => {
        setSelectedAssignment(assignment);
        setLoading(true);
        setShowSubmissionsPanel(true);
        setError('');
        setSuccess('');
        try {
            const res = await fetch(`/api/academics/submissions/?assignment_id=${assignment.id}`);
            if (res.ok) {
                const data = await res.json();
                setAssignmentSubmissions(data);
            }
        } catch (err) {
            console.error('Error fetching submissions for assignment:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleGradeSubmission = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        try {
            const res = await fetch(`/api/academics/submissions/${gradingInfo.submissionId}/`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    grade: parseFloat(gradingInfo.grade)
                })
            });

            if (res.ok) {
                setSuccess('Grade saved successfully!');
                // Auto post a copy into our Grades ledger table so it updates GPA
                const subObj = assignmentSubmissions.find(s => s.id.toString() === gradingInfo.submissionId);
                if (subObj) {
                    await fetch('/api/academics/grades/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            enrollment: subObj.enrollment,
                            assignment_name: `Assignment: ${selectedAssignment.title}`,
                            score: parseFloat(gradingInfo.grade)
                        })
                    });
                }
                
                setGradingInfo({ submissionId: '', grade: '' });
                handleViewSubmissions(selectedAssignment);
            } else {
                const data = await res.json();
                setError(data.detail || 'Failed to publish grade.');
            }
        } catch (err) {
            setError('Server connection error. Please try again.');
        }
    };

    // Helper to find student submission for an assignment
    const getSubmissionForAssignment = (assignId) => {
        return submissions.find(s => s.assignment === assignId);
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Assignments & Homework</h2>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
                        {userRole === 'student' || userRole === 'parent'
                            ? 'Complete homework, view deadlines, and check submission feedback'
                            : 'Post student homework assignments, inspect submissions, and publish grades'}
                    </p>
                </div>
                {(userRole === 'teacher' || userRole === 'admin') && !showSubmissionsPanel && (
                    <button
                        onClick={() => setShowAddAssignmentModal(true)}
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200 text-sm font-semibold shadow-md self-start sm:self-center"
                    >
                        <HiPlusCircle className="w-5 h-5" />
                        Create Assignment
                    </button>
                )}
                {showSubmissionsPanel && (
                    <button
                        onClick={() => setShowSubmissionsPanel(false)}
                        className="bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-655 text-gray-800 dark:text-white px-4 py-2 rounded-lg text-sm font-semibold shadow"
                    >
                        ✕ Close Submissions
                    </button>
                )}
            </div>

            {success && <div className="p-4 bg-green-50 text-green-700 rounded-lg text-sm font-medium border-l-4 border-green-500">{success}</div>}
            {error && <div className="p-4 bg-red-50 text-red-700 rounded-lg text-sm font-medium border-l-4 border-red-500">{error}</div>}

            {/* Assignments View / Submissions Grid */}
            {!showSubmissionsPanel ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {loading ? (
                        <div className="col-span-2 flex justify-center py-10"><span className="loader-blue"></span></div>
                    ) : assignments.length > 0 ? (
                        assignments.map((assignment) => {
                            const studentSub = getSubmissionForAssignment(assignment.id);
                            return (
                                <div key={assignment.id} className="bg-white dark:bg-gray-800 rounded-xl shadow p-5 border border-gray-150 dark:border-gray-700 flex flex-col justify-between hover:shadow-md transition">
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between">
                                            <span className="px-3 py-1 bg-violet-100 text-violet-800 dark:bg-violet-900/30 dark:text-violet-300 rounded-full font-bold text-xs uppercase tracking-wide">
                                                {assignment.subject_name}
                                            </span>
                                            <span className="text-xs text-gray-400 font-semibold flex items-center gap-1">
                                                <HiCalendar className="w-4 h-4 text-blue-500" />
                                                Due: {assignment.due_date}
                                            </span>
                                        </div>

                                        <h3 className="text-lg font-bold text-gray-800 dark:text-white">{assignment.title}</h3>
                                        <p className="text-sm text-gray-500 dark:text-gray-400">{assignment.description}</p>
                                    </div>

                                    {/* Action Footers */}
                                    <div className="border-t dark:border-gray-700 mt-4 pt-3 flex items-center justify-between">
                                        {userRole === 'student' || userRole === 'parent' ? (
                                            studentSub ? (
                                                <div className="flex items-center gap-2 text-green-600 dark:text-green-400 font-semibold text-xs">
                                                    <HiCheckCircle className="w-5 h-5" />
                                                    <span>Submitted {studentSub.grade !== null && `• Grade: ${studentSub.grade}%`}</span>
                                                </div>
                                            ) : (
                                                <button
                                                    onClick={() => handleOpenSubmitModal(assignment)}
                                                    className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-xs font-semibold shadow"
                                                >
                                                    <HiPaperAirplane className="w-4 h-4 rotate-90" />
                                                    Submit Homework
                                                </button>
                                            )
                                        ) : (
                                            <button
                                                onClick={() => handleViewSubmissions(assignment)}
                                                className="flex items-center gap-1.5 bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg text-xs font-semibold shadow"
                                            >
                                                <HiClipboardList className="w-4 h-4" />
                                                Inspect Submissions
                                            </button>
                                        )}
                                    </div>
                                </div>
                            );
                        })
                    ) : (
                        <div className="col-span-2 text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-xl shadow">
                            <span className="text-4xl mb-2 block">📝</span>
                            No homework assignments posted yet.
                        </div>
                    )}
                </div>
            ) : (
                /* inspect Submissions Panel */
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 space-y-6">
                    <div>
                        <span className="text-xs font-bold bg-violet-100 text-violet-800 dark:bg-violet-900/30 dark:text-violet-300 px-3 py-1 rounded-full">{selectedAssignment.subject_name}</span>
                        <h3 className="text-xl font-bold text-gray-800 dark:text-white mt-2">{selectedAssignment.title}</h3>
                        <p className="text-gray-500 text-sm mt-1">{selectedAssignment.description}</p>
                    </div>

                    <div className="border-t dark:border-gray-700 pt-4 space-y-4">
                        <h4 className="text-md font-bold text-gray-700 dark:text-gray-300">Submitted Hand-Ins</h4>
                        {assignmentSubmissions.length > 0 ? (
                            <div className="space-y-4">
                                {assignmentSubmissions.map((sub) => (
                                    <div key={sub.id} className="border dark:border-gray-700 rounded-xl p-4 bg-gray-50 dark:bg-gray-900/50 space-y-3">
                                        <div className="flex items-center justify-between">
                                            <span className="font-semibold text-gray-800 dark:text-white text-sm">{sub.student_name}</span>
                                            <span className="text-xs text-gray-400">Date: {sub.submission_date}</span>
                                        </div>
                                        <div className="text-sm text-gray-600 dark:text-gray-400 p-3 bg-white dark:bg-gray-800 border dark:border-gray-750 rounded-lg whitespace-pre-wrap font-mono">
                                            {sub.content}
                                        </div>

                                        <div className="flex items-center justify-between border-t dark:border-gray-700 pt-2 text-xs">
                                            {sub.grade !== null ? (
                                                <span className="text-green-600 dark:text-green-400 font-bold">Graded: {sub.grade}%</span>
                                            ) : (
                                                <form onSubmit={handleGradeSubmission} className="flex items-center gap-3 w-full max-w-xs">
                                                    <input
                                                        type="number" required min="0" max="100" step="0.1"
                                                        placeholder="Score %"
                                                        className="border rounded p-1 w-20 text-center dark:bg-gray-800 text-gray-800 dark:text-white"
                                                        onChange={(e) => setGradingInfo({ submissionId: sub.id.toString(), grade: e.target.value })}
                                                    />
                                                    <button
                                                        type="submit"
                                                        onClick={() => setGradingInfo(prev => ({ ...prev, submissionId: sub.id.toString() }))}
                                                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded font-semibold text-xs transition"
                                                    >
                                                        Publish Score
                                                    </button>
                                                </form>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-sm text-gray-500 italic py-4">No submissions received for this assignment.</p>
                        )}
                    </div>
                </div>
            )}

            {/* Create Assignment Modal */}
            {showAddAssignmentModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Create Homework Assignment</h3>
                            <button onClick={() => setShowAddAssignmentModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        <form onSubmit={handleCreateAssignment} className="space-y-4">
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Subject Assignment</label>
                                <select
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newAssignment.subject}
                                    onChange={(e) => setNewAssignment({ ...newAssignment, subject: e.target.value })}
                                >
                                    {subjects.map((s) => (
                                        <option key={s.id} value={s.id}>{s.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Title</label>
                                <input
                                    type="text" required
                                    placeholder="e.g. Mechanical Waves Exercise"
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newAssignment.title}
                                    onChange={(e) => setNewAssignment({ ...newAssignment, title: e.target.value })}
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Description / Instructions</label>
                                <textarea
                                    required rows="4"
                                    placeholder="Provide detailed instructions and homework guidelines..."
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newAssignment.description}
                                    onChange={(e) => setNewAssignment({ ...newAssignment, description: e.target.value })}
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Due Date</label>
                                <input
                                    type="date" required
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newAssignment.due_date}
                                    onChange={(e) => setNewAssignment({ ...newAssignment, due_date: e.target.value })}
                                />
                            </div>
                            <div className="flex justify-end gap-3 pt-3 border-t dark:border-gray-700">
                                <button type="button" onClick={() => setShowAddAssignmentModal(false)} className="px-4 py-2 border rounded text-gray-500 text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition">Post Assignment</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Submit Homework Modal */}
            {showSubmitModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-lg w-full p-6 space-y-4">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Submit Homework</h3>
                            <button onClick={() => setShowSubmitModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        <div>
                            <span className="text-xs font-bold bg-blue-50 text-blue-700 px-3 py-1 rounded-full">{selectedAssignment.subject_name}</span>
                            <h4 className="font-bold text-md text-gray-800 dark:text-white mt-2">{selectedAssignment.title}</h4>
                            <p className="text-xs text-gray-500 mt-1">{selectedAssignment.description}</p>
                        </div>
                        <form onSubmit={handleSubmitHomework} className="space-y-4">
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Homework Content / Solutions</label>
                                <textarea
                                    required rows="6"
                                    placeholder="Type in your essay, answers, or solution summaries here..."
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm font-mono text-gray-800 dark:text-white"
                                    value={submissionContent}
                                    onChange={(e) => setSubmissionContent(e.target.value)}
                                />
                            </div>
                            <div className="flex justify-end gap-3 pt-3 border-t dark:border-gray-700">
                                <button type="button" onClick={() => setShowSubmitModal(false)} className="px-4 py-2 border rounded text-gray-500 text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition">Submit Solution</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
