import PanelFrame from './PanelFrame'
import { formatDate } from '../dashboard-data'

function renderMoodStars(value) {
  return `${'★'.repeat(value)}${'☆'.repeat(5 - value)}`
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
    <PanelFrame title="Mood / Energy / Focus" tag="1 check-in / ngày">
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
        placeholder="Ghi chú ngắn: hôm nay mệt vì..., Reading tốt vì..., cần tránh điều gì..."
      />
      <button className="system-button" onClick={onSave} type="button">
        Ghi check-in hôm nay
      </button>

      <div className="subsection-divider" />

      <div className="backlog-header">
        <h3>Lịch sử gần nhất</h3>
        <span>Backend hiện mới lưu mood và energy.</span>
      </div>
      <div className="checkin-history">
        {recentCheckins.map((item) => (
          <div key={item.id} className="checkin-history__item">
            <span>{formatDate(item.checkin_date)}</span>
            <strong>
              M{item.mood} · E{item.energy}
            </strong>
            <p>{item.note || 'Không có ghi chú.'}</p>
          </div>
        ))}
      </div>
    </PanelFrame>
  )
}

export default CheckInPanel
