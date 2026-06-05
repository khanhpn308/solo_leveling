import PanelFrame from './PanelFrame'
import { formatDate, getQuestActionMeta, getQuestRewardValue, getTodayISO } from '../dashboard-data'

function QuestActionButton({ quest, pendingState, todayIso, onQuestAction }) {
  const actionMeta = getQuestActionMeta(quest, pendingState, todayIso)

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

function renderQuestCard(quest, onQuestAction, questPendingById, successQuestId, todayIso) {
  const pendingState = questPendingById[quest.id]
  const isPending = Boolean(pendingState)
  const isSuccess = successQuestId === quest.id

  return (
    <article
      key={quest.id}
      className={`quest-node quest-node--${quest.status} ${quest.completed ? 'is-complete' : ''} ${isPending ? 'is-pending' : ''} ${isSuccess ? 'is-success-flash' : ''}`}
    >
      <div className="quest-node__main">
        <p className="quest-node__meta">
          {formatDate(quest.quest_date)} / Week {quest.week_no} / {quest.skill_name}
        </p>
        <h3>{quest.title}</h3>
        <p>{quest.details}</p>
        <div className="quest-node__foot">
          <span>{quest.source}</span>
          <span>{quest.completed && !quest.rewardClaimed ? 'Reward waiting' : quest.status}</span>
        </div>
      </div>
      <div className="quest-node__reward">
        <strong>+{getQuestRewardValue(quest)}</strong>
        <span>{quest.completed && !quest.rewardClaimed ? 'claim XP' : 'XP'}</span>
        <QuestActionButton
          quest={quest}
          pendingState={pendingState}
          todayIso={todayIso}
          onQuestAction={onQuestAction}
        />
      </div>
    </article>
  )
}

function renderBacklogCard(quest, onQuestAction, questPendingById, successQuestId, todayIso) {
  const pendingState = questPendingById[quest.id]
  const isPending = Boolean(pendingState)

  return (
    <article
      key={quest.id}
      className={`backlog-item backlog-item--${quest.status} ${isPending ? 'is-pending' : ''} ${successQuestId === quest.id ? 'is-success-flash' : ''}`}
    >
      <div>
        <strong>{quest.title}</strong>
        <p>
          {quest.skill_name} / {formatDate(quest.quest_date)}
        </p>
      </div>
      <div className="backlog-item__actions">
        <span>{quest.completed && !quest.rewardClaimed ? 'Reward waiting' : quest.status}</span>
        <QuestActionButton
          quest={quest}
          pendingState={pendingState}
          todayIso={todayIso}
          onQuestAction={onQuestAction}
        />
      </div>
    </article>
  )
}

function DailyQuestPanel({ quests, backlog, onQuestAction, commandDeck, questPendingById, successQuestId, rewardPulseToken }) {
  const todayIso = getTodayISO()

  return (
    <PanelFrame
      title="Quest Board"
      tag={`${commandDeck.completedToday}/${Math.max(commandDeck.totalToday, 3)} daily clears`}
      className={rewardPulseToken ? 'panel-frame--reward-pulse' : ''}
    >
      <div className="quest-summary">
        <div className={`quest-summary__card ${rewardPulseToken ? 'quest-summary__card--pulse' : ''}`}>
          <span>Daily Command</span>
          <strong>{quests.length}</strong>
        </div>
        <div className={`quest-summary__card ${rewardPulseToken ? 'quest-summary__card--pulse' : ''}`}>
          <span>Backlog</span>
          <strong>{commandDeck.backlogCount}</strong>
        </div>
        <div className={`quest-summary__card ${rewardPulseToken ? 'quest-summary__card--pulse' : ''}`}>
          <span>Claim Ready</span>
          <strong>{quests.filter((quest) => quest.completed && !quest.rewardClaimed).length}</strong>
        </div>
      </div>

      <div className="quest-stack">
        {quests.map((quest) => renderQuestCard(quest, onQuestAction, questPendingById, successQuestId, todayIso))}
      </div>

      <div className="subsection-divider" />

      <div className="backlog-header">
        <h3>Overdue Backlog</h3>
        <span>Finish the quest first, then claim the reward XP from the cleared card.</span>
      </div>
      <div className="backlog-list">
        {backlog.length === 0 ? (
          <div className="empty-state">There is no overdue backlog right now.</div>
        ) : (
          backlog.map((quest) => renderBacklogCard(quest, onQuestAction, questPendingById, successQuestId, todayIso))
        )}
      </div>
    </PanelFrame>
  )
}

export default DailyQuestPanel
