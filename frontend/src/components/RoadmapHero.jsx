import { useEffect, useMemo, useState } from 'react'
import { formatDate } from '../dashboard-data'
import OverlayFrame from './OverlayFrame'

function StatCard({ label, value, detail, tone = 'cyan' }) {
  return (
    <article className={`hero-stat-card hero-stat-card--${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  )
}

function buildPhaseSessions(phase) {
  if (!phase?.weeks?.length) return []

  return phase.weeks.flatMap((week) =>
    week.sessions.map((session) => ({
      ...session,
      weekNo: week.week_no,
      weekRangeLabel: week.weekRangeLabel,
      weeklyFocus: week.weekly_focus,
    })),
  )
}

function RoadmapHero({ player, roadmap, mainQuestMap, currentPhaseLabel, statCards, roadmapBounds }) {
  const [selectedPhaseCode, setSelectedPhaseCode] = useState(null)
  const [isPhaseOverlayOpen, setIsPhaseOverlayOpen] = useState(false)

  useEffect(() => {
    const defaultPhaseCode = mainQuestMap?.currentPhaseCode ?? roadmap.find((phase) => phase.isCurrent)?.code ?? roadmap[0]?.code ?? null
    setSelectedPhaseCode((current) => current ?? defaultPhaseCode)
  }, [mainQuestMap?.currentPhaseCode, roadmap])

  const selectedPhase = useMemo(
    () => mainQuestMap?.phases?.find((phase) => phase.code === selectedPhaseCode) ?? mainQuestMap?.phases?.[0] ?? null,
    [mainQuestMap, selectedPhaseCode],
  )

  const selectedPhaseSessions = useMemo(() => buildPhaseSessions(selectedPhase), [selectedPhase])

  return (
    <section className="hero-panel">
      <div className="hero-panel__copy">
        <p className="hero-panel__eyebrow">Home Dashboard</p>
        <h1>{player.displayName}</h1>
        <p className="hero-panel__subtitle">
          The 18-month roadmap is live. The current phase is {currentPhaseLabel}, with a focus on steady quest rhythm and daily check-ins.
        </p>
      </div>

      <div className="roadmap-track">
        {roadmap.length === 0 ? (
          <div className="empty-state">Roadmap phase data is still loading or not available yet.</div>
        ) : (
          roadmap.map((phase) => (
            <button
              key={phase.code}
              className={`roadmap-phase roadmap-phase--${phase.state} ${phase.isCurrent ? 'is-current' : ''} ${
                selectedPhaseCode === phase.code ? 'is-selected' : ''
              }`}
              type="button"
              onClick={() => {
                setSelectedPhaseCode(phase.code)
                setIsPhaseOverlayOpen(true)
              }}
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
            </button>
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

      {selectedPhase && isPhaseOverlayOpen ? (
        <OverlayFrame
          title={`${selectedPhase.title} / ${selectedPhase.subtitle}`}
          subtitle={`Week ${selectedPhase.weekStart}-${selectedPhase.weekEnd} / ${selectedPhase.completedSessions}/${selectedPhase.totalSessions} sessions completed`}
          onClose={() => setIsPhaseOverlayOpen(false)}
          className="overlay-frame--phase"
          actions={<strong className="roadmap-phase-overlay__count">{selectedPhaseSessions.length} sessions</strong>}
        >
          <section className="roadmap-phase-overlay">
            <header className="roadmap-phase-detail__header">
              <div>
                <p className="panel-frame__eyebrow">Phase sessions</p>
                <h3>
                  {selectedPhase.title} / {selectedPhase.subtitle}
                </h3>
                <span>
                  {selectedPhase.weeks.length} weeks / {selectedPhase.completedSessions}/{selectedPhase.totalSessions} sessions completed
                </span>
              </div>
            </header>

            <div className="roadmap-phase-overlay__scroll">
              <div className="roadmap-phase-detail__weeks">
                {selectedPhase.weeks.map((week) => (
                  <article
                    key={week.id}
                    className={`roadmap-phase-week ${week.isCurrentWeek ? 'is-current' : ''}`}
                  >
                    <header className="roadmap-phase-week__header">
                      <div>
                        <p>
                          Week {week.week_no} / {week.weekRangeLabel}
                        </p>
                        <h4>{week.weekly_focus}</h4>
                        <span>{week.weekly_output}</span>
                      </div>
                      <strong>
                        {week.completedSessions}/{week.sessions.length}
                      </strong>
                    </header>

                    <div className="roadmap-phase-session-list">
                      {week.sessions.map((session) => (
                        <article
                          key={session.id}
                          className={`roadmap-phase-session roadmap-phase-session--${session.statusTone} ${
                            session.isCurrentSession ? 'is-current' : ''
                          }`}
                        >
                          <div className="roadmap-phase-session__meta">
                            <p>
                              {formatDate(session.study_date)} / {session.weekday_label} / {session.session_label}
                            </p>
                            <span className={`panel-chip panel-chip--${session.statusTone}`}>{session.statusLabel}</span>
                          </div>
                          <h5>
                            {session.skillText} {session.isCurrentSession ? '/ Today' : ''}
                          </h5>
                          <div className="roadmap-phase-session__grid">
                            <p>{session.taskText}</p>
                            <strong>{session.deliverableText}</strong>
                          </div>
                        </article>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </section>
        </OverlayFrame>
      ) : null}
    </section>
  )
}

export default RoadmapHero
