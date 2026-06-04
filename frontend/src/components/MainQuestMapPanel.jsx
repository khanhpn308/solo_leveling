import { useEffect, useState } from 'react'
import { formatDate } from '../dashboard-data'
import PanelFrame from './PanelFrame'

function MainQuestMapPanel({ map, loading, error }) {
  const [expandedPhaseCodes, setExpandedPhaseCodes] = useState([])
  const [expandedWeekNos, setExpandedWeekNos] = useState([])

  useEffect(() => {
    if (!map?.phases?.length) return

    const defaultPhaseCode = map.currentPhaseCode ?? map.defaultOpenPhaseCode
    const defaultWeekNo = map.currentWeekNo ?? map.defaultOpenWeekNo

    if (defaultPhaseCode) {
      setExpandedPhaseCodes((current) =>
        current.includes(defaultPhaseCode) ? current : [...current, defaultPhaseCode],
      )
    }

    if (defaultWeekNo) {
      setExpandedWeekNos((current) =>
        current.includes(defaultWeekNo) ? current : [...current, defaultWeekNo],
      )
    }
  }, [map])

  function togglePhase(code) {
    setExpandedPhaseCodes((current) =>
      current.includes(code) ? current.filter((item) => item !== code) : [...current, code],
    )
  }

  function toggleWeek(weekNo) {
    setExpandedWeekNos((current) =>
      current.includes(weekNo) ? current.filter((item) => item !== weekNo) : [...current, weekNo],
    )
  }

  return (
    <PanelFrame
      title="Main Quest Map"
      tag={loading ? 'Syncing...' : `Read-only · ${map?.totalWeeks ?? 0} tuan`}
    >
      {loading ? <div className="empty-state">Dang dong bo Main Quest Map tu backend...</div> : null}

      {!loading && error ? (
        <div className="empty-state empty-state--warning">
          Khong tai duoc Main Quest Map. Daily Quest van hoat dong binh thuong.
        </div>
      ) : null}

      {!loading && !error && (!map || map.totalWeeks === 0) ? (
        <div className="empty-state">Chua co study-plan data de ve Main Quest Map.</div>
      ) : null}

      {!loading && !error && map ? (
        <div className="main-quest-map">
          <div className="main-quest-map__summary">
            <div className="quest-summary__card">
              <span>Phase</span>
              <strong>{map.phases.length}</strong>
            </div>
            <div className="quest-summary__card">
              <span>Week</span>
              <strong>{map.totalWeeks}</strong>
            </div>
            <div className="quest-summary__card">
              <span>Session</span>
              <strong>{map.totalSessions}</strong>
            </div>
          </div>

          {map.integrity.totalWarnings > 0 ? (
            <div className="main-quest-integrity">
              <strong>Integrity warning</strong>
              <p>
                Missing: {map.integrity.missingSessions} · Duplicate: {map.integrity.duplicateSessions} · Orphan:{' '}
                {map.integrity.orphanQuests}
              </p>
            </div>
          ) : null}

          <div className="main-quest-phase-list">
            {map.phases.map((phase) => {
              const isPhaseOpen = expandedPhaseCodes.includes(phase.code)
              const phaseBodyId = `main-quest-phase-${phase.code}`

              return (
                <section
                  key={phase.code}
                  className={`main-quest-phase ${phase.isCurrentPhase ? 'is-current' : ''}`}
                >
                  <button
                    className="main-quest-phase__toggle"
                    onClick={() => togglePhase(phase.code)}
                    type="button"
                    aria-expanded={isPhaseOpen}
                    aria-controls={phaseBodyId}
                  >
                    <div>
                      <p className="main-quest-phase__eyebrow">{phase.code}</p>
                      <h3>
                        {phase.title} · {phase.subtitle}
                      </h3>
                      <p className="main-quest-phase__meta">
                        Week {phase.weekStart}-{phase.weekEnd} · {phase.totalWeeks} tuan ·{' '}
                        {phase.completedSessions}/{phase.totalSessions} session da xong
                        {phase.warningSessions > 0 ? ` · ${phase.warningSessions} warning` : ''}
                      </p>
                    </div>
                    <span className="panel-chip">{isPhaseOpen ? 'Collapse' : 'Expand'}</span>
                  </button>

                  {isPhaseOpen ? (
                    <div className="main-quest-week-list" id={phaseBodyId}>
                      {phase.weeks.map((week) => {
                        const isWeekOpen = expandedWeekNos.includes(week.week_no)
                        const weekBodyId = `main-quest-week-${week.week_no}`

                        return (
                          <article
                            key={week.id}
                            className={`main-quest-week ${week.isCurrentWeek ? 'is-current' : ''}`}
                          >
                            <button
                              className="main-quest-week__toggle"
                              onClick={() => toggleWeek(week.week_no)}
                              type="button"
                              aria-expanded={isWeekOpen}
                              aria-controls={weekBodyId}
                            >
                              <div>
                                <p className="main-quest-week__meta">
                                  Tuan {week.week_no} · {week.weekRangeLabel}
                                </p>
                                <h4>{week.weekly_focus}</h4>
                                <p className="main-quest-week__output">{week.weekly_output}</p>
                              </div>
                              <div className="main-quest-week__chips">
                                {week.isCurrentWeek ? <span className="panel-chip">Current week</span> : null}
                                {week.warningSessions > 0 ? (
                                  <span className="panel-chip panel-chip--warning">{week.warningSessions} warning</span>
                                ) : null}
                                <span className="panel-chip">
                                  {week.completedSessions}/{week.sessions.length} clear
                                </span>
                              </div>
                            </button>

                            {isWeekOpen ? (
                              <div className="main-quest-week__body" id={weekBodyId}>
                                <div className="main-quest-week__materials">
                                  <strong>Tai lieu tuan</strong>
                                  {week.materials.length > 0 ? (
                                    <ul className="main-quest-inline-list">
                                      {week.materials.map((item) => (
                                        <li key={item}>{item}</li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <p>Chua co material summary o cap tuan.</p>
                                  )}
                                </div>

                                <div className="main-quest-session-list">
                                  {week.sessions.map((session) => (
                                    <article
                                      key={session.id}
                                      className={`main-quest-session main-quest-session--${session.statusTone} ${
                                        session.isCurrentSession ? 'is-current' : ''
                                      }`}
                                    >
                                      <div className="main-quest-session__head">
                                        <div>
                                          <p className="main-quest-session__meta">
                                            {formatDate(session.study_date)} · {session.weekday_label} ·{' '}
                                            {session.session_label}
                                          </p>
                                          <h5>
                                            {session.skillText} {session.isCurrentSession ? '· Hom nay' : ''}
                                          </h5>
                                        </div>
                                        <div className="main-quest-session__status">
                                          <span className={`panel-chip panel-chip--${session.statusTone}`}>
                                            {session.statusLabel}
                                          </span>
                                          <strong>
                                            {session.xpMeta.value === '--' ? '--' : `+${session.xpMeta.value}`}
                                          </strong>
                                          <span>{session.xpMeta.label}</span>
                                        </div>
                                      </div>

                                      {session.integrity ? (
                                        <div className="main-quest-session__warning">
                                          {session.integrity.detail}
                                        </div>
                                      ) : null}

                                      <div className="main-quest-session__grid">
                                        <div>
                                          <span className="main-quest-session__label">Task detail</span>
                                          <p>{session.taskText}</p>
                                        </div>
                                        <div>
                                          <span className="main-quest-session__label">Deliverable</span>
                                          <p>{session.deliverableText}</p>
                                        </div>
                                      </div>

                                      <p className="main-quest-session__xp-detail">{session.xpMeta.detail}</p>

                                      <div className="main-quest-session__materials">
                                        <span className="main-quest-session__label">Tai lieu</span>
                                        {session.materialItems.length > 0 ? (
                                          <ul className="main-quest-inline-list">
                                            {session.materialItems.map((item) => (
                                              <li key={`${session.id}-${item}`}>{item}</li>
                                            ))}
                                          </ul>
                                        ) : (
                                          <p>{session.sourceText || 'Chua co tai lieu cho session nay.'}</p>
                                        )}
                                      </div>
                                    </article>
                                  ))}
                                </div>
                              </div>
                            ) : null}
                          </article>
                        )
                      })}
                    </div>
                  ) : null}
                </section>
              )
            })}
          </div>
        </div>
      ) : null}
    </PanelFrame>
  )
}

export default MainQuestMapPanel
