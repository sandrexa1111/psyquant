import React, { useState } from 'react';
import { Bot, X, Send, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const FloatingCoach = () => {
    // Instead of small popup, button now goes to full page
    const handleClick = () => {
        window.location.href = '/ai-coach';
    };

    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleClick}
                className="flex items-center gap-3 px-5 py-4 rounded-full shadow-xl transition-all bg-indigo-600 text-white hover:bg-indigo-700"
            >
                <Bot size={24} />
                <span className="font-bold">Ask AI Coach</span>
                <ChevronRight size={16} />
            </motion.button>
        </div>
    );
};

export default FloatingCoach;
