import PanelFrame from './PanelFrame'

function WeeklyMissionPanel({ weeklyMission, pulseActive = false }) {
  if (!weeklyMission) return null

  return (
    <PanelFrame
      title="Weekly Mission"
      tag={`Reward +${weeklyMission.rewardXp} player XP`}
      className={pulseActive ? 'panel-frame--reward-pulse' : ''}
    >
      <div className="weekly-highlight">
        <div>
          <p className="weekly-highlight__code">{weeklyMission.code}</p>
          <h3>{weeklyMission.title}</h3>
          <span className="weekly-highlight__state">{weeklyMission.sourceLabel}</span>
        </div>
        <div className="weekly-progress">
          <strong>{weeklyMission.progressText}</strong>
          <span>{weeklyMission.stateLabel}</span>
        </div>
      </div>

      <div className="mission-card__progress-track" aria-hidden="true">
        <span style={{ width: `${weeklyMission.percent}%` }} />
      </div>

      <ul className="mission-lines">
        {weeklyMission.items.map((item) => (
          <li key={item.id}>{item.description}</li>
        ))}
      </ul>
    </PanelFrame>
  )
}

export default WeeklyMissionPanel
