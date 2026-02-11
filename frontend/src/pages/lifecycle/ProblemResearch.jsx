import { useState, useEffect } from 'react'
import { papersAPI } from '../../api/client'
import StepHeader from './StepHeader'
import {
  Search, Plus, ExternalLink, BookOpen, FileText, Trash2, Edit3,
  Save, X, ChevronDown, ChevronUp,
} from 'lucide-react'

const reviewStatusColors = {
  pending: 'badge-yellow',
  reviewed: 'badge-blue',
  proposal_created: 'badge-green',
}

export default function ProblemResearch({ projectId, stepNumber, step, onStepUpdate }) {
  const [papers, setPapers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [expandedId, setExpandedId] = useState(null)
  const [form, setForm] = useState({
    title: '', authors: '', abstract: '', summary: '',
    source_url: '', doi: '', year: '', venue: '',
    open_problems: '', proposal_notes: '',
  })

  useEffect(() => {
    loadPapers()
  }, [projectId])

  const loadPapers = async () => {
    try {
      const res = await papersAPI.list(projectId)
      setPapers(res.data)
    } catch (err) {
      console.error('Failed to load papers:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const data = { ...form, year: form.year ? parseInt(form.year) : null }
    try {
      if (editingId) {
        await papersAPI.update(projectId, editingId, data)
      } else {
        await papersAPI.create(projectId, data)
      }
      resetForm()
      loadPapers()
    } catch (err) {
      console.error('Failed to save paper:', err)
    }
  }

  const handleEdit = (paper) => {
    setForm({
      title: paper.title || '',
      authors: paper.authors || '',
      abstract: paper.abstract || '',
      summary: paper.summary || '',
      source_url: paper.source_url || '',
      doi: paper.doi || '',
      year: paper.year || '',
      venue: paper.venue || '',
      open_problems: paper.open_problems || '',
      proposal_notes: paper.proposal_notes || '',
    })
    setEditingId(paper.id)
    setShowForm(true)
  }

  const handleDelete = async (paperId) => {
    if (!confirm('Delete this paper?')) return
    try {
      await papersAPI.delete(projectId, paperId)
      loadPapers()
    } catch (err) {
      console.error('Failed to delete paper:', err)
    }
  }

  const handleReviewStatus = async (paperId, status) => {
    try {
      await papersAPI.update(projectId, paperId, { review_status: status })
      loadPapers()
    } catch (err) {
      console.error('Failed to update status:', err)
    }
  }

  const resetForm = () => {
    setForm({
      title: '', authors: '', abstract: '', summary: '',
      source_url: '', doi: '', year: '', venue: '',
      open_problems: '', proposal_notes: '',
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
        icon={Search}
        description="Download research papers, create summaries, find open problem statements. Cycle: review -> create proposal -> update."
      />

      {/* Add paper button */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800">
          Research Papers ({papers.length})
        </h3>
        <button
          onClick={() => { resetForm(); setShowForm(!showForm) }}
          className="btn-primary flex items-center gap-1.5 text-sm"
        >
          <Plus className="w-4 h-4" />
          Add Paper
        </button>
      </div>

      {/* Paper Form */}
      {showForm && (
        <div className="card mb-4 border-primary-200">
          <h4 className="font-semibold text-gray-800 mb-4">
            {editingId ? 'Edit Paper' : 'Add New Paper'}
          </h4>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Title *</label>
              <input
                type="text"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className="input-field text-sm"
                placeholder="Paper title"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Authors</label>
                <input
                  type="text"
                  value={form.authors}
                  onChange={(e) => setForm({ ...form, authors: e.target.value })}
                  className="input-field text-sm"
                  placeholder="Author names"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Year</label>
                <input
                  type="number"
                  value={form.year}
                  onChange={(e) => setForm({ ...form, year: e.target.value })}
                  className="input-field text-sm"
                  placeholder="2024"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Venue</label>
                <input
                  type="text"
                  value={form.venue}
                  onChange={(e) => setForm({ ...form, venue: e.target.value })}
                  className="input-field text-sm"
                  placeholder="Conference/Journal"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">DOI</label>
                <input
                  type="text"
                  value={form.doi}
                  onChange={(e) => setForm({ ...form, doi: e.target.value })}
                  className="input-field text-sm"
                  placeholder="10.xxxx/xxxxx"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Source URL</label>
              <input
                type="url"
                value={form.source_url}
                onChange={(e) => setForm({ ...form, source_url: e.target.value })}
                className="input-field text-sm"
                placeholder="https://arxiv.org/abs/..."
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Abstract</label>
              <textarea
                value={form.abstract}
                onChange={(e) => setForm({ ...form, abstract: e.target.value })}
                className="input-field text-sm min-h-[60px]"
                placeholder="Paper abstract..."
                rows={3}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Summary</label>
              <textarea
                value={form.summary}
                onChange={(e) => setForm({ ...form, summary: e.target.value })}
                className="input-field text-sm min-h-[60px]"
                placeholder="Your summary of the paper..."
                rows={3}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Open Problems Found</label>
              <textarea
                value={form.open_problems}
                onChange={(e) => setForm({ ...form, open_problems: e.target.value })}
                className="input-field text-sm min-h-[60px]"
                placeholder="List open problems identified in this paper..."
                rows={2}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Proposal Notes</label>
              <textarea
                value={form.proposal_notes}
                onChange={(e) => setForm({ ...form, proposal_notes: e.target.value })}
                className="input-field text-sm min-h-[60px]"
                placeholder="Your proposal based on this paper..."
                rows={2}
              />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary text-sm flex items-center gap-1">
                <Save className="w-4 h-4" />
                {editingId ? 'Update' : 'Save'}
              </button>
              <button type="button" onClick={resetForm} className="btn-secondary text-sm">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Papers list */}
      {loading ? (
        <div className="text-center py-8">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      ) : papers.length === 0 ? (
        <div className="card text-center py-8">
          <BookOpen className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">No research papers added yet</p>
          <p className="text-gray-400 text-xs mt-1">Add papers from Mendeley, arXiv, or other sources</p>
        </div>
      ) : (
        <div className="space-y-3">
          {papers.map((paper) => (
            <div key={paper.id} className="card">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <FileText className="w-4 h-4 text-blue-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="font-medium text-gray-900 text-sm">{paper.title}</h4>
                      <div className="flex items-center gap-2 mt-1 flex-wrap">
                        {paper.authors && <span className="text-xs text-gray-500">{paper.authors}</span>}
                        {paper.year && <span className="text-xs text-gray-400">({paper.year})</span>}
                        {paper.venue && <span className="badge-blue text-[10px]">{paper.venue}</span>}
                        <span className={`${reviewStatusColors[paper.review_status]} text-[10px]`}>
                          {paper.review_status?.replace(/_/g, ' ')}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 flex-shrink-0">
                      {paper.source_url && (
                        <a
                          href={paper.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      )}
                      <button
                        onClick={() => handleEdit(paper)}
                        className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDelete(paper.id)}
                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setExpandedId(expandedId === paper.id ? null : paper.id)}
                        className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                      >
                        {expandedId === paper.id ? (
                          <ChevronUp className="w-3.5 h-3.5" />
                        ) : (
                          <ChevronDown className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>
                  </div>

                  {expandedId === paper.id && (
                    <div className="mt-3 space-y-3 text-sm">
                      {paper.abstract && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 mb-1">Abstract</p>
                          <p className="text-gray-600 text-xs">{paper.abstract}</p>
                        </div>
                      )}
                      {paper.summary && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 mb-1">Summary</p>
                          <p className="text-gray-600 text-xs">{paper.summary}</p>
                        </div>
                      )}
                      {paper.open_problems && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 mb-1">Open Problems</p>
                          <p className="text-gray-600 text-xs">{paper.open_problems}</p>
                        </div>
                      )}
                      {paper.proposal_notes && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 mb-1">Proposal Notes</p>
                          <p className="text-gray-600 text-xs">{paper.proposal_notes}</p>
                        </div>
                      )}
                      <div className="flex gap-2 pt-2">
                        <select
                          value={paper.review_status}
                          onChange={(e) => handleReviewStatus(paper.id, e.target.value)}
                          className="input-field text-xs py-1 w-auto"
                        >
                          <option value="pending">Pending Review</option>
                          <option value="reviewed">Reviewed</option>
                          <option value="proposal_created">Proposal Created</option>
                        </select>
                      </div>
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
