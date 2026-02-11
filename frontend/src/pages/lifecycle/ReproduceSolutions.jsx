import { Copy } from 'lucide-react'
import ExperimentStep from './ExperimentStep'

export default function ReproduceSolutions(props) {
  return (
    <ExperimentStep
      {...props}
      experimentType="reproduction"
      icon={Copy}
      title="Reproduced Solutions"
      description="Reproduce current state-of-the-art solutions to understand existing approaches, verify reported results, and establish a solid foundation for improvements."
    />
  )
}
