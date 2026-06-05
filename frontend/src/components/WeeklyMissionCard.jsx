function WeeklyMissionCard({ mission, loading, error, pulseActive, claimPending, onClaim }) {
  if (loading) {
    return <div className="empty-state">Syncing the weekly mission feed...</div>
  }

  if (error) {
    return <div className="empty-state">Weekly mission unavailable: {error}</div>
  }

  if (!mission) {
    return <div className="empty-state">Could not load the weekly mission.</div>
  }

  return (
    <section className={`mission-card ${pulseActive ? 'mission-card--pulse' : ''}`}>
      <header className="mission-card__header">
        <div>
          <p>{mission.code}</p>
          <h3>{mission.title}</h3>
          <span className="mission-card__state">{mission.stateLabel}</span>
        </div>
        <div className="mission-card__reward">
          <strong>+{mission.rewardXp}</strong>
          <span>player XP</span>
        </div>
      </header>

      <div className="mission-card__progress">
        <div className="mission-card__progress-meta">
          <strong>{mission.progressText}</strong>
          <span>{mission.sourceLabel}</span>
        </div>
        <div className="mission-card__progress-track" aria-hidden="true">
          <span style={{ width: `${mission.percent}%` }} />
        </div>
      </div>

      <p className="mission-card__description">{mission.description || mission.helperText}</p>
      <p className="mission-card__helper">{mission.helperText}</p>

      <div className="mission-card__claim-row">
        <span>Reward cache: +{mission.rewardXp} XP</span>
        <button
          className={`system-button quest-action-button quest-action-button--${mission.isComplete && !mission.rewardClaimed ? 'claim' : 'claimed'}`}
          type="button"
          disabled={!mission.isComplete || mission.rewardClaimed || claimPending}
          onClick={() => onClaim && onClaim(mission)}
        >
          {claimPending ? 'Claiming...' : mission.rewardClaimed ? 'CLAIMED' : 'CLAIM'}
        </button>
      </div>

      <div className="mission-item-list">
        {mission.items?.map((item) => (
          <article
            key={item.id}
            className={`mission-item mission-item--${String(item.status || 'pending').toLowerCase()} ${item.isComplete ? 'is-complete' : ''}`}
          >
            <div>
              <strong>{item.description}</strong>
              <span>{item.progressLabel}</span>
            </div>
            <em>{item.statusLabel}</em>
          </article>
        ))}
      </div>
    </section>
  )
}

export default WeeklyMissionCard
