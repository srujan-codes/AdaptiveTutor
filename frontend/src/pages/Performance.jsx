/**
 * Performance page — score chart, AI insights, strategy recommendation.
 * Route: /performance
 */
import { useState, useEffect, useCallback } from 'react'
import { performanceApi, strategyApi } from '../api/client'
import Navbar from '../components/Navbar'
import ScoreChart from '../components/ScoreChart'
import InsightsPanel from '../components/InsightsPanel'
import {
  BarChart2, TrendingUp, Target, BookOpen, Award,
  RefreshCw, Lock, AlertCircle, ChevronRight, Sparkles,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

function StatCard({ icon, label, value, color, sub }) {
  return (
    <div className="glass-card" style={{ padding: '1.25rem 1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
        <span style={{ color }}>{icon}</span>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</span>
      </div>
      <div style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, fontSize: '1.75rem', color: 'var(--text-primary)' }}>{value}</div>
      {sub && <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: 2 }}>{sub}</div>}
    </div>
  )
}

function LockedSection({ sessionsLeft }) {
  return (
    <div style={{
      textAlign: 'center', padding: '2.5rem 1.5rem',
      border: '1px dashed rgba(99,136,255,0.25)', borderRadius: 14,
      background: 'rgba(99,136,255,0.03)',
    }}>
      <Lock size={28} style={{ color: 'var(--text-muted)', marginBottom: '0.875rem' }} />
      <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>Unlocks soon</p>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', maxWidth: 320, margin: '0 auto' }}>
        Complete <strong style={{ color: 'var(--accent-blue)' }}>{sessionsLeft} more {sessionsLeft === 1 ? 'session' : 'sessions'}</strong> so the AI has enough data to generate insights.
      </p>
    </div>
  )
}

export default function Performance() {
  const navigate = useNavigate()

  const [perf, setPerf] = useState(null)
  const [insights, setInsights] = useState(null)
  const [strategy, setStrategy] = useState(null)

  const [loadingPerf, setLoadingPerf] = useState(true)
  const [loadingInsights, setLoadingInsights] = useState(false)
  const [loadingStrategy, setLoadingStrategy] = useState(false)

  const [insightsError, setInsightsError] = useState('')
  const [strategyError, setStrategyError] = useState('')
  const [perfError, setPerfError] = useState('')

  const loadPerf = useCallback(async () => {
    setLoadingPerf(true)
    setPerfError('')
    try {
      const res = await performanceApi.list()
      setPerf(res.data)
    } catch (err) {
      setPerfError('Failed to load performance data.')
      console.error(err)
    } finally {
      setLoadingPerf(false)
    }
  }, [])

  const loadInsights = useCallback(async () => {
    setLoadingInsights(true)
    setInsightsError('')
    try {
      const res = await performanceApi.insights()
      setInsights(res.data)
    } catch (err) {
      if (err.response?.status === 400) {
        // < 3 sessions — graceful empty state handled by LockedSection
      } else {
        setInsightsError('Failed to generate insights. Please try again.')
      }
    } finally {
      setLoadingInsights(false)
    }
  }, [])

  const loadStrategy = useCallback(async () => {
    setLoadingStrategy(true)
    setStrategyError('')
    try {
      const res = await strategyApi.nextTopic()
      setStrategy(res.data)
    } catch (err) {
      if (err.response?.status !== 400) {
        setStrategyError('Failed to load strategy recommendation.')
      }
      // 400 = not enough sessions, handled by LockedSection
    } finally {
      setLoadingStrategy(false)
    }
  }, [])

  useEffect(() => {
    loadPerf()
  }, [loadPerf])

  // Load insights & strategy once we know there are enough sessions
  useEffect(() => {
    if (perf?.total_sessions >= 3) {
      loadInsights()
      loadStrategy()
    }
  }, [perf, loadInsights, loadStrategy])

  const totalSessions = perf?.total_sessions ?? 0
  const avgPct = perf?.average_score != null ? `${(perf.average_score / 5 * 100).toFixed(0)}%` : '—'
  const sessionsLeft = Math.max(0, 3 - totalSessions)
  const hasEnoughSessions = totalSessions >= 3

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />

      <main style={{ maxWidth: 1100, margin: '0 auto', padding: '2rem 1.5rem' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, fontSize: 'clamp(1.4rem,4vw,2rem)', color: 'var(--text-primary)', marginBottom: '0.3rem' }}>
              Your Performance
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Track your progress and get AI-powered insights.
            </p>
          </div>
          <button
            id="refresh-perf-btn"
            className="btn-secondary"
            onClick={() => { loadPerf(); if (hasEnoughSessions) { loadInsights(); loadStrategy() } }}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}
          >
            <RefreshCw size={15} /> Refresh
          </button>
        </div>

        {/* Perf error */}
        {perfError && (
          <div style={{
            display: 'flex', gap: '0.5rem',
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)',
            borderRadius: 10, padding: '0.875rem 1rem', marginBottom: '1.5rem',
          }}>
            <AlertCircle size={15} style={{ color: '#ef4444', flexShrink: 0, marginTop: 1 }} />
            <p style={{ color: '#ef4444', margin: 0, fontSize: '0.875rem' }}>{perfError}</p>
          </div>
        )}

        {/* Stats row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.75rem' }}>
          <StatCard
            icon={<BookOpen size={18} />}
            label="Total Sessions"
            value={loadingPerf ? '…' : totalSessions}
            color="var(--accent-blue)"
          />
          <StatCard
            icon={<TrendingUp size={18} />}
            label="Avg Score"
            value={loadingPerf ? '…' : avgPct}
            color="var(--accent-green)"
            sub={perf ? `${perf.average_score?.toFixed(1) ?? '—'} / 5` : null}
          />
          <StatCard
            icon={<Award size={18} />}
            label="Best Topic"
            value={loadingPerf ? '…' : (perf?.best_topic || '—')}
            color="var(--accent-purple)"
          />
          <StatCard
            icon={<Target size={18} />}
            label="Needs Work"
            value={loadingPerf ? '…' : (perf?.weakest_topic || '—')}
            color="var(--accent-orange)"
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1.5fr) minmax(0,1fr)', gap: '1.5rem', alignItems: 'start' }}>
          {/* Left column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Score chart */}
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
                <BarChart2 size={17} style={{ color: 'var(--accent-blue)' }} />
                <h2 style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>Score History</h2>
              </div>

              {loadingPerf ? (
                <div style={{ textAlign: 'center', padding: '2rem 0' }}>
                  <div className="spinner" style={{ margin: '0 auto' }} />
                </div>
              ) : !perf?.records?.length ? (
                <div style={{ textAlign: 'center', padding: '2rem 0', color: 'var(--text-muted)' }}>
                  <BarChart2 size={32} style={{ margin: '0 auto 0.75rem', display: 'block', opacity: 0.3 }} />
                  <p style={{ fontSize: '0.875rem' }}>No sessions yet. Start learning to see your chart!</p>
                  <button className="btn-primary" onClick={() => navigate('/dashboard')} style={{ margin: '1rem auto 0', display: 'flex', fontSize: '0.85rem', padding: '0.5rem 1.25rem' }}>
                    Start a Lesson <ChevronRight size={14} />
                  </button>
                </div>
              ) : (
                <ScoreChart records={perf.records} />
              )}
            </div>

            {/* AI Insights */}
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
                <Sparkles size={17} style={{ color: 'var(--accent-purple)' }} />
                <h2 style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>AI Insights</h2>
                {loadingInsights && <span className="spinner" style={{ width: 16, height: 16, marginLeft: 'auto' }} />}
              </div>

              {!hasEnoughSessions ? (
                <LockedSection sessionsLeft={sessionsLeft} />
              ) : insightsError ? (
                <div style={{ display: 'flex', gap: '0.5rem', color: '#ef4444', fontSize: '0.875rem' }}>
                  <AlertCircle size={15} style={{ flexShrink: 0, marginTop: 1 }} />
                  {insightsError}
                </div>
              ) : !loadingInsights && insights ? (
                <InsightsPanel insights={insights} />
              ) : loadingInsights ? (
                <div style={{ textAlign: 'center', padding: '2rem 0' }}>
                  <div className="spinner" style={{ margin: '0 auto 0.875rem' }} />
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Analyzing your performance…</p>
                </div>
              ) : null}
            </div>
          </div>

          {/* Right column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Strategy recommendation */}
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
                <Target size={17} style={{ color: 'var(--accent-cyan)' }} />
                <h2 style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>Next Topic</h2>
                {loadingStrategy && <span className="spinner" style={{ width: 16, height: 16, marginLeft: 'auto' }} />}
              </div>

              {!hasEnoughSessions ? (
                <LockedSection sessionsLeft={sessionsLeft} />
              ) : strategyError ? (
                <p style={{ color: '#ef4444', fontSize: '0.875rem' }}>{strategyError}</p>
              ) : !loadingStrategy && strategy ? (
                <div className="fade-in">
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '0.35rem' }}>Recommended topic:</p>
                  <p style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 700, fontSize: '1.1rem', color: 'var(--accent-cyan)', marginBottom: '0.75rem' }}>
                    {strategy.next_topic}
                  </p>
                  {strategy.rationale && (
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', lineHeight: 1.6, marginBottom: '1rem' }}>
                      {strategy.rationale}
                    </p>
                  )}
                  {strategy.estimated_difficulty && (
                    <div style={{ marginBottom: '1rem' }}>
                      <span className={`badge badge-${strategy.estimated_difficulty}`}>
                        {strategy.estimated_difficulty}
                      </span>
                    </div>
                  )}
                  <button
                    id="study-next-topic-btn"
                    className="btn-primary"
                    onClick={() => navigate('/dashboard')}
                    style={{ width: '100%', justifyContent: 'center', fontSize: '0.875rem' }}
                  >
                    Study This <ChevronRight size={15} />
                  </button>
                </div>
              ) : loadingStrategy ? (
                <div style={{ textAlign: 'center', padding: '1.5rem 0' }}>
                  <div className="spinner" style={{ margin: '0 auto 0.75rem' }} />
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Planning your next step…</p>
                </div>
              ) : null}
            </div>

            {/* Recent sessions list */}
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)', marginBottom: '1rem' }}>All Sessions</h3>
              {loadingPerf ? (
                <div className="spinner" style={{ margin: '1rem auto', display: 'block' }} />
              ) : !perf?.records?.length ? (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center' }}>No sessions yet.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: 380, overflowY: 'auto' }}>
                  {perf.records.map((r, i) => {
                    const scoreColor = r.score >= 4 ? 'var(--accent-green)' : r.score >= 2 ? 'var(--accent-blue)' : 'var(--accent-orange)'
                    return (
                      <div key={r.id} style={{
                        display: 'flex', alignItems: 'center', gap: '0.75rem',
                        padding: '0.6rem 0.75rem', borderRadius: 8,
                        background: i % 2 === 0 ? 'rgba(255,255,255,0.02)' : 'transparent',
                      }}>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <p style={{ fontWeight: 500, fontSize: '0.8rem', color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', margin: 0 }}>
                            {r.topic}
                          </p>
                          <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0 }}>
                            {new Date(r.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <span style={{ fontWeight: 700, fontSize: '0.85rem', color: scoreColor, flexShrink: 0 }}>
                          {r.score}/5
                        </span>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
