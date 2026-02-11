import { useState } from 'react'
import { lifecycleAPI } from '../../api/client'
import { CheckCircle, Clock, AlertCircle, Play, Pause, RotateCcw } from 'lucide-react'

const statusConfig = {
  not_started: { label: 'Not Started', color: 'bg-gray-100 text-gray-600', icon: Clock },
  in_progress: { label: 'In Progress', color: 'bg-blue-100 text-blue-700', icon: Play },
  in_review: { label: 'In Review', color: 'bg-yellow-100 text-yellow-700', icon: Pause },
  completed: { label: 'Completed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  blocked: { label: 'Blocked', color: 'bg-red-100 text-red-700', icon: AlertCircle },
}

export default function StepHeader({ projectId, step, onStepUpdate, icon: Icon, description }) {
  const [notes, setNotes] = useState(step?.notes || '')
  const [progress, setProgress] = useState(step?.progress_percentage || 0)
  const [saving, setSaving] = useState(false)

  const updateStep = async (data) => {
    setSaving(true)
    try {
      await lifecycleAPI.updateStep(projectId, step.step_number, data)
      onStepUpdate?.()
    } catch (err) {
      console.error('Failed to update step:', err)
    } finally {
      setSaving(false)
    }
  }

  const handleStatusChange = (newStatus) => {
    updateStep({ status: newStatus })
  }

  const handleSaveNotes = () => {
    updateStep({ notes, progress_percentage: progress })
  }

  if (!step) return null

  const StatusIcon = statusConfig[step.status]?.icon || Clock

  return (
    <div className="card mb-6">
      <div className="flex flex-col sm:flex-row sm:items-start gap-4">
        <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center flex-shrink-0">
          <Icon className="w-6 h-6 text-primary-600" />
        </div>
        <div className="flex-1">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
            <h2 className="text-lg font-bold text-gray-900">
              Step {step.step_number}: {step.step_name}
            </h2>
            <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${statusConfig[step.status]?.color}`}>
              <StatusIcon className="w-3 h-3" />
              {statusConfig[step.status]?.label}
            </span>
          </div>
          <p className="text-sm text-gray-500 mb-4">{description || step.description}</p>

          {/* Status & Progress controls */}
          <div className="flex flex-col sm:flex-row gap-3 mb-4">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Status</label>
              <select
                value={step.status}
                onChange={(e) => handleStatusChange(e.target.value)}
                className="input-field text-sm py-1.5 w-auto"
              >
                <option value="not_started">Not Started</option>
                <option value="in_progress">In Progress</option>
                <option value="in_review">In Review</option>
                <option value="completed">Completed</option>
                <option value="blocked">Blocked</option>
              </select>
            </div>
            <div className="flex-1 max-w-xs">
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Progress: {progress}%
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={progress}
                onChange={(e) => setProgress(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
              />
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Notes</label>
            <div className="flex gap-2">
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="input-field text-sm min-h-[60px] resize-y flex-1"
                placeholder="Add notes for this step..."
                rows={2}
              />
              <button
                onClick={handleSaveNotes}
                disabled={saving}
                className="btn-primary self-end text-sm py-1.5 px-3"
              >
                {saving ? '...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
