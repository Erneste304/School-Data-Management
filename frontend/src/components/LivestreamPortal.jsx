import React, { useState, useEffect } from 'react';
import { HiVideoCamera, HiPlusCircle, HiClock, HiUser, HiEye, HiVolumeUp } from 'react-icons/hi';

export default function LivestreamPortal() {
    const [streams, setStreams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [userRole, setUserRole] = useState(localStorage.getItem('userRole') || 'admin');
    const [form, setForm] = useState({
        title: '', description: '', scheduled_start: '',
        stream_url: '', is_public: true
    });
    const [activeStream, setActiveStream] = useState(null);

    useEffect(() => {
        fetchStreams();
    }, []);

    const fetchStreams = async () => {
        setLoading(true);
        try {
            const res = await fetch('/livestream/api/list/');
            if (res.ok) {
                setStreams(await res.json());
            }
        } catch (err) {
            console.error('Error fetching stream data:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateStream = async (e) => {
        e.preventDefault();
        try {
            const res = await fetch('/livestream/api/list/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...form,
                    status: 'scheduled',
                    scheduled_start: new Date(form.scheduled_start).toISOString()
                })
            });

            if (res.ok) {
                fetchStreams();
                setShowCreateModal(false);
                setForm({ title: '', description: '', scheduled_start: '', stream_url: '', is_public: true });
            }
        } catch (err) {
            console.error('Error creating stream session:', err);
        }
    };

    const getStatusBadgeColor = (status) => {
        const styles = {
            live: 'bg-red-100 text-red-800 dark:bg-red-950/30 dark:text-red-300 animate-pulse font-bold',
            scheduled: 'bg-blue-100 text-blue-800 dark:bg-blue-950/30 dark:text-blue-300',
            ended: 'bg-gray-105 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
        };
        return styles[status] || styles.scheduled;
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <HiVideoCamera className="w-7 h-7 text-red-500" />
                        Virtual Classrooms & Streams
                    </h2>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Join active broadcasts, assemblies, or schedule new video sessions</p>
                </div>
                {(userRole === 'admin' || userRole === 'head_teacher' || userRole === 'teacher') && (
                    <button onClick={() => setShowCreateModal(true)}
                        className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition duration-200 text-sm font-semibold shadow-md self-start sm:self-center">
                        <HiPlusCircle className="w-5 h-5" /> Schedule Broadcast
                    </button>
                )}
            </div>

            {activeStream && (
                <div className="bg-white dark:bg-gray-800 rounded-2xl shadow border dark:border-gray-700 p-4 space-y-4">
                    <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                        <div>
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">{activeStream.title}</h3>
                            <p className="text-xs text-gray-400">Streamed by {activeStream.created_by_name || 'Teacher'}</p>
                        </div>
                        <button onClick={() => setActiveStream(null)} className="text-xs text-red-600 font-bold hover:underline">
                            Close Player
                        </button>
                    </div>
                    {/* Simulated Player / Embed */}
                    <div className="aspect-video bg-black rounded-xl overflow-hidden flex items-center justify-center text-white relative">
                        {activeStream.stream_url ? (
                            <iframe
                                className="w-full h-full border-0"
                                src={activeStream.stream_url.replace("watch?v=", "embed/")}
                                title={activeStream.title}
                                allowFullScreen
                            />
                        ) : (
                            <div className="text-center space-y-2">
                                <span className="text-5xl block animate-pulse">🎥</span>
                                <p className="font-bold text-sm">Live Broadcast Feed Pending...</p>
                                <p className="text-xs text-gray-400">This scheduled session will start broadcasting shortly.</p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {loading ? (
                <div className="flex justify-center py-12"><span className="loader-blue"></span></div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {streams.length > 0 ? (
                        streams.map(str => (
                            <div key={str.id} className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 flex flex-col justify-between hover:shadow-md transition">
                                <div>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className={`px-2 py-0.5 rounded text-xs capitalize ${getStatusBadgeColor(str.status)}`}>
                                            {str.status_display}
                                        </span>
                                        <div className="flex items-center gap-1 text-xs text-gray-400">
                                            <HiEye className="w-4 h-4" />
                                            <span>{str.view_count || 0}</span>
                                        </div>
                                    </div>
                                    <h3 className="font-bold text-gray-800 dark:text-white mt-1 text-base leading-snug">{str.title}</h3>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 line-clamp-3">{str.description}</p>
                                </div>
                                <div className="mt-4 pt-4 border-t dark:border-gray-755 space-y-3">
                                    <div className="flex items-center justify-between text-xs text-gray-450 dark:text-gray-400">
                                        <span className="flex items-center gap-1"><HiClock className="w-4 h-4 text-blue-500" /> {new Date(str.scheduled_start).toLocaleString()}</span>
                                        <span className="flex items-center gap-1"><HiUser className="w-4 h-4 text-emerald-500" /> {str.created_by_name || 'Presenter'}</span>
                                    </div>
                                    <button
                                        onClick={() => setActiveStream(str)}
                                        className="w-full text-center py-2 bg-red-50 hover:bg-red-100 text-red-650 rounded-lg text-xs font-bold transition"
                                    >
                                        Watch Broadcast
                                    </button>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="col-span-full text-center py-12 text-gray-550 bg-white dark:bg-gray-800 rounded-xl shadow-sm">
                            <span className="text-4xl mb-2 block">📡</span> No active or scheduled virtual sessions.
                        </div>
                    )}
                </div>
            )}

            {/* Create Stream Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Schedule Stream Session</h3>
                            <button onClick={() => setShowCreateModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        <form onSubmit={handleCreateStream} className="space-y-3">
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Session Title</label>
                                <input type="text" required className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-855 dark:text-white"
                                    value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Broadcast Stream URL (YouTube, Vimeo, etc.)</label>
                                <input type="url" required placeholder="https://www.youtube.com/watch?v=..." className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={form.stream_url} onChange={(e) => setForm({ ...form, stream_url: e.target.value })} />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Scheduled Start Time</label>
                                <input type="datetime-local" required className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={form.scheduled_start} onChange={(e) => setForm({ ...form, scheduled_start: e.target.value })} />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Description / Syllabus</label>
                                <textarea required rows="3" className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
                            </div>
                            <div className="flex justify-end gap-3 pt-3 border-t dark:border-gray-700">
                                <button type="button" onClick={() => setShowCreateModal(false)} className="px-4 py-2 border rounded text-gray-500 text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-red-650 text-white rounded text-sm hover:bg-red-700 transition">Schedule Stream</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
