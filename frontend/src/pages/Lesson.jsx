/**
 * Lesson page — displays AI-generated lesson content.
 * Route: /lesson/:lessonId
 */
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { lessonsApi, quizzesApi } from '../api/client'
import Navbar from '../components/Navbar'
import { BookOpen, Clock, Tag, ChevronRight, AlertCircle, ArrowLeft } from 'lucide-react'

export default function Lesson() {
  const { lessonId } = useParams()
  const navigate = useNavigate()

  const [lesson, setLesson] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [quizLoading, setQuizLoading] = useState(false)
  const [quizError, setQuizError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const res = await lessonsApi.get(lessonId)
        setLesson(res.data)
      } catch (err) {
        if (err.response?.status === 404) {
          setError('This lesson was not found.')
        } else {
          setError('Failed to load lesson. Please go back and try again.')
        }
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [lessonId])

  async function handleStartQuiz() {
    setQuizLoading(true)
    setQuizError('')
    try {
      const res = await quizzesApi.generate({ lesson_id: lessonId })
      // Pass quiz data via state to avoid re-fetching
      navigate(`/quiz/${lessonId}`, { state: { questions: res.data } })
    } catch (err) {
      setQuizError(err.response?.data?.detail || 'Failed to generate quiz. Please try again.')
    } finally {
      setQuizLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />

      <main style={{ maxWidth: 820, margin: '0 auto', padding: '2rem 1.5rem' }}>
        {/* Back link */}
        <button
          onClick={() => navigate('/dashboard')}
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: '0.4rem',
            color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem',
            padding: 0, transition: 'color 0.15s',
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = 'var(--text-primary)'}
          onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-muted)'}
        >
          <ArrowLeft size={15} /> Back to Dashboard
        </button>

        {/* Loading */}
        {loading && (
          <div style={{ textAlign: 'center', padding: '5rem 0' }}>
            <div className="spinner" style={{ width: 40, height: 40, margin: '0 auto 1.25rem' }} />
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Loading lesson…</p>
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div style={{
            display: 'flex', alignItems: 'flex-start', gap: '0.5rem',
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)',
            borderRadius: 10, padding: '1rem',
          }}>
            <AlertCircle size={16} style={{ color: '#ef4444', flexShrink: 0, marginTop: 1 }} />
            <p style={{ color: '#ef4444', margin: 0 }}>{error}</p>
          </div>
        )}

        {/* Lesson content */}
        {lesson && !loading && (
          <div className="fade-in">
            {/* Header card */}
            <div className="glass-card" style={{ padding: '1.75rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.875rem', flexWrap: 'wrap' }}>
                <span className={`badge badge-${lesson.difficulty}`}>{lesson.difficulty}</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  <Clock size={12} /> ~{lesson.estimated_duration_minutes} min read
                </span>
              </div>

              <h1 style={{
                fontFamily: 'Outfit, sans-serif', fontWeight: 800,
                fontSize: 'clamp(1.4rem, 4vw, 2rem)',
                color: 'var(--text-primary)', lineHeight: 1.25, marginBottom: '1.25rem',
              }}>
                {lesson.title}
              </h1>

              {/* Key concepts */}
              {lesson.key_concepts?.length > 0 && (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.6rem' }}>
                    <Tag size={13} style={{ color: 'var(--accent-blue)' }} />
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 600 }}>Key Concepts</span>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                    {lesson.key_concepts.map((c) => (
                      <span key={c} style={{
                        background: 'rgba(99,136,255,0.1)',
                        border: '1px solid rgba(99,136,255,0.2)',
                        borderRadius: 999, padding: '0.2rem 0.7rem',
                        fontSize: '0.75rem', color: 'var(--accent-blue)', fontWeight: 500,
                      }}>{c}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Lesson content */}
            <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
              <div className="prose">
                <ReactMarkdown>{lesson.content}</ReactMarkdown>
              </div>
            </div>

            {/* Quiz error */}
            {quizError && (
              <div style={{
                display: 'flex', gap: '0.5rem',
                background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)',
                borderRadius: 10, padding: '0.875rem 1rem', marginBottom: '1rem',
              }}>
                <AlertCircle size={15} style={{ color: '#ef4444', flexShrink: 0, marginTop: 1 }} />
                <p style={{ color: '#ef4444', margin: 0, fontSize: '0.875rem' }}>{quizError}</p>
              </div>
            )}

            {/* Take Quiz CTA */}
            <div className="glass-card" style={{
              padding: '1.5rem', textAlign: 'center',
              background: 'linear-gradient(135deg, rgba(99,136,255,0.08), rgba(159,122,234,0.05))',
              borderColor: 'rgba(99,136,255,0.2)',
            }}>
              <BookOpen size={28} style={{ color: 'var(--accent-blue)', marginBottom: '0.75rem' }} />
              <h3 style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
                Ready to Test Your Knowledge?
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.25rem' }}>
                Take a 5-question quiz to reinforce what you've learned. The AI will adjust your difficulty based on your score.
              </p>
              <button
                id="start-quiz-btn"
                className="btn-primary"
                onClick={handleStartQuiz}
                disabled={quizLoading}
                style={{ padding: '0.875rem 2rem', fontSize: '1rem', margin: '0 auto', display: 'inline-flex' }}
              >
                {quizLoading ? (
                  <>
                    <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
                    Generating quiz…
                  </>
                ) : (
                  <>
                    Take the Quiz <ChevronRight size={18} />
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
