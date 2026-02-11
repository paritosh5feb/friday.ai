import { Scaling } from 'lucide-react'
import ExperimentStep from './ExperimentStep'

export default function ScaleExperiments(props) {
  return (
    <ExperimentStep
      {...props}
      experimentType="scaled"
      icon={Scaling}
      title="Scaled Experiments"
      description="If preliminary results look promising, scale up the small experiments to full-scale runs with complete datasets and comprehensive configurations."
    />
  )
}
