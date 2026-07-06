/**
 * Performance Dashboard Component
 *
 * Features:
 * - Real-time Web Vitals metrics display
 * - Historical data visualization
 * - Performance trends charts
 * - Alert history
 */

import React, { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  AlertCircle, 
  RefreshCw,
  Clock,
  Zap,
  Eye,
  MousePointerClick
} from 'lucide-react'
import './PerformanceDashboard.css'
import api from '../utils/api'
import { getCollectedMetrics } from '../utils/webVitals'

const COLORS = {
  good: '#10b981',
  needsImprovement: '#f59e0b',
  poor: '#ef4444',
  primary: '#3b82f6',
  secondary: '#8b5cf6'
}

const CHART_COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4']

function PerformanceDashboard() {
  const { t } = useTranslation(['performance', 'common'])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [timeRange, setTimeRange] = useState(7) // days
  const [currentMetrics, setCurrentMetrics] = useState(null)
  const [historyData, setHistoryData] = useState([])
  const [summaryData, setSummaryData] = useState(null)
  const [alertHistory, setAlertHistory] = useState([])
  const [thresholds, setThresholds] = useState(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(30000) // 30 seconds

  // Fetch current metrics from browser
  const fetchCurrentMetrics = useCallback(() => {
    const metrics = getCollectedMetrics()
    if (Object.keys(metrics).length > 0) {
      setCurrentMetrics(metrics)
    }
  }, [])

  // Fetch historical data
  const fetchHistoryData = useCallback(async () => {
    try {
      const { data } = await api.get(`/metrics/web-vitals/history`, { params: { days: timeRange } })
      setHistoryData(data?.metrics || [])
    } catch (error) {
      console.error('Failed to fetch history data:', error)
    }
  }, [timeRange])

  // Fetch summary statistics
  const fetchSummary = useCallback(async () => {
    try {
      const { data } = await api.get(`/metrics/web-vitals/summary`, { params: { days: timeRange } })
      setSummaryData(data)
    } catch (error) {
      console.error('Failed to fetch summary:', error)
    }
  }, [timeRange])

  // Fetch alert history
  const fetchAlertHistory = useCallback(async () => {
    try {
      const { data } = await api.get('/metrics/web-vitals/alerts/history', { params: { limit: 50 } })
      setAlertHistory(data?.alerts || [])
    } catch (error) {
      console.error('Failed to fetch alert history:', error)
    }
  }, [])

  // Fetch thresholds
  const fetchThresholds = useCallback(async () => {
    try {
      const { data } = await api.get('/metrics/web-vitals/thresholds')
      setThresholds(data?.thresholds)
    } catch (error) {
      console.error('Failed to fetch thresholds:', error)
    }
  }, [])

  // Refresh all data
  const refreshData = useCallback(async () => {
    setRefreshing(true)
    try {
      await Promise.all([
        fetchCurrentMetrics(),
        fetchHistoryData(),
        fetchSummary(),
        fetchAlertHistory(),
        fetchThresholds()
      ])
    } finally {
      setRefreshing(false)
    }
  }, [fetchCurrentMetrics, fetchHistoryData, fetchSummary, fetchAlertHistory, fetchThresholds])

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      await refreshData()
      setLoading(false)
    }
    loadData()
  }, [refreshData])

  // Auto refresh
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      refreshData()
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [autoRefresh, refreshInterval, refreshData])

  // Update when time range changes
  useEffect(() => {
    fetchHistoryData()
    fetchSummary()
  }, [timeRange, fetchHistoryData, fetchSummary])

  // Format chart data
  const formatChartData = () => {
    return historyData.map(item => ({
      date: new Date(item.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
      LCP: item.lcp,
      FID: item.fid,
      CLS: item.cls ? (item.cls * 1000).toFixed(2) : null,
      FCP: item.fcp,
      TTFB: item.ttfb
    })).filter(item => item.LCP || item.FID || item.CLS || item.FCP || item.TTFB)
  }

  // Get metric rating color
  const getRatingColor = (metric, value) => {
    if (!thresholds || !thresholds[metric]) return COLORS.primary
    
    const threshold = thresholds[metric]
    if (value <= threshold.good) return COLORS.good
    if (value <= threshold.needs_improvement) return COLORS.needsImprovement
    return COLORS.poor
  }

  // Get metric rating text
  const getRatingText = (metric, value) => {
    if (!thresholds || !thresholds[metric]) return t('common:unknown')
    
    const threshold = thresholds[metric]
    if (value <= threshold.good) return t('common:good')
    if (value <= threshold.needs_improvement) return t('common:needsImprovement')
    return t('common:poor')
  }

  // Metric card component
  const MetricCard = ({ title, value, unit, rating, icon: Icon, metric }) => {
    const color = getRatingColor(metric, value)
    const ratingText = getRatingText(metric, value)
    
    return (
      <div className="metric-card">
        <div className="metric-header">
          <Icon size={20} color={color} />
          <span className="metric-title">{title}</span>
        </div>
        <div className="metric-value">
          <span className="value">{value?.toFixed ? value.toFixed(2) : value || 'N/A'}</span>
          {unit && <span className="unit">{unit}</span>}
        </div>
        <div className="metric-rating" style={{ color }}>
          {ratingText}
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="performance-dashboard loading">
        <div className="loading-spinner">
          <RefreshCw size={32} className="spinning" />
          <p>{t('performance:loadingData')}</p>
        </div>
      </div>
    )
  }

  const chartData = formatChartData()

  return (
    <div className="performance-dashboard">
      <div className="dashboard-header">
        <div className="header-left">
          <Activity size={24} />
          <h1>{t('performance:title')}</h1>
        </div>
        <div className="header-controls">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="time-range-select"
          >
            <option value={1}>{t('performance:timeRange.1')}</option>
            <option value={7}>{t('performance:timeRange.7')}</option>
            <option value={30}>{t('performance:timeRange.30')}</option>
            <option value={90}>{t('performance:timeRange.90')}</option>
          </select>
          <button 
            onClick={refreshData} 
            disabled={refreshing}
            className="refresh-btn"
            title={t('performance:refreshData')}
          >
            <RefreshCw size={18} className={refreshing ? 'spinning' : ''} />
          </button>
          <label className="auto-refresh-toggle">
            <input 
              type="checkbox" 
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            <span>{t('performance:autoRefresh')}</span>
          </label>
        </div>
      </div>

      {/* Current Metrics */}
      <div className="metrics-grid">
        {currentMetrics?.LCP && (
          <MetricCard
            title={t('performance:metrics.lcp')}
            value={currentMetrics.LCP.value}
            unit="ms"
            rating={currentMetrics.LCP.rating}
            metric="LCP"
            icon={Eye}
          />
        )}
        {currentMetrics?.FID && (
          <MetricCard
            title={t('performance:metrics.fid')}
            value={currentMetrics.FID.value}
            unit="ms"
            rating={currentMetrics.FID.rating}
            metric="FID"
            icon={MousePointerClick}
          />
        )}
        {currentMetrics?.CLS && (
          <MetricCard
            title={t('performance:metrics.cls')}
            value={currentMetrics.CLS.value}
            unit=""
            rating={currentMetrics.CLS.rating}
            metric="CLS"
            icon={Zap}
          />
        )}
        {currentMetrics?.FCP && (
          <MetricCard
            title={t('performance:metrics.fcp')}
            value={currentMetrics.FCP.value}
            unit="ms"
            rating={currentMetrics.FCP.rating}
            metric="FCP"
            icon={Clock}
          />
        )}
        {currentMetrics?.TTFB && (
          <MetricCard
            title={t('performance:metrics.ttfb')}
            value={currentMetrics.TTFB.value}
            unit="ms"
            rating={currentMetrics.TTFB.rating}
            metric="TTFB"
            icon={TrendingUp}
          />
        )}
      </div>

      {/* Summary Statistics */}
      {summaryData && (
        <div className="summary-section">
          <h2>{t('performance:summaryTitle')}</h2>
          <div className="summary-grid">
            {summaryData.lcp && (
              <div className="summary-card">
                <h3>LCP</h3>
                <div className="summary-stats">
                  <div>{t('performance:statAvg', { value: `${summaryData.lcp.avg?.toFixed(2)}ms` })}</div>
                  <div>{t('performance:statMin', { value: `${summaryData.lcp.min?.toFixed(2)}ms` })}</div>
                  <div>{t('performance:statMax', { value: `${summaryData.lcp.max?.toFixed(2)}ms` })}</div>
                  <div>{t('performance:statP95', { value: `${summaryData.lcp.p95?.toFixed(2)}ms` })}</div>
                </div>
              </div>
            )}
            {summaryData.fid && (
              <div className="summary-card">
                <h3>FID</h3>
                <div className="summary-stats">
                  <div>{t('performance:statAvg', { value: `${summaryData.fid.avg?.toFixed(2)}ms` })}</div>
                  <div>{t('performance:statMin', { value: `${summaryData.fid.min?.toFixed(2)}ms` })}</div>
                  <div>{t('performance:statMax', { value: `${summaryData.fid.max?.toFixed(2)}ms` })}</div>
                  <div>{t('performance:statP95', { value: `${summaryData.fid.p95?.toFixed(2)}ms` })}</div>
                </div>
              </div>
            )}
            {summaryData.cls && (
              <div className="summary-card">
                <h3>CLS</h3>
                <div className="summary-stats">
                  <div>{t('performance:statAvg', { value: summaryData.cls.avg?.toFixed(4) })}</div>
                  <div>{t('performance:statMin', { value: summaryData.cls.min?.toFixed(4) })}</div>
                  <div>{t('performance:statMax', { value: summaryData.cls.max?.toFixed(4) })}</div>
                  <div>{t('performance:statP95', { value: summaryData.cls.p95?.toFixed(4) })}</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Performance Trends Chart */}
      {chartData.length > 0 && (
        <div className="chart-section">
          <h2>{t('performance:trendsTitle')}</h2>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorLCP" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={CHART_COLORS[0]} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={CHART_COLORS[0]} stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorFID" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={CHART_COLORS[1]} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={CHART_COLORS[1]} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="LCP" 
                stroke={CHART_COLORS[0]} 
                fillOpacity={1} 
                fill="url(#colorLCP)"
                name="LCP (ms)"
              />
              <Area 
                type="monotone" 
                dataKey="FID" 
                stroke={CHART_COLORS[1]} 
                fillOpacity={1} 
                fill="url(#colorFID)"
                name="FID (ms)"
              />
              <Area 
                type="monotone" 
                dataKey="FCP" 
                stroke={CHART_COLORS[2]} 
                fillOpacity={0.6}
                name="FCP (ms)"
              />
              <Area 
                type="monotone" 
                dataKey="TTFB" 
                stroke={CHART_COLORS[3]} 
                fillOpacity={0.6}
                name="TTFB (ms)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* CLS Trend Chart */}
      {chartData.length > 0 && chartData.some(d => d.CLS) && (
        <div className="chart-section">
          <h2>{t('performance:clsTrendTitle')}</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="CLS" 
                stroke={CHART_COLORS[4]} 
                strokeWidth={2}
                name="CLS (×1000)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Alert History */}
      {alertHistory.length > 0 && (
        <div className="alert-section">
          <h2>
            <AlertCircle size={20} />
            {t('performance:alertHistory')}
          </h2>
          <div className="alert-list">
            {alertHistory.slice(0, 10).map((alert, index) => (
              <div key={index} className="alert-item">
                <div className="alert-header">
                  <span className="alert-metric">{alert.metric}</span>
                  <span className={`alert-level ${alert.level}`}>{alert.level}</span>
                </div>
                <div className="alert-details">
                  <span>{t('common:value')}: {alert.value}</span>
                  <span>{new Date(alert.timestamp).toLocaleString('zh-CN')}</span>
                </div>
                <div className="alert-message">{alert.message}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {chartData.length === 0 && !loading && (
        <div className="empty-state">
          <Activity size={48} />
          <p>{t('performance:noData')}</p>
          <p className="empty-hint">{t('performance:noDataHint')}</p>
        </div>
      )}
    </div>
  )
}

export default PerformanceDashboard
