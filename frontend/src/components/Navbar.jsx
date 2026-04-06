/**
 * Navbar — top navigation bar.
 */
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { BookOpen, BarChart2, LogOut, Brain } from 'lucide-react'

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  function handleLogout() {
    logout()
    navigate('/')
  }

  const isActive = (path) => location.pathname === path

  return (
    <nav style={{
      background: 'rgba(10,15,30,0.85)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
    }}>
      <div style={{
        maxWidth: 1200,
        margin: '0 auto',
        padding: '0 1.5rem',
        height: 64,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* Logo */}
        <Link to={isAuthenticated ? '/dashboard' : '/'} style={{
          display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none'
        }}>
          <div style={{
            width: 36, height: 36,
            background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
            borderRadius: 10,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Brain size={20} color="white" />
          </div>
          <span style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, fontSize: '1.1rem', color: 'var(--text-primary)' }}>
            Adaptive<span style={{ color: 'var(--accent-blue)' }}>Tutor</span>
          </span>
        </Link>

        {/* Nav Links */}
        {isAuthenticated && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <NavLink to="/dashboard" active={isActive('/dashboard')} icon={<BookOpen size={16} />}>
              Dashboard
            </NavLink>
            <NavLink to="/performance" active={isActive('/performance')} icon={<BarChart2 size={16} />}>
              Performance
            </NavLink>
          </div>
        )}

        {/* Right side */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {isAuthenticated ? (
            <>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                {user?.username}
              </span>
              <DifficultyBadge difficulty={user?.current_difficulty} />
              <button
                id="nav-logout-btn"
                onClick={handleLogout}
                className="btn-secondary"
                style={{ padding: '0.4rem 0.9rem', fontSize: '0.875rem' }}
              >
                <LogOut size={14} />
                Logout
              </button>
            </>
          ) : (
            <Link to="/login">
              <button className="btn-primary" style={{ padding: '0.5rem 1.25rem', fontSize: '0.875rem' }}>
                Get Started
              </button>
            </Link>
          )}
        </div>
      </div>
    </nav>
  )
}

function NavLink({ to, active, icon, children }) {
  return (
    <Link to={to} style={{ textDecoration: 'none' }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: '0.4rem',
        padding: '0.4rem 0.875rem',
        borderRadius: 8,
        fontSize: '0.875rem',
        fontWeight: 500,
        color: active ? 'var(--accent-blue)' : 'var(--text-secondary)',
        background: active ? 'rgba(99,136,255,0.12)' : 'transparent',
        transition: 'all 0.15s',
        cursor: 'pointer',
      }}>
        {icon}
        {children}
      </div>
    </Link>
  )
}

function DifficultyBadge({ difficulty }) {
  if (!difficulty) return null
  return (
    <span className={`badge badge-${difficulty}`}>
      {difficulty}
    </span>
  )
}
