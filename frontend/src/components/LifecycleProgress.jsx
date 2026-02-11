import {
  Search, FlaskConical, Copy, TestTube, BarChart3,
  Table2, Scaling, MessageSquareText, FileText, Check, Clock, AlertCircle, Pause,
} from 'lucide-react'

const stepIcons = {
  1: Search,
  2: FlaskConical,
  3: Copy,
  4: TestTube,
  5: BarChart3,
  6: Table2,
  7: Scaling,
  8: MessageSquareText,
  9: FileText,
}

const statusColors = {
  not_started: 'bg-gray-200 text-gray-500 border-gray-300',
  in_progress: 'bg-blue-100 text-blue-600 border-blue-400 ring-2 ring-blue-200',
  in_review: 'bg-yellow-100 text-yellow-600 border-yellow-400',
  completed: 'bg-green-100 text-green-600 border-green-400',
  blocked: 'bg-red-100 text-red-600 border-red-400',
}

const statusBadgeColors = {
  not_started: 'badge-gray',
  in_progress: 'badge-blue',
  in_review: 'badge-yellow',
  completed: 'badge-green',
  blocked: 'badge-red',
}

const StatusIcon = ({ status }) => {
  switch (status) {
    case 'completed':
      return <Check className="w-3 h-3" />
    case 'in_progress':
      return <Clock className="w-3 h-3 animate-pulse" />
    case 'blocked':
      return <AlertCircle className="w-3 h-3" />
    case 'in_review':
      return <Pause className="w-3 h-3" />
    default:
      return null
  }
}

export default function LifecycleProgress({ steps, currentStep, onStepClick, compact = false }) {
  if (!steps || steps.length === 0) return null

  if (compact) {
    return (
      <div className="flex items-center gap-1">
        {steps.map((step) => {
          const Icon = stepIcons[step.step_number]
          return (
            <button
              key={step.step_number}
              onClick={() => onStepClick?.(step.step_number)}
              title={`Step ${step.step_number}: ${step.step_name}`}
              className={`w-7 h-7 rounded-full flex items-center justify-center border transition-all duration-200 hover:scale-110 ${
                statusColors[step.status]
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
            </button>
          )
        })}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {steps.map((step, index) => {
        const Icon = stepIcons[step.step_number]
        const isActive = step.step_number === currentStep
        return (
          <div key={step.step_number}>
            <button
              onClick={() => onStepClick?.(step.step_number)}
              className={`w-full flex items-start gap-3 p-3 rounded-xl border transition-all duration-200 text-left ${
                isActive
                  ? 'bg-primary-50 border-primary-200 shadow-sm'
                  : 'bg-white border-gray-200 hover:bg-gray-50 hover:border-gray-300'
              }`}
            >
              <div
                className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center border-2 ${
                  statusColors[step.status]
                }`}
              >
                <Icon className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400 font-mono">#{step.step_number}</span>
                  <h4 className={`text-sm font-semibold truncate ${isActive ? 'text-primary-900' : 'text-gray-700'}`}>
                    {step.step_name}
                  </h4>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <span className={statusBadgeColors[step.status]}>
                    <StatusIcon status={step.status} />
                    <span className="ml-1">{step.status.replace(/_/g, ' ')}</span>
                  </span>
                  {step.progress_percentage > 0 && (
                    <span className="text-xs text-gray-400">{step.progress_percentage}%</span>
                  )}
                </div>
                {/* Progress bar */}
                <div className="mt-2 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      step.status === 'completed'
                        ? 'bg-green-500'
                        : step.status === 'in_progress'
                        ? 'bg-blue-500'
                        : step.status === 'blocked'
                        ? 'bg-red-500'
                        : 'bg-gray-300'
                    }`}
                    style={{ width: `${step.progress_percentage}%` }}
                  />
                </div>
              </div>
            </button>

            {/* Connector line */}
            {index < steps.length - 1 && (
              <div className="flex justify-start ml-7">
                <div
                  className={`w-0.5 h-3 ${
                    step.status === 'completed' ? 'bg-green-300' : 'bg-gray-200'
                  }`}
                />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
