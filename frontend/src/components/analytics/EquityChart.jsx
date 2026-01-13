import React, { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

const EquityChart = ({ data }) => {
    const chartContainerRef = useRef();

    useEffect(() => {
        if (!data || data.length === 0) return;
        if (!chartContainerRef.current) return;

        let chart = null;

        try {
            chart = createChart(chartContainerRef.current, {
                layout: {
                    background: { type: ColorType.Solid, color: 'white' },
                    textColor: '#334155',
                },
                width: chartContainerRef.current.clientWidth,
                height: 300,
                grid: {
                    vertLines: { visible: false },
                    horzLines: { color: '#f1f5f9' },
                },
                rightPriceScale: {
                    borderColor: '#e2e8f0',
                    visible: true,
                },
                timeScale: {
                    borderColor: '#e2e8f0',
                    visible: true,
                },
            });

            // Area Series for "Growth" look
            const areaSeries = chart.addAreaSeries({
                lineColor: '#4f46e5', // Indigo 600
                topColor: 'rgba(79, 70, 229, 0.4)',
                bottomColor: 'rgba(79, 70, 229, 0.0)',
                lineWidth: 2,
            });

            areaSeries.setData(data);
            chart.timeScale().fitContent();

            // Resize Observer
            const resizeObserver = new ResizeObserver(entries => {
                if (entries.length === 0 || !entries[0].target) return;
                const newRect = entries[0].contentRect;
                chart.applyOptions({ width: newRect.width });
            });

            resizeObserver.observe(chartContainerRef.current);

            return () => {
                resizeObserver.disconnect();
                chart.remove();
            };

        } catch (err) {
            console.error("EquityChart Error:", err);
            if (chart) chart.remove();
        }
    }, [data]);

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden p-6">
            <h3 className="font-bold text-slate-700 mb-4">Portfolio Growth</h3>
            <div ref={chartContainerRef} className="w-full h-[300px]" />
        </div>
    );
};

export default EquityChart;
