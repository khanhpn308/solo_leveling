import React from 'react'
import PanelFrame from './PanelFrame'
import { formatDate, getQuestActionMeta, getQuestRewardValue, getTodayISO, uniqueItems } from '../dashboard-data'

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
        {quest.completed && quest.completion_payload ? <div className="quest-completion-payload">{quest.completion_payload}</div> : null}
        <div className="quest-node__foot">
          <span>{quest.source}</span>
          <span>{quest.completed && !quest.rewardClaimed ? 'Reward waiting' : quest.status}</span>
        </div>
      </div>
      <div className="quest-node__reward">
        <strong>+{getQuestRewardValue(quest)}</strong>
        <span>{quest.completed && !quest.rewardClaimed ? 'claim XP' : 'XP'}</span>
        {quest.reward_skill_name ? <small className="quest-reward-skill">{quest.reward_skill_name}</small> : null}
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

function DailyQuestPanel({ quests, onQuestAction, commandDeck, questPendingById, successQuestId, rewardPulseToken }) {
  const todayIso = getTodayISO()
  const [filterSkill, setFilterSkill] = React.useState("")
  const skillOptions = uniqueItems((quests ?? []).map((q) => q.skill_name))

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
          <span>Claim Ready</span>
          <strong>{quests.filter((quest) => quest.completed && !quest.rewardClaimed).length}</strong>
        </div>
      </div>

      <div className="quest-tabs">
        <button
          type="button"
          className={`quest-tab-button ${filterSkill === "" ? "is-active" : ""}`}
          onClick={() => setFilterSkill("")}
        >
          All
        </button>
        {skillOptions.map((s) => (
          <button
            key={s}
            type="button"
            className={`quest-tab-button ${filterSkill === s ? "is-active" : ""}`}
            onClick={() => setFilterSkill(s)}
          >
            {s}
          </button>
        ))}
      </div>

      <div className="quest-stack">
        {(filterSkill ? quests.filter((q) => q.skill_name === filterSkill) : quests).map((quest) => renderQuestCard(quest, onQuestAction, questPendingById, successQuestId, todayIso))}
      </div>

    </PanelFrame>
  )
}

export default DailyQuestPanel
