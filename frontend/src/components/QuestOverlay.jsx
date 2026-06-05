import DailyQuestPanel from './DailyQuestPanel'
import MainQuestMapPanel from './MainQuestMapPanel'
import { formatDate, getTodayISO } from '../dashboard-data'
import OverlayFrame from './OverlayFrame'
import WeeklyMissionCard from './WeeklyMissionCard'

const QUEST_TABS = [
  { key: 'main', label: 'Main' },
  { key: 'daily', label: 'Daily' },
  { key: 'weekly', label: 'Weekly' },
  { key: 'archive', label: 'Archive' },
]

function QuestOverlay({
  open,
  activeTab,
  onTabChange,
  onClose,
  mainQuestMap,
  mainQuestLoading,
  mainQuestError,
  dailyQuests,
  backlogQuests,
  allQuests,
  commandDeck,
  onToggleQuest,
  weeklyMission,
}) {
  if (!open) return null

  const currentWeek = mainQuestMap?.phases
    ?.flatMap((phase) => phase.weeks)
    .find((week) => week.week_no === mainQuestMap.currentWeekNo)
  const currentSession =
    currentWeek?.sessions.find((session) => session.id === mainQuestMap.currentSessionId) ??
    currentWeek?.sessions[0] ??
    null

  return (
    <OverlayFrame
      title="Quest Board"
      subtitle="Main roadmap, current daily command, and weekly mission in one full overlay."
      onClose={onClose}
      className="overlay-frame--quest"
      actions={
        <div className="overlay-tab-row">
          {QUEST_TABS.map((tab) => (
            <button
              key={tab.key}
              className={`overlay-tab ${activeTab === tab.key ? 'is-active' : ''}`}
              type="button"
              disabled={tab.disabled}
              onClick={() => !tab.disabled && onTabChange(tab.key)}
            >
              {tab.label}
              {tab.disabled ? <small>soon</small> : null}
            </button>
          ))}
        </div>
      }
    >
      {activeTab === 'main' ? (
        <div className="quest-main-tab">
          {mainQuestLoading ? <div className="empty-state">Loading the current main quest...</div> : null}

          {!mainQuestLoading && currentSession ? (
            <section className={`current-main-quest current-main-quest--${currentSession.statusTone}`}>
              <header>
                <div>
                  <p>Current Main Quest</p>
                  <h3>{currentSession.skillText}</h3>
                  <strong>
                    {formatDate(currentSession.study_date)} / {currentSession.weekday_label} / {currentSession.session_label}
                  </strong>
                </div>
                <div className="current-main-quest__reward">
                  <span>{currentSession.statusLabel}</span>
                  <strong>
                    {currentSession.xpMeta.value === '--' ? '--' : `+${currentSession.xpMeta.value}`}
                  </strong>
                </div>
              </header>
              <div className="current-main-quest__grid">
                <article>
                  <span>Task detail</span>
                  <p>{currentSession.taskText}</p>
                </article>
                <article>
                  <span>Deliverable</span>
                  <p>{currentSession.deliverableText}</p>
                </article>
              </div>
              <p className="current-main-quest__note">{currentSession.xpMeta.detail}</p>
            </section>
          ) : null}

          <MainQuestMapPanel map={mainQuestMap} loading={mainQuestLoading} error={mainQuestError} />
        </div>
      ) : null}

      {activeTab === 'daily' ? (
        <DailyQuestPanel
          quests={dailyQuests}
          backlog={backlogQuests}
          onToggleQuest={onToggleQuest}
          commandDeck={commandDeck}
        />
      ) : null}

      {activeTab === 'weekly' ? <WeeklyMissionCard mission={weeklyMission} /> : null}

      {activeTab === 'archive' ? <PanelArchive quests={allQuests} onToggleQuest={onToggleQuest} /> : null}
    </OverlayFrame>
  )
}

function PanelArchive({ quests, onToggleQuest }) {
  const todayIso = getTodayISO()
  const sorted = [...quests].sort((left, right) => new Date(left.quest_date).getTime() - new Date(right.quest_date).getTime())

  return (
    <div className="quest-main-tab">
      <div className="backlog-header">
        <h3>Current Window Archive</h3>
        <span>Browse and complete quests from the currently loaded quest window.</span>
      </div>

      <div className="backlog-list">
        {sorted.length === 0 ? (
          <div className="empty-state">There are no quests in the current window.</div>
        ) : (
          sorted.map((quest) => (
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
                  {quest.skill_name} / {formatDate(quest.quest_date)} / Week {quest.week_no}
                </p>
              </div>
              <span>{quest.statusLabel || quest.status}</span>
            </button>
          ))
        )}
      </div>
    </div>
  )
}

export default QuestOverlay
