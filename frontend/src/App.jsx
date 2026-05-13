import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import MainLayout from './layouts/MainLayout'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Explainability from './pages/Explainability'
import Analytics from './pages/Analytics'
import SourceAnalysis from './pages/SourceAnalysis'
import GraphExplorer from './pages/GraphExplorer'
import ModelMetrics from './pages/ModelMetrics'
import About from './pages/About'
import Login from './pages/Login'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<MainLayout />}>
          <Route path="/"               element={<Home />} />
          <Route path="/dashboard"      element={<Dashboard />} />
          <Route path="/explainability" element={<Explainability />} />
          <Route path="/analytics"      element={<Analytics />} />
          <Route path="/sources"        element={<SourceAnalysis />} />
          <Route path="/graph"          element={<GraphExplorer />} />
          <Route path="/metrics"        element={<ModelMetrics />} />
          <Route path="/about"          element={<About />} />
          <Route path="*"               element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}
