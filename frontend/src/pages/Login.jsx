/**
 * Login page — handles both login and registration.
 */
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Brain, Eye, EyeOff, AlertCircle } from 'lucide-react'

export default function Login() {
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [form, setForm] = useState({ email: '', username: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { login, register } = useAuth()
  const navigate = useNavigate()

  function handleChange(e) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
    setError('')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    // Basic validation
    if (!form.email || !form.password) {
      setError('Please fill in all required fields.')
      return
    }
    if (mode === 'register' && !form.username) {
      setError('Username is required.')
      return
    }
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }

    setLoading(true)
    try {
      if (mode === 'login') {
        await login(form.email, form.password)
      } else {
        await register(form.email, form.username, form.password)
      }
      navigate('/dashboard')
    } catch (err) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else if (err.response?.status === 409) {
        setError('An account with this email or username already exists.')
      } else if (err.response?.status === 401) {
        setError('Invalid email or password.')
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg-primary)', padding: '2rem',
      position: 'relative', overflow: 'hidden',
    }}>
      {/* Background glow */}
      <div style={{
        position: 'absolute', top: -200, left: '50%', transform: 'translateX(-50%)',
        width: 600, height: 600,
        background: 'radial-gradient(circle, rgba(99,136,255,0.12) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      <div className="glass-card fade-in" style={{
        width: '100%', maxWidth: 440, padding: '2.5rem',
        position: 'relative', zIndex: 1,
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: 52, height: 52,
            background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
            borderRadius: 14, display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 1rem',
          }}>
            <Brain size={26} color="white" />
          </div>
          <h1 style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, fontSize: '1.6rem', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
            {mode === 'login' ? 'Welcome back' : 'Create account'}
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            {mode === 'login' ? 'Sign in to continue learning' : 'Start your adaptive learning journey'}
          </p>
        </div>

        {/* Mode toggle */}
        <div style={{
          display: 'flex', background: 'rgba(255,255,255,0.04)',
          border: '1px solid var(--border)', borderRadius: 10,
          padding: 4, marginBottom: '1.5rem',
        }}>
          {['login', 'register'].map((m) => (
            <button
              key={m}
              id={`tab-${m}`}
              type="button"
              onClick={() => { setMode(m); setError('') }}
              style={{
                flex: 1, padding: '0.55rem', borderRadius: 7,
                fontSize: '0.875rem', fontWeight: 600, border: 'none', cursor: 'pointer',
                transition: 'all 0.2s',
                background: mode === m ? 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))' : 'transparent',
                color: mode === m ? 'white' : 'var(--text-secondary)',
              }}
            >
              {m === 'login' ? 'Sign In' : 'Register'}
            </button>
          ))}
        </div>

        {/* Error banner */}
        {error && (
          <div style={{
            display: 'flex', alignItems: 'flex-start', gap: '0.5rem',
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)',
            borderRadius: 8, padding: '0.75rem 0.875rem', marginBottom: '1.25rem',
          }}>
            <AlertCircle size={16} style={{ color: '#ef4444', flexShrink: 0, marginTop: 1 }} />
            <p style={{ color: '#ef4444', fontSize: '0.875rem', margin: 0 }}>{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 500, marginBottom: '0.4rem' }}>
              Email
            </label>
            <input
              id="email-input"
              type="email"
              name="email"
              className="input-field"
              placeholder="you@example.com"
              value={form.email}
              onChange={handleChange}
              required
              autoComplete="email"
            />
          </div>

          {mode === 'register' && (
            <div>
              <label style={{ display: 'block', color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 500, marginBottom: '0.4rem' }}>
                Username
              </label>
              <input
                id="username-input"
                type="text"
                name="username"
                className="input-field"
                placeholder="learner123"
                value={form.username}
                onChange={handleChange}
                autoComplete="username"
              />
            </div>
          )}

          <div>
            <label style={{ display: 'block', color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 500, marginBottom: '0.4rem' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="password-input"
                type={showPw ? 'text' : 'password'}
                name="password"
                className="input-field"
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
                required
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                style={{ paddingRight: '2.75rem' }}
              />
              <button
                type="button"
                onClick={() => setShowPw((v) => !v)}
                style={{
                  position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: 'var(--text-muted)', display: 'flex',
                }}
              >
                {showPw ? <EyeOff size={17} /> : <Eye size={17} />}
              </button>
            </div>
          </div>

          <button
            id="auth-submit-btn"
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ width: '100%', justifyContent: 'center', marginTop: '0.5rem', padding: '0.875rem' }}
          >
            {loading ? (
              <>
                <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
                {mode === 'login' ? 'Signing in…' : 'Creating account…'}
              </>
            ) : (
              mode === 'login' ? 'Sign In' : 'Create Account'
            )}
          </button>
        </form>

        <p style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '1.5rem' }}>
          <Link to="/" style={{ color: 'var(--accent-blue)', textDecoration: 'none', fontWeight: 500 }}>
            ← Back to home
          </Link>
        </p>
      </div>
    </div>
  )
}
