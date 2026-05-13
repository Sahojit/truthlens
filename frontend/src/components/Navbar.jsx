import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, User, LogOut, Zap } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()

  return (
    <motion.nav
      initial={{ y: -60, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="sticky top-0 z-50 glass-card rounded-none border-x-0 border-t-0 px-6 py-3"
    >
      <div className="max-w-[1400px] mx-auto flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-primary/20 flex items-center justify-center
                          border border-primary/30 group-hover:shadow-neon-blue transition-all">
            <Shield className="w-5 h-5 text-primary" />
          </div>
          <div>
            <span className="font-display font-bold text-xl gradient-text">TruthLens</span>
            <span className="hidden sm:block text-[10px] text-slate-500 -mt-1">
              AI Misinformation Detector
            </span>
          </div>
        </Link>

        {/* Center badge */}
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full
                        bg-success/10 border border-success/20 text-success text-xs font-medium">
          <Zap className="w-3 h-3" />
          <span>Ensemble AI Active</span>
        </div>

        {/* Right */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <span className="hidden sm:block text-sm text-slate-400">
                {user?.username || user?.email}
              </span>
              <button onClick={logout}
                className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-white
                           transition-colors px-3 py-1.5 rounded-lg hover:bg-white/5">
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Sign Out</span>
              </button>
            </>
          ) : (
            <Link to="/login"
              className="flex items-center gap-1.5 text-sm btn-ghost py-2 px-4">
              <User className="w-4 h-4" />
              Sign In
            </Link>
          )}
        </div>
      </div>
    </motion.nav>
  )
}
