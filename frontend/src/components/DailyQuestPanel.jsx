import React from 'react'
import PanelFrame from './PanelFrame'
import { formatDate, getQuestActionMeta, getQuestRewardValue, getTodayISO, uniqueItems } from '../dashboard-data'

// Slot code → human label mapping (spec §5.1)
const SLOT_LABELS = {
  vocab_flashcard:  'Flashcard Gate',
  vocab_codex:      'Codex Entry',
  vocab_collocation:'Collocation Forge',
  listening:        'Listening',
  reading:          'Reading',
  writing:          'Writing',
  speaking:         'Speaking',
  grammar_review:   'Grammar Review',
  grammar_exercise: 'Grammar Exercise',
}

// Skill → accent colour (matches SKILL_THEME in dashboard-data)
const SLOT_ACCENT = {
  vocab_flashcard:   'green',
  vocab_codex:       'green',
  vocab_collocation: 'orange',
  listening:         'cyan',
  reading:           'amber',
  writing:           'rose',
  speaking:          'violet',
  grammar_review:    'steel',
  grammar_exercise:  'steel',
}

function SlotChip({ slotCode }) {
  if (!slotCode) return null
  const label = SLOT_LABELS[slotCode] ?? slotCode
  const accent = SLOT_ACCENT[slotCode] ?? 'cyan'
  return (
    <span className={`quest-slot-chip quest-slot-chip--${accent}`}>{label}</span>
  )
}

// Boss lock badge — shown when skill rank > confirmed_rank (boss-gated skills only)
// Writing/Speaking never reach boss_required, so promotion_status guards them.
function BossLockBadge({ quest }) {
  const status = quest.promotion_status
  if (!status || status === 'none' || status === 'passed') return null
  const confirmedRank = quest.confirmed_rank ?? quest.skill_confirmed_rank
  if (!confirmedRank) return null
  const label = `Rank ${confirmedRank} confirmed — Boss required to promote`
  return (
    <span className="quest-boss-lock" title={label}>
      🔒 {confirmedRank} confirmed
    </span>
  )
}

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

  // Distinguish completed-unclaimed (claim ready) from completed-claimed
  const isClaimReady = quest.completed && !quest.rewardClaimed

  return (
    <article
      key={quest.id}
      className={[
        'quest-node',
        `quest-node--${quest.status}`,
        quest.completed ? 'is-complete' : '',
        isClaimReady ? 'is-claim-ready' : '',
        isPending ? 'is-pending' : '',
        isSuccess ? 'is-success-flash' : '',
      ].filter(Boolean).join(' ')}
    >
      <div className="quest-node__main">
        <div className="quest-node__chips">
          <SlotChip slotCode={quest.daily_slot_code} />
          <BossLockBadge quest={quest} />
        </div>
        <p className="quest-node__meta">
          {formatDate(quest.quest_date)} / Week {quest.week_no} / {quest.skill_name}
        </p>
        <h3>{quest.title}</h3>
        <p>{quest.details}</p>
        {quest.completed && quest.completion_payload ? (
          <div className="quest-completion-payload">{quest.completion_payload}</div>
        ) : null}
        <div className="quest-node__foot">
          <span>{quest.source}</span>
        </div>
      </div>
      <div className="quest-node__reward">
        <strong>+{getQuestRewardValue(quest)}</strong>
        <span>{isClaimReady ? 'claim XP' : 'XP'}</span>
        {quest.reward_skill_name ? (
          <small className="quest-reward-skill">{quest.reward_skill_name}</small>
        ) : null}
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

function claimGroup(quest) {
  if (quest.completed && !quest.rewardClaimed) return 0  // claim-ready → top
  if (!quest.completed) return 1                         // not done → middle
  return 2                                               // claimed → bottom
}

function sortByClaimStatus(list) {
  return [...list].sort((a, b) => claimGroup(a) - claimGroup(b))
}

function DailyQuestPanel({ quests, onQuestAction, commandDeck, questPendingById, successQuestId, rewardPulseToken, skills }) {
  const todayIso = getTodayISO()
  const [filterSkill, setFilterSkill] = React.useState("")
  const skillOptions = uniqueItems((quests ?? []).map((q) => q.skill_name))

  // Attach promotion_status + confirmed_rank from skills array onto each quest
  // so BossLockBadge can read it without a separate prop chain
  const skillStatusMap = React.useMemo(() => {
    const map = {}
    for (const skill of (skills ?? [])) {
      map[skill.name] = {
        promotion_status: skill.promotion_status ?? 'none',
        confirmed_rank: skill.confirmed_rank ?? skill.rank ?? 'F',
      }
    }
    return map
  }, [skills])

  const enrichedQuests = React.useMemo(() => {
    return (quests ?? []).map((q) => {
      const sk = skillStatusMap[q.skill_name] ?? {}
      return {
        ...q,
        promotion_status: sk.promotion_status ?? 'none',
        skill_confirmed_rank: sk.confirmed_rank ?? null,
      }
    })
  }, [quests, skillStatusMap])

  const claimReadyCount = enrichedQuests.filter((q) => q.completed && !q.rewardClaimed).length
  const totalToday = Math.max(enrichedQuests.length, 9)  // spec §5.1: 9 slots/day

  return (
    <PanelFrame
      title="Quest Board"
      tag={`${commandDeck.completedToday}/${totalToday} daily clears`}
      className={rewardPulseToken ? 'panel-frame--reward-pulse' : ''}
    >
      <div className="quest-summary">
        <div className={`quest-summary__card ${rewardPulseToken ? 'quest-summary__card--pulse' : ''}`}>
          <span>Daily Slots</span>
          <strong>{enrichedQuests.length}</strong>
        </div>
        <div className={`quest-summary__card ${claimReadyCount > 0 ? 'quest-summary__card--pulse' : ''}`}>
          <span>Claim Ready</span>
          <strong>{claimReadyCount}</strong>
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
        {sortByClaimStatus(filterSkill
          ? enrichedQuests.filter((q) => q.skill_name === filterSkill)
          : enrichedQuests
        ).map((quest) =>
          renderQuestCard(quest, onQuestAction, questPendingById, successQuestId, todayIso)
        )}
      </div>
    </PanelFrame>
  )
}

export default DailyQuestPanel
