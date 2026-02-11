import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { projectsAPI } from '../api/client'
import {
  FolderKanban, Plus, TrendingUp, Clock, CheckCircle2, PauseCircle,
  ArrowRight, Sparkles, BarChart3,
} from 'lucide-react'

const statusBadge = {
  planning: { color: 'badge-blue', label: 'Planning' },
  in_progress: { color: 'badge-yellow', label: 'In Progress' },
  completed: { color: 'badge-green', label: 'Completed' },
  on_hold: { color: 'badge-gray', label: 'On Hold' },
  archived: { color: 'badge-purple', label: 'Archived' },
}

const lifecycleStepNames = {
  1: 'Research',
  2: 'Baseline',
  3: 'Reproduce',
  4: 'Partial Exp.',
  5: 'Benchmarks',
  6: 'Tables',
  7: 'Scale',
  8: 'Final Eval.',
  9: 'LaTeX Report',
}

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [recentProjects, setRecentProjects] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const [statsRes, projectsRes] = await Promise.all([
        projectsAPI.stats(),
        projectsAPI.list(0, 6),
      ])
      setStats(statsRes.data)
      setRecentProjects(projectsRes.data.projects)
    } catch (err) {
      console.error('Failed to load dashboard:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  const statCards = [
    {
      label: 'Total Projects',
      value: stats?.total || 0,
      icon: FolderKanban,
      color: 'text-primary-600 bg-primary-50',
    },
    {
      label: 'In Progress',
      value: stats?.in_progress || 0,
      icon: TrendingUp,
      color: 'text-yellow-600 bg-yellow-50',
    },
    {
      label: 'Completed',
      value: stats?.completed || 0,
      icon: CheckCircle2,
      color: 'text-green-600 bg-green-50',
    },
    {
      label: 'On Hold',
      value: stats?.on_hold || 0,
      icon: PauseCircle,
      color: 'text-gray-600 bg-gray-100',
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.full_name?.split(' ')[0] || user?.username}
          </h1>
          <p className="text-gray-500 mt-1">Here's an overview of your AI research projects</p>
        </div>
        <Link to="/projects/new" className="btn-primary flex items-center gap-2 self-start">
          <Plus className="w-4 h-4" />
          New Project
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="card">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${stat.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-xs text-gray-500">{stat.label}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* AI Research Lifecycle Overview */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">AI Research Lifecycle</h2>
        </div>
        <div className="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-9 gap-2">
          {Object.entries(lifecycleStepNames).map(([num, name]) => (
            <div
              key={num}
              className="text-center p-3 bg-gradient-to-b from-gray-50 to-white rounded-lg border border-gray-200"
            >
              <div className="w-8 h-8 rounded-full bg-primary-100 text-primary-700 font-bold text-sm flex items-center justify-center mx-auto mb-2">
                {num}
              </div>
              <p className="text-xs text-gray-600 font-medium leading-tight">{name}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Projects */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Projects</h2>
          <Link to="/projects" className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1">
            View all <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        {recentProjects.length === 0 ? (
          <div className="card text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FolderKanban className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-700 mb-2">No projects yet</h3>
            <p className="text-gray-500 mb-4">Create your first AI research project to get started</p>
            <Link to="/projects/new" className="btn-primary inline-flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Create Project
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentProjects.map((project) => (
              <div
                key={project.id}
                onClick={() => navigate(`/projects/${project.id}`)}
                className="card-hover group"
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-gray-900 group-hover:text-primary-700 transition-colors line-clamp-1">
                    {project.title}
                  </h3>
                  <span className={statusBadge[project.status]?.color || 'badge-gray'}>
                    {statusBadge[project.status]?.label || project.status}
                  </span>
                </div>

                {project.description && (
                  <p className="text-sm text-gray-500 mb-3 line-clamp-2">{project.description}</p>
                )}

                <div className="flex items-center justify-between text-xs text-gray-400">
                  <div className="flex items-center gap-1">
                    <BarChart3 className="w-3 h-3" />
                    Step {project.current_step}/9: {lifecycleStepNames[project.current_step]}
                  </div>
                  {project.domain && (
                    <span className="badge-purple">{project.domain}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
