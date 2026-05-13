import { useEffect, useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { getSampleGraph, buildEntityGraph } from '../services/api'
import { Network, Play } from 'lucide-react'
import toast from 'react-hot-toast'

const TYPE_COLORS = {
  PERSON: '#f97316', ORG: '#3b82f6', GPE: '#22c55e',
  LOC: '#a855f7', EVENT: '#ec4899', NORP: '#f43f5e', MISC: '#64748b',
}

function GraphCanvas({ nodes = [], edges = [] }) {
  const canvasRef = useRef(null)
  const simRef    = useRef(null)

  useEffect(() => {
    if (!nodes.length) return
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const W   = canvas.offsetWidth  || 700
    const H   = canvas.offsetHeight || 420
    canvas.width  = W
    canvas.height = H

    // ── Force simulation state ──────────────────────────────
    const pos = {}
    const vel = {}
    nodes.forEach((n, i) => {
      const angle = (i / nodes.length) * Math.PI * 2
      const r = Math.min(W, H) * 0.3
      pos[n.id] = { x: W / 2 + r * Math.cos(angle), y: H / 2 + r * Math.sin(angle) }
      vel[n.id] = { x: 0, y: 0 }
    })

    const nodeRadius = (n) => Math.max(14, Math.min(30, (n.degree || 1) * 5 + 10))

    const REPEL   = 4500
    const SPRING  = 0.03
    const REST    = 120
    const GRAVITY = 0.015
    const DAMP    = 0.82
    let   frame   = 0

    const tick = () => {
      // Repulsion between all node pairs
      const ids = nodes.map(n => n.id)
      for (let a = 0; a < ids.length; a++) {
        for (let b = a + 1; b < ids.length; b++) {
          const pa = pos[ids[a]], pb = pos[ids[b]]
          const dx = pa.x - pb.x, dy = pa.y - pb.y
          const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1)
          const f = REPEL / (dist * dist)
          const fx = (dx / dist) * f, fy = (dy / dist) * f
          vel[ids[a]].x += fx; vel[ids[a]].y += fy
          vel[ids[b]].x -= fx; vel[ids[b]].y -= fy
        }
      }

      // Spring attraction along edges
      edges.forEach(e => {
        if (!pos[e.source] || !pos[e.target]) return
        const pa = pos[e.source], pb = pos[e.target]
        const dx = pb.x - pa.x, dy = pb.y - pa.y
        const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1)
        const f = (dist - REST) * SPRING
        const fx = (dx / dist) * f, fy = (dy / dist) * f
        vel[e.source].x += fx; vel[e.source].y += fy
        vel[e.target].x -= fx; vel[e.target].y -= fy
      })

      // Gravity to centre
      ids.forEach(id => {
        vel[id].x += (W / 2 - pos[id].x) * GRAVITY
        vel[id].y += (H / 2 - pos[id].y) * GRAVITY
      })

      // Integrate + clamp to canvas
      ids.forEach(id => {
        vel[id].x *= DAMP; vel[id].y *= DAMP
        pos[id].x = Math.max(32, Math.min(W - 32, pos[id].x + vel[id].x))
        pos[id].y = Math.max(32, Math.min(H - 32, pos[id].y + vel[id].y))
      })

      // ── Draw ────────────────────────────────────────────────
      ctx.clearRect(0, 0, W, H)

      // Edges
      edges.forEach(e => {
        const src = pos[e.source], tgt = pos[e.target]
        if (!src || !tgt) return
        ctx.beginPath()
        ctx.moveTo(src.x, src.y)
        ctx.lineTo(tgt.x, tgt.y)
        ctx.strokeStyle = `rgba(99,102,241,${Math.min(0.7, (e.weight || 1) * 0.18 + 0.15)})`
        ctx.lineWidth = Math.min((e.weight || 1) * 1.2, 4)
        ctx.stroke()
      })

      // Nodes
      nodes.forEach(n => {
        const { x, y } = pos[n.id]
        const r     = nodeRadius(n)
        const color = TYPE_COLORS[n.type] || TYPE_COLORS.MISC

        // Glow
        const grd = ctx.createRadialGradient(x, y, r * 0.2, x, y, r * 1.6)
        grd.addColorStop(0, color + '30')
        grd.addColorStop(1, 'transparent')
        ctx.beginPath(); ctx.arc(x, y, r * 1.6, 0, Math.PI * 2)
        ctx.fillStyle = grd; ctx.fill()

        // Circle
        ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2)
        ctx.fillStyle = color + '22'; ctx.fill()
        ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.stroke()

        // Label — full text below node
        const words = n.label.split(' ')
        const line1 = words.slice(0, 2).join(' ')
        const line2 = words.slice(2).join(' ')
        ctx.fillStyle = '#e2e8f0'
        ctx.font = `bold ${Math.max(10, Math.min(13, r * 0.55))}px Inter, sans-serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'top'
        ctx.fillText(line1, x, y + r + 4)
        if (line2) ctx.fillText(line2, x, y + r + 18)

        // Type tag
        ctx.font = `9px Inter, sans-serif`
        ctx.fillStyle = color
        ctx.textBaseline = 'middle'
        ctx.fillText(n.type, x, y)
      })

      frame++
      if (frame < 180) simRef.current = requestAnimationFrame(tick)
    }

    simRef.current = requestAnimationFrame(tick)
    return () => { if (simRef.current) cancelAnimationFrame(simRef.current) }
  }, [nodes, edges])

  if (!nodes.length) return (
    <div className="flex items-center justify-center h-full text-slate-500 text-sm">
      No entities found. Paste a news article above to generate a graph.
    </div>
  )

  return <canvas ref={canvasRef} className="w-full h-full rounded-xl" />
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
        <div className="h-[400px] bg-dark-800/60 rounded-xl overflow-hidden">
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
