import { useState, useEffect } from 'react'
import { benchmarksAPI } from '../../api/client'
import StepHeader from './StepHeader'
import {
  BarChart3, Plus, Save, Trash2, Edit3, ChevronDown, ChevronUp, Star,
} from 'lucide-react'

export default function BenchmarkEvaluations({ projectId, stepNumber, step, onStepUpdate }) {
  const [benchmarks, setBenchmarks] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [expandedId, setExpandedId] = useState(null)
  const [form, setForm] = useState({
    benchmark_name: '', dataset: '', model_name: '',
    metrics: '{}', environment: '', notes: '', is_baseline: false,
  })

  useEffect(() => {
    loadBenchmarks()
  }, [projectId])

  const loadBenchmarks = async () => {
    try {
      const res = await benchmarksAPI.list(projectId)
      setBenchmarks(res.data)
    } catch (err) {
      console.error('Failed to load benchmarks:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    let metrics = null
    try { metrics = form.metrics ? JSON.parse(form.metrics) : null } catch { metrics = null }

    const data = {
      benchmark_name: form.benchmark_name,
      dataset: form.dataset || null,
      model_name: form.model_name || null,
      metrics,
      environment: form.environment || null,
      notes: form.notes || null,
      is_baseline: form.is_baseline,
    }

    try {
      if (editingId) {
        await benchmarksAPI.update(projectId, editingId, data)
      } else {
        await benchmarksAPI.create(projectId, data)
      }
      resetForm()
      loadBenchmarks()
    } catch (err) {
      console.error('Failed to save benchmark:', err)
    }
  }

  const handleEdit = (bench) => {
    setForm({
      benchmark_name: bench.benchmark_name || '',
      dataset: bench.dataset || '',
      model_name: bench.model_name || '',
      metrics: bench.metrics ? JSON.stringify(bench.metrics, null, 2) : '{}',
      environment: bench.environment || '',
      notes: bench.notes || '',
      is_baseline: bench.is_baseline || false,
    })
    setEditingId(bench.id)
    setShowForm(true)
  }

  const handleDelete = async (benchId) => {
    if (!confirm('Delete this benchmark result?')) return
    try {
      await benchmarksAPI.delete(projectId, benchId)
      loadBenchmarks()
    } catch (err) {
      console.error('Failed to delete:', err)
    }
  }

  const resetForm = () => {
    setForm({
      benchmark_name: '', dataset: '', model_name: '',
      metrics: '{}', environment: '', notes: '', is_baseline: false,
    })
    setEditingId(null)
    setShowForm(false)
  }

  return (
    <div>
      <StepHeader
        projectId={projectId}
        step={step}
        onStepUpdate={onStepUpdate}
        icon={BarChart3}
        description="Run comprehensive benchmark evaluations against standard datasets and metrics to validate your approach against established baselines."
      />

      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800">
          Benchmark Results ({benchmarks.length})
        </h3>
        <button
          onClick={() => { resetForm(); setShowForm(!showForm) }}
          className="btn-primary flex items-center gap-1.5 text-sm"
        >
          <Plus className="w-4 h-4" />
          Add Benchmark
        </button>
      </div>

      {showForm && (
        <div className="card mb-4 border-primary-200">
          <h4 className="font-semibold text-gray-800 mb-4">
            {editingId ? 'Edit Benchmark' : 'New Benchmark Result'}
          </h4>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Benchmark Name *</label>
              <input
                type="text"
                value={form.benchmark_name}
                onChange={(e) => setForm({ ...form, benchmark_name: e.target.value })}
                className="input-field text-sm"
                placeholder="e.g., GLUE, ImageNet, BLEU"
                required
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
                  placeholder="e.g., MNLI, SST-2"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Model Name</label>
                <input
                  type="text"
                  value={form.model_name}
                  onChange={(e) => setForm({ ...form, model_name: e.target.value })}
                  className="input-field text-sm"
                  placeholder="e.g., BERT-base"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Metrics (JSON)</label>
              <textarea
                value={form.metrics}
                onChange={(e) => setForm({ ...form, metrics: e.target.value })}
                className="input-field text-sm font-mono min-h-[80px]"
                placeholder='{"accuracy": 0.95, "f1": 0.93, "precision": 0.94, "recall": 0.92}'
                rows={4}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Environment</label>
              <textarea
                value={form.environment}
                onChange={(e) => setForm({ ...form, environment: e.target.value })}
                className="input-field text-sm"
                placeholder="Hardware/software configuration..."
                rows={2}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Notes</label>
              <textarea
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                className="input-field text-sm"
                placeholder="Additional notes..."
                rows={2}
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_baseline"
                checked={form.is_baseline}
                onChange={(e) => setForm({ ...form, is_baseline: e.target.checked })}
                className="w-4 h-4 text-primary-600 rounded"
              />
              <label htmlFor="is_baseline" className="text-sm text-gray-700">
                This is a baseline benchmark
              </label>
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary text-sm flex items-center gap-1">
                <Save className="w-4 h-4" />
                {editingId ? 'Update' : 'Save'}
              </button>
              <button type="button" onClick={resetForm} className="btn-secondary text-sm">Cancel</button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      ) : benchmarks.length === 0 ? (
        <div className="card text-center py-8">
          <BarChart3 className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">No benchmark results yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {benchmarks.map((bench) => (
            <div key={bench.id} className="card">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium text-gray-900 text-sm">{bench.benchmark_name}</h4>
                    {bench.is_baseline && (
                      <span className="badge-yellow flex items-center gap-1">
                        <Star className="w-3 h-3" />
                        Baseline
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-400">
                    {bench.dataset && <span>Dataset: {bench.dataset}</span>}
                    {bench.model_name && <span>Model: {bench.model_name}</span>}
                  </div>

                  {bench.metrics && Object.keys(bench.metrics).length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {Object.entries(bench.metrics).map(([key, val]) => (
                        <span key={key} className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">
                          <span className="font-medium">{key}:</span> {typeof val === 'number' ? val.toFixed(4) : val}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  <button onClick={() => handleEdit(bench)} className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded">
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                  <button onClick={() => handleDelete(bench.id)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setExpandedId(expandedId === bench.id ? null : bench.id)}
                    className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                  >
                    {expandedId === bench.id ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {expandedId === bench.id && (
                <div className="mt-3 pt-3 border-t border-gray-100 space-y-2 text-xs text-gray-600">
                  {bench.environment && <div><span className="font-medium">Environment:</span> {bench.environment}</div>}
                  {bench.notes && <div><span className="font-medium">Notes:</span> {bench.notes}</div>}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
