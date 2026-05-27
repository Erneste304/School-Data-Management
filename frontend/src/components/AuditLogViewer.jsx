import React, { useState, useEffect } from 'react';
import { HiShieldCheck, HiSearch, HiRefresh, HiUser } from 'react-icons/hi';

export default function AuditLogViewer() {
    const [logs, setLogs] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [actionFilter, setActionFilter] = useState('');
    const [search, setSearch] = useState('');
    const [selectedLog, setSelectedLog] = useState(null);

    useEffect(() => {
        fetchLogs();
        fetchStats();
    }, [actionFilter]);

    const fetchLogs = async () => {
        setLoading(true);
        try {
            let url = '/api/audit/logs/';
            if (actionFilter) {
                url += `?action=${actionFilter}`;
            }
            const res = await fetch(url);
            if (res.ok) {
                setLogs(await res.json());
            }
        } catch (err) {
            console.error('Error fetching audit logs:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const res = await fetch('/api/audit/stats/');
            if (res.ok) {
                setStats(await res.json());
            }
        } catch (err) {
            console.error('Error fetching audit stats:', err);
        }
    };

    const getActionBadgeColor = (action) => {
        const colors = {
            create: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
            update: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
            delete: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
            login: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
            logout: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
        };
        return colors[action] || 'bg-gray-100 text-gray-800';
    };

    const filteredLogs = logs.filter(log => {
        if (!search) return true;
        const q = search.toLowerCase();
        return (
            log.username?.toLowerCase().includes(q) ||
            log.model_name?.toLowerCase().includes(q) ||
            log.description?.toLowerCase().includes(q) ||
            log.object_repr?.toLowerCase().includes(q)
        );
    });

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <HiShieldCheck className="w-7 h-7 text-indigo-650" />
                        System Audit Logs
                    </h2>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
                        Track model creations, edits, deletions, security logins and user operations
                    </p>
                </div>
                <button
                    onClick={() => { fetchLogs(); fetchStats(); }}
                    className="flex items-center gap-1 bg-gray-100 hover:bg-gray-255 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                >
                    <HiRefresh className="w-5 h-5" />
                    Refresh Logs
                </button>
            </div>

            {/* Audit Statistics Dashboard */}
            {stats && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow border dark:border-gray-700">
                        <p className="text-xs text-gray-500 uppercase font-semibold">Total Logged Changes</p>
                        <p className="text-2xl font-bold text-gray-800 dark:text-white mt-1">{stats.total_logs}</p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow border dark:border-gray-700">
                        <p className="text-xs text-gray-500 uppercase font-semibold">Actions (Last 24 Hours)</p>
                        <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">{stats.logs_24h}</p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow border dark:border-gray-700">
                        <p className="text-xs text-gray-500 uppercase font-semibold">Create / Update / Delete splits</p>
                        <div className="flex gap-4 text-xs font-semibold mt-2">
                            <span className="text-green-600">Creates: {stats.actions_by_type?.create || 0}</span>
                            <span className="text-blue-655">Updates: {stats.actions_by_type?.update || 0}</span>
                            <span className="text-red-600">Deletes: {stats.actions_by_type?.delete || 0}</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Search & Filters */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4 flex flex-col sm:flex-row gap-4 items-center">
                <div className="flex items-center gap-2 w-full sm:w-64 bg-gray-50 dark:bg-gray-900 rounded-lg px-3 py-2 border dark:border-gray-700">
                    <HiSearch className="text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Search logs by user, model or description..."
                        className="bg-transparent outline-none text-sm w-full text-gray-800 dark:text-white"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>

                <select
                    className="border border-gray-300 dark:border-gray-700 rounded-lg p-2 bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-white text-sm"
                    value={actionFilter}
                    onChange={(e) => setActionFilter(e.target.value)}
                >
                    <option value="">All Actions</option>
                    <option value="create">Create</option>
                    <option value="update">Update</option>
                    <option value="delete">Delete</option>
                    <option value="login">Login</option>
                    <option value="logout">Logout</option>
                </select>
            </div>

            {/* Audit Logs Table */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
                {loading ? (
                    <div className="flex justify-center py-10"><span className="loader-blue"></span></div>
                ) : filteredLogs.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-300 text-xs font-semibold uppercase border-b border-gray-200 dark:border-gray-700">
                                    <th className="p-4">Time</th>
                                    <th className="p-4">Actor</th>
                                    <th className="p-4">Action</th>
                                    <th className="p-4">Entity</th>
                                    <th className="p-4">Details</th>
                                    <th className="p-4">IP Address</th>
                                    <th className="p-4">Changes</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                {filteredLogs.map((log) => (
                                    <tr key={log.id} className="hover:bg-gray-50 dark:hover:bg-gray-755 transition text-sm">
                                        <td className="p-4 text-gray-500 dark:text-gray-400">
                                            {new Date(log.timestamp).toLocaleString()}
                                        </td>
                                        <td className="p-4 font-semibold text-gray-800 dark:text-white flex items-center gap-1.5">
                                            <HiUser className="text-gray-400 w-4 h-4" />
                                            {log.username}
                                        </td>
                                        <td className="p-4">
                                            <span className={`px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${getActionBadgeColor(log.action)}`}>
                                                {log.action_display}
                                            </span>
                                        </td>
                                        <td className="p-4 text-gray-500 font-mono text-xs">{log.app_name}.{log.model_name}</td>
                                        <td className="p-4 text-gray-800 dark:text-white font-medium">{log.description || log.object_repr}</td>
                                        <td className="p-4 text-gray-400 font-mono text-xs">{log.user_ip}</td>
                                        <td className="p-4">
                                            {log.changes && Object.keys(log.changes).length > 0 ? (
                                                <button
                                                    onClick={() => setSelectedLog(log)}
                                                    className="text-indigo-600 hover:text-indigo-800 text-xs font-bold underline"
                                                >
                                                    View Diff ({Object.keys(log.changes).length})
                                                </button>
                                            ) : (
                                                <span className="text-gray-400 italic text-xs">No Diff</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="text-center py-12 text-gray-500">
                        <span className="text-4xl mb-2 block">📋</span>
                        No audit records found.
                    </div>
                )}
            </div>

            {/* Changes Inspector Modal */}
            {selectedLog && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full p-6 space-y-4 max-h-[85vh] overflow-y-auto">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Audit Change Log Inspector</h3>
                            <button onClick={() => setSelectedLog(null)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs text-gray-500 bg-gray-50 dark:bg-gray-900 p-3 rounded">
                            <p>Actor: <span className="font-bold text-gray-700 dark:text-white">{selectedLog.username}</span></p>
                            <p>Time: <span className="font-bold text-gray-700 dark:text-white">{new Date(selectedLog.timestamp).toLocaleString()}</span></p>
                            <p>Model: <span className="font-bold text-gray-700 dark:text-white">{selectedLog.app_name}.{selectedLog.model_name}</span></p>
                            <p>Rep: <span className="font-bold text-gray-700 dark:text-white">{selectedLog.object_repr}</span></p>
                        </div>

                        <div className="space-y-3">
                            <h4 className="text-sm font-bold text-gray-700 dark:text-gray-300">Modifications Field-by-Field:</h4>
                            <div className="border rounded dark:border-gray-750 divide-y divide-gray-150 dark:divide-gray-700 text-xs font-mono">
                                {Object.entries(selectedLog.changes).map(([field, delta]) => (
                                    <div key={field} className="p-3 grid grid-cols-3 gap-2 hover:bg-gray-50 dark:hover:bg-gray-900">
                                        <div className="font-bold text-indigo-600 dark:text-indigo-400 capitalize truncate">{field}</div>
                                        <div className="text-red-600 bg-red-50 dark:bg-red-950/20 p-1.5 rounded line-through overflow-x-auto">
                                            {JSON.stringify(delta.old)}
                                        </div>
                                        <div className="text-green-600 bg-green-50 dark:bg-green-950/20 p-1.5 rounded overflow-x-auto">
                                            {JSON.stringify(delta.new)}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="flex justify-end pt-2 border-t dark:border-gray-700">
                            <button
                                onClick={() => setSelectedLog(null)}
                                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-655 text-gray-800 dark:text-white rounded text-sm font-semibold"
                            >
                                Close Inspector
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
