import { formatDate } from '../dashboard-data'

function getRankClass(rank) {
  return `skill-rank-badge--${String(rank || 'F').toLowerCase()}`
}

function SkillCards({ skills, compact = false }) {
  if (compact) {
    return (
      <div className="skill-grid skill-grid--compact">
        {skills.map((skill) => (
          <article key={skill.id} className={`skill-node skill-node--compact skill-node--${skill.theme.accent}`}>
            <header className="skill-node__header">
              <div>
                <p>{skill.theme.label}</p>
                <h3>
                  <span className="skill-node__icon">{skill.icon}</span>
                  {skill.name}
                </h3>
              </div>
              <div className={`skill-rank-badge ${getRankClass(skill.rank)}`}>
                <span>Rank</span>
                <strong>{skill.rank}</strong>
              </div>
            </header>

            <div className="skill-node__stats skill-node__stats--compact">
              <div>
                <span>Level</span>
                <strong>Lv.{skill.level}</strong>
              </div>
              <div>
                <span>XP</span>
                <strong>{skill.xp}</strong>
              </div>
            </div>

            <div className="progress-track">
              <div className="progress-track__fill" style={{ width: `${skill.progress}%` }} />
            </div>
          </article>
        ))}
      </div>
    )
  }

  return (
    <div className="skill-grid">
      {skills.map((skill) => (
        <article key={skill.id} className={`skill-node skill-node--${skill.theme.accent}`}>
          <header className="skill-node__header">
            <div>
              <p>{skill.theme.label}</p>
              <h3>
                <span className="skill-node__icon">{skill.icon}</span>
                {skill.name}
              </h3>
            </div>
            <div className={`skill-rank-badge ${getRankClass(skill.rank)}`}>
              <span>Rank</span>
              <strong>{skill.rank}</strong>
            </div>
          </header>

          <div className="skill-node__stats">
            <div>
              <span>XP</span>
              <strong>{skill.xp}</strong>
            </div>
            <div>
              <span>Level</span>
              <strong>Lv.{skill.level}</strong>
            </div>
            <div>
              <span>Last</span>
              <strong>{formatDate(skill.last_practiced)}</strong>
            </div>
          </div>

          <div className="progress-track">
            <div className="progress-track__fill" style={{ width: `${skill.progress}%` }} />
          </div>

          <p className="skill-node__note">{skill.user_weakness_note || skill.weak_point || 'No weakness note yet.'}</p>
        </article>
      ))}
    </div>
  )
}

export default SkillCards
