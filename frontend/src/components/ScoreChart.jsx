/**
 * ScoreChart — Recharts line chart of quiz score history.
 */
import {
  ResponsiveContainer, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine,
} from 'recharts'

const difficultyColor = {
  beginner: '#34d399',
  intermediate: '#6388ff',
  advanced: '#fb923c',
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div style={{
      background: 'var(--bg-card)', border: '1px solid var(--border)',
      borderRadius: 10, padding: '0.75rem 1rem',
      boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
    }}>
      <p style={{ color: 'var(--text-primary)', fontWeight: 600, marginBottom: 4 }}>
        {d.topic}
      </p>
      <p style={{ color: difficultyColor[d.difficulty] || 'var(--accent-blue)', fontSize: '0.8rem', marginBottom: 4 }}>
        {d.difficulty}
      </p>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
        Score: <strong style={{ color: 'var(--text-primary)' }}>{d.score}/5</strong> ({Math.round(d.score / 5 * 100)}%)
      </p>
    </div>
  )
}

/**
 * @param {{ records: Array<{ topic, score, difficulty, created_at }> }} props
 */
export default function ScoreChart({ records }) {
  if (!records?.length) return null

  const data = records.slice().reverse().map((r, i) => ({
    name: `#${i + 1}`,
    score: r.score,
    topic: r.topic,
    difficulty: r.difficulty,
    created_at: r.created_at,
  }))

  return (
    <div style={{ width: '100%', height: 260 }}>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,136,255,0.1)" />
          <XAxis
            dataKey="name"
            stroke="var(--text-muted)"
            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
          />
          <YAxis
            domain={[0, 5]}
            ticks={[0, 1, 2, 3, 4, 5]}
            stroke="var(--text-muted)"
            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            y={3}
            stroke="rgba(99,136,255,0.3)"
            strokeDasharray="4 4"
            label={{ value: 'Pass', fill: 'var(--text-muted)', fontSize: 11, position: 'right' }}
          />
          <Line
            type="monotone"
            dataKey="score"
            stroke="var(--accent-blue)"
            strokeWidth={2.5}
            dot={{ fill: 'var(--accent-blue)', r: 5, strokeWidth: 0 }}
            activeDot={{ r: 7, fill: 'var(--accent-purple)' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
