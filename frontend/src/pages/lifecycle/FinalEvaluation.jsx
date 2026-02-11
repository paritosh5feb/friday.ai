import { useState, useEffect } from 'react'
import { experimentsAPI, benchmarksAPI } from '../../api/client'
import StepHeader from './StepHeader'
import { MessageSquareText, CheckCircle, XCircle, BarChart3, FlaskConical } from 'lucide-react'

export default function FinalEvaluation({ projectId, stepNumber, step, onStepUpdate }) {
  const [experiments, setExperiments] = useState([])
  const [benchmarks, setBenchmarks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [projectId])

  const loadData = async () => {
    try {
      const [expRes, benchRes] = await Promise.all([
        experimentsAPI.list(projectId),
        benchmarksAPI.list(projectId),
      ])
      setExperiments(expRes.data)
      setBenchmarks(benchRes.data)
    } catch (err) {
      console.error('Failed to load data:', err)
    } finally {
      setLoading(false)
    }
  }

  const completedExps = experiments.filter(e => e.status === 'completed')
  const failedExps = experiments.filter(e => e.status === 'failed')
  const totalMetrics = new Set()
  experiments.forEach(e => {
    if (e.results) Object.keys(e.results).forEach(k => totalMetrics.add(k))
  })
  benchmarks.forEach(b => {
    if (b.metrics) Object.keys(b.metrics).forEach(k => totalMetrics.add(k))
  })

  if (loading) {
    return (
      <div>
        <StepHeader
          projectId={projectId}
          step={step}
          onStepUpdate={onStepUpdate}
          icon={MessageSquareText}
        />
        <div className="text-center py-8">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <StepHeader
        projectId={projectId}
        step={step}
        onStepUpdate={onStepUpdate}
        icon={MessageSquareText}
        description="Evaluation, collation, discussion, and evaluation of final results across all experiments and benchmarks."
      />

      {/* Summary Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="card text-center">
          <FlaskConical className="w-6 h-6 text-blue-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-gray-900">{experiments.length}</p>
          <p className="text-xs text-gray-500">Total Experiments</p>
        </div>
        <div className="card text-center">
          <CheckCircle className="w-6 h-6 text-green-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-green-600">{completedExps.length}</p>
          <p className="text-xs text-gray-500">Completed</p>
        </div>
        <div className="card text-center">
          <XCircle className="w-6 h-6 text-red-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-red-600">{failedExps.length}</p>
          <p className="text-xs text-gray-500">Failed</p>
        </div>
        <div className="card text-center">
          <BarChart3 className="w-6 h-6 text-purple-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-gray-900">{benchmarks.length}</p>
          <p className="text-xs text-gray-500">Benchmarks</p>
        </div>
      </div>

      {/* Collated Results */}
      {(completedExps.length > 0 || benchmarks.length > 0) && totalMetrics.size > 0 && (
        <div className="card mb-6">
          <h3 className="font-semibold text-gray-800 mb-4">Collated Results Overview</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full text-xs">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-3 py-2 text-left font-semibold text-gray-600 border-b">Name</th>
                  <th className="px-3 py-2 text-left font-semibold text-gray-600 border-b">Type</th>
                  <th className="px-3 py-2 text-left font-semibold text-gray-600 border-b">Status</th>
                  {[...totalMetrics].sort().map(m => (
                    <th key={m} className="px-3 py-2 text-left font-semibold text-gray-600 border-b">{m}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {completedExps.map(exp => (
                  <tr key={`exp-${exp.id}`} className="hover:bg-gray-50">
                    <td className="px-3 py-1.5 text-gray-700 border-b border-gray-100 font-medium">{exp.name}</td>
                    <td className="px-3 py-1.5 text-gray-500 border-b border-gray-100">{exp.experiment_type}</td>
                    <td className="px-3 py-1.5 border-b border-gray-100">
                      <span className="badge-green">completed</span>
                    </td>
                    {[...totalMetrics].sort().map(m => (
                      <td key={m} className="px-3 py-1.5 text-gray-700 border-b border-gray-100">
                        {exp.results?.[m] !== undefined
                          ? (typeof exp.results[m] === 'number' ? exp.results[m].toFixed(4) : exp.results[m])
                          : '-'}
                      </td>
                    ))}
                  </tr>
                ))}
                {benchmarks.map(bench => (
                  <tr key={`bench-${bench.id}`} className="hover:bg-blue-50">
                    <td className="px-3 py-1.5 text-gray-700 border-b border-gray-100 font-medium">{bench.benchmark_name}</td>
                    <td className="px-3 py-1.5 text-gray-500 border-b border-gray-100">benchmark</td>
                    <td className="px-3 py-1.5 border-b border-gray-100">
                      {bench.is_baseline
                        ? <span className="badge-yellow">baseline</span>
                        : <span className="badge-blue">benchmark</span>}
                    </td>
                    {[...totalMetrics].sort().map(m => (
                      <td key={m} className="px-3 py-1.5 text-gray-700 border-b border-gray-100">
                        {bench.metrics?.[m] !== undefined
                          ? (typeof bench.metrics[m] === 'number' ? bench.metrics[m].toFixed(4) : bench.metrics[m])
                          : '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Experiment Conclusions */}
      {completedExps.some(e => e.conclusion) && (
        <div className="card mb-6">
          <h3 className="font-semibold text-gray-800 mb-4">Experiment Conclusions</h3>
          <div className="space-y-3">
            {completedExps.filter(e => e.conclusion).map(exp => (
              <div key={exp.id} className="p-3 bg-green-50 rounded-lg border border-green-100">
                <h4 className="text-sm font-medium text-green-800 mb-1">{exp.name} ({exp.experiment_type})</h4>
                <p className="text-xs text-green-700">{exp.conclusion}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Discussion Placeholder */}
      <div className="card">
        <h3 className="font-semibold text-gray-800 mb-2">Discussion Points</h3>
        <p className="text-sm text-gray-500 mb-3">
          Use the step notes above to document your discussion, analysis, and final evaluation of the results.
          Consider the following:
        </p>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-400 mt-1.5 flex-shrink-0"></span>
            How do your results compare to the baseline and reproduced solutions?
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-400 mt-1.5 flex-shrink-0"></span>
            Did scaling the experiments improve or degrade performance?
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-400 mt-1.5 flex-shrink-0"></span>
            What are the key takeaways and limitations?
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-400 mt-1.5 flex-shrink-0"></span>
            What future work could extend these findings?
          </li>
        </ul>
      </div>
    </div>
  )
}
