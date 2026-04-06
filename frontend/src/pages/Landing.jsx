/**
 * Landing page — hero, features, CTA.
 */
import { Link } from 'react-router-dom'
import { Brain, Zap, BarChart2, Target, ArrowRight, Sparkles } from 'lucide-react'

const FEATURES = [
  {
    icon: <Sparkles size={24} />,
    color: 'var(--accent-blue)',
    title: 'AI-Generated Lessons',
    desc: 'Claude generates rich, structured lesson content on any topic, at your exact difficulty level — in seconds.',
  },
  {
    icon: <Brain size={24} />,
    color: 'var(--accent-purple)',
    title: '5 Specialized AI Agents',
    desc: 'Content, Quiz, Difficulty, Performance, and Strategy agents work together to build a personalized learning loop.',
  },
  {
    icon: <Zap size={24} />,
    color: 'var(--accent-cyan)',
    title: 'Adaptive Difficulty',
    desc: 'Score 4-5? The system upgrades your level. Struggling? It scales back. Always in your zone of proximal development.',
  },
  {
    icon: <BarChart2 size={24} />,
    color: 'var(--accent-green)',
    title: 'Deep Performance Analytics',
    desc: "Track session history, get AI-generated insights on your strengths and weaknesses, and visual score trends.",
  },
  {
    icon: <Target size={24} />,
    color: 'var(--accent-orange)',
    title: 'Smart Topic Recommendations',
    desc: 'The Strategy Agent analyzes your learning gaps and tells you exactly what to study next.',
  },
]

export default function Landing() {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* ── Simple top bar ── */}
      <nav style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '1.25rem 2rem',
        borderBottom: '1px solid var(--border)',
        background: 'rgba(10,15,30,0.8)',
        backdropFilter: 'blur(12px)',
        position: 'sticky', top: 0, zIndex: 50,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{
            width: 36, height: 36,
            background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
            borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Brain size={20} color="white" />
          </div>
          <span style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, fontSize: '1.15rem', color: 'var(--text-primary)' }}>
            Adaptive<span style={{ color: 'var(--accent-blue)' }}>Tutor</span>
          </span>
        </div>
        <Link to="/login">
          <button className="btn-primary" id="landing-cta-btn" style={{ padding: '0.5rem 1.25rem', fontSize: '0.9rem' }}>
            Get Started Free <ArrowRight size={15} />
          </button>
        </Link>
      </nav>

      {/* ── Hero ── */}
      <section style={{
        maxWidth: 900, margin: '0 auto', textAlign: 'center',
        padding: '6rem 2rem 4rem',
      }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
          background: 'rgba(99,136,255,0.1)', border: '1px solid rgba(99,136,255,0.25)',
          borderRadius: 999, padding: '0.3rem 1rem', marginBottom: '1.75rem',
          fontSize: '0.8rem', color: 'var(--accent-blue)', fontWeight: 600,
        }}>
          <Sparkles size={14} />
          Powered by Anthropic Claude — 5 Specialized AI Agents
        </div>

        <h1 style={{
          fontFamily: 'Outfit, sans-serif', fontWeight: 900,
          fontSize: 'clamp(2.25rem, 6vw, 4rem)',
          lineHeight: 1.1, marginBottom: '1.5rem',
          color: 'var(--text-primary)',
        }}>
          Learn Anything.<br />
          <span className="gradient-text">At Your Own Pace.</span>
        </h1>

        <p style={{
          fontSize: 'clamp(1rem, 2.5vw, 1.2rem)',
          color: 'var(--text-secondary)', lineHeight: 1.75,
          maxWidth: 640, margin: '0 auto 2.5rem',
        }}>
          AdaptiveTutor uses 5 AI agents to generate custom lessons, quiz you, 
          automatically adjust difficulty, and guide your next steps — all personalized to you.
        </p>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/login">
            <button id="hero-start-btn" className="btn-primary" style={{ padding: '0.875rem 2rem', fontSize: '1rem' }}>
              Start Learning Now <ArrowRight size={18} />
            </button>
          </Link>
        </div>
      </section>

      {/* ── Features ── */}
      <section style={{ maxWidth: 1100, margin: '0 auto', padding: '2rem 2rem 6rem' }}>
        <h2 style={{
          fontFamily: 'Outfit, sans-serif', fontWeight: 800,
          fontSize: 'clamp(1.5rem, 3vw, 2rem)',
          textAlign: 'center', color: 'var(--text-primary)', marginBottom: '3rem',
        }}>
          Everything You Need to Learn Smarter
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1.25rem',
        }}>
          {FEATURES.map((f) => (
            <FeatureCard key={f.title} {...f} />
          ))}
        </div>
      </section>

      {/* ── CTA Banner ── */}
      <section style={{
        background: 'linear-gradient(135deg, rgba(99,136,255,0.12) 0%, rgba(159,122,234,0.08) 100%)',
        border: '1px solid var(--border)',
        borderRadius: 24, margin: '0 2rem 5rem', padding: '3rem 2rem',
        maxWidth: 1100, marginLeft: 'auto', marginRight: 'auto',
        textAlign: 'center',
      }}>
        <h2 style={{
          fontFamily: 'Outfit, sans-serif', fontWeight: 800,
          fontSize: 'clamp(1.5rem, 3vw, 2.25rem)',
          color: 'var(--text-primary)', marginBottom: '1rem',
        }}>
          Ready to start learning?
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', marginBottom: '2rem', maxWidth: 500, margin: '0 auto 2rem' }}>
          Your personalized AI tutor is waiting. No setup needed — just pick a topic and go.
        </p>
        <Link to="/login">
          <button className="btn-primary" style={{ padding: '0.875rem 2.5rem', fontSize: '1rem' }}>
            Create Free Account <ArrowRight size={18} />
          </button>
        </Link>
      </section>
    </div>
  )
}

function FeatureCard({ icon, color, title, desc }) {
  return (
    <div className="glass-card" style={{ padding: '1.5rem' }}>
      <div style={{
        width: 48, height: 48,
        background: `${color}18`,
        border: `1px solid ${color}35`,
        borderRadius: 12,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        marginBottom: '1rem', color,
      }}>
        {icon}
      </div>
      <h3 style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
        {title}
      </h3>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: 1.65, margin: 0 }}>
        {desc}
      </p>
    </div>
  )
}
