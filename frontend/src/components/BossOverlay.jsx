import BossTimelinePanel from './BossTimelinePanel'
import { formatDate } from '../dashboard-data'
import OverlayFrame from './OverlayFrame'

function BossOverlay({ open, bossView, onClose }) {
  return (
    <OverlayFrame
      open={open}
      title="Boss Battles"
      subtitle="Current boss first, then the full battle timeline."
      onClose={onClose}
      className="overlay-frame--boss"
    >
      {bossView.currentBoss ? (
        <section className={`boss-hero boss-hero--${bossView.currentBoss.uiStatus}`}>
          <div>
            <p>{`${formatDate(bossView.currentBoss.battle_date)} / ${bossView.currentBoss.stage}`}</p>
            <h3>{bossView.currentBoss.title}</h3>
            <strong>{bossView.currentBoss.goal}</strong>
            <span>{bossView.currentBoss.practice_suggestion || 'No extra practice suggestion.'}</span>
          </div>
          <div className="boss-hero__reward">
            <em>{bossView.currentBoss.displayStatus}</em>
            <strong>+{bossView.currentBoss.reward_xp} XP</strong>
          </div>
        </section>
      ) : (
        <div className="empty-state">No boss battle data is available yet.</div>
      )}

      <BossTimelinePanel bosses={bossView.timeline} />
    </OverlayFrame>
  )
}

export default BossOverlay
