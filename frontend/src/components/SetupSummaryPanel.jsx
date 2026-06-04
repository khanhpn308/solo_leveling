import PanelFrame from './PanelFrame'
import { TEST_EVIDENCE } from '../dashboard-data'

function SetupSummaryPanel({ player, skills }) {
  return (
    <PanelFrame
      title="Thiết lập chiến dịch"
      tag={player.hasStarted ? 'Đã khóa mốc bắt đầu' : `Còn ${player.daysUntilStart} ngày`}
    >
      <div className="setup-grid">
        <div className="setup-card">
          <span className="setup-card__label">Target</span>
          <strong>{player.target}</strong>
          <p>B1 hiện tại, Listening mạnh hơn Reading.</p>
        </div>
        <div className="setup-card">
          <span className="setup-card__label">Evidence</span>
          <strong>{TEST_EVIDENCE.length} nguồn điểm đầu vào</strong>
          <p>IELTS/TOEIC/Aptis/CEFR sẽ dùng để gợi ý skill rank.</p>
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
        <h3>Confirmed Skill Rank</h3>
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
