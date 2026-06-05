import PanelFrame from './PanelFrame'
import { formatDate, getTodayISO } from '../dashboard-data'

function statusLabel(status) {
  if (status === 'completed') return 'Completed'
  if (status === 'overdue') return 'Overdue'
  if (status === 'expired') return 'Expired'
  return 'Pending'
}

function DailyQuestPanel({ quests, backlog, onToggleQuest, commandDeck }) {
  const todayIso = getTodayISO()

  return (
    <PanelFrame
      title="Quest Board"
      tag={`${commandDeck.completedToday}/${Math.max(commandDeck.totalToday, 3)} daily clears`}
    >
      <div className="quest-summary">
        <div className="quest-summary__card">
          <span>Daily Command</span>
          <strong>{quests.length}</strong>
        </div>
        <div className="quest-summary__card">
          <span>Backlog</span>
          <strong>{commandDeck.backlogCount}</strong>
        </div>
        <div className="quest-summary__card">
          <span>Check-in</span>
          <strong>{commandDeck.activeCheckIn ? 'Done' : 'Pending'}</strong>
        </div>
      </div>

      <div className="quest-stack">
        {quests.map((quest) => (
          <button
            key={quest.id}
            className={`quest-node quest-node--${quest.status} ${quest.completed ? 'is-complete' : ''}`}
            onClick={() => onToggleQuest(quest)}
            type="button"
          >
            <div className="quest-node__main">
              <p className="quest-node__meta">
                {formatDate(quest.quest_date)} / Week {quest.week_no} / {quest.skill_name}
              </p>
              <h3>{quest.title}</h3>
              <p>{quest.details}</p>
              <div className="quest-node__foot">
                <span>{quest.source}</span>
                <span>{statusLabel(quest.status)}</span>
              </div>
            </div>
            <div className="quest-node__reward">
              <strong>+{quest.earnedXp}</strong>
              <span>XP</span>
            </div>
          </button>
        ))}
      </div>

      <div className="subsection-divider" />

      <div className="backlog-header">
        <h3>Overdue Backlog</h3>
        <span>Recovery completions only earn 50% XP. After 3 days, quests expire.</span>
      </div>
      <div className="backlog-list">
        {backlog.length === 0 ? (
          <div className="empty-state">There is no overdue backlog right now.</div>
        ) : (
          backlog.map((quest) => (
            <button
              key={quest.id}
              className={`backlog-item backlog-item--${quest.status}`}
              type="button"
              disabled={quest.status === 'expired' || quest.quest_date > todayIso}
              onClick={() => onToggleQuest(quest)}
            >
              <div>
                <strong>{quest.title}</strong>
                <p>
                  {quest.skill_name} / {formatDate(quest.quest_date)}
                </p>
              </div>
              <span>{statusLabel(quest.status)}</span>
            </button>
          ))
        )}
      </div>
    </PanelFrame>
  )
}

export default DailyQuestPanel
