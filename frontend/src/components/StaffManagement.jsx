import React, { useState, useEffect } from 'react';
import { HiUsers, HiPlusCircle, HiSearch, HiMail, HiPhone } from 'react-icons/hi';

export default function StaffManagement() {
    const [staff, setStaff] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [roleFilter, setRoleFilter] = useState('');
    const [showAddModal, setShowAddModal] = useState(false);
    const [newStaff, setNewStaff] = useState({
        username: '', email: '', first_name: '', last_name: '',
        role: 'teacher', phone: '', password: '', password2: ''
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const STAFF_ROLES = [
        { value: '', label: 'All Roles' },
        { value: 'admin', label: 'Admin' },
        { value: 'head_teacher', label: 'Head Teacher' },
        { value: 'dos', label: 'Director of Studies' },
        { value: 'dod', label: 'Director of Discipline' },
        { value: 'teacher', label: 'Teacher' },
        { value: 'animateur', label: 'Animateur' },
        { value: 'animatrice', label: 'Animatrice' },
        { value: 'accountant', label: 'Accountant' },
    ];

    useEffect(() => {
        fetchStaff();
    }, [roleFilter]);

    const fetchStaff = async () => {
        setLoading(true);
        try {
            let url = '/api/accounts/users/';
            // Filter to staff roles only
            if (roleFilter) {
                url += `?role=${roleFilter}`;
            }
            const res = await fetch(url);
            if (res.ok) {
                let data = await res.json();
                // Only show staff members (not students/parents/public)
                if (!roleFilter) {
                    data = data.filter(u => 
                        !['student', 'parent', 'public'].includes(u.role)
                    );
                }
                setStaff(data);
            }
        } catch (err) {
            console.error('Error fetching staff:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleAddStaff = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        if (newStaff.password !== newStaff.password2) {
            setError('Passwords do not match.');
            return;
        }

        try {
            const res = await fetch('/api/accounts/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newStaff)
            });

            if (res.ok || res.status === 201) {
                setSuccess('Staff member registered successfully!');
                setShowAddModal(false);
                setNewStaff({
                    username: '', email: '', first_name: '', last_name: '',
                    role: 'teacher', phone: '', password: '', password2: ''
                });
                fetchStaff();
            } else {
                const data = await res.json();
                const errMsg = typeof data === 'object' 
                    ? Object.values(data).flat().join(' ') 
                    : data.detail || 'Registration failed.';
                setError(errMsg);
            }
        } catch (err) {
            setError('Server connection error.');
        }
    };

    const filteredStaff = staff.filter(s => {
        if (!search) return true;
        const q = search.toLowerCase();
        return (
            s.full_name?.toLowerCase().includes(q) ||
            s.username?.toLowerCase().includes(q) ||
            s.email?.toLowerCase().includes(q)
        );
    });

    const getRoleBadgeColor = (role) => {
        const colors = {
            admin: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
            head_teacher: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300',
            dos: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
            dod: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
            teacher: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300',
            animateur: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-300',
            animatrice: 'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-300',
            accountant: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
        };
        return colors[role] || 'bg-gray-100 text-gray-700';
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Staff Management</h2>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Manage teachers, administrators, and school personnel</p>
                </div>
                <button onClick={() => setShowAddModal(true)}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition text-sm font-semibold shadow-md self-start sm:self-center">
                    <HiPlusCircle className="w-5 h-5" /> Add Staff Member
                </button>
            </div>

            {success && <div className="p-4 bg-green-50 text-green-700 rounded-lg text-sm font-medium border-l-4 border-green-500">{success}</div>}
            {error && <div className="p-4 bg-red-50 text-red-700 rounded-lg text-sm font-medium border-l-4 border-red-500">{error}</div>}

            {/* Search & Filters */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4 flex flex-col sm:flex-row gap-4 items-center">
                <div className="flex items-center gap-2 w-full sm:w-64 bg-gray-50 dark:bg-gray-900 rounded-lg px-3 py-2 border dark:border-gray-700">
                    <HiSearch className="text-gray-400 w-5 h-5" />
                    <input type="text" placeholder="Search staff..." className="bg-transparent outline-none text-sm w-full text-gray-800 dark:text-white"
                        value={search} onChange={(e) => setSearch(e.target.value)} />
                </div>
                <select className="border dark:border-gray-700 rounded-lg p-2 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-white text-sm"
                    value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
                    {STAFF_ROLES.map(r => (
                        <option key={r.value} value={r.value}>{r.label}</option>
                    ))}
                </select>
                <div className="flex items-center gap-2 text-gray-500 text-sm ml-auto">
                    <HiUsers className="w-5 h-5" /> {filteredStaff.length} members
                </div>
            </div>

            {/* Staff Grid */}
            {loading ? (
                <div className="flex justify-center py-10"><span className="loader-blue"></span></div>
            ) : filteredStaff.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {filteredStaff.map((member) => (
                        <div key={member.id} className="bg-white dark:bg-gray-800 rounded-xl shadow p-5 border border-gray-100 dark:border-gray-700 hover:shadow-md transition">
                            <div className="flex items-start justify-between mb-3">
                                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow">
                                    {member.first_name?.[0]}{member.last_name?.[0]}
                                </div>
                                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${getRoleBadgeColor(member.role)}`}>
                                    {member.role_label}
                                </span>
                            </div>
                            <h3 className="font-bold text-gray-800 dark:text-white">{member.full_name}</h3>
                            <p className="text-xs text-gray-400 mb-3">@{member.username}</p>
                            <div className="space-y-1.5 text-sm text-gray-500">
                                <div className="flex items-center gap-2">
                                    <HiMail className="w-4 h-4 text-blue-500" />
                                    <span className="truncate">{member.email}</span>
                                </div>
                                {member.phone && (
                                    <div className="flex items-center gap-2">
                                        <HiPhone className="w-4 h-4 text-emerald-500" />
                                        <span>{member.phone}</span>
                                    </div>
                                )}
                            </div>
                            {member.profile && (
                                <div className="mt-3 pt-3 border-t dark:border-gray-700 text-xs text-gray-400 space-y-1">
                                    {member.profile.employee_id && <p>ID: <span className="font-mono text-blue-500">{member.profile.employee_id}</span></p>}
                                    {member.profile.department && <p>Dept: {member.profile.department}</p>}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            ) : (
                <div className="text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-xl shadow">
                    <span className="text-4xl mb-2 block">👥</span>
                    No staff members found.
                </div>
            )}

            {/* Add Staff Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-lg w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Register New Staff</h3>
                            <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        <form onSubmit={handleAddStaff} className="space-y-3">
                            <div className="grid grid-cols-2 gap-3">
                                <div className="flex flex-col">
                                    <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">First Name</label>
                                    <input type="text" required className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                        value={newStaff.first_name} onChange={(e) => setNewStaff({ ...newStaff, first_name: e.target.value })} />
                                </div>
                                <div className="flex flex-col">
                                    <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Last Name</label>
                                    <input type="text" required className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                        value={newStaff.last_name} onChange={(e) => setNewStaff({ ...newStaff, last_name: e.target.value })} />
                                </div>
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Username</label>
                                <input type="text" required className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newStaff.username} onChange={(e) => setNewStaff({ ...newStaff, username: e.target.value })} />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Email</label>
                                <input type="email" required className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={newStaff.email} onChange={(e) => setNewStaff({ ...newStaff, email: e.target.value })} />
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="flex flex-col">
                                    <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Role</label>
                                    <select className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                        value={newStaff.role} onChange={(e) => setNewStaff({ ...newStaff, role: e.target.value })}>
                                        {STAFF_ROLES.filter(r => r.value).map(r => (
                                            <option key={r.value} value={r.value}>{r.label}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="flex flex-col">
                                    <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Phone</label>
                                    <input type="text" className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                        value={newStaff.phone} onChange={(e) => setNewStaff({ ...newStaff, phone: e.target.value })} />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="flex flex-col">
                                    <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Password</label>
                                    <input type="password" required minLength={8} className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                        value={newStaff.password} onChange={(e) => setNewStaff({ ...newStaff, password: e.target.value })} />
                                </div>
                                <div className="flex flex-col">
                                    <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Confirm Password</label>
                                    <input type="password" required minLength={8} className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                        value={newStaff.password2} onChange={(e) => setNewStaff({ ...newStaff, password2: e.target.value })} />
                                </div>
                            </div>
                            <div className="flex justify-end gap-3 pt-3 border-t dark:border-gray-700">
                                <button type="button" onClick={() => setShowAddModal(false)} className="px-4 py-2 border rounded text-gray-500 text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition">Register Staff</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
