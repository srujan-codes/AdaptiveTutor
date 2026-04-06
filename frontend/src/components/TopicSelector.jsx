/**
 * TopicSelector — lets users pick a topic and start a lesson.
 */
import { useState } from 'react'
import { Sparkles, ChevronDown } from 'lucide-react'

const SUGGESTED_TOPICS = [
  'Python Basics', 'JavaScript Promises', 'React Hooks',
  'SQL Joins', 'Machine Learning Fundamentals', 'REST APIs',
  'Data Structures: Arrays', 'Sorting Algorithms', 'CSS Flexbox',
  'Git Version Control', 'Docker Fundamentals', 'TypeScript Generics',
]

const DIFFICULTIES = ['beginner', 'intermediate', 'advanced']

/**
 * @param {{ onGenerate: (topic: string, difficulty: string) => void, loading: boolean }} props
 */
export default function TopicSelector({ onGenerate, loading }) {
  const [topic, setTopic] = useState('')
  const [difficulty, setDifficulty] = useState('beginner')
  const [showSuggestions, setShowSuggestions] = useState(false)

  function handleSubmit(e) {
    e.preventDefault()
    if (!topic.trim() || loading) return
    onGenerate(topic.trim(), difficulty)
  }

  function pickSuggestion(t) {
    setTopic(t)
    setShowSuggestions(false)
  }

  return (
    <div className="glass-card" style={{ padding: '1.75rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem' }}>
        <Sparkles size={20} style={{ color: 'var(--accent-blue)' }} />
        <h2 style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 700, fontSize: '1.125rem', color: 'var(--text-primary)' }}>
          Start a New Lesson
        </h2>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Topic input */}
        <div style={{ position: 'relative', marginBottom: '1rem' }}>
          <input
            id="topic-input"
            type="text"
            className="input-field"
            placeholder="Enter any topic (e.g. Python Lists, Recursion…)"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
            autoComplete="off"
          />

          {/* Suggestions dropdown */}
          {showSuggestions && !topic && (
            <div style={{
              position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 20,
              background: 'var(--bg-card)', border: '1px solid var(--border)',
              borderRadius: 10, marginTop: 4, overflow: 'hidden',
              boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
            }}>
              {SUGGESTED_TOPICS.map((t) => (
                <button
                  key={t}
                  type="button"
                  onMouseDown={() => pickSuggestion(t)}
                  style={{
                    display: 'block', width: '100%', textAlign: 'left',
                    padding: '0.6rem 1rem', background: 'transparent',
                    color: 'var(--text-secondary)', fontSize: '0.875rem',
                    border: 'none', cursor: 'pointer', transition: 'background 0.15s',
                  }}
                  onMouseEnter={(e) => e.target.style.background = 'rgba(99,136,255,0.1)'}
                  onMouseLeave={(e) => e.target.style.background = 'transparent'}
                >
                  {t}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Difficulty selector */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
          {DIFFICULTIES.map((d) => (
            <button
              key={d}
              type="button"
              id={`difficulty-${d}`}
              onClick={() => setDifficulty(d)}
              style={{
                padding: '0.4rem 1rem',
                borderRadius: 8,
                fontSize: '0.8rem',
                fontWeight: 600,
                textTransform: 'capitalize',
                cursor: 'pointer',
                border: '1px solid',
                transition: 'all 0.15s',
                ...(difficulty === d
                  ? {
                      background: d === 'beginner' ? 'rgba(52,211,153,0.2)' : d === 'intermediate' ? 'rgba(99,136,255,0.2)' : 'rgba(251,146,60,0.2)',
                      borderColor: d === 'beginner' ? 'var(--accent-green)' : d === 'intermediate' ? 'var(--accent-blue)' : 'var(--accent-orange)',
                      color: d === 'beginner' ? 'var(--accent-green)' : d === 'intermediate' ? 'var(--accent-blue)' : 'var(--accent-orange)',
                    }
                  : {
                      background: 'transparent',
                      borderColor: 'var(--border)',
                      color: 'var(--text-secondary)',
                    }),
              }}
            >
              {d}
            </button>
          ))}
        </div>

        <button
          id="generate-lesson-btn"
          type="submit"
          className="btn-primary"
          disabled={!topic.trim() || loading}
          style={{ width: '100%', justifyContent: 'center' }}
        >
          {loading ? (
            <>
              <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
              Generating lesson…
            </>
          ) : (
            <>
              <Sparkles size={16} />
              Generate Lesson
            </>
          )}
        </button>
      </form>
    </div>
  )
}
