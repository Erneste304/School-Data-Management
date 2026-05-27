import React, { useState, useEffect } from 'react';
import { HiCalendar, HiClock, HiOfficeBuilding, HiUser } from 'react-icons/hi';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export default function ScheduleView() {
    const [schedule, setSchedule] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedDay, setSelectedDay] = useState(DAYS[new Date().getDay() - 1] || 'Monday');

    useEffect(() => {
        fetchSchedule();
    }, []);

    const fetchSchedule = async () => {
        try {
            const res = await fetch('/api/academics/my-schedule/');
            if (res.ok) {
                const data = await res.json();
                setSchedule(data);
            }
        } catch (err) {
            console.error('Error fetching personal schedule:', err);
        } finally {
            setLoading(false);
        }
    };

    // Filter schedule by active day
    const filteredSchedule = schedule.filter(item => item.day_of_week === selectedDay);

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Class Timetable & Schedule</h2>
                <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">View your classes, timings, teachers, and room numbers for the week</p>
            </div>

            {/* Day Selector */}
            <div className="flex flex-wrap gap-2 border-b border-gray-200 dark:border-gray-700 pb-3">
                {DAYS.map(day => (
                    <button
                        key={day}
                        onClick={() => setSelectedDay(day)}
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${
                            selectedDay === day
                                ? 'bg-blue-600 text-white shadow-md'
                                : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                        }`}
                    >
                        {day}
                    </button>
                ))}
            </div>

            {/* Timetable Contents */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
                {loading ? (
                    <div className="flex justify-center py-10"><span className="loader-blue"></span></div>
                ) : filteredSchedule.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {filteredSchedule.map((item, index) => (
                            <div key={item.id || index} className="border border-gray-150 dark:border-gray-700 rounded-xl p-5 bg-gradient-to-r from-gray-50 to-white dark:from-gray-750 dark:to-gray-800 flex flex-col justify-between hover:shadow-md transition">
                                <div className="space-y-3">
                                    <div className="flex items-center justify-between">
                                        <span className="px-3 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded-full font-bold text-xs uppercase tracking-wide">
                                            {item.class_name || 'Active Class'}
                                        </span>
                                        <div className="flex items-center gap-1 text-gray-500 text-xs">
                                            <HiClock className="w-4 h-4 text-blue-500" />
                                            <span>{item.duration} mins</span>
                                        </div>
                                    </div>

                                    <h3 className="text-lg font-bold text-gray-800 dark:text-white">{item.subject_name}</h3>

                                    <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 dark:text-gray-400 pt-2">
                                        <div className="flex items-center gap-2">
                                            <HiOfficeBuilding className="w-4 h-4 text-gray-400" />
                                            <span>Room: <strong className="text-gray-800 dark:text-white font-medium">{item.room || 'TBD'}</strong></span>
                                        </div>
                                        {item.teacher_name && (
                                            <div className="flex items-center gap-2">
                                                <HiUser className="w-4 h-4 text-gray-400" />
                                                <span>Teacher: <strong className="text-gray-800 dark:text-white font-medium">{item.teacher_name}</strong></span>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="border-t dark:border-gray-700 mt-4 pt-3 flex items-center justify-between text-xs text-gray-500">
                                    <span className="font-semibold text-blue-600 dark:text-blue-400 flex items-center gap-1.5">
                                        <HiCalendar className="w-4 h-4" />
                                        {item.start_time.substring(0, 5)} - {item.end_time.substring(0, 5)}
                                    </span>
                                    <span>Term 1</span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center py-12 text-center">
                        <span className="text-4xl mb-3">📅</span>
                        <h4 className="text-base font-semibold text-gray-700 dark:text-gray-300">No Classes Scheduled</h4>
                        <p className="text-gray-500 text-sm mt-1">Enjoy your free day! There are no lessons on {selectedDay}.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
