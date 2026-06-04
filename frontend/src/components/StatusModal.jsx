import OverlayFrame from './OverlayFrame'
import SkillCards from './SkillCards'

const AVATAR_SWATCHES = [
  { key: 'cyan', label: 'Cyan Core' },
  { key: 'amber', label: 'Amber Crest' },
  { key: 'rose', label: 'Rose Pulse' },
  { key: 'violet', label: 'Violet Rune' },
]

function MoodButton({ active, label, value, onSelect }) {
  return (
    <button className={`checkin-pill ${active ? 'is-active' : ''}`} type="button" onClick={() => onSelect(value)}>
      {label}
    </button>
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
  skills,
}) {
  if (!open) return null

  return (
    <OverlayFrame
      title="Status Center"
      subtitle="Player profile, today check-in, and skill diagnostics."
      onClose={onClose}
      className="overlay-frame--status"
    >
      <div className="status-modal">
        <section className="status-modal__summary">
          <button
            className="status-avatar"
            type="button"
            onClick={() => onCheckInDraftChange({ field: 'avatarPicker', value: !checkInDraft.avatarPicker })}
          >
            <span>{player.displayName.slice(0, 1).toUpperCase()}</span>
            <small>Avatar</small>
          </button>

          <div className="status-profile">
            <p className="status-profile__eyebrow">{player.title}</p>
            <h3>{player.displayName}</h3>
            <div className="status-profile__meta">
              <span>Rank {player.rank}</span>
              <span>Lv.{player.level}</span>
              {player.target ? <span>Target {player.target}</span> : null}
            </div>

            <div className="xp-meter">
              <div className="xp-meter__bar">
                <div style={{ width: `${player.xpProgress.percent}%` }} />
              </div>
              <div className="xp-meter__meta">
                <strong>{player.totalXp} XP</strong>
                <span>{player.xpProgress.remainingXp} XP to next level</span>
              </div>
            </div>

            <div className="profile-signal-grid">
              <article>
                <span>Strongest</span>
                <strong>{player.strongestSkill || '--'}</strong>
              </article>
              <article>
                <span>Weakest</span>
                <strong>{player.weakestSkill || '--'}</strong>
              </article>
              <article>
                <span>Study Plan</span>
                <strong>{player.studyDaysPerWeek || '--'} days / week</strong>
              </article>
              <article>
                <span>Session</span>
                <strong>{player.sessionMinutes || '--'} min</strong>
              </article>
            </div>
          </div>

          {checkInDraft.avatarPicker ? (
            <section className="avatar-picker">
              <header>
                <strong>Avatar Picker</strong>
                <span>Placeholder only. No persistence this round.</span>
              </header>
              <div className="avatar-picker__grid">
                {AVATAR_SWATCHES.map((swatch) => (
                  <button key={swatch.key} className={`avatar-swatch avatar-swatch--${swatch.key}`} type="button">
                    <span>{player.displayName.slice(0, 1).toUpperCase()}</span>
                    <small>{swatch.label}</small>
                  </button>
                ))}
              </div>
            </section>
          ) : null}
        </section>

        <section className="status-modal__checkin">
          <div className="modal-block">
            <header className="modal-block__header">
              <div>
                <p>Today Check-in</p>
                <strong>{activeCheckIn ? 'Da co du lieu hom nay' : 'Chua check-in hom nay'}</strong>
              </div>
            </header>

            <div className="checkin-grid">
              <div>
                <span>Mood</span>
                <div className="checkin-pill-row">
                  {[1, 2, 3, 4, 5].map((value) => (
                    <MoodButton
                      key={`mood-${value}`}
                      active={checkInDraft.mood === value}
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
                  onChange={(event) => onCheckInDraftChange({ field: 'focus', value: Number(event.target.value) })}
                />
              </div>
            </div>

            <textarea
              className="system-textarea"
              value={checkInDraft.note}
              onChange={(event) => onCheckInDraftChange({ field: 'note', value: event.target.value })}
              placeholder="Ghi chu ngan ve tinh trang hoc hom nay..."
            />

            <button className="system-button" type="button" onClick={onSaveCheckIn}>
              Luu check-in
            </button>
          </div>

          <div className="modal-block">
            <header className="modal-block__header">
              <div>
                <p>Badge Wall</p>
                <strong>Placeholder</strong>
              </div>
            </header>
            <div className="empty-state">Badge showcase se mo rong o vong sau.</div>
          </div>
        </section>

        <section className="status-modal__skills">
          <div className="modal-block">
            <header className="modal-block__header">
              <div>
                <p>Detailed Skills</p>
                <strong>XP, level, rank, and weakness notes</strong>
              </div>
            </header>
            <SkillCards skills={skills} compact />
          </div>
        </section>
      </div>
    </OverlayFrame>
  )
}

export default StatusModal
