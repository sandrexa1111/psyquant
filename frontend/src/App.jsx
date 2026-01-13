import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/auth/Login';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Analytics from './pages/Analytics';
import Market from './pages/Market';
import Trade from './pages/Trade';
import Settings from './pages/Settings';
import Onboarding from './pages/Onboarding';

import TradeReplay from './pages/TradeReplay';
import AICoach from './pages/AICoach';

// Behavior Intelligence Pages
import BehaviorGraph from './pages/BehaviorGraph';
import Psychology from './pages/Psychology';
import StrategyDNA from './pages/StrategyDNA';
import RiskMeter from './pages/RiskMeter';
import Evolution from './pages/Evolution';
import Journal from './pages/Journal';


const ProtectedRoute = ({ children }) => {
    const { user } = useAuth();
    if (!user) {
        return <Login />;
    }
    return children;
};

const App = () => {
    return (
        <Router>
            <AuthProvider>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route
                        path="/"
                        element={
                            <ProtectedRoute>
                                <Dashboard />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/profile"
                        element={
                            <ProtectedRoute>
                                <Profile />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/analytics"
                        element={
                            <ProtectedRoute>
                                <Analytics />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/market"
                        element={
                            <ProtectedRoute>
                                <Market />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/trade"
                        element={
                            <ProtectedRoute>
                                <Trade />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/onboarding"
                        element={
                            <ProtectedRoute>
                                <Onboarding />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/settings"
                        element={
                            <ProtectedRoute>
                                <Settings />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/trade/replay/:id"
                        element={
                            <ProtectedRoute>
                                <TradeReplay />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/ai-coach"
                        element={
                            <ProtectedRoute>
                                <AICoach />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/behavior"
                        element={
                            <ProtectedRoute>
                                <BehaviorGraph />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/psychology"
                        element={
                            <ProtectedRoute>
                                <Psychology />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/strategy-dna"
                        element={
                            <ProtectedRoute>
                                <StrategyDNA />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/risk-meter"
                        element={
                            <ProtectedRoute>
                                <RiskMeter />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/evolution"
                        element={
                            <ProtectedRoute>
                                <Evolution />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/journal"
                        element={
                            <ProtectedRoute>
                                <Journal />
                            </ProtectedRoute>
                        }
                    />
                    {/* Fallback */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </AuthProvider>
        </Router>
    );
};

export default App;
