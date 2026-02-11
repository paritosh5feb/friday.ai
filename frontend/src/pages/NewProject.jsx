import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { projectsAPI } from '../api/client'
import { FolderPlus, ArrowLeft, Sparkles } from 'lucide-react'

const domains = [
  'Natural Language Processing',
  'Computer Vision',
  'Reinforcement Learning',
  'Generative AI',
  'Speech & Audio',
  'Robotics',
  'Graph Neural Networks',
  'Time Series',
  'Multimodal',
  'Other',
]

export default function NewProject() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '',
    description: '',
    domain: '',
    tags: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await projectsAPI.create(form)
      navigate(`/projects/${res.data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back
      </button>

      <div className="card">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
            <FolderPlus className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Create New Project</h1>
            <p className="text-sm text-gray-500">Start a new AI research project with all 9 lifecycle steps</p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Project Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="input-field"
              placeholder="e.g., Attention Mechanism for Low-Resource NER"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Description</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="input-field min-h-[100px] resize-y"
              placeholder="Describe your research project, goals, and expected outcomes..."
              rows={4}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Domain</label>
            <select
              value={form.domain}
              onChange={(e) => setForm({ ...form, domain: e.target.value })}
              className="input-field cursor-pointer"
            >
              <option value="">Select a domain</option>
              {domains.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Tags</label>
            <input
              type="text"
              value={form.tags}
              onChange={(e) => setForm({ ...form, tags: e.target.value })}
              className="input-field"
              placeholder="e.g., transformer, attention, NER (comma-separated)"
            />
            <p className="text-xs text-gray-400 mt-1">Comma-separated tags for categorization</p>
          </div>

          {/* Lifecycle Preview */}
          <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-primary-600" />
              <span className="text-sm font-medium text-gray-700">
                9 Lifecycle Steps will be auto-created
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs text-gray-500">
              {[
                '1. Problem Research',
                '2. Baseline Experiments',
                '3. Reproduce Solutions',
                '4. Partial Experiments',
                '5. Benchmark Eval.',
                '6. Result Tables',
                '7. Scale Experiments',
                '8. Final Evaluation',
                '9. LaTeX Reports',
              ].map((step) => (
                <div key={step} className="flex items-center gap-1.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary-400"></div>
                  {step}
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button type="submit" disabled={loading} className="btn-primary flex items-center gap-2">
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <FolderPlus className="w-4 h-4" />
              )}
              Create Project
            </button>
            <button type="button" onClick={() => navigate(-1)} className="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
