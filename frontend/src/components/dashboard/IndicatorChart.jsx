import React, { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

const IndicatorChart = ({ data, type = 'rsi', color = '#8b5cf6', height = 150 }) => {
    const chartContainerRef = useRef();

    useEffect(() => {
        if (!data || data.length === 0) return;
        if (!chartContainerRef.current) return;

        let chart = null;

        const handleResize = () => {
            if (chart && chartContainerRef.current) {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };

        try {
            chart = createChart(chartContainerRef.current, {
                layout: {
                    background: { type: ColorType.Solid, color: 'white' },
                    textColor: '#334155',
                },
                width: chartContainerRef.current.clientWidth,
                height: height,
                grid: {
                    vertLines: { color: '#f1f5f9' },
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

            // Add Series based on type
            const series = chart.addLineSeries({
                color: color,
                lineWidth: 2,
            });

            const validData = data.filter(d => d.value !== null && d.value !== undefined);
            series.setData(validData);

            // For RSI, add reference lines (70/30)
            if (type === 'rsi') {
                const overboughtLine = chart.addLineSeries({
                    color: '#ef4444',
                    lineWidth: 1,
                    lineStyle: 1, // Dotted
                });
                // Create constant line data
                const lineData70 = validData.map(d => ({ time: d.time, value: 70 }));
                const lineData30 = validData.map(d => ({ time: d.time, value: 30 }));

                overboughtLine.setData(lineData70);

                const oversoldLine = chart.addLineSeries({
                    color: '#10b981',
                    lineWidth: 1,
                    lineStyle: 1,
                });
                oversoldLine.setData(lineData30);
            }

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
            console.error("Indicator Chart Error:", err);
            return () => {
                if (chart) chart.remove();
            };
        }
    }, [data, type]);

    // Safety for display value
    const lastValue = data && data.length > 0 ? data[data.length - 1]?.value : null;

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden p-4">
            <div className="mb-2 flex items-center justify-between">
                <h4 className="font-bold text-xs text-slate-500 uppercase">{type}</h4>
                <div className="text-xs font-mono font-bold text-slate-700">
                    {lastValue !== null && lastValue !== undefined ? lastValue.toFixed(2) : '-'}
                </div>
            </div>
            <div ref={chartContainerRef} className="w-full" style={{ height: height }} />
        </div>
    );
};

export default IndicatorChart;
