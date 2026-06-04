function StatCard({ label, value, detail, tone = 'cyan' }) {
  return (
    <article className={`hero-stat-card hero-stat-card--${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  )
}

function RoadmapHero({ player, roadmap, currentPhaseLabel, statCards, roadmapBounds }) {
  return (
    <section className="hero-panel">
      <div className="hero-panel__copy">
        <p className="hero-panel__eyebrow">Home Dashboard</p>
        <h1>{player.displayName}</h1>
        <p className="hero-panel__subtitle">
          Roadmap 18 thang dang chay. Phase hien tai la {currentPhaseLabel}, tap trung giu nhip quest va check-in hang ngay.
        </p>
      </div>

      <div className="roadmap-track">
        {roadmap.length === 0 ? (
          <div className="empty-state">Roadmap phase data dang tai hoac chua san sang.</div>
        ) : (
          roadmap.map((phase) => (
            <article
              key={phase.code}
              className={`roadmap-phase roadmap-phase--${phase.state} ${phase.isCurrent ? 'is-current' : ''}`}
            >
              <div className="roadmap-phase__beam" />
              <p>{phase.code}</p>
              <h2>{phase.title}</h2>
              <strong>{phase.subtitle}</strong>
              <span>{phase.dateLabel}</span>
              <small>{phase.weekLabel}</small>
              <div className="roadmap-phase__progress">
                <div style={{ width: `${phase.progress}%` }} />
              </div>
              <footer>
                <em>{phase.progress}% clear</em>
                <b>
                  {phase.completedSessions}/{phase.totalSessions} sessions
                </b>
              </footer>
            </article>
          ))
        )}
      </div>

      {roadmapBounds ? (
        <div className="roadmap-bounds">
          <span>Roadmap</span>
          <strong>
            {roadmapBounds.startDate} - {roadmapBounds.endDate}
          </strong>
        </div>
      ) : null}

      <div className="hero-stats-row">
        {statCards.map((card) => (
          <StatCard key={card.label} {...card} />
        ))}
      </div>
    </section>
  )
}

export default RoadmapHero
