import { Outlet } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'
import ParticleBackground from '../components/ParticleBackground'

export default function MainLayout() {
  return (
    <div className="min-h-screen flex flex-col relative overflow-x-hidden">
      <ParticleBackground />
      <Navbar />
      <div className="flex flex-1 relative z-10">
        <Sidebar />
        <main className="flex-1 p-6 lg:p-8 overflow-y-auto max-w-[1400px] mx-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
