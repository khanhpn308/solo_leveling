import { formatDate } from '../dashboard-data'

function CommandHeader({ player, summary }) {
  return (
    <section className="command-header">
      <div className="command-header__copy">
        <p className="system-kicker">Hunter System / IELTS Command Center</p>
        <h1>IELTS Quest Dashboard</h1>
        <p className="command-header__subtitle">
          Track the 18-month campaign, protect your streak, and see progress every day.
        </p>
        <div className="hero-stats">
          <div className="hero-stat">
            <span>Player Rank</span>
            <strong>{player.rank}</strong>
          </div>
          <div className="hero-stat">
            <span>Player Level</span>
            <strong>Lv.{player.level}</strong>
          </div>
          <div className="hero-stat">
            <span>Total XP</span>
            <strong>{player.totalXp}</strong>
          </div>
          <div className="hero-stat">
            <span>Current Streak</span>
            <strong>{summary.currentStreak} days</strong>
          </div>
        </div>
      </div>

      <div className="hero-status">
        <div className="hero-status__box">
          <span className="hero-status__label">Campaign</span>
          <strong>{player.hasStarted ? 'Active' : 'Pending'}</strong>
          <p>{player.phaseLabel}</p>
        </div>
        <div className="hero-status__box">
          <span className="hero-status__label">Timeline</span>
          <strong>{formatDate(player.start_date)}</strong>
          <p>
            {player.week_start && player.week_end
              ? `${formatDate(player.week_start)} - ${formatDate(player.week_end)}`
              : 'Waiting for backend sync'}
          </p>
        </div>
      </div>
    </section>
  )
}

export default CommandHeader
