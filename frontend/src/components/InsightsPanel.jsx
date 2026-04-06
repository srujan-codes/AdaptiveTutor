/**
 * InsightsPanel — displays AI-generated performance insights.
 */
import { TrendingUp, TrendingDown, AlertCircle, Lightbulb } from 'lucide-react'

function Section({ icon, title, items, color }) {
  if (!items?.length) return null
  return (
    <div style={{ marginBottom: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.6rem' }}>
        <span style={{ color }}>{icon}</span>
        <h4 style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>{title}</h4>
      </div>
      <ul style={{ paddingLeft: '1.25rem', margin: 0 }}>
        {items.map((item, i) => (
          <li key={i} style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '0.35rem', lineHeight: 1.6 }}>
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}

/**
 * @param {{ insights: { strengths, weaknesses, trends, recommendations, overall_assessment } }} props
 */
export default function InsightsPanel({ insights }) {
  if (!insights) return null

  return (
    <div className="fade-in">
      {insights.overall_assessment && (
        <div style={{
          background: 'rgba(99,136,255,0.08)',
          border: '1px solid rgba(99,136,255,0.2)',
          borderRadius: 10,
          padding: '0.875rem 1rem',
          marginBottom: '1.25rem',
          color: 'var(--text-secondary)',
          fontSize: '0.9rem',
          lineHeight: 1.65,
        }}>
          <Lightbulb size={14} style={{ color: 'var(--accent-blue)', marginRight: 6, verticalAlign: 'middle' }} />
          {insights.overall_assessment}
        </div>
      )}

      <Section
        icon={<TrendingUp size={16} />}
        title="Strengths"
        items={insights.strengths}
        color="var(--accent-green)"
      />
      <Section
        icon={<AlertCircle size={16} />}
        title="Areas to Improve"
        items={insights.weaknesses}
        color="var(--accent-orange)"
      />
      <Section
        icon={<TrendingDown size={16} />}
        title="Trends"
        items={insights.trends}
        color="var(--accent-blue)"
      />
      <Section
        icon={<Lightbulb size={16} />}
        title="Recommendations"
        items={insights.recommendations}
        color="var(--accent-purple)"
      />
    </div>
  )
}
