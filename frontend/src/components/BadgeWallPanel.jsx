import PanelFrame from './PanelFrame'

function BadgeWallPanel({ badges }) {
  return (
    <PanelFrame title="Badge Wall" tag="Milestone Rewards">
      <div className="badge-grid">
        {badges.map((badge) => (
          <article key={badge.id} className={`badge-node ${badge.unlocked ? 'is-unlocked' : 'is-locked'}`}>
            <span className="badge-node__icon">{badge.icon}</span>
            <strong>{badge.name}</strong>
            <p>{badge.description}</p>
          </article>
        ))}
      </div>
    </PanelFrame>
  )
}

export default BadgeWallPanel
