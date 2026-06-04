function WeeklyMissionCard({ mission }) {
  if (!mission) {
    return <div className="empty-state">Chua tai duoc weekly mission.</div>
  }

  return (
    <section className="mission-card">
      <header className="mission-card__header">
        <div>
          <p>{mission.pattern_code}</p>
          <h3>{mission.title}</h3>
        </div>
        <div className="mission-card__reward">
          <strong>+{mission.reward_xp}</strong>
          <span>player XP</span>
        </div>
      </header>

      <p className="mission-card__description">{mission.description}</p>

      <div className="mission-item-list">
        {mission.items?.map((item) => (
          <article key={item.id} className={`mission-item mission-item--${item.status.toLowerCase()}`}>
            <div>
              <strong>{item.description}</strong>
              <span>
                {item.current_count}/{item.target_count}
              </span>
            </div>
            <em>{item.status}</em>
          </article>
        ))}
      </div>
    </section>
  )
}

export default WeeklyMissionCard
