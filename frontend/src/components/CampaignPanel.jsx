import PanelFrame from './PanelFrame'
import { formatDate } from '../dashboard-data'

function CampaignPanel({ player, summary }) {
  return (
    <PanelFrame title="Campaign & Streak" tag={`Week ${player.currentWeekNo}`}>
      <div className="campaign-strip">
        <div className="campaign-metric">
          <span>Roadmap</span>
          <strong>{player.phaseLabel}</strong>
          <p>Bắt đầu: {formatDate(player.start_date)}</p>
        </div>
        <div className="campaign-metric">
          <span>Shield</span>
          <strong>2 / 2</strong>
          <p>UI sẵn sàng, backend shield chưa mở.</p>
        </div>
        <div className="campaign-metric">
          <span>Perfect Day</span>
          <strong>{summary.todayXp > 0 ? 'Có hoạt động' : 'Chưa kích hoạt'}</strong>
          <p>Điều kiện: đủ 3 daily quest + check-in trong ngày.</p>
        </div>
      </div>

      <div className="timeline-mini">
        <div className="timeline-mini__item is-active">
          <span>Phase hiện tại</span>
          <strong>{player.phaseLabel}</strong>
        </div>
        <div className="timeline-mini__item">
          <span>Quest đã clear</span>
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
