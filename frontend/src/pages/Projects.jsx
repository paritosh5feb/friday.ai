import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { projectsAPI } from '../api/client'
import {
  Plus, Search, FolderKanban, BarChart3, Calendar,
  Trash2, MoreVertical, Filter,
} from 'lucide-react'

const statusBadge = {
  planning: { color: 'badge-blue', label: 'Planning' },
  in_progress: { color: 'badge-yellow', label: 'In Progress' },
  completed: { color: 'badge-green', label: 'Completed' },
  on_hold: { color: 'badge-gray', label: 'On Hold' },
  archived: { color: 'badge-purple', label: 'Archived' },
}

const stepNames = {
  1: 'Problem Research',
  2: 'Baseline Experiments',
  3: 'Reproduce Solutions',
  4: 'Partial Experiments',
  5: 'Benchmarks',
  6: 'Result Tables',
  7: 'Scale Experiments',
  8: 'Final Evaluation',
  9: 'LaTeX Report',
}

export default function Projects() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [menuOpen, setMenuOpen] = useState(null)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const res = await projectsAPI.list(0, 100)
      setProjects(res.data.projects)
      setTotal(res.data.total)
    } catch (err) {
      console.error('Failed to load projects:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (e, projectId) => {
    e.stopPropagation()
    if (!confirm('Are you sure you want to delete this project? This cannot be undone.')) return
    try {
      await projectsAPI.delete(projectId)
      setProjects(projects.filter((p) => p.id !== projectId))
      setTotal(total - 1)
    } catch (err) {
      console.error('Delete failed:', err)
    }
    setMenuOpen(null)
  }

  const filteredProjects = projects.filter((p) => {
    const matchesSearch = p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || p.status === statusFilter
    return matchesSearch && matchesStatus
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-500 mt-1">{total} project{total !== 1 ? 's' : ''} total</p>
        </div>
        <Link to="/projects/new" className="btn-primary flex items-center gap-2 self-start">
          <Plus className="w-4 h-4" />
          New Project
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-field pl-10"
            placeholder="Search projects..."
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input-field pl-10 pr-8 appearance-none cursor-pointer"
          >
            <option value="all">All Status</option>
            <option value="planning">Planning</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="on_hold">On Hold</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      {/* Project List */}
      {filteredProjects.length === 0 ? (
        <div className="card text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <FolderKanban className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-700 mb-2">
            {searchQuery || statusFilter !== 'all' ? 'No matching projects' : 'No projects yet'}
          </h3>
          <p className="text-gray-500 mb-4">
            {searchQuery || statusFilter !== 'all'
              ? 'Try adjusting your search or filter'
              : 'Create your first AI research project to get started'}
          </p>
          {!searchQuery && statusFilter === 'all' && (
            <Link to="/projects/new" className="btn-primary inline-flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Create Project
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredProjects.map((project) => (
            <div
              key={project.id}
              onClick={() => navigate(`/projects/${project.id}`)}
              className="card-hover flex flex-col sm:flex-row sm:items-center gap-4"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-gray-900 truncate">{project.title}</h3>
                  <span className={statusBadge[project.status]?.color || 'badge-gray'}>
                    {statusBadge[project.status]?.label || project.status}
                  </span>
                  {project.domain && <span className="badge-purple">{project.domain}</span>}
                </div>
                {project.description && (
                  <p className="text-sm text-gray-500 line-clamp-1">{project.description}</p>
                )}
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-400 flex-shrink-0">
                <div className="flex items-center gap-1.5">
                  <BarChart3 className="w-4 h-4" />
                  <span>Step {project.current_step}: {stepNames[project.current_step]}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4" />
                  <span>{new Date(project.updated_at).toLocaleDateString()}</span>
                </div>

                <div className="relative">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setMenuOpen(menuOpen === project.id ? null : project.id)
                    }}
                    className="p-1 rounded hover:bg-gray-100"
                  >
                    <MoreVertical className="w-4 h-4" />
                  </button>
                  {menuOpen === project.id && (
                    <div className="absolute right-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10 min-w-[120px]">
                      <button
                        onClick={(e) => handleDelete(e, project.id)}
                        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
