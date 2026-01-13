import React from 'react';

const JournalList = ({ entries, onSelectEntry, onNewEntry }) => {
    return (
        <div className="bg-gray-900 border-r border-gray-800 w-1/3 flex flex-col h-full">
            <div className="p-4 border-b border-gray-800 flex justify-between items-center">
                <h2 className="text-xl font-bold text-white">Journal</h2>
                <button
                    onClick={onNewEntry}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-colors"
                >
                    + New Entry
                </button>
            </div>

            <div className="flex-1 overflow-y-auto">
                {entries.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        No entries yet. Start writing!
                    </div>
                ) : (
                    entries.map((entry) => (
                        <div
                            key={entry.id}
                            onClick={() => onSelectEntry(entry)}
                            className="p-4 border-b border-gray-800 hover:bg-gray-800 cursor-pointer transition-colors"
                        >
                            <h3 className="font-semibold text-gray-200 mb-1 truncate">{entry.title}</h3>
                            <p className="text-sm text-gray-400 line-clamp-2 mb-2">{entry.content}</p>

                            <div className="flex items-center justify-between text-xs text-gray-500">
                                <span>{new Date(entry.created_at).toLocaleDateString()}</span>

                                {entry.sentiment_score !== null && (
                                    <span className={`px-2 py-0.5 rounded ${entry.sentiment_score > 60 ? 'bg-green-900 text-green-300' :
                                            entry.sentiment_score < 40 ? 'bg-red-900 text-red-300' :
                                                'bg-gray-700 text-gray-300'
                                        }`}>
                                        {entry.sentiment_score > 60 ? 'Positive' :
                                            entry.sentiment_score < 40 ? 'Negative' : 'Neutral'}
                                    </span>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default JournalList;
