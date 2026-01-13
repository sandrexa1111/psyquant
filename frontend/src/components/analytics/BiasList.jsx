import React from 'react';
import { AlertTriangle, Info } from 'lucide-react';

const BiasList = ({ biases }) => {
    return (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm h-full">
            <div className="flex items-center gap-2 mb-4">
                <h2 className="text-lg font-semibold text-slate-800">Cognitive Biases</h2>
                <span className="bg-red-100 text-red-700 text-xs px-2 py-0.5 rounded-full font-medium">
                    {biases?.length || 0} Detected
                </span>
            </div>

            <div className="space-y-4">
                {(!biases || biases.length === 0) ? (
                    <div className="text-center py-8 text-slate-400">
                        <div className="inline-block p-3 bg-slate-50 rounded-full mb-2">
                            <Info size={24} />
                        </div>
                        <p>No active biases detected.</p>
                        <p className="text-xs mt-1">Great discipline!</p>
                    </div>
                ) : (
                    biases.map((bias, idx) => (
                        <div key={idx} className="p-4 bg-amber-50 border border-amber-200 rounded-md">
                            <div className="flex gap-3">
                                <div className="mt-1 text-amber-600">
                                    <AlertTriangle size={20} />
                                </div>
                                <div>
                                    <h3 className="font-medium text-amber-900">{bias.name}</h3>
                                    <p className="text-sm text-amber-800 mt-1">{bias.description}</p>
                                    <div className="mt-2 text-xs font-semibold text-amber-700">
                                        Tip: {bias.recommendation}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default BiasList;
