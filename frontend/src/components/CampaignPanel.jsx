import PanelFrame from './PanelFrame'
import { formatDate } from '../dashboard-data'

function CampaignPanel({ player, summary }) {
  return (
    <PanelFrame title="Campaign & Streak" tag={`Week ${player.currentWeekNo}`}>
      <div className="campaign-strip">
        <div className="campaign-metric">
          <span>Roadmap</span>
          <strong>{player.phaseLabel}</strong>
          <p>Start: {formatDate(player.start_date)}</p>
        </div>
        <div className="campaign-metric">
          <span>Shield</span>
          <strong>2 / 2</strong>
          <p>UI is ready, but backend shield logic is not enabled yet.</p>
        </div>
        <div className="campaign-metric">
          <span>Perfect Day</span>
          <strong>{summary.todayXp > 0 ? 'Activity detected' : 'Not activated'}</strong>
          <p>Condition: complete 3 daily quests and submit a check-in on the same day.</p>
        </div>
      </div>

      <div className="timeline-mini">
        <div className="timeline-mini__item is-active">
          <span>Current phase</span>
          <strong>{player.phaseLabel}</strong>
        </div>
        <div className="timeline-mini__item">
          <span>Quests cleared</span>
          <strong>
            {summary.totalCompletedQuests}/{summary.totalQuests}
          </strong>
        </div>
        <div className="timeline-mini__item">
          <span>Week XP</span>
          <strong>{summary.weekXp} XP</strong>
        </div>
      </div>
    </PanelFrame>
  )
}

export default CampaignPanel
