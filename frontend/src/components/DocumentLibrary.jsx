import React, { useState, useEffect } from 'react';
import { HiDocumentText, HiDownload, HiUpload, HiPlus, HiSearch, HiFolder, HiTag } from 'react-icons/hi';

export default function DocumentLibrary() {
    const [documents, setDocuments] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [userRole, setUserRole] = useState(localStorage.getItem('userRole') || 'admin');

    const [form, setForm] = useState({
        title: '',
        description: '',
        category: '',
        is_public: true,
        tags: '',
        file: null
    });

    useEffect(() => {
        fetchDocuments();
        fetchCategories();
    }, [selectedCategory]);

    const fetchDocuments = async () => {
        setLoading(true);
        try {
            let url = '/api/documents/files/';
            const params = [];
            if (selectedCategory) params.push(`category=${selectedCategory}`);
            if (searchQuery) params.push(`search=${searchQuery}`);
            if (params.length > 0) url += `?${params.join('&')}`;

            const res = await fetch(url);
            if (res.ok) {
                setDocuments(await res.json());
            }
        } catch (err) {
            console.error('Error fetching documents:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchCategories = async () => {
        try {
            const res = await fetch('/api/documents/categories/');
            if (res.ok) {
                setCategories(await res.json());
            }
        } catch (err) {
            console.error('Error fetching categories:', err);
        }
    };

    const handleFileChange = (e) => {
        setForm({ ...form, file: e.target.files[0] });
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!form.file || !form.title || !form.category) return;

        const formData = new FormData();
        formData.append('title', form.title);
        formData.append('description', form.description);
        formData.append('category', form.category);
        formData.append('is_public', form.is_public);
        formData.append('tags', form.tags);
        formData.append('file', form.file);

        try {
            const res = await fetch('/api/documents/files/', {
                method: 'POST',
                body: formData
            });

            if (res.ok) {
                fetchDocuments();
                setShowUploadModal(false);
                setForm({ title: '', description: '', category: '', is_public: true, tags: '', file: null });
            }
        } catch (err) {
            console.error('Error uploading document:', err);
        }
    };

    const handleDownload = async (docId, fileUrl) => {
        try {
            const res = await fetch(`/api/documents/files/${docId}/download/`, { method: 'POST' });
            if (res.ok) {
                const data = await res.json();
                setDocuments(prev => prev.map(d => d.id === docId ? { ...d, download_count: data.downloads } : d));
            }
        } catch (err) {
            console.error('Error recording download:', err);
        }
        window.open(fileUrl, '_blank');
    };

    const formatBytes = (bytes, decimals = 2) => {
        if (!bytes) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                        <HiDocumentText className="w-7 h-7 text-blue-600" />
                        Documents Library
                    </h2>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Access study materials, report cards, or upload campus forms</p>
                </div>
                {(userRole === 'admin' || userRole === 'head_teacher' || userRole === 'teacher') && (
                    <button onClick={() => setShowUploadModal(true)}
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200 text-sm font-semibold shadow-md self-start sm:self-center">
                        <HiUpload className="w-5 h-5" /> Upload Document
                    </button>
                )}
            </div>

            {/* Filter toolbar */}
            <div className="flex flex-col sm:flex-row gap-3 bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-150 dark:border-gray-700">
                <div className="flex-1 flex items-center gap-2 bg-gray-50 dark:bg-gray-900 rounded-lg px-3 py-2 border dark:border-gray-700 text-sm">
                    <HiSearch className="text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Search document title..."
                        className="bg-transparent outline-none w-full text-gray-800 dark:text-white"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && fetchDocuments()}
                    />
                </div>
                <div className="w-full sm:w-48">
                    <select
                        className="w-full bg-gray-50 dark:bg-gray-900 border dark:border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-700 dark:text-white focus:outline-none"
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                    >
                        <option value="">All Categories</option>
                        {categories.map(cat => (
                            <option key={cat.id} value={cat.id}>{cat.name}</option>
                        ))}
                    </select>
                </div>
                <button
                    onClick={fetchDocuments}
                    className="bg-blue-50 text-blue-600 hover:bg-blue-100 font-semibold px-4 py-2 rounded-lg text-sm transition"
                >
                    Apply Filter
                </button>
            </div>

            {/* Document listings grid */}
            {loading ? (
                <div className="flex justify-center py-12"><span className="loader-blue"></span></div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {documents.length > 0 ? (
                        documents.map(doc => (
                            <div key={doc.id} className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 flex flex-col justify-between hover:shadow-md transition">
                                <div>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="bg-blue-50 text-blue-700 dark:bg-blue-950/30 dark:text-blue-300 px-2 py-0.5 rounded text-xs font-semibold flex items-center gap-1">
                                            <HiFolder className="w-3.5 h-3.5" />
                                            {doc.category_name || 'General'}
                                        </span>
                                        <span className="text-[10px] text-gray-400 font-medium">
                                            {formatBytes(doc.file_size)}
                                        </span>
                                    </div>
                                    <h3 className="font-bold text-gray-800 dark:text-white text-base leading-snug truncate" title={doc.title}>
                                        {doc.title}
                                    </h3>
                                    <p className="text-sm text-gray-550 dark:text-gray-400 mt-2 line-clamp-2">
                                        {doc.description || 'No description provided.'}
                                    </p>
                                </div>
                                <div className="mt-4 pt-4 border-t dark:border-gray-755 space-y-3">
                                    <div className="flex items-center justify-between text-xs text-gray-450 dark:text-gray-400">
                                        <span>By {doc.uploaded_by_name}</span>
                                        <span>{doc.download_count || 0} Downloads</span>
                                    </div>
                                    <button
                                        onClick={() => handleDownload(doc.id, doc.file)}
                                        className="w-full flex items-center justify-center gap-1.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition shadow-sm"
                                    >
                                        <HiDownload className="w-4 h-4" /> Download File
                                    </button>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="col-span-full text-center py-12 text-gray-500 bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700">
                            <span className="text-4xl mb-2 block">📂</span> No documents available matching the query.
                        </div>
                    )}
                </div>
            )}

            {/* Upload Modal */}
            {showUploadModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 animate-fadeIn">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Upload Document</h3>
                            <button onClick={() => setShowUploadModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        <form onSubmit={handleUpload} className="space-y-4">
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Document Title</label>
                                <input type="text" required className="border rounded p-2.5 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Category</label>
                                <select required className="border rounded p-2.5 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                                    <option value="">Select Category</option>
                                    {categories.map(cat => (
                                        <option key={cat.id} value={cat.id}>{cat.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">File Upload</label>
                                <input type="file" required className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    onChange={handleFileChange} />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Tags (Comma-separated)</label>
                                <input type="text" placeholder="handout, quiz, physics" className="border rounded p-2.5 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Description</label>
                                <textarea rows="3" className="border rounded p-2.5 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
                            </div>
                            <div className="flex items-center gap-2">
                                <input type="checkbox" id="is_public" checked={form.is_public}
                                    onChange={(e) => setForm({ ...form, is_public: e.target.checked })} />
                                <label htmlFor="is_public" className="text-xs font-semibold text-gray-605 dark:text-gray-300">Make Public (all students can see)</label>
                            </div>
                            <div className="flex justify-end gap-3 pt-3 border-t dark:border-gray-700">
                                <button type="button" onClick={() => setShowUploadModal(false)} className="px-4 py-2 border rounded text-gray-500 text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition">Upload</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
