import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { setAuthToken } from '../services/api';

const AuthContext = createContext({});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check active sessions and sets the user
        const getSession = async () => {
            try {
                const { data: { session }, error } = await supabase.auth.getSession();
                if (error) throw error;
                setAuthToken(session?.access_token ?? null);
                setUser(session?.user ?? null);
            } catch (err) {
                console.error("Auth Exception:", err);
                setAuthToken(null);
                setUser(null);
            } finally {
                setLoading(false);
            }
        };

        getSession();

        // Listen for changes on auth state (logged in, signed out, etc.)
        let subscription = null;
        try {
            const { data } = supabase.auth.onAuthStateChange((_event, session) => {
                setAuthToken(session?.access_token ?? null);
                setUser(session?.user ?? null);
                setLoading(false);
            });
            subscription = data.subscription;
        } catch (e) {
            console.error("Auth Listener Error:", e);
        }

        return () => subscription?.unsubscribe();
    }, []);

    const value = {
        signUp: (data) => supabase.auth.signUp(data),
        signIn: (data) => supabase.auth.signInWithPassword(data),
        signOut: () => supabase.auth.signOut(),
        user,
    };

    return (
        <AuthContext.Provider value={value}>
            {loading ? (
                <div className="flex items-center justify-center h-screen bg-slate-50">
                    <div className="text-slate-500 font-medium animate-pulse">Loading Application...</div>
                </div>
            ) : (
                children
            )}
        </AuthContext.Provider>
    );
};
