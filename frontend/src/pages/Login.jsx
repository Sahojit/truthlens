import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Mail, Lock, User } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../contexts/AuthContext'
import { login as apiLogin, register as apiRegister } from '../services/api'

export default function Login() {
  const [mode, setMode]       = useState('login') // 'login' | 'register'
  const [email, setEmail]     = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      let data
      if (mode === 'login') {
        const res = await apiLogin({ email, password })
        data = res.data
      } else {
        const res = await apiRegister({ email, username, password })
        data = res.data
      }
      login(data.user, data.access_token)
      toast.success(`Welcome, ${data.user.username || data.user.email}!`)
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-900 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-8 w-full max-w-md"
      >
        {/* Logo */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-12 h-12 rounded-2xl bg-primary/20 flex items-center justify-center border border-primary/30">
            <Shield className="w-6 h-6 text-primary" />
          </div>
          <div>
            <div className="font-display font-bold text-2xl gradient-text">TruthLens</div>
            <div className="text-xs text-slate-500">AI Misinformation Detector</div>
          </div>
        </div>

        {/* Mode Toggle */}
        <div className="flex p-1 bg-white/5 rounded-xl mb-6">
          {['login', 'register'].map(m => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all capitalize ${
                mode === m ? 'bg-primary text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              {m === 'login' ? 'Sign In' : 'Sign Up'}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <div>
              <label className="block text-xs text-slate-400 mb-1.5">Username</label>
              <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus-within:border-primary/50 transition-all">
                <User className="w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  placeholder="your_username"
                  required
                  className="flex-1 bg-transparent text-white text-sm placeholder-slate-500 focus:outline-none"
                />
              </div>
            </div>
          )}
          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Email</label>
            <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus-within:border-primary/50 transition-all">
              <Mail className="w-4 h-4 text-slate-500" />
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="flex-1 bg-transparent text-white text-sm placeholder-slate-500 focus:outline-none"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Password</label>
            <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus-within:border-primary/50 transition-all">
              <Lock className="w-4 h-4 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={6}
                className="flex-1 bg-transparent text-white text-sm placeholder-slate-500 focus:outline-none"
              />
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2 py-3.5">
            {loading
              ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              : mode === 'login' ? 'Sign In' : 'Create Account'
            }
          </button>
        </form>

        <div className="mt-4 text-center">
          <Link to="/" className="text-sm text-primary/70 hover:text-primary transition-colors">
            ← Back to Detector (no account needed)
          </Link>
        </div>
      </motion.div>
    </div>
  )
}
