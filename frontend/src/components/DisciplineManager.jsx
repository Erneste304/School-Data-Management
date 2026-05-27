import React, { useState, useEffect } from 'react';
import { HiShieldExclamation, HiPlusCircle, HiSearch, HiCheckCircle, HiChevronRight, HiCalendar } from 'react-icons/hi';

export default function DisciplineManager() {
    const [userRole, setUserRole] = useState(localStorage.getItem('userRole') || 'student');
    const [cases, setCases] = useState([]);
    const [categories, setCategories] = useState([]);
    const [summary, setSummary] = useState(null);
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddModal, setShowAddModal] = useState(false);
    const [showActionModal, setShowActionModal] = useState(false);
    const [selectedCase, setSelectedCase] = useState(null);
    const [search, setSearch] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    
    // Forms
    const [newCase, setNewCase] = useState({
        student: '',
        category: '',
        incident_date: new Date().toISOString().slice(0, 16),
        incident_location: '',
        description: ''
    });
    const [newAction, setNewAction] = useState({
        action_type: 'warning',
        description: '',
        due_date: ''
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        fetchData();
        if (userRole === 'admin' || userRole === 'dod') {
            fetchStudents();
        }
    }, [userRole, statusFilter]);

    const fetchData = async () => {
        setLoading(true);
        try {
            let casesUrl = '/api/discipline/cases/';
            if (statusFilter) {
                casesUrl += `?status=${statusFilter}`;
            }

            const [casesRes, categoriesRes, summaryRes] = await Promise.all([
                fetch(casesUrl),
                fetch('/api/discipline/categories/'),
                fetch('/api/discipline/summary/')
            ]);

            if (casesRes.ok) setCases(await casesRes.json());
            if (categoriesRes.ok) {
                const cats = await categoriesRes.json();
                setCategories(cats);
                if (cats.length > 0) {
                    setNewCase(prev => ({ ...prev, category: cats[0].id.toString() }));
                }
            }
            if (summaryRes.ok) setSummary(await summaryRes.json());
        } catch (err) {
            console.error('Error fetching discipline data:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchStudents = async () => {
        try {
            const res = await fetch('/api/academics/students/');
            if (res.ok) {
                const data = await res.json();
                setStudents(data);
                if (data.length > 0) {
                    setNewCase(prev => ({ ...prev, student: data[0].id.toString() }));
                }
            }
        } catch (err) {
            console.error('Error fetching students:', err);
        }
    };

    const handleReportCase = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        try {
            const res = await fetch('/api/discipline/cases/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student: parseInt(newCase.student),
                    category: parseInt(newCase.category),
                    incident_date: new Date(newCase.incident_date).toISOString(),
                    incident_location: newCase.incident_location,
                    description: newCase.description,
                    status: 'reported'
                })
            });

            if (res.ok) {
                setSuccess('Incident reported successfully!');
                setShowAddModal(false);
                setNewCase({
                    student: students.length > 0 ? students[0].id.toString() : '',
                    category: categories.length > 0 ? categories[0].id.toString() : '',
                    incident_date: new Date().toISOString().slice(0, 16),
                    incident_location: '',
                    description: ''
                });
                fetchData();
            } else {
                const data = await res.json();
                setError(data.detail || 'Failed to submit discipline case.');
            }
        } catch (err) {
            setError('Server connection error.');
        }
    };

    const handleAddAction = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        try {
            const res = await fetch('/api/discipline/actions/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    case: selectedCase.id,
                    action_type: newAction.action_type,
                    description: newAction.description,
                    due_date: newAction.due_date ? new Date(newAction.due_date).toISOString() : null
                })
            });

            if (res.ok) {
                // Update case status to resolved/under investigation
                await fetch(`/api/discipline/cases/${selectedCase.id}/`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: 'resolved' })
                });

                setSuccess('Action logged and case status updated!');
                setShowActionModal(false);
                setNewAction({ action_type: 'warning', description: '', due_date: '' });
                fetchData();
            } else {
                const data = await res.json();
                setError(data.detail || 'Failed to add discipline action.');
            }
        } catch (err) {
            setError('Server connection error.');
        }
    };

    const getStatusBadge = (status) => {
        const styles = {
            reported: 'bg-blue-100 text-blue-755 dark:bg-blue-900/30 dark:text-blue-300',
            investigating: 'bg-yellow-100 text-yellow-755 dark:bg-yellow-900/30 dark:text-yellow-300',
            resolved: 'bg-green-100 text-green-755 dark:bg-green-900/30 dark:text-green-300',
            appealed: 'bg-purple-100 text-purple-755 dark:bg-purple-900/30 dark:text-purple-300',
            closed: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
        };
        return styles[status] || styles.reported;
    };

    const filteredCases = cases.filter(c => {
        if (!search) return true;
        const q = search.toLowerCase();
        return (
            c.student_name?.toLowerCase().includes(q) ||
            c.case_number?.toLowerCase().includes(q) ||
            c.description?.toLowerCase().includes(q)
        );
    });

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Discipline Registry</h2>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
                        Track student behavioral reports, disciplinary hearings, and interventions
                    </p>
                </div>
                {(userRole === 'admin' || userRole === 'dod' || userRole === 'teacher') && (
                    <button
                        onClick={() => setShowAddModal(true)}
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200 text-sm font-semibold shadow-md self-start sm:self-center"
                    >
                        <HiPlusCircle className="w-5 h-5" />
                        Report Incident
                    </button>
                )}
            </div>

            {success && <div className="p-4 bg-green-50 text-green-700 rounded-lg text-sm font-medium border-l-4 border-green-500">{success}</div>}
            {error && <div className="p-4 bg-red-50 text-red-700 rounded-lg text-sm font-medium border-l-4 border-red-500">{error}</div>}

            {/* Discipline Summary Panel */}
            {summary && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow border border-gray-150 dark:border-gray-700 flex items-center gap-4">
                        <div className="p-3 bg-red-100 dark:bg-red-950 text-red-655 dark:text-red-300 rounded-xl">
                            <HiShieldExclamation className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-gray-500 dark:text-gray-400 text-xs">Total Incidents</p>
                            <p className="text-2xl font-bold text-gray-800 dark:text-white">{summary.total_cases}</p>
                        </div>
                    </div>

                    <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow border border-gray-150 dark:border-gray-700 flex items-center gap-4">
                        <div className="p-3 bg-yellow-100 dark:bg-yellow-950 text-yellow-655 dark:text-yellow-300 rounded-xl">
                            <HiCalendar className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-gray-500 dark:text-gray-400 text-xs">Under Investigation</p>
                            <p className="text-2xl font-bold text-gray-800 dark:text-white">{summary.open_cases}</p>
                        </div>
                    </div>

                    <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow border border-gray-150 dark:border-gray-700 flex items-center gap-4">
                        <div className="p-3 bg-green-100 dark:bg-green-950 text-green-655 dark:text-green-300 rounded-xl">
                            <HiCheckCircle className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-gray-500 dark:text-gray-400 text-xs">Resolved Cases</p>
                            <p className="text-2xl font-bold text-gray-800 dark:text-white">{summary.resolved_cases}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* List & Filters */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4 flex flex-col sm:flex-row gap-4 items-center">
                <div className="flex items-center gap-2 w-full sm:w-64 bg-gray-50 dark:bg-gray-900 rounded-lg px-3 py-2 border dark:border-gray-700">
                    <HiSearch className="text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Search incident logs..."
                        className="bg-transparent outline-none text-sm w-full text-gray-800 dark:text-white"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>

                <select
                    className="border border-gray-300 dark:border-gray-700 rounded-lg p-2 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-white text-sm"
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                >
                    <option value="">All Statuses</option>
                    <option value="reported">Reported</option>
                    <option value="investigating">Under Investigation</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                </select>
            </div>

            {/* Cases Table */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
                {loading ? (
                    <div className="flex justify-center py-10"><span className="loader-blue"></span></div>
                ) : filteredCases.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-300 text-xs font-semibold uppercase border-b border-gray-200 dark:border-gray-700">
                                    <th className="p-4">Case #</th>
                                    <th className="p-4">Student</th>
                                    <th className="p-4">Incident Category</th>
                                    <th className="p-4">Date & Time</th>
                                    <th className="p-4">Severity</th>
                                    <th className="p-4">Status</th>
                                    <th className="p-4">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                {filteredCases.map((c) => (
                                    <tr key={c.id} className="hover:bg-gray-50 dark:hover:bg-gray-755 transition text-sm">
                                        <td className="p-4 font-mono text-blue-600 font-semibold">{c.case_number}</td>
                                        <td className="p-4 font-semibold text-gray-800 dark:text-white">{c.student_name}</td>
                                        <td className="p-4 text-gray-500 dark:text-gray-400">{c.category_name}</td>
                                        <td className="p-4 text-gray-500 dark:text-gray-400">
                                            {new Date(c.incident_date).toLocaleString()}
                                        </td>
                                        <td className="p-4">
                                            <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                                                c.severity === 'Major' || c.severity === 'Critical'
                                                    ? 'bg-red-100 text-red-800'
                                                    : 'bg-blue-100 text-blue-800'
                                            }`}>
                                                {c.severity}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            <span className={`px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${getStatusBadge(c.status)}`}>
                                                {c.status_display}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            {(userRole === 'admin' || userRole === 'dod') && c.status !== 'closed' && (
                                                <button
                                                    onClick={() => { setSelectedCase(c); setShowActionModal(true); }}
                                                    className="flex items-center gap-0.5 text-blue-600 hover:text-blue-800 text-xs font-semibold"
                                                >
                                                    Add Intervention
                                                    <HiChevronRight className="w-4 h-4" />
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="text-center py-12 text-gray-500">
                        <span className="text-4xl mb-2 block">⚖️</span>
                        No discipline logs found.
                    </div>
                )}
            </div>

            {/* Report incident Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Report Discipline Incident</h3>
                            <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        <form onSubmit={handleReportCase} className="space-y-4">
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Select Student</label>
                                <select
                                    required
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newCase.student}
                                    onChange={(e) => setNewCase({ ...newCase, student: e.target.value })}
                                >
                                    {students.map((s) => (
                                        <option key={s.id} value={s.id}>{s.student_id} - {s.user_name}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Category</label>
                                <select
                                    required
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newCase.category}
                                    onChange={(e) => setNewCase({ ...newCase, category: e.target.value })}
                                >
                                    {categories.map((cat) => (
                                        <option key={cat.id} value={cat.id}>{cat.name} ({cat.severity_display})</option>
                                    ))}
                                </select>
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Incident Time</label>
                                <input
                                    type="datetime-local" required
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newCase.incident_date}
                                    onChange={(e) => setNewCase({ ...newCase, incident_date: e.target.value })}
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Location</label>
                                <input
                                    type="text" required placeholder="e.g. Playground, Classroom 10A"
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newCase.incident_location}
                                    onChange={(e) => setNewCase({ ...newCase, incident_location: e.target.value })}
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Incident Description</label>
                                <textarea
                                    required rows="3" placeholder="Provide event details..."
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newCase.description}
                                    onChange={(e) => setNewCase({ ...newCase, description: e.target.value })}
                                />
                            </div>
                            <div className="flex justify-end gap-3 pt-3 border-t dark:border-gray-700">
                                <button type="button" onClick={() => setShowAddModal(false)} className="px-4 py-2 border rounded text-gray-500 text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition">Submit Report</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Add action/disciplinary intervention Modal */}
            {showActionModal && selectedCase && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Record Disciplinary Intervention</h3>
                            <button onClick={() => setShowActionModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        <div className="text-sm">
                            <p className="text-gray-500">Case: <span className="font-bold text-gray-800 dark:text-white">{selectedCase.case_number}</span></p>
                            <p className="text-gray-500 font-semibold">{selectedCase.description}</p>
                        </div>
                        <form onSubmit={handleAddAction} className="space-y-4">
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Action Type</label>
                                <select
                                    required
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newAction.action_type}
                                    onChange={(e) => setNewAction({ ...newAction, action_type: e.target.value })}
                                >
                                    <option value="warning">Verbal Warning</option>
                                    <option value="written_warning">Written Warning</option>
                                    <option value="community_service">Community Service</option>
                                    <option value="suspension">Suspension</option>
                                    <option value="expulsion">Expulsion</option>
                                    <option value="counseling">Counseling Session</option>
                                    <option value="parent_meeting">Parent Meeting</option>
                                </select>
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Details & Remarks</label>
                                <textarea
                                    required rows="3" placeholder="Provide disciplinary action details..."
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newAction.description}
                                    onChange={(e) => setNewAction({ ...newAction, description: e.target.value })}
                                />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Due/Completion Date (Optional)</label>
                                <input
                                    type="date"
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newAction.due_date}
                                    onChange={(e) => setNewAction({ ...newAction, due_date: e.target.value })}
                                />
                            </div>
                            <div className="flex justify-end gap-3 pt-3 border-t dark:border-gray-700">
                                <button type="button" onClick={() => setShowActionModal(false)} className="px-4 py-2 border rounded text-gray-500 text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition">Log Intervention</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
