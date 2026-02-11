import { TestTube } from 'lucide-react'
import ExperimentStep from './ExperimentStep'

export default function PartialExperiments(props) {
  return (
    <ExperimentStep
      {...props}
      experimentType="partial"
      icon={TestTube}
      title="Partial / Small-scale Experiments"
      description="Run partial experiments of the smallest possible scale to quickly validate your approach before committing to full-scale experiments."
    />
  )
}
