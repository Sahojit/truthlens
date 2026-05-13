import { useEffect, useState, useRef, useCallback } from 'react'
import { motion } from 'framer-motion'
import { getSampleGraph, buildEntityGraph } from '../services/api'
import { Network, Play } from 'lucide-react'
import toast from 'react-hot-toast'

const TYPE_COLORS = {
  PERSON: '#f97316', ORG: '#3b82f6', GPE: '#22c55e',
  LOC: '#a855f7', EVENT: '#ec4899', NORP: '#f43f5e', MISC: '#94a3b8',
}

function runForce(nodes, edges, W, H, steps = 220) {
  const pos = {}, vel = {}
  // Spread initial positions across full canvas in a grid-ish pattern
  nodes.forEach((n, i) => {
    const cols = Math.ceil(Math.sqrt(nodes.length))
    const col  = i % cols, row = Math.floor(i / cols)
    const jitter = () => (Math.random() - 0.5) * 60
    pos[n.id] = {
      x: 80 + (col / Math.max(cols - 1, 1)) * (W - 160) + jitter(),
      y: 80 + (row / Math.max(Math.ceil(nodes.length / cols) - 1, 1)) * (H - 160) + jitter(),
    }
    vel[n.id] = { x: 0, y: 0 }
  })

  const nodeR = (n) => Math.max(12, Math.min(26, (n.degree || 1) * 4 + 10))
  const REPEL  = 3200
  const SPRING = 0.025
  const REST   = Math.min(160, Math.max(80, (W * H) / (nodes.length * 120)))
  const GRAV   = 0.04
  const DAMP   = 0.78
  const ids    = nodes.map(n => n.id)

  for (let s = 0; s < steps; s++) {
    // Repulsion
    for (let a = 0; a < ids.length; a++) {
      for (let b = a + 1; b < ids.length; b++) {
        const pa = pos[ids[a]], pb = pos[ids[b]]
        const dx = pa.x - pb.x, dy = pa.y - pb.y
        const d  = Math.max(Math.sqrt(dx * dx + dy * dy), 0.5)
        const f  = REPEL / (d * d)
        vel[ids[a]].x += (dx / d) * f;  vel[ids[a]].y += (dy / d) * f
        vel[ids[b]].x -= (dx / d) * f;  vel[ids[b]].y -= (dy / d) * f
      }
    }
    // Springs
    edges.forEach(e => {
      const pa = pos[e.source], pb = pos[e.target]
      if (!pa || !pb) return
      const dx = pb.x - pa.x, dy = pb.y - pa.y
      const d  = Math.max(Math.sqrt(dx * dx + dy * dy), 0.5)
      const f  = (d - REST) * SPRING
      vel[e.source].x += (dx / d) * f;  vel[e.source].y += (dy / d) * f
      vel[e.target].x -= (dx / d) * f;  vel[e.target].y -= (dy / d) * f
    })
    // Gravity + integrate
    ids.forEach(id => {
      vel[id].x += (W / 2 - pos[id].x) * GRAV
      vel[id].y += (H / 2 - pos[id].y) * GRAV
      vel[id].x *= DAMP;  vel[id].y *= DAMP
      const r = nodeR(nodes.find(n => n.id === id))
      // extra bottom/side margin so labels (drawn below node) never clip
      pos[id].x = Math.max(r + 72, Math.min(W - r - 72, pos[id].x + vel[id].x))
      pos[id].y = Math.max(r + 28, Math.min(H - r - 52, pos[id].y + vel[id].y))
    })
  }
  return pos
}

function GraphCanvas({ nodes = [], edges = [] }) {
  const [positions, setPositions] = useState({})
  const svgRef = useRef(null)

  useEffect(() => {
    if (!nodes.length) return
    const W = svgRef.current?.clientWidth  || 720
    const H = svgRef.current?.clientHeight || 500
    // Run force in next tick so SVG has measured dimensions
    const id = setTimeout(() => {
      const W2 = svgRef.current?.clientWidth  || 720
      const H2 = svgRef.current?.clientHeight || 500
      setPositions(runForce(nodes, edges, W2, H2))
    }, 30)
    return () => clearTimeout(id)
  }, [nodes, edges])

  const nodeR = (n) => Math.max(12, Math.min(26, (n.degree || 1) * 4 + 10))

  if (!nodes.length) return (
    <div className="flex items-center justify-center h-full text-slate-500 text-sm">
      No entities found. Paste a news article above to generate a graph.
    </div>
  )

  return (
    <svg ref={svgRef} className="w-full" style={{ height: 540, display: 'block' }}>
      <defs>
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <radialGradient key={type} id={`glow-${type}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%"   stopColor={color} stopOpacity="0.35" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </radialGradient>
        ))}
      </defs>

      {/* Edges */}
      {edges.map((e, i) => {
        const src = positions[e.source], tgt = positions[e.target]
        if (!src || !tgt) return null
        const opacity = Math.min(0.65, (e.weight || 1) * 0.15 + 0.18)
        const width   = Math.min((e.weight || 1) * 1.2, 3.5)
        return (
          <line key={i}
            x1={src.x} y1={src.y} x2={tgt.x} y2={tgt.y}
            stroke="#6366f1" strokeOpacity={opacity} strokeWidth={width}
          />
        )
      })}

      {/* Nodes */}
      {nodes.map(n => {
        const pos   = positions[n.id]
        if (!pos) return null
        const r     = nodeR(n)
        const color = TYPE_COLORS[n.type] || TYPE_COLORS.MISC
        const words = n.label.split(' ')
        const line1 = words.slice(0, 2).join(' ')
        const line2 = words.slice(2).join(' ')
        return (
          <g key={n.id}>
            {/* Glow */}
            <circle cx={pos.x} cy={pos.y} r={r * 2.2}
              fill={`url(#glow-${n.type || 'MISC'})`} />
            {/* Node circle */}
            <circle cx={pos.x} cy={pos.y} r={r}
              fill={color + '25'} stroke={color} strokeWidth={2} />
            {/* Type badge inside */}
            <text x={pos.x} y={pos.y + 1}
              textAnchor="middle" dominantBaseline="middle"
              fontSize="8" fontWeight="600" fill={color} opacity="0.9"
              style={{ fontFamily: 'Inter, sans-serif', pointerEvents: 'none' }}>
              {n.type}
            </text>
            {/* Label line 1 below node */}
            <text x={pos.x} y={pos.y + r + 13}
              textAnchor="middle" dominantBaseline="middle"
              fontSize="11" fontWeight="700" fill="#e2e8f0"
              style={{ fontFamily: 'Inter, sans-serif', pointerEvents: 'none' }}>
              {line1}
            </text>
            {/* Label line 2 (if 3+ word name) */}
            {line2 && (
              <text x={pos.x} y={pos.y + r + 26}
                textAnchor="middle" dominantBaseline="middle"
                fontSize="11" fontWeight="700" fill="#e2e8f0"
                style={{ fontFamily: 'Inter, sans-serif', pointerEvents: 'none' }}>
                {line2}
              </text>
            )}
          </g>
        )
      })}
    </svg>
  )
}

export default function GraphExplorer() {
  const [graph, setGraph] = useState({ nodes: [], edges: [], metrics: {} })
  const [headline, setHeadline] = useState('')
  const [article, setArticle] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getSampleGraph().then(r => setGraph(r.data)).catch(() => {})
  }, [])

  const buildGraph = async () => {
    if (!headline || !article) { toast.error('Enter headline and article'); return }
    setLoading(true)
    try {
      const { data } = await buildEntityGraph({ headline, article })
      setGraph(data)
      toast.success('Entity graph built!')
    } catch {
      toast.error('Graph build failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-2">
        <Network className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-2xl font-display font-bold">Graph Explorer</h1>
          <p className="text-slate-400 text-sm">Entity co-occurrence and misinformation propagation</p>
        </div>
      </div>

      {/* Input */}
      <div className="glass-card p-5 space-y-3">
        <input
          value={headline}
          onChange={e => setHeadline(e.target.value)}
          placeholder="Headline…"
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3
                     text-white placeholder-slate-500 focus:outline-none focus:border-primary/50 text-sm"
        />
        <textarea
          value={article}
          onChange={e => setArticle(e.target.value)}
          placeholder="Article body (the richer, the better the graph)…"
          rows={4}
          className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3
                     text-white placeholder-slate-500 focus:outline-none focus:border-primary/50 text-sm resize-none"
        />
        <button onClick={buildGraph} disabled={loading} className="btn-primary flex items-center gap-2">
          {loading
            ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            : <Play className="w-4 h-4" />
          }
          Build Entity Graph
        </button>
      </div>

      {/* Graph */}
      <div className="glass-card p-5">
        <div className="section-title mb-1">Entity Relationship Graph</div>
        <div className="section-sub mb-4">
          Nodes: people, organisations, locations · Edges: co-occurrence in sentences
        </div>
        <div className="h-[540px] bg-dark-800/60 rounded-xl overflow-visible">
          <GraphCanvas nodes={graph.nodes} edges={graph.edges} />
        </div>

        {/* Metrics */}
        {graph.metrics && Object.keys(graph.metrics).length > 0 && (
          <div className="grid grid-cols-4 gap-4 mt-4">
            {Object.entries(graph.metrics).map(([k, v]) => (
              <div key={k} className="text-center">
                <div className="text-lg font-bold text-primary">{v}</div>
                <div className="text-xs text-slate-500 capitalize">{k.replace('_', ' ')}</div>
              </div>
            ))}
          </div>
        )}

        {/* Legend */}
        <div className="flex flex-wrap gap-3 mt-4 text-xs text-slate-400">
          {[['PERSON','#f97316'],['ORG','#3b82f6'],['GPE','#22c55e'],['LOC','#a855f7']].map(([t, c]) => (
            <span key={t} className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: c }} />
              {t}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
