import { useEffect, useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { getSampleGraph, buildEntityGraph } from '../services/api'
import { Network, Play } from 'lucide-react'
import toast from 'react-hot-toast'

// Simple D3-style canvas graph renderer
function GraphCanvas({ nodes = [], edges = [] }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    if (!nodes.length) return
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const W = canvas.width
    const H = canvas.height

    // Simple force-like positioning
    const nodeMap = {}
    const positioned = nodes.map((n, i) => {
      const angle = (i / nodes.length) * Math.PI * 2
      const r = Math.min(W, H) * 0.35
      const x = W / 2 + r * Math.cos(angle)
      const y = H / 2 + r * Math.sin(angle)
      nodeMap[n.id] = { x, y }
      return { ...n, x, y }
    })

    const typeColors = {
      PERSON: '#f97316', ORG: '#3b82f6', GPE: '#22c55e',
      LOC: '#a855f7', EVENT: '#ec4899', MISC: '#64748b',
    }

    ctx.clearRect(0, 0, W, H)

    // Draw edges
    edges.forEach(e => {
      const src = nodeMap[e.source]
      const tgt = nodeMap[e.target]
      if (!src || !tgt) return
      ctx.beginPath()
      ctx.moveTo(src.x, src.y)
      ctx.lineTo(tgt.x, tgt.y)
      ctx.strokeStyle = `rgba(99,102,241,${Math.min(0.6, e.weight * 0.15 + 0.1)})`
      ctx.lineWidth = Math.min(e.weight, 4)
      ctx.stroke()
    })

    // Draw nodes
    positioned.forEach(n => {
      const radius = Math.max(16, Math.min(32, n.degree * 4 + 10))
      ctx.beginPath()
      ctx.arc(n.x, n.y, radius, 0, Math.PI * 2)
      ctx.fillStyle = (typeColors[n.type] || '#64748b') + '30'
      ctx.fill()
      ctx.strokeStyle = typeColors[n.type] || '#64748b'
      ctx.lineWidth = 2
      ctx.stroke()

      ctx.fillStyle = '#e2e8f0'
      ctx.font = `${Math.max(9, radius * 0.5)}px Inter, sans-serif`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      const label = n.label.length > 10 ? n.label.slice(0, 10) + '…' : n.label
      ctx.fillText(label, n.x, n.y)
    })
  }, [nodes, edges])

  if (!nodes.length) return (
    <div className="flex items-center justify-center h-full text-slate-500 text-sm">
      No entities found. Paste a news article above to generate a graph.
    </div>
  )

  return <canvas ref={canvasRef} width={700} height={400} className="w-full rounded-xl" />
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
