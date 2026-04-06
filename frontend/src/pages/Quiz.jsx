/**
 * Quiz page — 5 MCQ questions, submit, results.
 * Route: /quiz/:lessonId
 * Receives questions via router state (from Lesson page) to avoid re-fetching.
 */
import { useState } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { quizzesApi } from '../api/client'
import Navbar from '../components/Navbar'
import {
  CheckCircle, XCircle, AlertCircle, ChevronRight,
  Trophy, ArrowLeft, Lightbulb,
} from 'lucide-react'

const LETTERS = ['A', 'B', 'C', 'D']

function ScoreBadge({ score }) {
  const pct = Math.round(score / 5 * 100)
  const color = score >= 4 ? 'var(--accent-green)' : score >= 2 ? 'var(--accent-blue)' : 'var(--accent-orange)'
  const label = score === 5 ? 'Perfect! 🎉' : score >= 4 ? 'Great job!' : score >= 2 ? 'Good effort' : 'Keep practicing'
  return (
    <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
      <div style={{
        width: 100, height: 100,
        background: `${color}18`, border: `3px solid ${color}`,
        borderRadius: '50%', display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem',
      }}>
        <span style={{ fontSize: '1.75rem', fontWeight: 900, color, lineHeight: 1 }}>{score}</span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/ 5</span>
      </div>
      <p style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, fontSize: '1.5rem', color: 'var(--text-primary)', margin: '0 0 0.25rem' }}>
        {label}
      </p>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{pct}% correct</p>
    </div>
  )
}

export default function Quiz() {
  const { lessonId } = useParams()
  const { state } = useLocation()
  const navigate = useNavigate()
  const { refreshUser } = useAuth()

  // questions can come from router state (from Lesson page)
  const questions = state?.questions ?? []

  // answers[i] is "A" | "B" | "C" | "D" | null
  const [answers, setAnswers] = useState(Array(5).fill(null))
  const [submitting, setSubmitting] = useState(false)
  const [results, setResults] = useState(null) // QuizSubmitResponse
  const [submitError, setSubmitError] = useState('')

  // If navigated to directly without questions, redirect back
  if (!questions.length) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
        <Navbar />
        <div style={{ textAlign: 'center', padding: '5rem 2rem' }}>
          <AlertCircle size={40} style={{ color: '#ef4444', marginBottom: '1rem' }} />
          <h2 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Quiz not found</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Please start a lesson first to generate a quiz.
          </p>
          <button className="btn-primary" onClick={() => navigate('/dashboard')}>
            Go to Dashboard
          </button>
        </div>
      </div>
    )
  }

  function selectAnswer(qIdx, letter) {
    if (results) return // frozen after submit
    setAnswers((prev) => {
      const next = [...prev]
      next[qIdx] = letter
      return next
    })
  }

  async function handleSubmit() {
    // Validate all 5 answered — strict requirement
    const unanswered = answers.findIndex((a) => a === null)
    if (unanswered !== -1) {
      setSubmitError(`Please answer question ${unanswered + 1} before submitting.`)
      return
    }

    setSubmitting(true)
    setSubmitError('')
    try {
      const res = await quizzesApi.submit({
        lesson_id: lessonId,
        answers: answers, // exactly 5 strings: ["A", "C", "B", "D", "A"]
      })
      setResults(res.data)
      // Refresh user so navbar shows updated difficulty
      refreshUser()
    } catch (err) {
      setSubmitError(err.response?.data?.detail || 'Failed to submit quiz. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const allAnswered = answers.every((a) => a !== null)
  const answeredCount = answers.filter(Boolean).length

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />

      <main style={{ maxWidth: 740, margin: '0 auto', padding: '2rem 1.5rem' }}>
        {/* Back */}
        <button
          onClick={() => navigate(`/lesson/${lessonId}`)}
          disabled={!!results}
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: '0.4rem',
            color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem', padding: 0,
          }}
        >
          <ArrowLeft size={15} /> Back to Lesson
        </button>

        {/* Results view */}
        {results ? (
          <div className="fade-in">
            <div className="glass-card" style={{ padding: '1.75rem', marginBottom: '1.5rem' }}>
              <ScoreBadge score={results.score} />

              {/* New difficulty badge */}
              {results.new_difficulty && (
                <div style={{
                  textAlign: 'center', marginBottom: '1.5rem',
                  paddingTop: '1rem', borderTop: '1px solid var(--border)',
                }}>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '0.4rem' }}>
                    Your difficulty level
                  </p>
                  <span className={`badge badge-${results.new_difficulty}`} style={{ fontSize: '0.8rem' }}>
                    {results.new_difficulty}
                  </span>
                </div>
              )}
            </div>

            {/* Question breakdown */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
              {results.results.map((r, i) => {
                const q = questions[i]
                return (
                  <div key={i} className="glass-card" style={{
                    padding: '1.25rem',
                    borderColor: r.is_correct ? 'rgba(52,211,153,0.3)' : 'rgba(251,146,60,0.3)',
                    background: r.is_correct ? 'rgba(52,211,153,0.04)' : 'rgba(251,146,60,0.04)',
                  }}>
                    <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '0.75rem' }}>
                      {r.is_correct
                        ? <CheckCircle size={18} style={{ color: 'var(--accent-green)', flexShrink: 0, marginTop: 1 }} />
                        : <XCircle size={18} style={{ color: 'var(--accent-orange)', flexShrink: 0, marginTop: 1 }} />}
                      <p style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.9rem', margin: 0 }}>
                        Q{r.question_number}. {q?.question_text}
                      </p>
                    </div>

                    {/* Show options */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginBottom: '0.75rem', paddingLeft: '1.75rem' }}>
                      {q?.options.map((opt, oi) => {
                        const letter = LETTERS[oi]
                        const isUserAnswer = r.user_answer === letter
                        const isCorrect = r.correct_answer === letter
                        let bg = 'transparent', color = 'var(--text-secondary)', border = '1px solid transparent'
                        if (isCorrect) { bg = 'rgba(52,211,153,0.1)'; color = 'var(--accent-green)'; border = '1px solid rgba(52,211,153,0.3)' }
                        else if (isUserAnswer && !isCorrect) { bg = 'rgba(251,146,60,0.1)'; color = 'var(--accent-orange)'; border = '1px solid rgba(251,146,60,0.3)' }
                        return (
                          <div key={oi} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', padding: '0.35rem 0.6rem', borderRadius: 7, background: bg, border, transition: 'all 0.15s' }}>
                            <span style={{ fontWeight: 700, fontSize: '0.8rem', color, minWidth: 18 }}>{letter}.</span>
                            <span style={{ fontSize: '0.85rem', color }}>{opt}</span>
                            {isCorrect && <CheckCircle size={13} style={{ color: 'var(--accent-green)', marginLeft: 'auto' }} />}
                            {isUserAnswer && !isCorrect && <XCircle size={13} style={{ color: 'var(--accent-orange)', marginLeft: 'auto' }} />}
                          </div>
                        )
                      })}
                    </div>

                    {/* Explanation */}
                    {r.explanation && (
                      <div style={{
                        display: 'flex', gap: '0.5rem', paddingLeft: '1.75rem',
                        background: 'rgba(99,136,255,0.06)', borderRadius: 8, padding: '0.6rem 0.75rem',
                      }}>
                        <Lightbulb size={13} style={{ color: 'var(--accent-blue)', flexShrink: 0, marginTop: 2 }} />
                        <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                          {r.explanation}
                        </p>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', gap: '0.875rem', flexWrap: 'wrap' }}>
              <button className="btn-primary" id="go-dashboard-btn" onClick={() => navigate('/dashboard')} style={{ flex: 1, justifyContent: 'center' }}>
                <Trophy size={16} /> Back to Dashboard
              </button>
              <button className="btn-secondary" id="view-performance-btn" onClick={() => navigate('/performance')} style={{ flex: 1, justifyContent: 'center' }}>
                <ChevronRight size={16} /> View Performance
              </button>
            </div>
          </div>
        ) : (
          /* Quiz form */
          <div className="fade-in">
            {/* Header */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h1 style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, fontSize: '1.75rem', color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
                Knowledge Check
              </h1>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                  Answer all 5 questions to submit.
                </p>
                <span style={{
                  background: 'rgba(99,136,255,0.1)', color: 'var(--accent-blue)',
                  border: '1px solid rgba(99,136,255,0.25)',
                  borderRadius: 999, padding: '0.15rem 0.7rem', fontSize: '0.75rem', fontWeight: 600,
                }}>
                  {answeredCount}/5 answered
                </span>
              </div>

              {/* Progress bar */}
              <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 999, marginTop: '0.75rem', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${answeredCount / 5 * 100}%`,
                  background: 'linear-gradient(90deg, var(--accent-blue), var(--accent-purple))',
                  borderRadius: 999, transition: 'width 0.3s ease',
                }} />
              </div>
            </div>

            {/* Questions */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '1.5rem' }}>
              {questions.map((q, qi) => (
                <QuestionCard
                  key={q.id}
                  question={q}
                  qIndex={qi}
                  selected={answers[qi]}
                  onSelect={(letter) => selectAnswer(qi, letter)}
                />
              ))}
            </div>

            {/* Submit error */}
            {submitError && (
              <div style={{
                display: 'flex', gap: '0.5rem',
                background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)',
                borderRadius: 10, padding: '0.875rem 1rem', marginBottom: '1rem',
              }}>
                <AlertCircle size={15} style={{ color: '#ef4444', flexShrink: 0, marginTop: 1 }} />
                <p style={{ color: '#ef4444', margin: 0, fontSize: '0.875rem' }}>{submitError}</p>
              </div>
            )}

            <button
              id="submit-quiz-btn"
              className="btn-primary"
              onClick={handleSubmit}
              disabled={submitting || !allAnswered}
              style={{ width: '100%', justifyContent: 'center', padding: '0.9375rem', fontSize: '1rem' }}
            >
              {submitting ? (
                <>
                  <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
                  Scoring your answers…
                </>
              ) : (
                `Submit Quiz (${answeredCount}/5 answered)`
              )}
            </button>
          </div>
        )}
      </main>
    </div>
  )
}

function QuestionCard({ question, qIndex, selected, onSelect }) {
  return (
    <div className="glass-card" style={{ padding: '1.25rem 1.375rem' }}>
      <p style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.9375rem', marginBottom: '1rem', lineHeight: 1.55 }}>
        <span style={{ color: 'var(--accent-blue)', fontFamily: 'Outfit, sans-serif', marginRight: '0.5rem' }}>Q{qIndex + 1}.</span>
        {question.question_text}
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {question.options.map((opt, oi) => {
          const letter = LETTERS[oi]
          const isSelected = selected === letter
          return (
            <button
              key={oi}
              id={`q${qIndex + 1}-option-${letter}`}
              type="button"
              onClick={() => onSelect(letter)}
              style={{
                display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
                padding: '0.75rem 1rem', width: '100%', textAlign: 'left',
                border: `1.5px solid ${isSelected ? 'var(--accent-blue)' : 'var(--border)'}`,
                background: isSelected ? 'rgba(99,136,255,0.1)' : 'rgba(255,255,255,0.02)',
                borderRadius: 10, cursor: 'pointer',
                transition: 'all 0.15s',
                transform: isSelected ? 'translateX(3px)' : 'none',
              }}
              onMouseEnter={(e) => !isSelected && (e.currentTarget.style.borderColor = 'rgba(99,136,255,0.4)')}
              onMouseLeave={(e) => !isSelected && (e.currentTarget.style.borderColor = 'var(--border)')}
            >
              <span style={{
                width: 26, height: 26, borderRadius: 7, flexShrink: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '0.75rem', fontWeight: 700,
                background: isSelected ? 'var(--accent-blue)' : 'rgba(255,255,255,0.05)',
                color: isSelected ? 'white' : 'var(--text-muted)',
                border: `1px solid ${isSelected ? 'var(--accent-blue)' : 'var(--border)'}`,
                transition: 'all 0.15s',
              }}>
                {letter}
              </span>
              <span style={{ color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.55, paddingTop: 2 }}>
                {opt}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
