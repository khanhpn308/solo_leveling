import PanelFrame from './PanelFrame'
import { TEST_EVIDENCE } from '../dashboard-data'

function SetupSummaryPanel({ player, skills }) {
  return (
    <PanelFrame title="Campaign Setup" tag={player.hasStarted ? 'Start locked in' : `${player.daysUntilStart} days left`}>
      <div className="setup-grid">
        <div className="setup-card">
          <span className="setup-card__label">Target</span>
          <strong>{player.target}</strong>
          <p>Current level is around B1, with Listening stronger than Reading.</p>
        </div>
        <div className="setup-card">
          <span className="setup-card__label">Evidence</span>
          <strong>{TEST_EVIDENCE.length} baseline evidence sources</strong>
          <p>IELTS / TOEIC / Aptis / CEFR records are used to suggest skill ranks.</p>
        </div>
      </div>

      <div className="setup-section">
        <h3>Test History</h3>
        <ul className="compact-list">
          {TEST_EVIDENCE.map((item) => (
            <li key={`${item.exam}-${item.date}`}>
              <strong>{item.exam}</strong>
              <span>{item.date}</span>
              <p>{item.details}</p>
            </li>
          ))}
        </ul>
      </div>

      <div className="setup-section">
        <h3>Confirmed Skill Ranks</h3>
        <div className="rank-row">
          {skills.map((skill) => (
            <div key={skill.id} className={`rank-token rank-token--${skill.theme.accent}`}>
              <span>{skill.name}</span>
              <strong>{skill.rank}</strong>
            </div>
          ))}
        </div>
      </div>
    </PanelFrame>
  )
}

export default SetupSummaryPanel
