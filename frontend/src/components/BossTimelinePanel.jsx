import PanelFrame from './PanelFrame'
import { formatDate } from '../dashboard-data'

function BossTimelinePanel({ bosses }) {
  return (
    <PanelFrame title="Boss Timeline" tag="1 boss / tháng">
      <div className="boss-timeline">
        {bosses.map((boss) => (
          <article key={boss.id} className="boss-node">
            <div className="boss-node__line" />
            <div className="boss-node__content">
              <p>
                {formatDate(boss.battle_date)} · {boss.stage}
              </p>
              <h3>{boss.title}</h3>
              <span>{boss.goal}</span>
            </div>
            <strong className={`boss-status boss-status--${boss.status.toLowerCase()}`}>{boss.status}</strong>
          </article>
        ))}
      </div>
    </PanelFrame>
  )
}

export default BossTimelinePanel
