import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { projectsAPI, lifecycleAPI } from '../api/client'
import LifecycleProgress from '../components/LifecycleProgress'
import ProblemResearch from './lifecycle/ProblemResearch'
import BaselineExperiment from './lifecycle/BaselineExperiment'
import ReproduceSolutions from './lifecycle/ReproduceSolutions'
import PartialExperiments from './lifecycle/PartialExperiments'
import BenchmarkEvaluations from './lifecycle/BenchmarkEvaluations'
import ResultTables from './lifecycle/ResultTables'
import ScaleExperiments from './lifecycle/ScaleExperiments'
import FinalEvaluation from './lifecycle/FinalEvaluation'
import LatexReport from './lifecycle/LatexReport'
import {
  ArrowLeft, Settings, Calendar, Tag, Globe, Edit3, Save, X, CheckCircle,
} from 'lucide-react'

const statusOptions = [
  { value: 'planning', label: 'Planning', color: 'bg-blue-500' },
  { value: 'in_progress', label: 'In Progress', color: 'bg-yellow-500' },
  { value: 'completed', label: 'Completed', color: 'bg-green-500' },
  { value: 'on_hold', label: 'On Hold', color: 'bg-gray-500' },
  { value: 'archived', label: 'Archived', color: 'bg-purple-500' },
]

const stepComponents = {
  1: ProblemResearch,
  2: BaselineExperiment,
  3: ReproduceSolutions,
  4: PartialExperiments,
  5: BenchmarkEvaluations,
  6: ResultTables,
  7: ScaleExperiments,
  8: FinalEvaluation,
  9: LatexReport,
}

export default function ProjectDetail() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [steps, setSteps] = useState([])
  const [activeStep, setActiveStep] = useState(1)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [editForm, setEditForm] = useState({})

  useEffect(() => {
    loadProject()
  }, [projectId])

  const loadProject = async () => {
    try {
      const [projRes, stepsRes] = await Promise.all([
        projectsAPI.get(projectId),
        lifecycleAPI.getSteps(projectId),
      ])
      setProject(projRes.data)
      setSteps(stepsRes.data)
      setActiveStep(projRes.data.current_step)
    } catch (err) {
      console.error('Failed to load project:', err)
      navigate('/projects')
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (newStatus) => {
    try {
      const res = await projectsAPI.update(projectId, { status: newStatus })
      setProject(res.data)
    } catch (err) {
      console.error('Failed to update status:', err)
    }
  }

  const startEdit = () => {
    setEditForm({
      title: project.title,
      description: project.description || '',
      domain: project.domain || '',
      tags: project.tags || '',
    })
    setEditing(true)
  }

  const saveEdit = async () => {
    try {
      const res = await projectsAPI.update(projectId, editForm)
      setProject(res.data)
      setEditing(false)
    } catch (err) {
      console.error('Failed to update project:', err)
    }
  }

  const refreshSteps = async () => {
    try {
      const stepsRes = await lifecycleAPI.getSteps(projectId)
      setSteps(stepsRes.data)
    } catch (err) {
      console.error('Failed to refresh steps:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  if (!project) return null

  const StepComponent = stepComponents[activeStep]

  return (
    <div className="space-y-6">
      {/* Top bar */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/projects')}
          className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1 min-w-0">
          {editing ? (
            <input
              type="text"
              value={editForm.title}
              onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
              className="input-field text-xl font-bold"
            />
          ) : (
            <h1 className="text-xl font-bold text-gray-900 truncate">{project.title}</h1>
          )}
        </div>
        <div className="flex items-center gap-2">
          {editing ? (
            <>
              <button onClick={saveEdit} className="btn-primary flex items-center gap-1 text-sm py-1.5">
                <Save className="w-4 h-4" /> Save
              </button>
              <button onClick={() => setEditing(false)} className="btn-secondary flex items-center gap-1 text-sm py-1.5">
                <X className="w-4 h-4" /> Cancel
              </button>
            </>
          ) : (
            <button onClick={startEdit} className="btn-secondary flex items-center gap-1 text-sm py-1.5">
              <Edit3 className="w-4 h-4" /> Edit
            </button>
          )}
        </div>
      </div>

      {/* Project info bar */}
      <div className="card flex flex-col sm:flex-row sm:items-center gap-4">
        <div className="flex items-center gap-3 flex-1">
          <select
            value={project.status}
            onChange={(e) => handleStatusChange(e.target.value)}
            className="input-field w-auto text-sm py-1.5 pr-8"
          >
            {statusOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>

          {project.domain && (
            <span className="badge-purple flex items-center gap-1">
              <Globe className="w-3 h-3" />
              {project.domain}
            </span>
          )}

          {project.tags && (
            <div className="hidden sm:flex items-center gap-1">
              {project.tags.split(',').map((tag, i) => (
                <span key={i} className="badge-blue flex items-center gap-1">
                  <Tag className="w-3 h-3" />
                  {tag.trim()}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            Created {new Date(project.created_at).toLocaleDateString()}
          </span>
          <span>Step {project.current_step}/9</span>
        </div>
      </div>

      {editing && (
        <div className="card space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={editForm.description}
              onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
              className="input-field min-h-[80px] resize-y"
              rows={3}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Domain</label>
              <input
                type="text"
                value={editForm.domain}
                onChange={(e) => setEditForm({ ...editForm, domain: e.target.value })}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
              <input
                type="text"
                value={editForm.tags}
                onChange={(e) => setEditForm({ ...editForm, tags: e.target.value })}
                className="input-field"
              />
            </div>
          </div>
        </div>
      )}

      {/* Main content: Sidebar + Step content */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Lifecycle Sidebar */}
        <div className="lg:w-80 flex-shrink-0">
          <div className="sticky top-4">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Lifecycle Progress
            </h2>
            <LifecycleProgress
              steps={steps}
              currentStep={activeStep}
              onStepClick={(num) => setActiveStep(num)}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="flex-1 min-w-0">
          {StepComponent && (
            <StepComponent
              projectId={parseInt(projectId)}
              stepNumber={activeStep}
              step={steps.find((s) => s.step_number === activeStep)}
              onStepUpdate={refreshSteps}
            />
          )}
        </div>
      </div>
    </div>
  )
}
