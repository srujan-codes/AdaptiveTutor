/**
 * Dashboard — main hub after login.
 * Shows: topic selector, recent sessions, stats, recommended topic.
 */
import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { lessonsApi, performanceApi, strategyApi } from '../api/client'
import Navbar from '../components/Navbar'
import TopicSelector from '../components/TopicSelector'
import {
  BookOpen, Target, TrendingUp, Clock, ChevronRight,
  Zap, AlertCircle, BarChart2,
} from 'lucide-react'

function StatCard({ icon, label, value, color }) {
  return (
    <div className="glass-card" style={{ padding: '1.25rem 1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <div style={{
        width: 44, height: 44,
        background: `${color}18`,
        border: `1px solid ${color}30`,
        borderRadius: 12,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color, flexShrink: 0,
      }}>
        {icon}
      </div>
      <div>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 500, marginBottom: 2 }}>{label}</div>
        <div style={{ color: 'var(--text-primary)', fontWeight: 700, fontSize: '1.375rem', lineHeight: 1 }}>{value}</div>
      </div>
    </div>
  )
}

function SessionRow({ record, index }) {
  const scoreColor = record.score >= 4 ? 'var(--accent-green)' : record.score >= 2 ? 'var(--accent-blue)' : 'var(--accent-orange)'
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '1rem',
      padding: '0.875rem 1rem',
      borderRadius: 10,
      background: index % 2 === 0 ? 'rgba(255,255,255,0.02)' : 'transparent',
      transition: 'background 0.15s',
    }}>
      <div style={{
        width: 36, height: 36, borderRadius: 10,
        background: 'rgba(99,136,255,0.1)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: 'var(--accent-blue)', fontSize: '0.8rem', fontWeight: 700, flexShrink: 0,
      }}>
        {index + 1}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '0.9rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {record.topic}
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginTop: 2 }}>
          <span className={`badge badge-${record.difficulty}`} style={{ padding: '0.1rem 0.5rem', fontSize: '0.65rem' }}>
            {record.difficulty}
          </span>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
            {new Date(record.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>
      <div style={{ color: scoreColor, fontWeight: 700, fontSize: '1rem', flexShrink: 0 }}>
        {record.score}/5
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { user, refreshUser } = useAuth()
  const navigate = useNavigate()

  const [perf, setPerf] = useState(null)
  const [strategy, setStrategy] = useState(null)
  const [loadingPerf, setLoadingPerf] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [genError, setGenError] = useState('')

  const loadData = useCallback(async () => {
    setLoadingPerf(true)
    try {
      const [perfRes] = await Promise.allSettled([performanceApi.list()])
      if (perfRes.status === 'fulfilled') setPerf(perfRes.value.data)

      // Only fetch strategy if >= 3 sessions
      if (perfRes.status === 'fulfilled' && perfRes.value.data.total_sessions >= 3) {
        try {
          const stratRes = await strategyApi.nextTopic()
          setStrategy(stratRes.data)
        } catch { /* < 3 sessions or error — no strategy yet */ }
      }
    } catch (err) {
      console.error('Failed to load dashboard data', err)
    } finally {
      setLoadingPerf(false)
    }
  }, [])

  useEffect(() => {
    loadData()
    refreshUser()
  }, [loadData, refreshUser])

  async function handleGenerate(topic, difficulty) {
    setGenerating(true)
    setGenError('')
    try {
      const res = await lessonsApi.generate({ topic, difficulty })
      navigate(`/lesson/${res.data.id}`)
    } catch (err) {
      setGenError(err.response?.data?.detail || 'Failed to generate lesson. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  const totalSessions = perf?.total_sessions ?? 0
  const avgScore = perf?.average_score != null ? (perf.average_score / 5 * 100).toFixed(0) : '—'
  const recentRecords = perf?.records?.slice(0, 8) ?? []

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />

      <main style={{ maxWidth: 1100, margin: '0 auto', padding: '2rem 1.5rem' }}>
        {/* Header */}
        <div style={{ marginBottom: '2rem' }}>
          <h1 style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, fontSize: 'clamp(1.5rem,4vw,2rem)', color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
            Welcome back, {user?.username} 👋
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            What would you like to learn today?
          </p>
        </div>

        {/* Gen error */}
        {genError && (
          <div style={{
            display: 'flex', alignItems: 'flex-start', gap: '0.5rem',
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)',
            borderRadius: 10, padding: '0.875rem 1rem', marginBottom: '1.5rem',
          }}>
            <AlertCircle size={16} style={{ color: '#ef4444', flexShrink: 0, marginTop: 2 }} />
            <p style={{ color: '#ef4444', fontSize: '0.875rem', margin: 0 }}>{genError}</p>
          </div>
        )}

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0,1.4fr) minmax(0,1fr)',
          gap: '1.5rem',
          alignItems: 'start',
        }}>
          {/* Left column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Topic selector */}
            <TopicSelector onGenerate={handleGenerate} loading={generating} />

            {/* Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <StatCard
                icon={<BookOpen size={20} />}
                label="Sessions"
                value={loadingPerf ? '…' : totalSessions}
                color="var(--accent-blue)"
              />
              <StatCard
                icon={<TrendingUp size={20} />}
                label="Avg Score"
                value={loadingPerf ? '…' : `${avgScore}%`}
                color="var(--accent-green)"
              />
              <StatCard
                icon={<Zap size={20} />}
                label="Level"
                value={user?.current_difficulty ?? '—'}
                color="var(--accent-purple)"
              />
              <StatCard
                icon={<Target size={20} />}
                label="Best Topic"
                value={loadingPerf ? '…' : (perf?.best_topic ? perf.best_topic.split(' ').slice(0,1)[0] : '—')}
                color="var(--accent-orange)"
              />
            </div>
          </div>

          {/* Right column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Recommended next topic */}
            {strategy && (
              <div className="glass-card fade-in" style={{ padding: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.875rem' }}>
                  <Target size={16} style={{ color: 'var(--accent-purple)' }} />
                  <h3 style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)' }}>AI Recommendation</h3>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Next topic to study:</p>
                <p style={{ fontWeight: 700, fontSize: '1.05rem', color: 'var(--accent-cyan)', marginBottom: '0.5rem' }}>
                  {strategy.next_topic}
                </p>
                {strategy.rationale && (
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.55, marginBottom: '1rem' }}>
                    {strategy.rationale}
                  </p>
                )}
                <button
                  id="study-recommended-btn"
                  className="btn-primary"
                  onClick={() => handleGenerate(strategy.next_topic, user?.current_difficulty || 'beginner')}
                  disabled={generating}
                  style={{ width: '100%', justifyContent: 'center', fontSize: '0.85rem', padding: '0.625rem' }}
                >
                  Study This Topic <ChevronRight size={15} />
                </button>
              </div>
            )}

            {/* Less than 3 sessions prompt */}
            {!strategy && totalSessions < 3 && !loadingPerf && (
              <div className="glass-card" style={{
                padding: '1.25rem', textAlign: 'center',
                borderColor: 'rgba(159,122,234,0.2)',
                background: 'rgba(159,122,234,0.05)',
              }}>
                <Target size={28} style={{ color: 'var(--accent-purple)', marginBottom: '0.75rem' }} />
                <p style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.9rem', marginBottom: '0.4rem' }}>
                  Unlock Smart Recommendations
                </p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', lineHeight: 1.55 }}>
                  Complete <strong style={{ color: 'var(--accent-purple)' }}>{3 - totalSessions} more {3 - totalSessions === 1 ? 'session' : 'sessions'}</strong> to
                  get AI-powered topic recommendations.
                </p>
              </div>
            )}

            {/* Recent sessions */}
            <div className="glass-card" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Clock size={15} style={{ color: 'var(--accent-blue)' }} />
                  <h3 style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)' }}>Recent Sessions</h3>
                </div>
                <a href="/performance" style={{ color: 'var(--accent-blue)', fontSize: '0.75rem', fontWeight: 500, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                  View all <ChevronRight size={13} />
                </a>
              </div>

              {loadingPerf ? (
                <div style={{ textAlign: 'center', padding: '1.5rem 0' }}>
                  <div className="spinner" style={{ margin: '0 auto' }} />
                </div>
              ) : recentRecords.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '1.5rem 0', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                  <BookOpen size={28} style={{ margin: '0 auto 0.75rem', display: 'block', opacity: 0.4 }} />
                  No sessions yet. Start your first lesson!
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.1rem' }}>
                  {recentRecords.map((r, i) => <SessionRow key={r.id} record={r} index={i} />)}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
