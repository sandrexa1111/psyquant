import React, { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

const InteractiveChart = ({ data, colors = {} }) => {
    const chartContainerRef = useRef();

    useEffect(() => {
        if (!data || !data.candles || data.candles.length === 0) return;
        if (!chartContainerRef.current) return;

        let chart = null;

        // Create resize handler that matches the one added
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
                height: 400,
                grid: {
                    vertLines: { color: '#f1f5f9' },
                    horzLines: { color: '#f1f5f9' },
                },
                rightPriceScale: {
                    borderColor: '#e2e8f0',
                },
                timeScale: {
                    borderColor: '#e2e8f0',
                },
            });

            // Candlestick Series
            const candleSeries = chart.addCandlestickSeries({
                upColor: '#10b981',
                downColor: '#f43f5e',
                borderVisible: false,
                wickUpColor: '#10b981',
                wickDownColor: '#f43f5e',
            });

            candleSeries.setData(data.candles);

            // Volume Series
            const volumeSeries = chart.addHistogramSeries({
                priceFormat: { type: 'volume' },
                priceScaleId: '',
                scaleMargins: { top: 0.8, bottom: 0 },
            });

            if (data.volume) {
                volumeSeries.setData(data.volume);
            }

            // Bollinger Bands (if available)
            if (data.indicators) {
                const { bb_upper, bb_middle, bb_lower } = data.indicators;

                if (bb_upper) {
                    const bbUpperSeries = chart.addLineSeries({
                        color: 'rgba(59, 130, 246, 0.5)',
                        lineWidth: 1,
                        lineStyle: 1,
                        priceLineVisible: false,
                        lastValueVisible: false,
                    });
                    bbUpperSeries.setData(bb_upper.filter(d => d.value !== null));
                }

                if (bb_middle) {
                    const bbMiddleSeries = chart.addLineSeries({
                        color: 'rgba(249, 115, 22, 0.8)',
                        lineWidth: 1,
                        lineStyle: 0,
                        priceLineVisible: false,
                        lastValueVisible: false,
                    });
                    bbMiddleSeries.setData(bb_middle.filter(d => d.value !== null));
                }

                if (bb_lower) {
                    const bbLowerSeries = chart.addLineSeries({
                        color: 'rgba(59, 130, 246, 0.5)',
                        lineWidth: 1,
                        lineStyle: 1,
                        priceLineVisible: false,
                        lastValueVisible: false,
                    });
                    bbLowerSeries.setData(bb_lower.filter(d => d.value !== null));
                }
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
            console.error("Chart Error:", err);
            return () => {
                if (chart) chart.remove();
            };
        }
    }, [data]);

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden p-4">
            <div className="mb-4">
                <h3 className="font-bold text-slate-700">Technical Analysis: {data?.symbol}</h3>
            </div>
            <div ref={chartContainerRef} className="w-full h-[400px]" />
        </div>
    );
};

export default InteractiveChart;
