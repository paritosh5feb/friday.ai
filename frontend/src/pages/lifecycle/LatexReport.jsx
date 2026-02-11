import { useState, useEffect } from 'react'
import { reportsAPI } from '../../api/client'
import StepHeader from './StepHeader'
import {
  FileText, Plus, Save, Trash2, Edit3, Wand2, Download,
  ChevronDown, ChevronUp, Copy, Check,
} from 'lucide-react'

const templateLabels = {
  ieee: 'IEEE Conference',
  acm: 'ACM SIGCONF',
  neurips: 'NeurIPS',
  custom: 'Custom Article',
}

const statusColors = {
  draft: 'badge-yellow',
  review: 'badge-blue',
  final: 'badge-green',
}

export default function LatexReport({ projectId, stepNumber, step, onStepUpdate }) {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [expandedId, setExpandedId] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [copied, setCopied] = useState(null)
  const [form, setForm] = useState({
    title: '', template_type: 'ieee', content: '', status: 'draft',
  })

  useEffect(() => {
    loadReports()
  }, [projectId])

  const loadReports = async () => {
    try {
      const res = await reportsAPI.list(projectId)
      setReports(res.data)
    } catch (err) {
      console.error('Failed to load reports:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const data = {
      title: form.title,
      template_type: form.template_type,
      content: form.content || null,
      ...(editingId ? { status: form.status } : {}),
    }
    try {
      if (editingId) {
        await reportsAPI.update(projectId, editingId, data)
      } else {
        await reportsAPI.create(projectId, data)
      }
      resetForm()
      loadReports()
    } catch (err) {
      console.error('Failed to save report:', err)
    }
  }

  const handleGenerate = async (templateType) => {
    setGenerating(true)
    try {
      await reportsAPI.generate(projectId, templateType)
      loadReports()
    } catch (err) {
      console.error('Failed to generate:', err)
    } finally {
      setGenerating(false)
    }
  }

  const handleEdit = (report) => {
    setForm({
      title: report.title || '',
      template_type: report.template_type || 'ieee',
      content: report.content || '',
      status: report.status || 'draft',
    })
    setEditingId(report.id)
    setShowForm(true)
  }

  const handleDelete = async (reportId) => {
    if (!confirm('Delete this report?')) return
    try {
      await reportsAPI.delete(projectId, reportId)
      loadReports()
    } catch (err) {
      console.error('Failed to delete:', err)
    }
  }

  const handleCopy = async (content, reportId) => {
    try {
      await navigator.clipboard.writeText(content)
      setCopied(reportId)
      setTimeout(() => setCopied(null), 2000)
    } catch (err) {
      console.error('Copy failed:', err)
    }
  }

  const handleDownload = (report) => {
    const blob = new Blob([report.content || ''], { type: 'text/x-latex' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${report.title.replace(/\s+/g, '_')}.tex`
    a.click()
    URL.revokeObjectURL(url)
  }

  const resetForm = () => {
    setForm({ title: '', template_type: 'ieee', content: '', status: 'draft' })
    setEditingId(null)
    setShowForm(false)
  }

  return (
    <div>
      <StepHeader
        projectId={projectId}
        step={step}
        onStepUpdate={onStepUpdate}
        icon={FileText}
        description="Generate publication-ready LaTeX reports from all project data. Supports IEEE, ACM, NeurIPS, and custom templates."
      />

      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h3 className="font-semibold text-gray-800">LaTeX Reports ({reports.length})</h3>
        <div className="flex gap-2 flex-wrap">
          {/* Auto-generate buttons */}
          <div className="relative group">
            <button
              disabled={generating}
              className="btn-success flex items-center gap-1.5 text-sm"
              onClick={() => handleGenerate('ieee')}
            >
              <Wand2 className="w-4 h-4" />
              {generating ? 'Generating...' : 'Auto-Generate Report'}
            </button>
          </div>
          <button
            onClick={() => { resetForm(); setShowForm(!showForm) }}
            className="btn-primary flex items-center gap-1.5 text-sm"
          >
            <Plus className="w-4 h-4" />
            Custom Report
          </button>
        </div>
      </div>

      {/* Template selection for auto-generation */}
      <div className="card mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Quick Generate from Template</h4>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
          {Object.entries(templateLabels).map(([key, label]) => (
            <button
              key={key}
              onClick={() => handleGenerate(key)}
              disabled={generating}
              className="p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-all text-center text-sm"
            >
              <FileText className="w-5 h-5 text-primary-500 mx-auto mb-1" />
              <span className="font-medium text-gray-700">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Manual form */}
      {showForm && (
        <div className="card mb-4 border-primary-200">
          <h4 className="font-semibold text-gray-800 mb-4">
            {editingId ? 'Edit Report' : 'New Report'}
          </h4>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Title *</label>
                <input
                  type="text"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="input-field text-sm"
                  placeholder="Report title"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Template</label>
                <select
                  value={form.template_type}
                  onChange={(e) => setForm({ ...form, template_type: e.target.value })}
                  className="input-field text-sm"
                >
                  {Object.entries(templateLabels).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>
            </div>
            {editingId && (
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Status</label>
                <select
                  value={form.status}
                  onChange={(e) => setForm({ ...form, status: e.target.value })}
                  className="input-field text-sm w-auto"
                >
                  <option value="draft">Draft</option>
                  <option value="review">In Review</option>
                  <option value="final">Final</option>
                </select>
              </div>
            )}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">LaTeX Content</label>
              <textarea
                value={form.content}
                onChange={(e) => setForm({ ...form, content: e.target.value })}
                className="input-field text-sm font-mono min-h-[200px]"
                placeholder="\\documentclass{article}&#10;\\begin{document}&#10;..."
                rows={10}
              />
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

      {/* Reports list */}
      {loading ? (
        <div className="text-center py-8">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      ) : reports.length === 0 ? (
        <div className="card text-center py-8">
          <FileText className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">No LaTeX reports yet</p>
          <p className="text-gray-400 text-xs mt-1">Auto-generate a report from your project data</p>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((report) => (
            <div key={report.id} className="card">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <h4 className="font-medium text-gray-900 text-sm">{report.title}</h4>
                    <span className={statusColors[report.status] || 'badge-gray'}>
                      {report.status}
                    </span>
                    <span className="badge-purple text-[10px]">
                      {templateLabels[report.template_type] || report.template_type}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(report.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  {report.content && (
                    <>
                      <button
                        onClick={() => handleCopy(report.content, report.id)}
                        className="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded"
                        title="Copy LaTeX"
                      >
                        {copied === report.id ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                      </button>
                      <button
                        onClick={() => handleDownload(report)}
                        className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded"
                        title="Download .tex"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                    </>
                  )}
                  <button onClick={() => handleEdit(report)} className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded">
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                  <button onClick={() => handleDelete(report.id)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setExpandedId(expandedId === report.id ? null : report.id)}
                    className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                  >
                    {expandedId === report.id ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {expandedId === report.id && report.content && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <pre className="text-[11px] text-gray-600 bg-gray-50 p-4 rounded-lg overflow-x-auto max-h-96 overflow-y-auto font-mono leading-relaxed">
                    {report.content}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
