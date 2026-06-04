import PanelFrame from './PanelFrame'
import SkillCards from './SkillCards'

function SkillMatrixPanel({ skills }) {
  return (
    <PanelFrame title="Skill Matrix" tag="Confirmed Rank + XP / Level">
      <SkillCards skills={skills} />
    </PanelFrame>
  )
}

export default SkillMatrixPanel
