import { useEffect, useState } from 'react'
import { formatDate, getQuestActionMeta, getQuestRewardValue, getTodayISO } from '../dashboard-data'
import PanelFrame from './PanelFrame'

function MainQuestActionButton({ quest, pendingState, onQuestAction }) {
  if (!quest) return null

  const actionMeta = getQuestActionMeta(quest, pendingState, getTodayISO())

  return (
    <button
      className={`system-button quest-action-button quest-action-button--${actionMeta.tone}`}
      type="button"
      disabled={actionMeta.disabled}
      onClick={() => actionMeta.action && onQuestAction(quest, actionMeta.action)}
    >
      {actionMeta.label}
    </button>
  )
}

function MainQuestMapPanel({ map, loading, error, onQuestAction, questPendingById, successQuestId }) {
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
    <PanelFrame title="Main Quest Map" tag={loading ? 'Syncing...' : `Claim flow live / ${map?.totalWeeks ?? 0} weeks`}>
      {loading ? <div className="empty-state">Syncing Main Quest Map from the backend...</div> : null}

      {!loading && error ? (
        <div className="empty-state empty-state--warning">
          Main Quest Map could not be loaded. Daily Quests still work normally.
        </div>
      ) : null}

      {!loading && !error && (!map || map.totalWeeks === 0) ? (
        <div className="empty-state">No study-plan data is available to render the Main Quest Map.</div>
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
                Missing: {map.integrity.missingSessions} / Duplicate: {map.integrity.duplicateSessions} / Orphan:{' '}
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
                        {phase.title} / {phase.subtitle}
                      </h3>
                      <p className="main-quest-phase__meta">
                        Week {phase.weekStart}-{phase.weekEnd} / {phase.totalWeeks} weeks /{' '}
                        {phase.completedSessions}/{phase.totalSessions} sessions completed
                        {phase.warningSessions > 0 ? ` / ${phase.warningSessions} warning` : ''}
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
                                  Week {week.week_no} / {week.weekRangeLabel}
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
                                  {week.completedSessions}/{week.sessions.length} complete
                                </span>
                              </div>
                            </button>

                            {isWeekOpen ? (
                              <div className="main-quest-week__body" id={weekBodyId}>
                                <div className="main-quest-week__materials">
                                  <strong>Week materials</strong>
                                  {week.materials.length > 0 ? (
                                    <ul className="main-quest-inline-list">
                                      {week.materials.map((item) => (
                                        <li key={item}>{item}</li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <p>No week-level material summary yet.</p>
                                  )}
                                </div>

                                <div className="main-quest-session-list">
                                  {week.sessions.map((session) => {
                                    const pendingState = session.quest ? questPendingById[session.quest.id] : null

                                    return (
                                      <article
                                        key={session.id}
                                        className={`main-quest-session main-quest-session--${session.statusTone} ${
                                          session.isCurrentSession ? 'is-current' : ''
                                        } ${successQuestId === session.quest?.id ? 'is-success-flash' : ''}`}
                                      >
                                        <div className="main-quest-session__head">
                                          <div>
                                            <p className="main-quest-session__meta">
                                              {formatDate(session.study_date)} / {session.weekday_label} / {session.session_label}
                                            </p>
                                            <h5>
                                              {session.skillText} {session.isCurrentSession ? '/ Today' : ''}
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
                                          <span className="main-quest-session__label">Materials</span>
                                          {session.materialItems.length > 0 ? (
                                            <ul className="main-quest-inline-list">
                                              {session.materialItems.map((item) => (
                                                <li key={`${session.id}-${item}`}>{item}</li>
                                              ))}
                                            </ul>
                                          ) : (
                                            <p>{session.sourceText || 'No materials listed for this session yet.'}</p>
                                          )}
                                        </div>

                                        {session.quest ? (
                                          <div className="main-quest-session__actions">
                                            <span className="main-quest-session__claim">
                                              Reward cache: +{getQuestRewardValue(session.quest)} XP
                                            </span>
                                            <MainQuestActionButton
                                              quest={session.quest}
                                              pendingState={pendingState}
                                              onQuestAction={onQuestAction}
                                            />
                                          </div>
                                        ) : null}
                                      </article>
                                    )
                                  })}
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
