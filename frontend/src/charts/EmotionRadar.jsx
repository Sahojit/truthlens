import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Radar, ResponsiveContainer, Tooltip
} from 'recharts'

const EMOTION_COLORS = {
  fear: '#ef4444', anger: '#f97316', disgust: '#a855f7',
  sadness: '#3b82f6', surprise: '#f59e0b',
  joy: '#22c55e', trust: '#06b6d4', anticipation: '#ec4899',
}

export default function EmotionRadar({ data = {} }) {
  const chartData = Object.entries(data).map(([key, value]) => ({
    subject: key.charAt(0).toUpperCase() + key.slice(1),
    value: Math.round(value * 100),
    fullMark: 100,
  }))

  if (chartData.length === 0) return null

  return (
    <div className="glass-card p-5">
      <div className="section-title mb-0.5">Emotion Radar</div>
      <div className="section-sub mb-4">Emotional manipulation indicators</div>
      <ResponsiveContainer width="100%" height={280}>
        <RadarChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
          <PolarGrid stroke="rgba(255,255,255,0.08)" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tick={{ fill: '#64748b', fontSize: 9 }}
          />
          <Radar
            name="Emotion"
            dataKey="value"
            stroke="#ef4444"
            fill="#ef4444"
            fillOpacity={0.2}
            strokeWidth={2}
          />
          <Tooltip
            contentStyle={{
              background: '#1a1a2e',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 8,
              color: '#e2e8f0',
            }}
            formatter={(val) => [`${val}%`, 'Score']}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
