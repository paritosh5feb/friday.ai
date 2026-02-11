import { useState, useEffect } from 'react'
import { tablesAPI } from '../../api/client'
import StepHeader from './StepHeader'
import {
  Table2, Plus, Save, Trash2, Edit3, Wand2, ChevronDown, ChevronUp,
} from 'lucide-react'

export default function ResultTables({ projectId, stepNumber, step, onStepUpdate }) {
  const [tables, setTables] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [expandedId, setExpandedId] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [form, setForm] = useState({
    title: '', description: '', table_type: 'comparison',
    headers: '', rows: '',
  })

  useEffect(() => {
    loadTables()
  }, [projectId])

  const loadTables = async () => {
    try {
      const res = await tablesAPI.list(projectId)
      setTables(res.data)
    } catch (err) {
      console.error('Failed to load tables:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    let headers = []
    let rows = []
    try {
      headers = form.headers.split(',').map(h => h.trim()).filter(Boolean)
      rows = form.rows.split('\n').filter(Boolean).map(row =>
        row.split(',').map(cell => cell.trim())
      )
    } catch {}

    const data = {
      title: form.title,
      description: form.description || null,
      table_type: form.table_type,
      table_data: { headers, rows },
    }

    try {
      if (editingId) {
        await tablesAPI.update(projectId, editingId, data)
      } else {
        await tablesAPI.create(projectId, data)
      }
      resetForm()
      loadTables()
    } catch (err) {
      console.error('Failed to save table:', err)
    }
  }

  const handleAutoGenerate = async () => {
    setGenerating(true)
    try {
      await tablesAPI.autoGenerate(projectId)
      loadTables()
    } catch (err) {
      console.error('Failed to auto-generate:', err)
    } finally {
      setGenerating(false)
    }
  }

  const handleEdit = (table) => {
    const data = table.table_data || {}
    setForm({
      title: table.title || '',
      description: table.description || '',
      table_type: table.table_type || 'comparison',
      headers: (data.headers || []).join(', '),
      rows: (data.rows || []).map(r => r.join(', ')).join('\n'),
    })
    setEditingId(table.id)
    setShowForm(true)
  }

  const handleDelete = async (tableId) => {
    if (!confirm('Delete this table?')) return
    try {
      await tablesAPI.delete(projectId, tableId)
      loadTables()
    } catch (err) {
      console.error('Failed to delete:', err)
    }
  }

  const resetForm = () => {
    setForm({ title: '', description: '', table_type: 'comparison', headers: '', rows: '' })
    setEditingId(null)
    setShowForm(false)
  }

  const renderTable = (tableData) => {
    if (!tableData?.headers?.length) return <p className="text-xs text-gray-400 italic">No data</p>
    return (
      <div className="overflow-x-auto">
        <table className="min-w-full text-xs">
          <thead>
            <tr className="bg-gray-50">
              {tableData.headers.map((h, i) => (
                <th key={i} className="px-3 py-2 text-left font-semibold text-gray-600 border-b">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(tableData.rows || []).map((row, ri) => (
              <tr key={ri} className="hover:bg-gray-50">
                {row.map((cell, ci) => (
                  <td key={ci} className="px-3 py-1.5 text-gray-700 border-b border-gray-100">{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  return (
    <div>
      <StepHeader
        projectId={projectId}
        step={step}
        onStepUpdate={onStepUpdate}
        icon={Table2}
        description="Create tables summarizing results from partial experiments and benchmark evaluations. You can auto-generate tables from existing data."
      />

      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h3 className="font-semibold text-gray-800">Result Tables ({tables.length})</h3>
        <div className="flex gap-2">
          <button
            onClick={handleAutoGenerate}
            disabled={generating}
            className="btn-success flex items-center gap-1.5 text-sm"
          >
            <Wand2 className="w-4 h-4" />
            {generating ? 'Generating...' : 'Auto-Generate'}
          </button>
          <button
            onClick={() => { resetForm(); setShowForm(!showForm) }}
            className="btn-primary flex items-center gap-1.5 text-sm"
          >
            <Plus className="w-4 h-4" />
            Add Table
          </button>
        </div>
      </div>

      {showForm && (
        <div className="card mb-4 border-primary-200">
          <h4 className="font-semibold text-gray-800 mb-4">
            {editingId ? 'Edit Table' : 'New Result Table'}
          </h4>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Title *</label>
              <input
                type="text"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className="input-field text-sm"
                placeholder="Table title"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
                <input
                  type="text"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="input-field text-sm"
                  placeholder="Table description"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Type</label>
                <select
                  value={form.table_type}
                  onChange={(e) => setForm({ ...form, table_type: e.target.value })}
                  className="input-field text-sm"
                >
                  <option value="comparison">Comparison</option>
                  <option value="ablation">Ablation Study</option>
                  <option value="summary">Summary</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Headers (comma-separated)</label>
              <input
                type="text"
                value={form.headers}
                onChange={(e) => setForm({ ...form, headers: e.target.value })}
                className="input-field text-sm"
                placeholder="Model, Accuracy, F1, Precision, Recall"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Rows (one row per line, comma-separated values)
              </label>
              <textarea
                value={form.rows}
                onChange={(e) => setForm({ ...form, rows: e.target.value })}
                className="input-field text-sm font-mono min-h-[80px]"
                placeholder="BERT-base, 0.95, 0.93, 0.94, 0.92&#10;RoBERTa, 0.96, 0.95, 0.95, 0.94"
                rows={4}
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

      {loading ? (
        <div className="text-center py-8">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      ) : tables.length === 0 ? (
        <div className="card text-center py-8">
          <Table2 className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">No result tables yet</p>
          <p className="text-gray-400 text-xs mt-1">Auto-generate from experiments or create manually</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tables.map((table) => (
            <div key={table.id} className="card">
              <div className="flex items-start justify-between gap-3 mb-3">
                <div>
                  <h4 className="font-medium text-gray-900 text-sm">{table.title}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    {table.description && <span className="text-xs text-gray-400">{table.description}</span>}
                    <span className="badge-blue text-[10px]">{table.table_type}</span>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={() => handleEdit(table)} className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded">
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                  <button onClick={() => handleDelete(table.id)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
              {renderTable(table.table_data)}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
