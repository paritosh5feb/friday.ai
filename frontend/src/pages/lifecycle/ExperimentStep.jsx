/**
 * Shared experiment component for Steps 2, 3, 4, and 7.
 * Handles baseline, reproduction, partial, and scaled experiments.
 */
import { useState, useEffect } from 'react'
import { experimentsAPI } from '../../api/client'
import StepHeader from './StepHeader'
import {
  Plus, Save, Trash2, Edit3, ChevronDown, ChevronUp,
  Play, CheckCircle, XCircle, Clock, FlaskConical,
} from 'lucide-react'

const statusConfig = {
  planned: { label: 'Planned', color: 'badge-gray', icon: Clock },
  running: { label: 'Running', color: 'badge-blue', icon: Play },
  completed: { label: 'Completed', color: 'badge-green', icon: CheckCircle },
  failed: { label: 'Failed', color: 'badge-red', icon: XCircle },
}

export default function ExperimentStep({
  projectId, stepNumber, step, onStepUpdate,
  experimentType, icon, description, title,
}) {
  const [experiments, setExperiments] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [expandedId, setExpandedId] = useState(null)
  const [form, setForm] = useState({
    name: '', description: '', hypothesis: '', methodology: '',
    dataset: '', model_architecture: '',
    hyperparameters: '{}', results: '{}', conclusion: '',
  })

  useEffect(() => {
    loadExperiments()
  }, [projectId])

  const loadExperiments = async () => {
    try {
      const res = await experimentsAPI.list(projectId, experimentType)
      setExperiments(res.data)
    } catch (err) {
      console.error('Failed to load experiments:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    let hyperparams = null
    let results = null
    try {
      hyperparams = form.hyperparameters ? JSON.parse(form.hyperparameters) : null
    } catch { hyperparams = null }
    try {
      results = form.results && form.results !== '{}' ? JSON.parse(form.results) : null
    } catch { results = null }

    const data = {
      name: form.name,
      experiment_type: experimentType,
      description: form.description || null,
      hypothesis: form.hypothesis || null,
      methodology: form.methodology || null,
      dataset: form.dataset || null,
      model_architecture: form.model_architecture || null,
      hyperparameters: hyperparams,
      ...(editingId ? { results, conclusion: form.conclusion || null } : {}),
    }

    try {
      if (editingId) {
        await experimentsAPI.update(projectId, editingId, data)
      } else {
        await experimentsAPI.create(projectId, data)
      }
      resetForm()
      loadExperiments()
    } catch (err) {
      console.error('Failed to save experiment:', err)
    }
  }

  const handleEdit = (exp) => {
    setForm({
      name: exp.name || '',
      description: exp.description || '',
      hypothesis: exp.hypothesis || '',
      methodology: exp.methodology || '',
      dataset: exp.dataset || '',
      model_architecture: exp.model_architecture || '',
      hyperparameters: exp.hyperparameters ? JSON.stringify(exp.hyperparameters, null, 2) : '{}',
      results: exp.results ? JSON.stringify(exp.results, null, 2) : '{}',
      conclusion: exp.conclusion || '',
    })
    setEditingId(exp.id)
    setShowForm(true)
  }

  const handleDelete = async (expId) => {
    if (!confirm('Delete this experiment?')) return
    try {
      await experimentsAPI.delete(projectId, expId)
      loadExperiments()
    } catch (err) {
      console.error('Failed to delete experiment:', err)
    }
  }

  const handleStatusChange = async (expId, status) => {
    try {
      await experimentsAPI.update(projectId, expId, { status })
      loadExperiments()
    } catch (err) {
      console.error('Failed to update status:', err)
    }
  }

  const resetForm = () => {
    setForm({
      name: '', description: '', hypothesis: '', methodology: '',
      dataset: '', model_architecture: '',
      hyperparameters: '{}', results: '{}', conclusion: '',
    })
    setEditingId(null)
    setShowForm(false)
  }

  const Icon = icon

  return (
    <div>
      <StepHeader
        projectId={projectId}
        step={step}
        onStepUpdate={onStepUpdate}
        icon={icon}
        description={description}
      />

      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800">
          {title} ({experiments.length})
        </h3>
        <button
          onClick={() => { resetForm(); setShowForm(!showForm) }}
          className="btn-primary flex items-center gap-1.5 text-sm"
        >
          <Plus className="w-4 h-4" />
          Add Experiment
        </button>
      </div>

      {/* Experiment Form */}
      {showForm && (
        <div className="card mb-4 border-primary-200">
          <h4 className="font-semibold text-gray-800 mb-4">
            {editingId ? 'Edit Experiment' : 'New Experiment'}
          </h4>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Name *</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="input-field text-sm"
                placeholder="Experiment name"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Hypothesis</label>
              <textarea
                value={form.hypothesis}
                onChange={(e) => setForm({ ...form, hypothesis: e.target.value })}
                className="input-field text-sm min-h-[60px]"
                placeholder="What you expect to prove..."
                rows={2}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="input-field text-sm min-h-[60px]"
                placeholder="Experiment description..."
                rows={2}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Methodology</label>
              <textarea
                value={form.methodology}
                onChange={(e) => setForm({ ...form, methodology: e.target.value })}
                className="input-field text-sm min-h-[60px]"
                placeholder="Describe the methodology..."
                rows={2}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Dataset</label>
                <input
                  type="text"
                  value={form.dataset}
                  onChange={(e) => setForm({ ...form, dataset: e.target.value })}
                  className="input-field text-sm"
                  placeholder="e.g., CIFAR-10, CoNLL-2003"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Model Architecture</label>
                <input
                  type="text"
                  value={form.model_architecture}
                  onChange={(e) => setForm({ ...form, model_architecture: e.target.value })}
                  className="input-field text-sm"
                  placeholder="e.g., BERT, ResNet-50"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Hyperparameters (JSON)</label>
              <textarea
                value={form.hyperparameters}
                onChange={(e) => setForm({ ...form, hyperparameters: e.target.value })}
                className="input-field text-sm font-mono min-h-[60px]"
                placeholder='{"learning_rate": 0.001, "epochs": 100}'
                rows={3}
              />
            </div>
            {editingId && (
              <>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Results (JSON)</label>
                  <textarea
                    value={form.results}
                    onChange={(e) => setForm({ ...form, results: e.target.value })}
                    className="input-field text-sm font-mono min-h-[60px]"
                    placeholder='{"accuracy": 0.95, "f1": 0.93}'
                    rows={3}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Conclusion</label>
                  <textarea
                    value={form.conclusion}
                    onChange={(e) => setForm({ ...form, conclusion: e.target.value })}
                    className="input-field text-sm min-h-[60px]"
                    placeholder="Conclusions drawn from this experiment..."
                    rows={2}
                  />
                </div>
              </>
            )}
            <div className="flex gap-2">
              <button type="submit" className="btn-primary text-sm flex items-center gap-1">
                <Save className="w-4 h-4" />
                {editingId ? 'Update' : 'Create'}
              </button>
              <button type="button" onClick={resetForm} className="btn-secondary text-sm">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Experiments list */}
      {loading ? (
        <div className="text-center py-8">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      ) : experiments.length === 0 ? (
        <div className="card text-center py-8">
          <FlaskConical className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">No experiments yet</p>
          <p className="text-gray-400 text-xs mt-1">Create your first experiment to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {experiments.map((exp) => {
            const StatusIcon = statusConfig[exp.status]?.icon || Clock
            return (
              <div key={exp.id} className="card">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <h4 className="font-medium text-gray-900 text-sm">{exp.name}</h4>
                      <span className={statusConfig[exp.status]?.color || 'badge-gray'}>
                        <StatusIcon className="w-3 h-3 mr-1 inline" />
                        {statusConfig[exp.status]?.label || exp.status}
                      </span>
                    </div>
                    {exp.dataset && (
                      <span className="text-xs text-gray-400">Dataset: {exp.dataset}</span>
                    )}
                    {exp.model_architecture && (
                      <span className="text-xs text-gray-400 ml-3">Model: {exp.model_architecture}</span>
                    )}

                    {/* Results preview */}
                    {exp.results && Object.keys(exp.results).length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {Object.entries(exp.results).map(([key, val]) => (
                          <span key={key} className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs">
                            <span className="font-medium">{key}:</span> {typeof val === 'number' ? val.toFixed(4) : val}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-1 flex-shrink-0">
                    <select
                      value={exp.status}
                      onChange={(e) => handleStatusChange(exp.id, e.target.value)}
                      className="input-field text-xs py-1 w-auto"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <option value="planned">Planned</option>
                      <option value="running">Running</option>
                      <option value="completed">Completed</option>
                      <option value="failed">Failed</option>
                    </select>
                    <button
                      onClick={() => handleEdit(exp)}
                      className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleDelete(exp.id)}
                      className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => setExpandedId(expandedId === exp.id ? null : exp.id)}
                      className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                    >
                      {expandedId === exp.id ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {expandedId === exp.id && (
                  <div className="mt-3 pt-3 border-t border-gray-100 space-y-2 text-xs text-gray-600">
                    {exp.hypothesis && <div><span className="font-medium text-gray-500">Hypothesis:</span> {exp.hypothesis}</div>}
                    {exp.description && <div><span className="font-medium text-gray-500">Description:</span> {exp.description}</div>}
                    {exp.methodology && <div><span className="font-medium text-gray-500">Methodology:</span> {exp.methodology}</div>}
                    {exp.hyperparameters && (
                      <div>
                        <span className="font-medium text-gray-500">Hyperparameters:</span>
                        <pre className="mt-1 p-2 bg-gray-50 rounded text-[11px] overflow-x-auto">
                          {JSON.stringify(exp.hyperparameters, null, 2)}
                        </pre>
                      </div>
                    )}
                    {exp.results && (
                      <div>
                        <span className="font-medium text-gray-500">Results:</span>
                        <pre className="mt-1 p-2 bg-green-50 rounded text-[11px] overflow-x-auto">
                          {JSON.stringify(exp.results, null, 2)}
                        </pre>
                      </div>
                    )}
                    {exp.conclusion && <div><span className="font-medium text-gray-500">Conclusion:</span> {exp.conclusion}</div>}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
