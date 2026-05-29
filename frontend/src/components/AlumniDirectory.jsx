import React, { useState, useEffect } from 'react';
import { HiUsers, HiAcademicCap, HiSearch, HiBriefcase, HiCalendar, HiLink, HiMail, HiBadgeCheck } from 'react-icons/hi';

export default function AlumniDirectory() {
    const [profiles, setProfiles] = useState([]);
    const [events, setEvents] = useState([]);
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [activeTab, setActiveTab] = useState('directory'); // directory, events, jobs
    const [filterMentor, setFilterMentor] = useState(false);

    useEffect(() => {
        fetchDirectory();
        fetchEvents();
        fetchJobs();
    }, []);

    const fetchDirectory = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/alumni/profiles/');
            if (res.ok) {
                setProfiles(await res.json());
            }
        } catch (err) {
            console.error('Error fetching alumni directory:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchEvents = async () => {
        try {
            const res = await fetch('/api/alumni/events/');
            if (res.ok) {
                setEvents(await res.json());
            }
        } catch (err) {
            console.error('Error fetching alumni events:', err);
        }
    };

    const fetchJobs = async () => {
        try {
            const res = await fetch('/api/alumni/jobs/');
            if (res.ok) {
                setJobs(await res.json());
            }
        } catch (err) {
            console.error('Error fetching jobs:', err);
        }
    };

    const filteredProfiles = profiles.filter(p => {
        const matchesSearch = p.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            p.graduation_class?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            p.graduation_year?.toString().includes(searchQuery);
        const matchesMentor = filterMentor ? p.is_willing_to_mentor : true;
        return matchesSearch && matchesMentor;
    });

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                    <HiAcademicCap className="w-7 h-7 text-indigo-650" />
                    Alumni Portal
                </h2>
                <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Connect with graduates, find mentorships, or check out career opportunities</p>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-700">
                <button
                    onClick={() => setActiveTab('directory')}
                    className={`pb-3 px-4 text-sm font-semibold border-b-2 transition ${activeTab === 'directory'
                            ? 'border-indigo-650 text-indigo-600 dark:text-indigo-400'
                            : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                >
                    Alumni Directory
                </button>
                <button
                    onClick={() => setActiveTab('events')}
                    className={`pb-3 px-4 text-sm font-semibold border-b-2 transition ${activeTab === 'events'
                            ? 'border-indigo-650 text-indigo-600 dark:text-indigo-400'
                            : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                >
                    Networking Events
                </button>
                <button
                    onClick={() => setActiveTab('jobs')}
                    className={`pb-3 px-4 text-sm font-semibold border-b-2 transition ${activeTab === 'jobs'
                            ? 'border-indigo-650 text-indigo-600 dark:text-indigo-400'
                            : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                >
                    Job Opportunities
                </button>
            </div>

            {/* Tab Contents */}
            {activeTab === 'directory' && (
                <div className="space-y-6 animate-fadeIn">
                    {/* Filters */}
                    <div className="flex flex-col sm:flex-row gap-3 bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
                        <div className="flex-1 flex items-center gap-2 bg-gray-50 dark:bg-gray-900 rounded-lg px-3 py-2 border dark:border-gray-700 text-sm">
                            <HiSearch className="text-gray-400 w-5 h-5" />
                            <input
                                type="text"
                                placeholder="Search by name, class, year..."
                                className="bg-transparent outline-none w-full text-gray-800 dark:text-white"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                id="mentorFilter"
                                checked={filterMentor}
                                onChange={(e) => setFilterMentor(e.target.checked)}
                                className="rounded text-indigo-600 focus:ring-indigo-500"
                            />
                            <label htmlFor="mentorFilter" className="text-sm font-medium text-gray-600 dark:text-gray-300">
                                Open to Mentor
                            </label>
                        </div>
                    </div>

                    {loading ? (
                        <div className="flex justify-center py-12"><span className="loader-blue"></span></div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {filteredProfiles.length > 0 ? (
                                filteredProfiles.map(p => (
                                    <div key={p.id} className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 flex flex-col justify-between hover:shadow-md transition">
                                        <div>
                                            <div className="flex justify-between items-start">
                                                <div className="w-12 h-12 rounded-full bg-indigo-50 text-indigo-650 flex items-center justify-center font-bold text-lg">
                                                    {p.full_name?.[0]}
                                                </div>
                                                {p.is_willing_to_mentor && (
                                                    <span className="bg-indigo-100 text-indigo-850 dark:bg-indigo-950/30 dark:text-indigo-300 text-[10px] font-bold px-2 py-0.5 rounded flex items-center gap-1">
                                                        <HiBadgeCheck className="w-3.5 h-3.5 text-indigo-600" />
                                                        Mentor
                                                    </span>
                                                )}
                                            </div>
                                            <h3 className="font-bold text-gray-800 dark:text-white mt-3 text-lg leading-snug">{p.full_name}</h3>
                                            <p className="text-xs text-indigo-600 dark:text-indigo-400 font-semibold mt-0.5">
                                                Class of {p.graduation_year} • {p.graduation_class}
                                            </p>
                                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 line-clamp-3">
                                                {p.bio || 'No profile biography provided.'}
                                            </p>
                                        </div>
                                        <div className="mt-4 pt-4 border-t dark:border-gray-755 space-y-3">
                                            {p.current_occupation && (
                                                <div className="text-xs text-gray-500 dark:text-gray-400">
                                                    <span className="font-semibold text-gray-700 dark:text-gray-300">Current Role:</span> {p.current_occupation} at {p.current_employer || 'Self'}
                                                </div>
                                            )}
                                            {p.linkedin_profile && (
                                                <a
                                                    href={p.linkedin_profile}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="w-full flex items-center justify-center gap-1.5 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 dark:bg-indigo-950/30 dark:text-indigo-300 rounded-lg text-xs font-bold transition"
                                                >
                                                    <HiLink className="w-4 h-4" /> Linkedin Profile
                                                </a>
                                            )}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="col-span-full text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700">
                                    <span className="text-4xl mb-2 block">🎓</span> No alumni matches found.
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'events' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fadeIn">
                    {events.length > 0 ? (
                        events.map(ev => (
                            <div key={ev.id} className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 flex gap-4">
                                <div className="p-3 bg-indigo-50 dark:bg-indigo-950/30 rounded-xl flex items-center justify-center self-start text-indigo-650">
                                    <HiCalendar className="w-7 h-7" />
                                </div>
                                <div className="flex-1 space-y-2">
                                    <div>
                                        <span className="bg-indigo-100 text-indigo-805 text-[10px] font-bold px-2 py-0.5 rounded capitalize">
                                            {ev.event_type}
                                        </span>
                                        <h3 className="font-bold text-gray-850 dark:text-white mt-1 text-base">{ev.title}</h3>
                                        <p className="text-xs text-gray-400 mt-0.5">{ev.location} • {new Date(ev.event_date).toLocaleString()}</p>
                                    </div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">{ev.description}</p>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="col-span-full text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-xl shadow-sm">
                            <span className="text-4xl mb-2 block">📅</span> No networking events scheduled.
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'jobs' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fadeIn">
                    {jobs.length > 0 ? (
                        jobs.map(jb => (
                            <div key={jb.id} className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 flex gap-4">
                                <div className="p-3 bg-emerald-50 dark:bg-emerald-950/30 rounded-xl flex items-center justify-center self-start text-emerald-600">
                                    <HiBriefcase className="w-7 h-7" />
                                </div>
                                <div className="flex-1 space-y-2">
                                    <div>
                                        <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded">
                                            {jb.job_type}
                                        </span>
                                        <h3 className="font-bold text-gray-850 dark:text-white mt-1 text-base">{jb.title}</h3>
                                        <p className="text-xs text-gray-400 mt-0.5">{jb.company} • {jb.location}</p>
                                    </div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">{jb.description}</p>
                                    {jb.application_link && (
                                        <a
                                            href={jb.application_link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:underline font-semibold"
                                        >
                                            Apply Link <HiLink className="w-3.5 h-3.5" />
                                        </a>
                                    )}
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="col-span-full text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-xl shadow-sm">
                            <span className="text-4xl mb-2 block">💼</span> No job listings posted.
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
