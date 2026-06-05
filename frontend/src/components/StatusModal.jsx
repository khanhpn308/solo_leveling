import { useMemo, useState } from 'react'
import OverlayFrame from './OverlayFrame'
import SkillCards from './SkillCards'
import { formatDate } from '../dashboard-data'

function ConditionCard({ label, value, note }) {
  return (
    <article className="status-condition-card">
      <span>{label}</span>
      <strong className="status-neon-number">{value}</strong>
      {note ? <p>{note}</p> : null}
    </article>
  )
}

function MoodButton({ active, disabled, label, value, onSelect }) {
  return (
    <button
      className={`checkin-pill ${active ? 'is-active' : ''}`}
      type="button"
      disabled={disabled}
      onClick={() => onSelect(value)}
    >
      {label}
    </button>
  )
}

function AuxSection({ title, meta, open, onToggle, children }) {
  return (
    <section className={`status-aux ${open ? 'is-open' : ''}`}>
      <button className="status-aux__toggle" type="button" onClick={onToggle} aria-expanded={open}>
        <div>
          <p>{title}</p>
          <strong>{meta}</strong>
        </div>
        <span className="panel-chip">{open ? 'Hide' : 'Show'}</span>
      </button>
      {open ? <div className="status-aux__body">{children}</div> : null}
    </section>
  )
}

function StatusModal({
  open,
  onClose,
  player,
  activeCheckIn,
  checkInDraft,
  onCheckInDraftChange,
  onSaveCheckIn,
  checkInSaving,
  checkInFeedback,
  skills,
  badges,
  recentCheckins,
}) {
  const [isCheckInOpen, setIsCheckInOpen] = useState(false)
  const [isBadgeOpen, setIsBadgeOpen] = useState(false)
  const [isHistoryOpen, setIsHistoryOpen] = useState(false)

  const todayCondition = useMemo(
    () => ({
      mood: activeCheckIn?.mood ?? checkInDraft.mood,
      energy: activeCheckIn?.energy ?? checkInDraft.energy,
      focus: activeCheckIn?.focus ?? checkInDraft.focus,
      note: activeCheckIn?.note || 'No note for today yet.',
    }),
    [activeCheckIn, checkInDraft],
  )

  return (
    <OverlayFrame
      open={open}
      title="Status"
      onClose={onClose}
      className="overlay-frame--status overlay-frame--status-minimal"
    >
      <div className="status-modal status-modal--quad">
        <section className="status-shell">
          <div className="status-shell__hero">
            <div className="status-portrait">
              <div className="status-avatar" aria-hidden="true">
                <span>{player.displayName.slice(0, 1).toUpperCase()}</span>
              </div>
            </div>

            <div className="status-core">
              <p className="status-profile__eyebrow">{player.title}</p>
              <h3>{player.displayName}</h3>

              <div className="status-core__metrics">
                <article>
                  <span>Level</span>
                  <strong className="status-neon-number">{player.level}</strong>
                </article>
                <article>
                  <span>Rank</span>
                  <strong className="status-neon-number">{player.rank}</strong>
                </article>
                <article>
                  <span>Target</span>
                  <strong>{player.target || '--'}</strong>
                </article>
              </div>

              <div className="xp-meter xp-meter--status">
                <div className="xp-meter__bar">
                  <div style={{ width: `${player.xpProgress.percent}%` }} />
                </div>
                <div className="xp-meter__meta">
                  <strong className="status-neon-number status-neon-number--small">{player.totalXp}</strong>
                  <span>{player.xpProgress.remainingXp} XP to next level</span>
                </div>
              </div>
            </div>
          </div>

          <section className="status-condition">
            <header className="modal-block__header">
              <div>
                <p>Daily Condition</p>
                <strong>{activeCheckIn ? 'Checked in today' : 'Check-in needed today'}</strong>
              </div>
              <button className="system-button system-button--ghost" type="button" onClick={() => setIsCheckInOpen((current) => !current)}>
                {isCheckInOpen ? 'Collapse check-in' : 'Check-in'}
              </button>
            </header>

            <div className="status-condition__grid">
              <ConditionCard label="Mood" value={todayCondition.mood} />
              <ConditionCard label="Energy" value={todayCondition.energy} />
              <ConditionCard label="Focus" value={todayCondition.focus} />
            </div>

            <p className="status-condition__note">{todayCondition.note}</p>

            {isCheckInOpen ? (
              <div className="status-checkin-editor">
                <div className="checkin-grid">
                  <div>
                    <span>Mood</span>
                    <div className="checkin-pill-row">
                      {[1, 2, 3, 4, 5].map((value) => (
                        <MoodButton
                          key={`mood-${value}`}
                          active={checkInDraft.mood === value}
                          disabled={checkInSaving}
                          label={`${value}`}
                          value={value}
                          onSelect={(nextValue) => onCheckInDraftChange({ field: 'mood', value: nextValue })}
                        />
                      ))}
                    </div>
                  </div>

                  <div>
                    <span>Energy</span>
                    <input
                      type="range"
                      min="1"
                      max="5"
                      value={checkInDraft.energy}
                      disabled={checkInSaving}
                      onChange={(event) => onCheckInDraftChange({ field: 'energy', value: Number(event.target.value) })}
                    />
                  </div>

                  <div>
                    <span>Focus</span>
                    <input
                      type="range"
                      min="1"
                      max="5"
                      value={checkInDraft.focus}
                      disabled={checkInSaving}
                      onChange={(event) => onCheckInDraftChange({ field: 'focus', value: Number(event.target.value) })}
                    />
                  </div>
                </div>

                <textarea
                  className="system-textarea"
                  value={checkInDraft.note}
                  disabled={checkInSaving}
                  onChange={(event) => onCheckInDraftChange({ field: 'note', value: event.target.value })}
                  placeholder="Add a short note about today's study condition..."
                />

                {checkInFeedback ? (
                  <div className={`inline-feedback inline-feedback--${checkInFeedback.tone}`}>{checkInFeedback.message}</div>
                ) : null}

                <button className="system-button" type="button" onClick={onSaveCheckIn} disabled={checkInSaving}>
                  {checkInSaving ? 'Saving check-in...' : 'Save check-in'}
                </button>
              </div>
            ) : null}
          </section>
        </section>

        <section className="modal-block modal-block--status">
          <header className="modal-block__header">
            <div>
              <p>Skill Matrix</p>
            </div>
          </header>
          <SkillCards skills={skills} compact />
        </section>

        <AuxSection
          title="Badge Wall"
          meta={`${badges.length} badges`}
          open={isBadgeOpen}
          onToggle={() => setIsBadgeOpen((current) => !current)}
        >
          <div className="status-badge-grid">
            {badges.length === 0 ? (
              <div className="empty-state">No badges unlocked yet.</div>
            ) : (
              badges.map((badge) => (
                <article key={badge.id} className={`badge-node ${badge.unlocked ? 'is-unlocked' : 'is-locked'}`}>
                  <span className="badge-node__icon">{badge.icon}</span>
                  <strong>{badge.name}</strong>
                  <p>{badge.description}</p>
                </article>
              ))
            )}
          </div>
        </AuxSection>

        <AuxSection
          title="Recent Check-ins"
          meta={`${recentCheckins.length} entries`}
          open={isHistoryOpen}
          onToggle={() => setIsHistoryOpen((current) => !current)}
        >
          <div className="checkin-history">
            {recentCheckins.length === 0 ? (
              <div className="empty-state">No recent check-ins yet.</div>
            ) : (
              recentCheckins.map((item) => (
                <div key={item.id} className="checkin-history__item">
                  <span>{formatDate(item.checkin_date)}</span>
                  <strong>
                    M{item.mood} / E{item.energy} / F{item.focus}
                  </strong>
                  <p>{item.note || 'No note.'}</p>
                </div>
              ))
            )}
          </div>
        </AuxSection>
      </div>
    </OverlayFrame>
  )
}

export default StatusModal
