import { useEffect, useMemo, useState } from 'react'
import BossOverlay from './components/BossOverlay'
import CertificateOverlay from './components/CertificateOverlay'
import HomeTopBar from './components/HomeTopBar'
import NavigationDrawer from './components/NavigationDrawer'
import QuestOverlay from './components/QuestOverlay'
import RoadmapHero from './components/RoadmapHero'
import StatusModal from './components/StatusModal'
import {
  buildBossView,
  buildDashboardView,
  buildMainQuestMap,
  buildPlayerSnapshot,
  buildRoadmapBounds,
  buildRoadmapPhaseTrack,
  buildSuggestionInbox,
  formatDate,
  filterCertificateRecords,
  getTodayISO,
} from './dashboard-data'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const EMPTY_CHECKIN_DRAFT = {
  mood: 3,
  energy: 3,
  focus: 3,
  note: '',
  avatarPicker: false,
}

async function api(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'API error')
  }

  return response.json()
}

function formatHostDateTime(now) {
  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(now)
}

function App() {
  const [summary, setSummary] = useState(null)
  const [profile, setProfile] = useState(null)
  const [quests, setQuests] = useState([])
  const [checkins, setCheckins] = useState([])
  const [studyPlanWeeks, setStudyPlanWeeks] = useState([])
  const [mainQuests, setMainQuests] = useState([])
  const [weeklyMission, setWeeklyMission] = useState(null)
  const [bossBattles, setBossBattles] = useState([])
  const [rankSuggestions, setRankSuggestions] = useState([])
  const [weaknessSuggestions, setWeaknessSuggestions] = useState([])
  const [testRecords, setTestRecords] = useState([])

  const [appLoading, setAppLoading] = useState(true)
  const [appError, setAppError] = useState('')
  const [mainQuestLoading, setMainQuestLoading] = useState(true)
  const [mainQuestError, setMainQuestError] = useState('')
  const [weeklyLoading, setWeeklyLoading] = useState(true)
  const [weeklyError, setWeeklyError] = useState('')
  const [suggestionsLoading, setSuggestionsLoading] = useState(true)
  const [suggestionsError, setSuggestionsError] = useState('')
  const [certificatesLoading, setCertificatesLoading] = useState(true)
  const [certificatesError, setCertificatesError] = useState('')

  const [isNavOpen, setIsNavOpen] = useState(false)
  const [isInboxOpen, setIsInboxOpen] = useState(false)
  const [isStatusOpen, setIsStatusOpen] = useState(false)
  const [isQuestOpen, setIsQuestOpen] = useState(false)
  const [isCertificateOpen, setIsCertificateOpen] = useState(false)
  const [isBossOpen, setIsBossOpen] = useState(false)
  const [activeQuestTab, setActiveQuestTab] = useState('main')
  const [hostNow, setHostNow] = useState(() => new Date())
  const [checkInDraft, setCheckInDraft] = useState(EMPTY_CHECKIN_DRAFT)

  useEffect(() => {
    const timer = window.setInterval(() => {
      setHostNow(new Date())
    }, 60000)

    return () => window.clearInterval(timer)
  }, [])

  useEffect(() => {
    loadInitialData()
    loadMainQuestData()
    loadWeeklyMission()
    loadSuggestions()
    loadCertificates()
    loadBossBattles()
  }, [])

  const view = useMemo(() => {
    if (!summary) return null
    return buildDashboardView(summary, quests, checkins)
  }, [summary, quests, checkins])

  const mainQuestMap = useMemo(
    () => buildMainQuestMap(studyPlanWeeks, mainQuests),
    [studyPlanWeeks, mainQuests],
  )

  const roadmapTrack = useMemo(() => buildRoadmapPhaseTrack(mainQuestMap), [mainQuestMap])
  const roadmapBounds = useMemo(() => buildRoadmapBounds(studyPlanWeeks), [studyPlanWeeks])

  const playerSnapshot = useMemo(() => {
    if (!summary && !profile) return null
    return buildPlayerSnapshot(summary?.player, profile ?? {})
  }, [summary, profile])

  const inboxItems = useMemo(
    () => buildSuggestionInbox(rankSuggestions, weaknessSuggestions, view?.skills ?? []),
    [rankSuggestions, weaknessSuggestions, view?.skills],
  )

  const certificateRecords = useMemo(() => filterCertificateRecords(testRecords), [testRecords])
  const bossView = useMemo(() => buildBossView(bossBattles), [bossBattles])

  useEffect(() => {
    if (!view) return

    const current = view.commandDeck.activeCheckIn
    setCheckInDraft({
      mood: current?.mood ?? 3,
      energy: current?.energy ?? 3,
      focus: current?.focus ?? 3,
      note: current?.note ?? '',
      avatarPicker: false,
    })
  }, [view])

  async function loadInitialData() {
    try {
      setAppLoading(true)
      setAppError('')

      const [summaryData, profileData, questData, checkinData] = await Promise.all([
        api('/summary'),
        api('/profile'),
        api('/quests'),
        api('/checkins'),
      ])

      setSummary(summaryData)
      setProfile(profileData)
      setQuests(questData)
      setCheckins(checkinData)
    } catch (error) {
      setAppError(error.message)
    } finally {
      setAppLoading(false)
    }
  }

  async function loadMainQuestData() {
    try {
      setMainQuestLoading(true)
      setMainQuestError('')

      const [weeksData, mainQuestData] = await Promise.all([api('/study-plan/weeks'), api('/main-quests')])
      setStudyPlanWeeks(weeksData)
      setMainQuests(mainQuestData)
    } catch (error) {
      setMainQuestError(error.message)
    } finally {
      setMainQuestLoading(false)
    }
  }

  async function loadWeeklyMission() {
    try {
      setWeeklyLoading(true)
      setWeeklyError('')
      const mission = await api('/weekly-mission/current')
      setWeeklyMission(mission)
    } catch (error) {
      setWeeklyError(error.message)
    } finally {
      setWeeklyLoading(false)
    }
  }

  async function loadSuggestions() {
    try {
      setSuggestionsLoading(true)
      setSuggestionsError('')

      const [rankData, weaknessData] = await Promise.all([api('/rank-suggestions'), api('/weakness-suggestions')])
      setRankSuggestions(rankData)
      setWeaknessSuggestions(weaknessData)
    } catch (error) {
      setSuggestionsError(error.message)
    } finally {
      setSuggestionsLoading(false)
    }
  }

  async function loadCertificates() {
    try {
      setCertificatesLoading(true)
      setCertificatesError('')
      const records = await api('/test-records')
      setTestRecords(records)
    } catch (error) {
      setCertificatesError(error.message)
    } finally {
      setCertificatesLoading(false)
    }
  }

  async function loadBossBattles() {
    const data = await api('/boss-battles')
    setBossBattles(data)
  }

  async function toggleQuest(quest) {
    await api(`/quests/${quest.id}/${quest.completed ? 'uncomplete' : 'complete'}`, {
      method: 'POST',
    })

    await Promise.all([loadInitialData(), loadWeeklyMission(), loadSuggestions(), loadMainQuestData()])
  }

  async function saveCheckIn() {
    await api('/checkins', {
      method: 'POST',
      body: JSON.stringify({
        checkin_date: getTodayISO(),
        mood: checkInDraft.mood,
        energy: checkInDraft.energy,
        focus: checkInDraft.focus,
        note: checkInDraft.note,
      }),
    })

    await loadInitialData()
  }

  async function handleSuggestionAction(item, action) {
    const path =
      item.type === 'rank'
        ? `/rank-suggestions/${item.id}/${action}`
        : `/weakness-suggestions/${item.id}/${action}`

    await api(path, { method: 'POST' })
    await Promise.all([loadSuggestions(), loadInitialData()])
  }

  async function handleCreateCertificate(payload) {
    await api('/test-records', {
      method: 'POST',
      body: JSON.stringify(payload),
    })

    await Promise.all([loadCertificates(), loadSuggestions()])
  }

  function handleCheckInDraftChange({ field, value }) {
    setCheckInDraft((current) => ({ ...current, [field]: value }))
  }

  function openQuest(tab = 'main') {
    setActiveQuestTab(tab)
    setIsQuestOpen(true)
    setIsNavOpen(false)
  }

  function openCertificates() {
    setIsCertificateOpen(true)
    setIsNavOpen(false)
  }

  function openBoss() {
    setIsBossOpen(true)
    setIsNavOpen(false)
  }

  if (appLoading && !summary) {
    return <div className="boot-screen">SYSTEM LOADING...</div>
  }

  if (appError) {
    return <div className="boot-screen boot-screen--error">API ERROR: {appError}</div>
  }

  if (!view || !playerSnapshot) return null

  const mainQuestCleared = mainQuests.filter((quest) => quest.completed).length

  const statCards = [
    {
      label: 'Streak',
      value: `${playerSnapshot.currentStreak} ngay`,
      detail: `Best ${playerSnapshot.bestStreak} ngay`,
      tone: 'cyan',
    },
    {
      label: 'Shield',
      value: `${playerSnapshot.shieldCount} / 2`,
      detail: `Regen ${playerSnapshot.shieldRegenProgress}%`,
      tone: 'amber',
    },
    {
      label: 'Main Quest Cleared',
      value: `${mainQuestCleared}`,
      detail: `${mainQuests.length} total main quests`,
      tone: 'violet',
    },
  ]

  return (
    <main className="home-shell">
      <div className="app-shell__texture" />

      <HomeTopBar
        player={playerSnapshot}
        hostDateTime={formatHostDateTime(hostNow)}
        pendingCount={inboxItems.length}
        isInboxOpen={isInboxOpen}
        inboxItems={inboxItems}
        suggestionsLoading={suggestionsLoading}
        suggestionsError={suggestionsError}
        onToggleInbox={() => setIsInboxOpen((current) => !current)}
        onApplySuggestion={(item) => handleSuggestionAction(item, 'apply')}
        onDismissSuggestion={(item) => handleSuggestionAction(item, 'dismiss')}
        onOpenNav={() => setIsNavOpen(true)}
        onOpenStatus={() => setIsStatusOpen(true)}
      />

      <section className="home-shell__surface">
        <RoadmapHero
          player={playerSnapshot}
          roadmap={roadmapTrack}
          currentPhaseLabel={view.player.phaseLabel}
          statCards={statCards}
          roadmapBounds={
            roadmapBounds
              ? {
                  startDate: formatDate(roadmapBounds.startDate),
                  endDate: formatDate(roadmapBounds.endDate),
                }
              : null
          }
        />

        <div className="home-shell__support">
          <article className="support-panel">
            <p>Today Sync</p>
            <strong>{view.commandDeck.activeCheckIn ? 'Check-in ready' : 'Need check-in'}</strong>
            <span>{view.summary.todayXp} XP earned today</span>
          </article>

          <article className="support-panel">
            <p>Weekly Mission</p>
            <strong>{weeklyLoading ? 'Loading...' : weeklyError ? 'Unavailable' : weeklyMission?.title || '--'}</strong>
            <span>
              {weeklyLoading
                ? 'Dang tai weekly mission.'
                : weeklyError
                  ? weeklyError
                  : `${weeklyMission?.items?.length ?? 0} objectives`}
            </span>
          </article>

          <article className="support-panel">
            <p>Boss Status</p>
            <strong>{bossView.currentBoss?.title || 'No boss loaded'}</strong>
            <span>{bossView.currentBoss?.status || 'Pending'}</span>
          </article>
        </div>
      </section>

      <NavigationDrawer
        open={isNavOpen}
        onClose={() => setIsNavOpen(false)}
        onOpenQuestTab={openQuest}
        onOpenCertificates={openCertificates}
        onOpenBoss={openBoss}
      />

      <StatusModal
        open={isStatusOpen}
        onClose={() => setIsStatusOpen(false)}
        player={playerSnapshot}
        activeCheckIn={view.commandDeck.activeCheckIn}
        checkInDraft={checkInDraft}
        onCheckInDraftChange={handleCheckInDraftChange}
        onSaveCheckIn={saveCheckIn}
        skills={view.skills}
      />

      <QuestOverlay
        open={isQuestOpen}
        activeTab={activeQuestTab}
        onTabChange={setActiveQuestTab}
        onClose={() => setIsQuestOpen(false)}
        mainQuestMap={mainQuestMap}
        mainQuestLoading={mainQuestLoading}
        mainQuestError={mainQuestError}
        dailyQuests={view.todayQuests}
        backlogQuests={view.backlogQuests}
        commandDeck={view.commandDeck}
        onToggleQuest={toggleQuest}
        weeklyMission={
          weeklyLoading || weeklyError
            ? null
            : weeklyMission || {
                pattern_code: view.weeklyMission.code,
                title: view.weeklyMission.title,
                description: '',
                reward_xp: view.weeklyMission.rewardXp,
                items: [],
              }
        }
      />

      <CertificateOverlay
        open={isCertificateOpen}
        loading={certificatesLoading}
        error={certificatesError}
        records={certificateRecords}
        onClose={() => setIsCertificateOpen(false)}
        onCreate={handleCreateCertificate}
      />

      <BossOverlay open={isBossOpen} bossView={bossView} onClose={() => setIsBossOpen(false)} />
    </main>
  )
}

export default App
