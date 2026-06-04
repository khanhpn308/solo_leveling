import PanelFrame from './PanelFrame'

function WeeklyMissionPanel({ weeklyMission }) {
  return (
    <PanelFrame title="Weekly Mission" tag={`Reward +${weeklyMission.rewardXp} player XP`}>
      <div className="weekly-highlight">
        <div>
          <p className="weekly-highlight__code">{weeklyMission.code}</p>
          <h3>{weeklyMission.title}</h3>
        </div>
        <div className="weekly-progress">
          <strong>{weeklyMission.progress}</strong>
          <span>quest tuần đã hoàn thành</span>
        </div>
      </div>

      <ul className="mission-lines">
        {weeklyMission.lines.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
    </PanelFrame>
  )
}

export default WeeklyMissionPanel
