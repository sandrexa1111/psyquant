import React from 'react';
import { RadialBarChart, RadialBar, Legend, ResponsiveContainer, Tooltip } from 'recharts';

const SkillProfile = ({ data }) => {
    if (!data) return null;

    const chartData = [
        { name: 'Profitability', score: data.breakdown?.profitability || 0, fill: '#8884d8' },
        { name: 'Risk Mgmt', score: data.breakdown?.risk_management || 0, fill: '#83a6ed' },
        { name: 'Timing', score: data.breakdown?.timing || 0, fill: '#8dd1e1' },
        { name: 'Discipline', score: data.breakdown?.discipline || 0, fill: '#82ca9d' },
    ];

    const style = {
        top: '50%',
        right: 0,
        transform: 'translate(0, -50%)',
        lineHeight: '24px',
    };

    return (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-slate-800">Trader Skill DNA</h2>
                <div className="text-2xl font-bold text-indigo-600">{data.overall_score}<span className="text-sm text-slate-400 font-normal">/100</span></div>
            </div>

            <div className="h-[250px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <RadialBarChart cx="50%" cy="50%" innerRadius="10%" outerRadius="80%" barSize={10} data={chartData}>
                        <RadialBar
                            minAngle={15}
                            label={{ position: 'insideStart', fill: '#fff' }}
                            background
                            clockWise
                            dataKey="score"
                        />
                        <Legend iconSize={10} layout="vertical" verticalAlign="middle" wrapperStyle={style} />
                        <Tooltip />
                    </RadialBarChart>
                </ResponsiveContainer>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                {chartData.map((item) => (
                    <div key={item.name} className="flex justify-between border-b border-slate-100 pb-1">
                        <span className="text-slate-500">{item.name}</span>
                        <span className="font-medium text-slate-800">{item.score}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default SkillProfile;
