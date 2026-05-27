import React, { useState, useEffect } from 'react';
import { HiCurrencyDollar, HiTrendingUp, HiTrendingDown, HiClock, HiCheckCircle, HiExclamationCircle, HiPlusCircle } from 'react-icons/hi';

export default function FinanceDashboard() {
    const [summary, setSummary] = useState(null);
    const [fees, setFees] = useState([]);
    const [payments, setPayments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview');
    const [showPaymentModal, setShowPaymentModal] = useState(false);
    const [selectedFee, setSelectedFee] = useState(null);
    const [paymentForm, setPaymentForm] = useState({
        amount: '', payment_method: 'mobile_money', reference_number: '', notes: ''
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [summaryRes, feesRes, paymentsRes] = await Promise.all([
                fetch('/api/finance/summary/'),
                fetch('/api/finance/student-fees/'),
                fetch('/api/finance/payments/')
            ]);

            if (summaryRes.ok) setSummary(await summaryRes.json());
            if (feesRes.ok) setFees(await feesRes.json());
            if (paymentsRes.ok) setPayments(await paymentsRes.json());
        } catch (err) {
            console.error('Error fetching finance data:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleRecordPayment = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        try {
            const res = await fetch('/api/finance/payments/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student: selectedFee.student,
                    student_fee: selectedFee.id,
                    amount: parseFloat(paymentForm.amount),
                    payment_method: paymentForm.payment_method,
                    reference_number: paymentForm.reference_number,
                    notes: paymentForm.notes
                })
            });
            if (res.ok) {
                setSuccess('Payment recorded successfully!');
                setShowPaymentModal(false);
                setPaymentForm({ amount: '', payment_method: 'mobile_money', reference_number: '', notes: '' });
                fetchData();
            } else {
                const data = await res.json();
                setError(data.detail || 'Failed to record payment.');
            }
        } catch (err) {
            setError('Server connection error.');
        }
    };

    const getStatusBadge = (status) => {
        const styles = {
            paid: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
            partial: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
            pending: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
            overdue: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
            waived: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
        };
        return styles[status] || styles.pending;
    };

    if (loading) {
        return <div className="flex justify-center py-16"><span className="loader-blue"></span></div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Finance & Billing</h2>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Track fee collections, payments, expenses, and overall financial health</p>
                </div>
            </div>

            {success && <div className="p-4 bg-green-50 text-green-700 rounded-lg text-sm font-medium border-l-4 border-green-500">{success}</div>}
            {error && <div className="p-4 bg-red-50 text-red-700 rounded-lg text-sm font-medium border-l-4 border-red-500">{error}</div>}

            {/* Summary Cards */}
            {summary && (
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
                    <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-5 shadow flex items-center gap-4 text-white">
                        <div className="p-3 bg-white/20 rounded-xl"><HiCurrencyDollar className="w-6 h-6" /></div>
                        <div>
                            <p className="text-white/70 text-xs">Total Expected</p>
                            <p className="text-xl font-bold">RWF {summary.total_expected.toLocaleString()}</p>
                        </div>
                    </div>
                    <div className="bg-gradient-to-br from-emerald-500 to-emerald-700 rounded-2xl p-5 shadow flex items-center gap-4 text-white">
                        <div className="p-3 bg-white/20 rounded-xl"><HiTrendingUp className="w-6 h-6" /></div>
                        <div>
                            <p className="text-white/70 text-xs">Collected</p>
                            <p className="text-xl font-bold">RWF {summary.total_collected.toLocaleString()}</p>
                            <p className="text-xs text-white/60">{summary.collection_rate}% collection rate</p>
                        </div>
                    </div>
                    <div className="bg-gradient-to-br from-rose-500 to-rose-700 rounded-2xl p-5 shadow flex items-center gap-4 text-white">
                        <div className="p-3 bg-white/20 rounded-xl"><HiExclamationCircle className="w-6 h-6" /></div>
                        <div>
                            <p className="text-white/70 text-xs">Outstanding Balance</p>
                            <p className="text-xl font-bold">RWF {summary.total_balance.toLocaleString()}</p>
                        </div>
                    </div>
                    <div className="bg-gradient-to-br from-violet-500 to-violet-700 rounded-2xl p-5 shadow flex items-center gap-4 text-white">
                        <div className="p-3 bg-white/20 rounded-xl"><HiTrendingDown className="w-6 h-6" /></div>
                        <div>
                            <p className="text-white/70 text-xs">Net Income</p>
                            <p className="text-xl font-bold">RWF {summary.net_income.toLocaleString()}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="flex gap-2 border-b dark:border-gray-700">
                {['overview', 'payments'].map(tab => (
                    <button key={tab} onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 text-sm font-semibold capitalize transition ${
                            activeTab === tab
                                ? 'border-b-2 border-blue-600 text-blue-600'
                                : 'text-gray-500 hover:text-gray-700'
                        }`}>
                        {tab === 'overview' ? 'Fee Invoices' : 'Payment History'}
                    </button>
                ))}
            </div>

            {/* Fee Invoices Table */}
            {activeTab === 'overview' && (
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
                    {fees.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-300 text-xs font-semibold uppercase border-b border-gray-200 dark:border-gray-700">
                                        <th className="p-4">Student</th>
                                        <th className="p-4">Fee Category</th>
                                        <th className="p-4">Total</th>
                                        <th className="p-4">Paid</th>
                                        <th className="p-4">Balance</th>
                                        <th className="p-4">Due Date</th>
                                        <th className="p-4">Status</th>
                                        <th className="p-4">Action</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                    {fees.map((fee) => (
                                        <tr key={fee.id} className="hover:bg-gray-50 dark:hover:bg-gray-755 transition text-sm">
                                            <td className="p-4 font-semibold text-gray-800 dark:text-white">{fee.student_name}</td>
                                            <td className="p-4 text-gray-500 dark:text-gray-400">{fee.category_name}</td>
                                            <td className="p-4 font-bold text-gray-800 dark:text-white">RWF {parseFloat(fee.total_amount).toLocaleString()}</td>
                                            <td className="p-4 text-emerald-600 font-semibold">RWF {parseFloat(fee.amount_paid).toLocaleString()}</td>
                                            <td className="p-4 text-rose-600 font-semibold">RWF {parseFloat(fee.balance).toLocaleString()}</td>
                                            <td className="p-4 text-gray-500 dark:text-gray-400">{fee.due_date}</td>
                                            <td className="p-4">
                                                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${getStatusBadge(fee.status)}`}>
                                                    {fee.status_display}
                                                </span>
                                            </td>
                                            <td className="p-4">
                                                {fee.status !== 'paid' && fee.status !== 'waived' && (
                                                    <button
                                                        onClick={() => { setSelectedFee(fee); setShowPaymentModal(true); }}
                                                        className="text-blue-600 hover:text-blue-800 text-xs font-semibold"
                                                    >
                                                        Record Payment
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
                            <span className="text-4xl mb-2 block">💰</span>
                            No fee records found.
                        </div>
                    )}
                </div>
            )}

            {/* Payment History Table */}
            {activeTab === 'payments' && (
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
                    {payments.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-300 text-xs font-semibold uppercase border-b border-gray-200 dark:border-gray-700">
                                        <th className="p-4">Receipt #</th>
                                        <th className="p-4">Student</th>
                                        <th className="p-4">Amount</th>
                                        <th className="p-4">Method</th>
                                        <th className="p-4">Date</th>
                                        <th className="p-4">Reference</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                    {payments.map((p) => (
                                        <tr key={p.id} className="hover:bg-gray-50 dark:hover:bg-gray-755 transition text-sm">
                                            <td className="p-4 font-mono text-blue-600 font-semibold">{p.receipt_number}</td>
                                            <td className="p-4 font-semibold text-gray-800 dark:text-white">{p.student_name}</td>
                                            <td className="p-4 text-emerald-600 font-bold">RWF {parseFloat(p.amount).toLocaleString()}</td>
                                            <td className="p-4 text-gray-500 capitalize">{p.method_display}</td>
                                            <td className="p-4 text-gray-500">{p.payment_date}</td>
                                            <td className="p-4 text-gray-400 text-xs">{p.reference_number || '—'}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="text-center py-12 text-gray-500">
                            <span className="text-4xl mb-2 block">🧾</span>
                            No payment records found.
                        </div>
                    )}
                </div>
            )}

            {/* Record Payment Modal */}
            {showPaymentModal && selectedFee && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
                        <div className="flex justify-between items-center border-b pb-3 dark:border-gray-700">
                            <h3 className="text-lg font-bold text-gray-800 dark:text-white">Record Payment</h3>
                            <button onClick={() => setShowPaymentModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                        </div>
                        <div className="text-sm">
                            <p className="text-gray-500">Student: <span className="font-bold text-gray-800 dark:text-white">{selectedFee.student_name}</span></p>
                            <p className="text-gray-500">Balance Due: <span className="font-bold text-rose-600">RWF {parseFloat(selectedFee.balance).toLocaleString()}</span></p>
                        </div>
                        <form onSubmit={handleRecordPayment} className="space-y-4">
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Amount (RWF)</label>
                                <input type="number" required min="1" max={parseFloat(selectedFee.balance)} step="1"
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={paymentForm.amount}
                                    onChange={(e) => setPaymentForm({ ...paymentForm, amount: e.target.value })} />
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Payment Method</label>
                                <select className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={paymentForm.payment_method}
                                    onChange={(e) => setPaymentForm({ ...paymentForm, payment_method: e.target.value })}>
                                    <option value="mobile_money">Mobile Money</option>
                                    <option value="bank_transfer">Bank Transfer</option>
                                    <option value="cash">Cash</option>
                                    <option value="cheque">Cheque</option>
                                    <option value="online">Online Payment</option>
                                </select>
                            </div>
                            <div className="flex flex-col">
                                <label className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-1">Reference Number</label>
                                <input type="text" placeholder="e.g. MTN MoMo TxnID"
                                    className="border rounded p-2 bg-gray-50 dark:bg-gray-900 text-sm text-gray-800 dark:text-white"
                                    value={paymentForm.reference_number}
                                    onChange={(e) => setPaymentForm({ ...paymentForm, reference_number: e.target.value })} />
                            </div>
                            <div className="flex justify-end gap-3 pt-3 border-t dark:border-gray-700">
                                <button type="button" onClick={() => setShowPaymentModal(false)} className="px-4 py-2 border rounded text-gray-500 text-sm">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-emerald-600 text-white rounded text-sm hover:bg-emerald-700 transition">Confirm Payment</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
