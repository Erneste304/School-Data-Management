import React, { useState, useEffect } from 'react';
import { HiBell, HiCheck, HiCheckCircle, HiX } from 'react-icons/hi';

export default function NotificationBell() {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [showPanel, setShowPanel] = useState(false);

    useEffect(() => {
        fetchNotifications();
        const interval = setInterval(fetchNotifications, 15000);
        return () => clearInterval(interval);
    }, []);

    const fetchNotifications = async () => {
        try {
            const res = await fetch('/api/notifications/list/');
            if (res.ok) {
                const data = await res.json();
                setNotifications(data);
                setUnreadCount(data.filter(n => !n.is_read).length);
            }
        } catch (err) {
            console.error('Error fetching notifications:', err);
        }
    };

    const markRead = async (id) => {
        try {
            await fetch(`/api/notifications/list/${id}/mark_read/`, { method: 'POST' });
            setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
            setUnreadCount(prev => Math.max(0, prev - 1));
        } catch (err) {
            console.error('Error marking notification read:', err);
        }
    };

    const markAllRead = async () => {
        try {
            await fetch('/api/notifications/list/mark_all_read/', { method: 'POST' });
            setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
            setUnreadCount(0);
        } catch (err) {
            console.error('Error marking all read:', err);
        }
    };

    const getTypeBadge = (type) => {
        const styles = {
            Academic: 'bg-blue-100 text-blue-700',
            Financial: 'bg-green-100 text-green-700',
            Discipline: 'bg-red-100 text-red-700',
            Event: 'bg-purple-100 text-purple-700',
            System: 'bg-gray-100 text-gray-700',
            Info: 'bg-sky-100 text-sky-700',
            Warning: 'bg-amber-100 text-amber-700',
            Success: 'bg-emerald-100 text-emerald-700',
            Error: 'bg-red-100 text-red-700',
        };
        return styles[type] || styles.Info;
    };

    return (
        <div className="relative">
            <button onClick={() => setShowPanel(!showPanel)} className="relative p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition">
                <HiBell className="w-6 h-6" />
                {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 bg-red-600 text-white text-[10px] font-bold w-5 h-5 flex items-center justify-center rounded-full animate-pulse">
                        {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                )}
            </button>

            {showPanel && (
                <>
                    <div className="fixed inset-0 z-40" onClick={() => setShowPanel(false)} />
                    <div className="absolute right-0 mt-2 w-96 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border dark:border-gray-700 z-50 max-h-[70vh] flex flex-col overflow-hidden">
                        <div className="p-4 border-b dark:border-gray-700 flex items-center justify-between">
                            <h3 className="font-bold text-gray-800 dark:text-white text-sm">Notifications</h3>
                            <div className="flex items-center gap-2">
                                {unreadCount > 0 && (
                                    <button onClick={markAllRead} className="text-xs text-blue-600 hover:underline font-semibold flex items-center gap-1">
                                        <HiCheckCircle className="w-4 h-4" /> Mark all read
                                    </button>
                                )}
                                <button onClick={() => setShowPanel(false)} className="text-gray-400 hover:text-gray-600"><HiX className="w-4 h-4" /></button>
                            </div>
                        </div>

                        <div className="flex-1 overflow-y-auto divide-y dark:divide-gray-700">
                            {notifications.length > 0 ? (
                                notifications.map(notif => (
                                    <div
                                        key={notif.id}
                                        onClick={() => !notif.is_read && markRead(notif.id)}
                                        className={`p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition ${
                                            !notif.is_read ? 'bg-blue-50/50 dark:bg-blue-950/10' : ''
                                        }`}
                                    >
                                        <div className="flex items-start justify-between gap-2">
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2 mb-1">
                                                    {!notif.is_read && <span className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0"></span>}
                                                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${getTypeBadge(notif.notification_type)}`}>
                                                        {notif.notification_type}
                                                    </span>
                                                </div>
                                                <p className="font-semibold text-sm text-gray-800 dark:text-white leading-tight">{notif.title}</p>
                                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">{notif.message}</p>
                                            </div>
                                            <span className="text-[10px] text-gray-400 flex-shrink-0 mt-1">
                                                {new Date(notif.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-10 text-gray-400 text-sm">
                                    <HiBell className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                                    No notifications yet.
                                </div>
                            )}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
