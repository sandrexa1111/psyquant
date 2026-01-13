import React from 'react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';

const MainLayout = ({ children }) => {
    return (
        <div className="min-h-screen bg-slate-50">
            <Sidebar />
            <TopBar />
            <main className="md:ml-64 pt-16 min-h-screen p-6">
                <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default MainLayout;
