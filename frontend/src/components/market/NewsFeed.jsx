import React from 'react';
import { ExternalLink, Clock } from 'lucide-react';

const NewsFeed = ({ news }) => {
    if (!news || news.length === 0) {
        return <div className="text-slate-400 text-sm">No recent news found.</div>;
    }

    return (
        <div className="space-y-4">
            <h3 className="font-bold text-slate-700">Latest Market News</h3>
            <div className="space-y-3">
                {news.map((item, index) => (
                    <div key={index} className="flex gap-4 p-3 bg-white rounded-lg border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                        {/* Thumbnail if available */}
                        {item.thumbnail && item.thumbnail.resolutions && (
                            <div className="w-20 h-16 flex-shrink-0">
                                <img
                                    src={item.thumbnail.resolutions[0].url}
                                    alt="News thumbnail"
                                    className="w-full h-full object-cover rounded-md"
                                />
                            </div>
                        )}

                        <div className="flex-1">
                            <a href={item.link} target="_blank" rel="noopener noreferrer" className="group">
                                <h4 className="text-sm font-semibold text-slate-800 group-hover:text-blue-600 line-clamp-2">
                                    {item.title}
                                </h4>
                            </a>
                            <div className="flex items-center gap-2 mt-2">
                                <span className="text-xs font-bold text-blue-500 bg-blue-50 px-2 py-0.5 rounded-full">
                                    {item.publisher || 'Unknown Source'}
                                </span>
                                <div className="flex items-center gap-1 text-slate-400 text-xs">
                                    <Clock size={10} />
                                    <span>
                                        {item.providerPublishTime
                                            ? new Date(item.providerPublishTime * 1000).toLocaleDateString()
                                            : new Date().toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="flex-shrink-0 pt-1">
                            <a href={item.link} target="_blank" rel="noopener noreferrer" className="text-slate-300 hover:text-blue-500">
                                <ExternalLink size={16} />
                            </a>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default NewsFeed;
