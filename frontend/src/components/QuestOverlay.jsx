import DailyQuestPanel from './DailyQuestPanel'
import MainQuestMapPanel from './MainQuestMapPanel'
import { formatDate } from '../dashboard-data'
import OverlayFrame from './OverlayFrame'
import WeeklyMissionCard from './WeeklyMissionCard'

const QUEST_TABS = [
  { key: 'main', label: 'Main' },
  { key: 'daily', label: 'Daily' },
  { key: 'weekly', label: 'Weekly' },
  { key: 'archive', label: 'Archive', disabled: true },
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
          {mainQuestLoading ? <div className="empty-state">Dang tai main quest hien tai...</div> : null}

          {!mainQuestLoading && currentSession ? (
            <section className={`current-main-quest current-main-quest--${currentSession.statusTone}`}>
              <header>
                <div>
                  <p>Main Quest Hien Tai</p>
                  <h3>{currentSession.skillText}</h3>
                  <strong>
                    {formatDate(currentSession.study_date)} · {currentSession.weekday_label} · {currentSession.session_label}
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

      {activeTab === 'archive' ? <div className="empty-state">Archive coming soon.</div> : null}
    </OverlayFrame>
  )
}

export default QuestOverlay
