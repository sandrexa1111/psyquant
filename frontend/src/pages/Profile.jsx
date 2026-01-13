import React, { useState, useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import { Edit2, MapPin, Mail, Phone, Facebook, Linkedin, Instagram, X as XIcon, Loader2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api, { getAccount } from '../services/api';

const Profile = () => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [simBalance, setSimBalance] = useState(100000);
    const [resetAmount, setResetAmount] = useState(100000);
    const [showSimSettings, setShowSimSettings] = useState(false);

    // Check mode
    useEffect(() => {
        const checkMode = async () => {
            try {
                const status = await api.get('/settings/status');
                if (status.data.mode === 'sim') {
                    setShowSimSettings(true);
                    const acct = await getAccount();
                    if (acct) setSimBalance(acct.cash);
                }
            } catch (e) {
                console.error("Failed to check status", e);
            }
        };
        checkMode();
    }, []);

    const handleResetSim = async () => {
        setLoading(true);
        try {
            await api.post('/settings/sim/reset', { balance: parseFloat(resetAmount) });
            // Refresh balance
            const acct = await getAccount();
            setSimBalance(acct.cash);
            alert(`Simulation reset to $${resetAmount.toLocaleString()}`);
        } catch (error) {
            console.error("Failed to reset sim", error);
            alert("Failed to reset simulation.");
        } finally {
            setLoading(false);
        }
    };

    // Mock user details if not in auth user object
    // In a real app, fetchProfile() from API
    const userDetails = {
        firstName: user?.full_name?.split(' ')[0] || "Musharof",
        lastName: user?.full_name?.split(' ').slice(1).join(' ') || "Chowdhury",
        email: user?.email || "randomuser@pimjo.com", // Typo in image, correcting to generic or similar
        phone: "+09 363 398 46",
        role: "Team Manager",
        location: "Arizona, United States",
        bio: "Team Manager",
        postalCode: "ERT 2489",
        taxId: "AS4568384",
        avatar: "https://i.pravatar.cc/150?u=a042581f4e29026704d"
    };

    return (
        <MainLayout>
            {/* Header Breadcrumb */}
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-slate-800">Profile</h1>
                <div className="text-sm text-slate-500">
                    <span className="hover:text-indigo-600 cursor-pointer">Home</span> &gt; <span className="text-slate-800 font-medium">Profile</span>
                </div>
            </div>

            <div className="flex flex-col gap-6 max-w-5xl mx-auto">

                {/* 1. Profile Card */}
                <div className="bg-white rounded-xl border border-slate-200 p-6 flex flex-col md:flex-row justify-between items-center gap-6 shadow-sm">
                    <div className="flex flex-col md:flex-row items-center gap-6">
                        <div className="relative">
                            <img src={userDetails.avatar} alt="Profile" className="w-24 h-24 rounded-full object-cover border-4 border-slate-50 shadow-sm" />
                        </div>
                        <div className="text-center md:text-left">
                            <h2 className="text-xl font-bold text-slate-800">{userDetails.firstName} {userDetails.lastName}</h2>
                            <div className="text-sm text-slate-500 mt-1 flex items-center justify-center md:justify-start gap-2">
                                <span>{userDetails.role}</span>
                                <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                                <span className="flex items-center gap-1"><MapPin size={12} /> {userDetails.location}</span>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        {/* Socials */}
                        <div className="flex gap-2 mr-4">
                            <button className="p-2 rounded-full bg-slate-50 text-slate-500 hover:bg-blue-50 hover:text-blue-600 transition-colors"><Facebook size={16} /></button>
                            <button className="p-2 rounded-full bg-slate-50 text-slate-500 hover:bg-slate-100 hover:text-black transition-colors"><XIcon size={16} /></button>
                            <button className="p-2 rounded-full bg-slate-50 text-slate-500 hover:bg-blue-50 hover:text-blue-700 transition-colors"><Linkedin size={16} /></button>
                            <button className="p-2 rounded-full bg-slate-50 text-slate-500 hover:bg-pink-50 hover:text-pink-600 transition-colors"><Instagram size={16} /></button>
                        </div>

                        <button className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">
                            <Edit2 size={14} /> Edit
                        </button>
                    </div>
                </div>

                {/* 2. Personal Information */}
                <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm relative">
                    <div className="flex justify-between items-start mb-6">
                        <h3 className="text-lg font-bold text-slate-800">Personal Information</h3>
                        <button className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">
                            <Edit2 size={14} /> Edit
                        </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-y-6 gap-x-12">
                        <div>
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 block">First Name</label>
                            <div className="text-slate-800 font-medium">{userDetails.firstName}</div>
                        </div>
                        <div>
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 block">Last Name</label>
                            <div className="text-slate-800 font-medium">{userDetails.lastName}</div>
                        </div>
                        <div>
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 block">Email address</label>
                            <div className="text-slate-800 font-medium flex items-center gap-2">
                                {userDetails.email}
                            </div>
                        </div>
                        <div>
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 block">Phone</label>
                            <div className="text-slate-800 font-medium">{userDetails.phone}</div>
                        </div>
                        <div>
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 block">Bio</label>
                            <div className="text-slate-800 font-medium">{userDetails.bio}</div>
                        </div>
                    </div>
                </div>

                {/* 3. Address */}
                <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm relative">
                    <div className="flex justify-between items-start mb-6">
                        <h3 className="text-lg font-bold text-slate-800">Address</h3>
                        <button className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors">
                            <Edit2 size={14} /> Edit
                        </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-y-6 gap-x-12">
                        <div>
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 block">Country</label>
                            <div className="text-slate-800 font-medium">United States</div>
                        </div>
                        <div>
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 block">City/State</label>
                            <div className="text-slate-800 font-medium">{userDetails.location}</div>
                        </div>
                        <div>
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 block">Postal Code</label>
                            <div className="text-slate-800 font-medium">{userDetails.postalCode}</div>
                        </div>
                        <div>
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 block">TAX ID</label>
                            <div className="text-slate-800 font-medium">{userDetails.taxId}</div>
                        </div>
                    </div>
                </div>

                {/* 4. Simulation Settings (Conditional) */}
                {showSimSettings && (
                    <div className="bg-indigo-50/50 rounded-xl border border-indigo-100 p-6 shadow-sm relative">
                        <div className="flex justify-between items-start mb-6">
                            <div>
                                <h3 className="text-lg font-bold text-indigo-900">Simulation Account</h3>
                                <p className="text-sm text-indigo-600/80">Manage your virtual trading environment.</p>
                            </div>
                            <div className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                                ACTIVE
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                            <div>
                                <div className="text-sm text-indigo-500 mb-1 font-medium">Current Cash Balance</div>
                                <div className="text-3xl font-bold text-indigo-900">${simBalance?.toLocaleString()}</div>
                                <div className="text-xs text-indigo-400 mt-2">
                                    Simulated data provided by backend generator.
                                </div>
                            </div>

                            <div className="bg-white p-4 rounded-lg border border-indigo-100 shadow-sm">
                                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 block">Reset Balance To</label>
                                <div className="flex gap-3">
                                    <div className="relative flex-1">
                                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">$</span>
                                        <input
                                            type="number"
                                            value={resetAmount}
                                            onChange={(e) => setResetAmount(e.target.value)}
                                            className="w-full pl-6 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                        />
                                    </div>
                                    <button
                                        onClick={handleResetSim}
                                        disabled={loading}
                                        className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors whitespace-nowrap"
                                    >
                                        {loading ? <Loader2 size={16} className="animate-spin" /> : "Reset Account"}
                                    </button>
                                </div>
                                <p className="text-xs text-slate-400 mt-2 text-center">
                                    Warning: This will wipe all current simulated positions and history.
                                </p>
                            </div>
                        </div>
                    </div>
                )}

            </div>
        </MainLayout>
    );
};

export default Profile;
