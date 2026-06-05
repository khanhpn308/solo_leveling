import PanelFrame from './PanelFrame'
import { formatDate } from '../dashboard-data'

function renderMoodStars(value) {
  return `${'*'.repeat(value)}${'-'.repeat(5 - value)}`
}

function CheckInPanel({
  mood,
  energy,
  focus,
  note,
  onMoodChange,
  onEnergyChange,
  onFocusChange,
  onNoteChange,
  onSave,
  recentCheckins,
}) {
  return (
    <PanelFrame title="Mood / Energy / Focus" tag="1 check-in / day">
      <div className="slider-stack">
        <label className="slider-field">
          <span>Mood</span>
          <input type="range" min="1" max="5" value={mood} onChange={onMoodChange} />
          <strong>{renderMoodStars(mood)}</strong>
        </label>
        <label className="slider-field">
          <span>Energy</span>
          <input type="range" min="1" max="5" value={energy} onChange={onEnergyChange} />
          <strong>{energy}/5</strong>
        </label>
        <label className="slider-field">
          <span>Focus</span>
          <input type="range" min="1" max="5" value={focus} onChange={onFocusChange} />
          <strong>{focus}/5</strong>
        </label>
      </div>

      <textarea
        className="system-textarea"
        value={note}
        onChange={onNoteChange}
        placeholder="Short note: tired because..., Reading felt strong because..., what should be avoided..."
      />
      <button className="system-button" onClick={onSave} type="button">
        Save today's check-in
      </button>

      <div className="subsection-divider" />

      <div className="backlog-header">
        <h3>Recent history</h3>
        <span>The backend currently stores mood and energy only.</span>
      </div>
      <div className="checkin-history">
        {recentCheckins.map((item) => (
          <div key={item.id} className="checkin-history__item">
            <span>{formatDate(item.checkin_date)}</span>
            <strong>
              M{item.mood} / E{item.energy}
            </strong>
            <p>{item.note || 'No note.'}</p>
          </div>
        ))}
      </div>
    </PanelFrame>
  )
}

export default CheckInPanel
