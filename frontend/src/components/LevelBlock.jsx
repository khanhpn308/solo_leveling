/**
 * LevelBlock — reusable horizontal-bar level card.
 * Props:
 *   level  { id, name, icon, pct, total_words, completed_words, locked }
 *   onSelect(level) — called on click if not locked
 *   isActive — highlight border
 */
function LevelBlock({ level, onSelect, isActive }) {
  const locked = level.locked
  const pct = level.pct || 0
  const ratio = pct / 100

  return (
    <button
      type="button"
      className={`level-block ${locked ? 'is-locked' : ''} ${isActive ? 'is-active' : ''}`}
      onClick={() => !locked && onSelect && onSelect(level)}
      disabled={locked}
      aria-pressed={isActive}
      aria-label={`${level.name}${locked ? ' (locked)' : `, ${pct}% complete`}`}
      style={{ '--level-ratio': ratio }}
    >
      <div className="level-block__top">
        <span className="level-block__icon" aria-hidden="true">{level.icon}</span>
        <span className="level-block__name">{level.name}</span>
        {locked
          ? <span className="level-block__lock" aria-hidden="true">🔒</span>
          : <span className="level-block__pct">{pct}%</span>
        }
      </div>
      <div className="level-block__bar" aria-hidden="true">
        <div
          className="level-block__bar-fill"
          style={{ width: `${pct}%` }}
        />
      </div>
      {!locked && (
        <div className="level-block__stats">
          {level.completed_words}/{level.total_words} words
        </div>
      )}
    </button>
  )
}

export default LevelBlock
