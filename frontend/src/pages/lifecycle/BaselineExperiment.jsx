import { FlaskConical } from 'lucide-react'
import ExperimentStep from './ExperimentStep'

export default function BaselineExperiment(props) {
  return (
    <ExperimentStep
      {...props}
      experimentType="baseline"
      icon={FlaskConical}
      title="Baseline Experiments"
      description="Establish baseline experiments to validate your Standard Experimental Hypothesis (SEH). These serve as the reference point for all future experiments."
    />
  )
}
