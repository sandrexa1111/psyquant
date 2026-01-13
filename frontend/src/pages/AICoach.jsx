import React, { useState, useEffect, useRef } from 'react';
import MainLayout from '../components/layout/MainLayout';
import { Bot, Send, User, ChevronRight, Zap, Target, Activity } from 'lucide-react';
import axios from 'axios';

const ChatMessage = ({ msg }) => {
    const isAi = msg.sender === 'ai';
    return (
        <div className={`flex gap-4 ${isAi ? '' : 'flex-row-reverse'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isAi ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-600'}`}>
                {isAi ? <Bot size={18} /> : <User size={18} />}
            </div>

            <div className={`max-w-[80%] space-y-2`}>
                <div className={`p-4 rounded-xl shadow-sm border ${isAi ? 'bg-white border-slate-100' : 'bg-indigo-600 text-white border-indigo-600'}`}>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                </div>

                {msg.embedded_data && (
                    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm w-full animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <div className="flex justify-between items-center mb-3">
                            <span className="text-xs font-bold text-slate-400 uppercase">{msg.embedded_data.type}</span>
                            <span className="text-xs text-indigo-600 font-medium">Synced Data</span>
                        </div>

                        {msg.embedded_data.type === 'trade_card' && (
                            <div className="bg-slate-50 p-3 rounded-lg flex justify-between items-center">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-white rounded shadow-sm font-bold text-slate-700">
                                        {msg.embedded_data.symbol}
                                    </div>
                                    <div className="text-sm">
                                        <div className="font-medium text-slate-900">Trade #{msg.embedded_data.trade_id.slice(0, 6)}</div>
                                        <div className="text-red-500 font-bold">{msg.embedded_data.pnl < 0 ? `-$${Math.abs(msg.embedded_data.pnl)}` : `+$${msg.embedded_data.pnl}`}</div>
                                    </div>
                                </div>
                                <button className="text-xs bg-white border border-slate-200 px-3 py-1.5 rounded-lg font-medium hover:bg-slate-100">
                                    View Details
                                </button>
                            </div>
                        )}

                        {msg.embedded_data.type === 'chart' && (
                            <div className="space-y-3">
                                <h4 className="font-bold text-slate-800 text-sm">{msg.embedded_data.title}</h4>
                                <div className="space-y-2">
                                    {msg.embedded_data.data.map((item, i) => (
                                        <div key={i} className="flex items-center gap-2">
                                            <span className="text-xs w-16 text-slate-500 text-right">{item.name}</span>
                                            <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                                                <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${item.value}%` }}></div>
                                            </div>
                                            <span className="text-xs font-mono">{item.value}%</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {msg.suggested_actions && msg.suggested_actions.length > 0 && (
                    <div className="flex flex-wrap gap-2 pt-1">
                        {msg.suggested_actions.map((action, i) => (
                            <button key={i} className="text-xs px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-full border border-indigo-100 hover:bg-indigo-100 transition-colors flex items-center gap-1">
                                <Zap size={12} className="text-indigo-500" />
                                {action}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

const AICoach = () => {
    const [messages, setMessages] = useState([
        {
            sender: 'ai',
            text: "Hello! I'm your AI Trading Coach. I'm connected to your live trading data.\n\nI can help you analyze your performance, detect biases like 'FOMO', or review specific trades. What would you like to focus on today?",
            suggested_actions: ["Why did I lose today?", "Analyze my weaknesses", "Review my last trade"]
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg = { sender: 'user', text: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            // Call Backend API
            const res = await axios.post('http://127.0.0.1:8000/ai/chat', {
                message: userMsg.text,
                conversation_history: [] // Could send history context
            });

            const aiMsg = {
                sender: 'ai',
                text: res.data.text,
                embedded_data: res.data.embedded_data,
                suggested_actions: res.data.suggested_actions
            };

            setMessages(prev => [...prev, aiMsg]);
        } catch (err) {
            console.error(err);
            setMessages(prev => [...prev, {
                sender: 'ai',
                text: "I'm having trouble connecting to my brain right now. Please try again later."
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <MainLayout>
            <div className="h-[calc(100vh-100px)] flex flex-col bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                {/* Header */}
                <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center text-white shadow-lg shadow-indigo-200">
                            <Bot size={24} />
                        </div>
                        <div>
                            <h2 className="font-bold text-slate-900">AI Trading Coach</h2>
                            <div className="flex items-center gap-1.5 text-xs text-emerald-600 font-medium">
                                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                                Online & Analyzing
                            </div>
                        </div>
                    </div>
                </div>

                {/* Chat Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/30">
                    {messages.map((m, i) => (
                        <ChatMessage key={i} msg={m} />
                    ))}
                    {loading && (
                        <div className="flex gap-4">
                            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                                <Bot size={18} />
                            </div>
                            <div className="bg-white p-4 rounded-xl border border-slate-100 shadow-sm">
                                <div className="flex gap-1">
                                    <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                    <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                    <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-slate-100 bg-white">
                    <div className="relative flex items-center gap-2 max-w-4xl mx-auto">
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="Ask about your performance, specific trades, or psychology..."
                            className="flex-1 p-3 pl-4 pr-12 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm shadow-sm"
                        />
                        <button
                            onClick={handleSend}
                            disabled={!input.trim() || loading}
                            className="absolute right-2 p-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                        >
                            <Send size={18} />
                        </button>
                    </div>
                    <div className="text-center mt-2">
                        <p className="text-[10px] text-slate-400">AI Coach can make mistakes. Consider checking important info.</p>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
};

export default AICoach;
