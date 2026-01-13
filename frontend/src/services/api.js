import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
});

export const setAuthToken = (token) => {
    if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
        delete api.defaults.headers.common['Authorization'];
    }
};

export const getAccount = async () => {
    const response = await api.get('/account');
    return response.data;
};

export const getPositions = async () => {
    const response = await api.get('/positions');
    return response.data;
};

export const getMarketData = async (symbol) => {
    const response = await api.get(`/market-data/${symbol}`);
    return response.data;
};

export const getHistory = async () => {
    const response = await api.get('/history');
    return response.data;
};

export const getPortfolioMetrics = async (period = '1A') => {
    try {
        const response = await api.get(`/analytics/metrics?period=${period}`);
        return response.data;
    } catch (error) {
        console.error("Error fetching metrics:", error);
        throw error;
    }
};

export const getSkillProfile = async () => {
    try {
        const response = await api.get('/ai/skills');
        return response.data;
    } catch (error) {
        console.error("Error fetching skills:", error);
        throw error;
    }
};

export const getBiases = async () => {
    try {
        const response = await api.get('/ai/biases');
        return response.data;
    } catch (error) {
        console.error("Error fetching biases:", error);
        throw error;
    }
};

export const getNews = async (symbol) => {
    const response = await api.get(`/market/news/${symbol}`);
    return response.data;
};

export const getScreener = async () => {
    const response = await api.get('/market/screener');
    return response.data;
};

export const getProfile = async (symbol) => {
    const response = await api.get(`/market/profile/${symbol}`);
    return response.data;
};

export const submitOrder = async (orderData) => {
    const response = await api.post('/trade/order', orderData);
    return response.data;
};

export const getOrders = async (status = 'open') => {
    const response = await api.get(`/trade/orders?status=${status}`);
    return response.data;
};

export const startAlgo = async () => {
    const response = await api.post('/algo/start');
    return response.data;
};

export const stopAlgo = async () => {
    const response = await api.post('/algo/stop');
    return response.data;
};

export const getAlgoStatus = async () => {
    const response = await api.get('/algo/status');
    return response.data;
};

export const getChartData = async (symbol, period = '1mo', interval = '1d') => {
    const response = await api.get(`/market/chart/${symbol}?period=${period}&interval=${interval}`);
    return response.data;
};

// ============================================================================
// Behavior Intelligence API
// ============================================================================

export const judgeTrade = async (tradeId) => {
    const response = await api.post('/ai/judge-trade', { trade_id: tradeId });
    return response.data;
};

export const getTradeJudgement = async (tradeId) => {
    const response = await api.get(`/ai/judge-trade/${tradeId}`);
    return response.data;
};

export const getRiskScore = async (lookbackDays = 30) => {
    const response = await api.get(`/ai/risk-score?lookback_days=${lookbackDays}`);
    return response.data;
};

export const getBehaviorPatterns = async (limit = 50) => {
    const response = await api.get(`/ai/behavior-patterns?limit=${limit}`);
    return response.data;
};

export const generateBehaviorChain = async (tradeId) => {
    const response = await api.post(`/ai/behavior-patterns/${tradeId}`);
    return response.data;
};

export const getStrategyDNA = async () => {
    const response = await api.get('/ai/strategy-dna');
    return response.data;
};

export const rebuildStrategyDNA = async (minTrades = 5) => {
    const response = await api.post(`/ai/strategy-dna/rebuild?min_trades=${minTrades}`);
    return response.data;
};

export const getIntelligenceSummary = async () => {
    const response = await api.get('/ai/summary');
    return response.data;
};

export const getSkillScore = async () => {
    const response = await api.get('/ai/skill-score');
    return response.data;
};

export const getBiasHeatmap = async () => {
    const response = await api.get('/ai/bias-heatmap');
    return response.data;
};

export const runBacktest = async () => {
    const response = await api.get('/ai/backtest');
    return response.data;
};

// ============================================================================
// Journal API
// ============================================================================

export const getJournalEntries = async (limit = 50, offset = 0) => {
    const response = await api.get(`/journal/?limit=${limit}&offset=${offset}`);
    return response.data;
};

export const createJournalEntry = async (entryData) => {
    const response = await api.post('/journal/', entryData);
    return response.data;
};

export const updateJournalEntry = async (id, entryData) => {
    const response = await api.put(`/journal/${id}`, entryData);
    return response.data;
};

export const deleteJournalEntry = async (id) => {
    const response = await api.delete(`/journal/${id}`);
    return response.data;
};

export const analyzeJournalEntry = async (id) => {
    const response = await api.post(`/journal/${id}/analyze`);
    return response.data;
};

export default api;
