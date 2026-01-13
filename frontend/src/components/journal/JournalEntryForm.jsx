import React, { useState, useEffect } from 'react';

const JournalEntryForm = ({ entry, onSave, onAnalyze }) => {
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [tags, setTags] = useState([]);
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    useEffect(() => {
        if (entry) {
            setTitle(entry.title);
            setContent(entry.content);
            setTags(entry.tags || []);
        } else {
            setTitle('');
            setContent('');
            setTags([]);
        }
    }, [entry]);

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave({ title, content, tags });
    };

    const handleAnalyze = async () => {
        setIsAnalyzing(true);
        try {
            await onAnalyze(entry.id);
        } catch (error) {
            console.error("Analysis failed:", error);
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="flex-1 flex flex-col h-full bg-gray-950 p-6 overflow-y-auto">
            <form onSubmit={handleSubmit} className="flex flex-col h-full max-w-4xl mx-auto w-full">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-white">
                        {entry ? 'Edit Entry' : 'New Reflection'}
                    </h2>
                    <div className="flex gap-3">
                        {entry && (
                            <button
                                type="button"
                                onClick={handleAnalyze}
                                disabled={isAnalyzing}
                                className={`px-4 py-2 rounded text-white font-medium flex items-center gap-2 ${isAnalyzing
                                        ? 'bg-purple-800 cursor-wait'
                                        : 'bg-purple-600 hover:bg-purple-700'
                                    }`}
                            >
                                {isAnalyzing ? 'Analyzing...' : '✨ Analyze with AI'}
                            </button>
                        )}
                        <button
                            type="submit"
                            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded font-medium"
                        >
                            Save Entry
                        </button>
                    </div>
                </div>

                <div className="space-y-4 flex-1 flex flex-col">
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Entry Title (e.g., FOMO after NFP news...)"
                        className="w-full bg-gray-900 border border-gray-800 rounded p-4 text-xl text-white placeholder-gray-600 focus:outline-none focus:border-blue-500"
                    />

                    <textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="Write your reflection here. How did you feel? What was your rationale? What did you learn?"
                        className="w-full flex-1 bg-gray-900 border border-gray-800 rounded p-4 text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500 resize-none font-mono"
                    />

                    {/* AI Feedback Panel */}
                    {entry && (entry.ai_feedback || entry.sentiment_score !== null) && (
                        <div className="bg-gray-900 border border-purple-900/50 rounded-lg p-6 mt-6">
                            <h3 className="text-purple-400 font-semibold mb-4 flex items-center gap-2">
                                🤖 AI Coach Insight
                            </h3>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
                                <div className="bg-gray-950 p-4 rounded text-center">
                                    <div className="text-sm text-gray-500 mb-1">Sentiment</div>
                                    <div className={`text-2xl font-bold ${entry.sentiment_score > 60 ? 'text-green-500' :
                                            entry.sentiment_score < 40 ? 'text-red-500' : 'text-gray-400'
                                        }`}>
                                        {entry.sentiment_score}/100
                                    </div>
                                </div>
                                <div className="bg-gray-950 p-4 rounded col-span-2">
                                    <div className="text-sm text-gray-500 mb-1">Feedback</div>
                                    <p className="text-gray-300 italic">"{entry.ai_feedback}"</p>
                                </div>
                            </div>

                            {entry.tags && entry.tags.length > 0 && (
                                <div className="flex flex-wrap gap-2">
                                    {entry.tags.map(tag => (
                                        <span key={tag} className="px-2 py-1 bg-purple-900/30 text-purple-300 rounded text-xs border border-purple-800">
                                            #{tag}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </form>
        </div>
    );
};

export default JournalEntryForm;
