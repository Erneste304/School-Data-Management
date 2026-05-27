import React, { useState, useEffect, useRef } from 'react';
import { HiChat, HiSearch, HiPaperAirplane, HiPlusCircle, HiUserGroup, HiVolumeUp, HiOutlineChatAlt } from 'react-icons/hi';

export default function ChatDashboard() {
    const [currentUser, setCurrentUser] = useState(null);
    const [rooms, setRooms] = useState([]);
    const [selectedRoom, setSelectedRoom] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMsg, setNewMsg] = useState('');
    const [loadingRooms, setLoadingRooms] = useState(true);
    const [loadingMessages, setLoadingMessages] = useState(false);
    const [searchRoom, setSearchRoom] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [roomForm, setRoomForm] = useState({ name: '', description: '', room_type: 'group' });
    const messagesEndRef = useRef(null);

    useEffect(() => {
        fetchCurrentUser();
        fetchRooms();
    }, []);

    useEffect(() => {
        if (selectedRoom) {
            fetchMessages(selectedRoom.slug);
            const interval = setInterval(() => {
                fetchMessagesSilently(selectedRoom.slug);
            }, 5000);
            return () => clearInterval(interval);
        }
    }, [selectedRoom]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const fetchCurrentUser = async () => {
        try {
            const res = await fetch('/api/accounts/me/');
            if (res.ok) {
                setCurrentUser(await res.json());
            }
        } catch (err) {
            console.error('Error fetching current user:', err);
        }
    };

    const fetchRooms = async () => {
        setLoadingRooms(true);
        try {
            const res = await fetch('/chat/api/rooms/');
            if (res.ok) {
                setRooms(await res.json());
            }
        } catch (err) {
            console.error('Error fetching rooms:', err);
        } finally {
            setLoadingRooms(false);
        }
    };

    const fetchMessages = async (slug) => {
        setLoadingMessages(true);
        try {
            const res = await fetch(`/chat/api/messages/${slug}/`);
            if (res.ok) {
                setMessages(await res.json());
            }
        } catch (err) {
            console.error('Error fetching messages:', err);
        } finally {
            setLoadingMessages(false);
        }
    };

    const fetchMessagesSilently = async (slug) => {
        try {
            const res = await fetch(`/chat/api/messages/${slug}/`);
            if (res.ok) {
                setMessages(await res.json());
            }
        } catch (err) {
            console.error('Error fetching messages silently:', err);
        }
    };

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!newMsg.trim() || !selectedRoom) return;

        const bodyContent = newMsg;
        setNewMsg('');

        try {
            const res = await fetch(`/chat/api/messages/${selectedRoom.slug}/send/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: bodyContent })
            });

            if (res.ok) {
                const message = await res.json();
                setMessages(prev => [...prev, message]);
            }
        } catch (err) {
            console.error('Error sending message:', err);
        }
    };

    const handleCreateRoom = async (e) => {
        e.preventDefault();
        if (!roomForm.name.trim()) return;

        try {
            const res = await fetch('/chat/api/rooms/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(roomForm)
            });

            if (res.ok) {
                const newRoom = await res.json();
                setRooms(prev => [newRoom, ...prev]);
                setSelectedRoom(newRoom);
                setShowCreateModal(false);
                setRoomForm({ name: '', description: '', room_type: 'group' });
            }
        } catch (err) {
            console.error('Error creating room:', err);
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const filteredRooms = rooms.filter(r =>
        r.name?.toLowerCase().includes(searchRoom.toLowerCase())
    );

    return (
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border dark:border-gray-700 h-[calc(100vh-140px)] flex overflow-hidden">
            {/* Rooms sidebar list */}
            <div className="w-80 border-r dark:border-gray-700 flex flex-col h-full bg-gray-50/50 dark:bg-gray-900/20">
                <div className="p-4 border-b dark:border-gray-700 space-y-3">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
                            <HiChat className="text-blue-500 w-5 h-5" /> Chats
                        </h2>
                        <button onClick={() => setShowCreateModal(true)} className="text-blue-600 hover:text-blue-800">
                            <HiPlusCircle className="w-6 h-6" />
                        </button>
                    </div>
                    <div className="flex items-center gap-2 bg-white dark:bg-gray-800 rounded-lg px-3 py-2 border dark:border-gray-700 text-xs">
                        <HiSearch className="text-gray-400 w-4 h-4" />
                        <input
                            type="text"
                            placeholder="Search chats..."
                            className="bg-transparent outline-none w-full text-gray-800 dark:text-white"
                            value={searchRoom}
                            onChange={(e) => setSearchRoom(e.target.value)}
                        />
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-2 space-y-1">
                    {loadingRooms ? (
                        <div className="flex justify-center py-10"><span className="loader-blue"></span></div>
                    ) : filteredRooms.length > 0 ? (
                        filteredRooms.map(room => (
                            <button
                                key={room.id}
                                onClick={() => setSelectedRoom(room)}
                                className={`w-full text-left p-3 rounded-xl flex items-center gap-3 transition ${
                                    selectedRoom?.id === room.id
                                        ? 'bg-blue-600 text-white'
                                        : 'hover:bg-gray-100 dark:hover:bg-gray-700/50 text-gray-755 dark:text-white'
                                }`}
                            >
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
                                    selectedRoom?.id === room.id
                                        ? 'bg-white/20 text-white'
                                        : 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-300'
                                }`}>
                                    {room.name?.[0]}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between">
                                        <p className="font-semibold text-sm truncate">{room.name}</p>
                                        <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                                            selectedRoom?.id === room.id
                                                ? 'bg-white/20 text-white'
                                                : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
                                        }`}>
                                            {room.room_type}
                                        </span>
                                    </div>
                                    <p className={`text-xs truncate mt-0.5 ${selectedRoom?.id === room.id ? 'text-white/80' : 'text-gray-400'}`}>
                                        {room.description || 'No description'}
                                    </p>
                                </div>
                            </button>
                        ))
                    ) : (
                        <div className="text-center py-10 text-xs text-gray-400">No rooms found.</div>
                    )}
                </div>
            </div>

            {/* Active Chat room main panel */}
            <div className="flex-1 flex flex-col h-full bg-white dark:bg-gray-800">
                {selectedRoom ? (
                    <>
                        {/* Chat Room header */}
                        <div className="p-4 border-b dark:border-gray-700 flex items-center justify-between bg-gray-50/50 dark:bg-gray-900/20">
                            <div>
                                <h3 className="font-bold text-gray-800 dark:text-white text-base">{selectedRoom.name}</h3>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{selectedRoom.description || 'Welcome to the room chat channel'}</p>
                            </div>
                            <div className="flex items-center gap-2 text-xs font-semibold text-gray-450 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-3 py-1.5 rounded-lg">
                                <HiUserGroup className="w-4 h-4 text-blue-500" />
                                <span>{selectedRoom.members_count || 1} Members</span>
                            </div>
                        </div>

                        {/* Message list window */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            {loadingMessages ? (
                                <div className="flex justify-center py-10"><span className="loader-blue"></span></div>
                            ) : messages.length > 0 ? (
                                messages.map((msg, index) => {
                                    const isMe = msg.sender?.id === currentUser?.id;
                                    return (
                                        <div key={msg.id || index} className={`flex items-start gap-2.5 ${isMe ? 'justify-end' : ''}`}>
                                            {!isMe && (
                                                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-650 flex items-center justify-center font-bold text-xs">
                                                    {msg.sender?.full_name?.[0]}
                                                </div>
                                            )}
                                            <div className={`max-w-[70%] rounded-2xl px-4 py-2 text-sm shadow-sm ${
                                                isMe
                                                    ? 'bg-blue-600 text-white rounded-tr-none'
                                                    : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-white rounded-tl-none'
                                            }`}>
                                                {!isMe && <p className="text-[10px] font-bold text-blue-500 mb-0.5">{msg.sender?.full_name}</p>}
                                                <p className="leading-relaxed">{msg.content}</p>
                                                <p className={`text-[9px] mt-1 text-right leading-none ${isMe ? 'text-white/70' : 'text-gray-400'}`}>
                                                    {msg.timestamp_formatted || new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                </p>
                                            </div>
                                        </div>
                                    );
                                })
                            ) : (
                                <div className="text-center py-12 text-gray-400">
                                    <HiOutlineChatAlt className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                                    No messages in this chat room yet. Start the conversation!
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Send message textbar footer */}
                        <form onSubmit={handleSendMessage} className="p-4 border-t dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/20 flex gap-3">
                            <input
                                type="text"
                                placeholder="Type your message..."
                                className="flex-1 border rounded-xl p-3 bg-white dark:bg-gray-900 text-sm text-gray-800 dark:text-white outline-none focus:border-blue-500"
                                value={newMsg}
                                onChange={(e) => setNewMsg(e.target.value)}
                            />
                            <button type="submit" className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition shadow-md flex items-center justify-center">
                                <HiPaperAirplane className="w-5 h-5 rotate-90" />
                            </button>
                        </form>
                    </>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-center p-6">
                        <span className="text-6xl mb-4">💬</span>
                        <h3 className="text-lg font-bold text-gray-700 dark:text-gray-300">No Chat Session Opened</h3>
                        <p className="text-xs text-gray-400 mt-1 max-w-sm">Select one of the chat channels from the sidebar, or create a new room to start discussing with staff members and classroom mates.</p>
                    </div>
                )}
            </div>

            {/* Create Room Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Create Chat Channel</h3>
                            <button onClick={() => setShowCreateModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        <form onSubmit={handleCreateRoom} className="space-y-4">
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Room Name</label>
                                <input type="text" required className="border rounded-lg p-2.5 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white focus:outline-none focus:border-blue-500"
                                    value={roomForm.name} onChange={(e) => setRoomForm({ ...roomForm, name: e.target.value })} />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Category / Type</label>
                                <select className="border rounded-lg p-2.5 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white focus:outline-none focus:border-blue-500"
                                    value={roomForm.room_type} onChange={(e) => setRoomForm({ ...roomForm, room_type: e.target.value })}>
                                    <option value="public">Public (Open to All)</option>
                                    <option value="group">Group Channel</option>
                                    <option value="staff">Staff Only (Teachers/Admins)</option>
                                </select>
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Description</label>
                                <textarea rows="3" className="border rounded-lg p-2.5 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white focus:outline-none focus:border-blue-500"
                                    value={roomForm.description} onChange={(e) => setRoomForm({ ...roomForm, description: e.target.value })} />
                            </div>
                            <div className="flex justify-end gap-3 pt-3 border-t dark:border-gray-700">
                                <button type="button" onClick={() => setShowCreateModal(false)} className="px-4 py-2 border rounded-lg text-gray-500 text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition">Create Room</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
