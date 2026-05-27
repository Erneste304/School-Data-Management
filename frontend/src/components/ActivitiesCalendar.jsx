import React, { useState, useEffect } from 'react';
import { HiCalendar, HiSpeakerphone, HiUserGroup, HiPlusCircle, HiClock, HiLocationMarker, HiFlag } from 'react-icons/hi';

export default function ActivitiesCalendar() {
    const [userRole, setUserRole] = useState(localStorage.getItem('userRole') || 'admin');
    const [events, setEvents] = useState([]);
    const [clubs, setClubs] = useState([]);
    const [announcements, setAnnouncements] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeSection, setActiveSection] = useState('events');
    const [showAddModal, setShowAddModal] = useState(false);
    const [eventForm, setEventForm] = useState({
        title: '', event_type: 'academic', description: '',
        start_date: '', end_date: '', venue: '', audience: 'public'
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [eventsRes, clubsRes, announcementsRes] = await Promise.all([
                fetch('/api/activities/events/'),
                fetch('/api/activities/clubs/'),
                fetch('/api/activities/announcements/')
            ]);

            if (eventsRes.ok) setEvents(await eventsRes.json());
            if (clubsRes.ok) setClubs(await clubsRes.json());
            if (announcementsRes.ok) setAnnouncements(await announcementsRes.json());
        } catch (err) {
            console.error('Error fetching activities data:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateEvent = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        try {
            const res = await fetch('/api/activities/events/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...eventForm,
                    start_date: new Date(eventForm.start_date).toISOString(),
                    end_date: new Date(eventForm.end_date).toISOString(),
                    is_published: true
                })
            });

            if (res.ok) {
                setSuccess('School event created successfully!');
                setShowAddModal(false);
                setEventForm({
                    title: '', event_type: 'academic', description: '',
                    start_date: '', end_date: '', venue: '', audience: 'public'
                });
                fetchData();
            } else {
                const data = await res.json();
                setError(data.detail || 'Failed to create event.');
            }
        } catch (err) {
            setError('Server connection error.');
        }
    };

    const getPriorityBadge = (prio) => {
        const styles = {
            urgent: 'bg-red-100 text-red-800 dark:bg-red-950/30 dark:text-red-300 font-bold',
            high: 'bg-orange-100 text-orange-800 dark:bg-orange-950/30 dark:text-orange-300 font-semibold',
            medium: 'bg-blue-100 text-blue-800 dark:bg-blue-950/30 dark:text-blue-300',
            low: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
        };
        return styles[prio] || styles.medium;
    };

    const getEventTypeColor = (type) => {
        const colors = {
            academic: 'border-l-4 border-blue-500',
            sports: 'border-l-4 border-emerald-500',
            cultural: 'border-l-4 border-amber-500',
            workshop: 'border-l-4 border-indigo-500',
            ceremony: 'border-l-4 border-purple-500',
        };
        return colors[type] || 'border-l-4 border-gray-400';
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Campus Activities & Calendar</h2>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Manage events, announcements, and school clubs</p>
                </div>
                {(userRole === 'admin' || userRole === 'head_teacher') && (
                    <button onClick={() => setShowAddModal(true)}
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200 text-sm font-semibold shadow-md self-start sm:self-center">
                        <HiPlusCircle className="w-5 h-5" /> Create Event
                    </button>
                )}
            </div>

            {success && <div className="p-4 bg-green-50 text-green-700 rounded-lg text-sm font-medium border-l-4 border-green-500">{success}</div>}
            {error && <div className="p-4 bg-red-50 text-red-700 rounded-lg text-sm font-medium border-l-4 border-red-500">{error}</div>}

            {/* Navigation Tabs */}
            <div className="flex gap-4 border-b dark:border-gray-700">
                <button onClick={() => setActiveSection('events')}
                    className={`pb-3 text-sm font-semibold flex items-center gap-2 transition border-b-2 ${
                        activeSection === 'events' ? 'border-blue-600 text-blue-650' : 'text-gray-500 hover:text-gray-700 border-transparent'
                    }`}>
                    <HiCalendar className="w-5 h-5" /> School Events ({events.length})
                </button>
                <button onClick={() => setActiveSection('announcements')}
                    className={`pb-3 text-sm font-semibold flex items-center gap-2 transition border-b-2 ${
                        activeSection === 'announcements' ? 'border-blue-600 text-blue-650' : 'text-gray-500 hover:text-gray-700 border-transparent'
                    }`}>
                    <HiSpeakerphone className="w-5 h-5" /> Announcements ({announcements.length})
                </button>
                <button onClick={() => setActiveSection('clubs')}
                    className={`pb-3 text-sm font-semibold flex items-center gap-2 transition border-b-2 ${
                        activeSection === 'clubs' ? 'border-blue-600 text-blue-650' : 'text-gray-500 hover:text-gray-700 border-transparent'
                    }`}>
                    <HiUserGroup className="w-5 h-5" /> Student Clubs ({clubs.length})
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center py-12"><span className="loader-blue"></span></div>
            ) : (
                <div className="grid grid-cols-1 gap-6">
                    {/* Events Grid */}
                    {activeSection === 'events' && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {events.length > 0 ? (
                                events.map(ev => (
                                    <div key={ev.id} className={`bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 flex flex-col justify-between hover:shadow-md transition ${getEventTypeColor(ev.event_type)}`}>
                                        <div>
                                            <span className="text-xs uppercase font-bold text-blue-600 dark:text-blue-400">{ev.event_type_display}</span>
                                            <h3 className="font-bold text-gray-800 dark:text-white mt-1 text-base leading-tight">{ev.title}</h3>
                                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 line-clamp-3">{ev.description}</p>
                                        </div>
                                        <div className="mt-4 pt-4 border-t dark:border-gray-700 space-y-2 text-xs text-gray-400">
                                            <div className="flex items-center gap-2">
                                                <HiClock className="w-4 h-4 text-gray-400" />
                                                <span>{new Date(ev.start_date).toLocaleString()}</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <HiLocationMarker className="w-4 h-4 text-gray-400" />
                                                <span className="truncate">{ev.venue}</span>
                                            </div>
                                            <div className="flex items-center justify-between mt-1 text-[10px] text-gray-500 uppercase font-semibold">
                                                <span>Audience: {ev.audience_display}</span>
                                                {ev.is_livestream && <span className="text-red-600 animate-pulse font-bold">● Live Stream</span>}
                                            </div>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="col-span-full text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-xl shadow-sm">
                                    <span className="text-4xl mb-2 block">📅</span> No events scheduled.
                                </div>
                            )}
                        </div>
                    )}

                    {/* Announcements Grid */}
                    {activeSection === 'announcements' && (
                        <div className="space-y-4">
                            {announcements.length > 0 ? (
                                announcements.map(an => (
                                    <div key={an.id} className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-150 dark:border-gray-700">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className={`px-2 py-0.5 rounded text-xs capitalize ${getPriorityBadge(an.priority)}`}>
                                                {an.priority_display} Priority
                                            </span>
                                            <span className="text-xs text-gray-400">{new Date(an.publish_date).toLocaleDateString()}</span>
                                        </div>
                                        <h3 className="font-bold text-gray-800 dark:text-white text-lg">{an.title}</h3>
                                        <p className="text-sm text-gray-600 dark:text-gray-300 mt-2 whitespace-pre-line">{an.content}</p>
                                        <div className="mt-4 pt-3 border-t dark:border-gray-750 flex items-center justify-between text-xs text-gray-400">
                                            <p>Audience: <span className="font-semibold capitalize">{an.audience}</span></p>
                                            <p>Posted by: <span className="font-semibold text-gray-700 dark:text-gray-305">{an.created_by_name || 'System'}</span></p>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-xl shadow-sm">
                                    <span className="text-4xl mb-2 block">📢</span> No announcements posted.
                                </div>
                            )}
                        </div>
                    )}

                    {/* Clubs Grid */}
                    {activeSection === 'clubs' && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {clubs.length > 0 ? (
                                clubs.map(club => (
                                    <div key={club.id} className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 flex flex-col justify-between hover:shadow-md transition">
                                        <div>
                                            <div className="flex items-center justify-between">
                                                <span className="text-xs font-bold text-indigo-600 uppercase bg-indigo-50 dark:bg-indigo-950/20 px-2.5 py-0.5 rounded">
                                                    {club.category}
                                                </span>
                                                {club.acronym && <span className="font-bold text-gray-400 text-xs">{club.acronym}</span>}
                                            </div>
                                            <h3 className="font-bold text-gray-800 dark:text-white mt-2 text-base">{club.name}</h3>
                                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 line-clamp-3">{club.description}</p>
                                        </div>
                                        <div className="mt-4 pt-4 border-t dark:border-gray-700 text-xs text-gray-400 space-y-1">
                                            <p>Patron: <span className="font-semibold text-gray-700 dark:text-gray-300">{club.patron_name}</span></p>
                                            <p>Meeting: <span className="font-semibold text-gray-700 dark:text-gray-300">{club.meeting_day || 'Weekly'}</span></p>
                                            {club.meeting_venue && <p>Venue: <span className="font-semibold text-gray-755 dark:text-gray-300">{club.meeting_venue}</span></p>}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="col-span-full text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-xl shadow-sm">
                                    <span className="text-4xl mb-2 block">🤝</span> No student clubs registered.
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Create Event Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Create School Event</h3>
                            <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        <form onSubmit={handleCreateEvent} className="space-y-3">
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Event Title</label>
                                <input type="text" required className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={eventForm.title} onChange={(e) => setEventForm({ ...eventForm, title: e.target.value })} />
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="flex flex-col">
                                    <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Event Type</label>
                                    <select className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                        value={eventForm.event_type} onChange={(e) => setEventForm({ ...eventForm, event_type: e.target.value })}>
                                        <option value="academic">Academic Event</option>
                                        <option value="sports">Sports Event</option>
                                        <option value="cultural">Cultural Event</option>
                                        <option value="workshop">Workshop</option>
                                        <option value="ceremony">Ceremony</option>
                                    </select>
                                </div>
                                <div className="flex flex-col">
                                    <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Audience</label>
                                    <select className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                        value={eventForm.audience} onChange={(e) => setEventForm({ ...eventForm, audience: e.target.value })}>
                                        <option value="public">Public</option>
                                        <option value="students">Students Only</option>
                                        <option value="staff">Staff Only</option>
                                        <option value="parents">Parents</option>
                                    </select>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="flex flex-col">
                                    <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Start Time</label>
                                    <input type="datetime-local" required className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                        value={eventForm.start_date} onChange={(e) => setEventForm({ ...eventForm, start_date: e.target.value })} />
                                </div>
                                <div className="flex flex-col">
                                    <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">End Time</label>
                                    <input type="datetime-local" required className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                        value={eventForm.end_date} onChange={(e) => setEventForm({ ...eventForm, end_date: e.target.value })} />
                                </div>
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Venue</label>
                                <input type="text" required className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={eventForm.venue} onChange={(e) => setEventForm({ ...eventForm, venue: e.target.value })} />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Description</label>
                                <textarea required rows="3" className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={eventForm.description} onChange={(e) => setEventForm({ ...eventForm, description: e.target.value })} />
                            </div>
                            <div className="flex justify-end gap-3 pt-3 border-t dark:border-gray-700">
                                <button type="button" onClick={() => setShowAddModal(false)} className="px-4 py-2 border rounded text-gray-500 text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition">Create Event</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
