function getRankClass(rank) {
  return `skill-rank-badge--${String(rank || 'F').toLowerCase()}`
}

/**
 * Renders buff lines for support sources (Grammar → Writing, Collocation → Vocabulary).
 * Shows muted/empty state when buffXp = 0; never hidden.
 * spec: ielts_xp_policy_rank_quest_spec.md §1.1 + §4
 */
function SupportBuffLines({ breakdown }) {
  if (!breakdown || breakdown.length === 0) return null
  return (
    <div className="skill-node__buffs">
      {breakdown.map((item) => (
        <span key={item.source} className={`skill-node__buff ${item.xp > 0 ? 'skill-node__buff--active' : 'skill-node__buff--empty'}`}>
          {item.xp > 0 ? `+${item.xp} XP` : '—'} from {item.source}
        </span>
      ))}
    </div>
  )
}

// Only the compact variant is rendered in the live app (StatusModal "Skill Matrix").
// The former full-mode branch + SkillMatrixPanel wrapper were dead code (imported
// nowhere) and were removed in session 8j (GAP-18-1 cleanup). The `compact` prop is
// kept for call-site clarity / future reuse.
function SkillCards({ skills }) {
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

          <SupportBuffLines breakdown={skill.support_breakdown} />
        </article>
      ))}
    </div>
  )
}

export default SkillCards
