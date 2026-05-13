import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Home, LayoutDashboard, BrainCircuit, BarChart3,
  Globe, Network, Activity, Info
} from 'lucide-react'

const navItems = [
  { to: '/',               icon: Home,           label: 'Detect'        },
  { to: '/dashboard',      icon: LayoutDashboard, label: 'Dashboard'    },
  { to: '/explainability', icon: BrainCircuit,   label: 'Explain AI'    },
  { to: '/analytics',      icon: BarChart3,      label: 'Analytics'     },
  { to: '/sources',        icon: Globe,          label: 'Sources'       },
  { to: '/graph',          icon: Network,        label: 'Graph'         },
  { to: '/metrics',        icon: Activity,       label: 'Metrics'       },
  { to: '/about',          icon: Info,           label: 'About'         },
]

export default function Sidebar() {
  return (
    <motion.aside
      initial={{ x: -60, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ delay: 0.1 }}
      className="hidden lg:flex flex-col w-20 xl:w-56 shrink-0 pt-6 px-3 gap-1
                 border-r border-white/5"
    >
      {navItems.map(({ to, icon: Icon, label }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200
             text-sm font-medium group
             ${isActive
               ? 'bg-primary/15 text-primary border border-primary/20'
               : 'text-slate-400 hover:text-white hover:bg-white/5'
             }`
          }
        >
          {({ isActive }) => (
            <>
              <Icon className={`w-5 h-5 shrink-0 ${isActive ? 'text-primary' : ''}`} />
              <span className="hidden xl:block">{label}</span>
            </>
          )}
        </NavLink>
      ))}
    </motion.aside>
  )
}
