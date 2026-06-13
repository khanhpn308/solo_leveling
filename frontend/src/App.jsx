import { lazy, Suspense, startTransition, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from './auth/AuthProvider'
import { apiFetch } from './api/client'
import { unlockRankExam, startRankExam } from './api/rankExam'
import HomeTopBar from './components/HomeTopBar'
import NavigationDrawer from './components/NavigationDrawer'
import OverlayShellFallback from './components/OverlayShellFallback'
import TestXpPanel from './components/TestXpPanel'
import RankExamScreen from './components/RankExamScreen'
import RankExamResultScreen from './components/RankExamResultScreen'
import RoadmapHero from './components/RoadmapHero'
import ToastRack from './components/ToastRack'
import {
  buildBossView,
  buildDashboardView,
  buildMainQuestMap,
  buildPlayerSnapshot,
  buildRoadmapBounds,
  buildRoadmapPhaseTrack,
  buildSuggestionInbox,
  filterCertificateRecords,
  formatDate,
  getTodayISO,
} from './dashboard-data'

const StatusModal = lazy(() => import('./components/StatusModal'))
const QuestOverlay = lazy(() => import('./components/QuestOverlay'))
const CertificateOverlay = lazy(() => import('./components/CertificateOverlay'))
const BossOverlay = lazy(() => import('./components/BossOverlay'))
const VocabularyWorkspace = lazy(() => import('./components/VocabularyWorkspace'))

const EMPTY_CHECKIN_DRAFT = {
  mood: 3,
  energy: 3,
  focus: 3,
  note: '',
  avatarPicker: false,
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

function isWeeklyItemComplete(item) {
  if (!item) return false
  if (typeof item.current_count === 'number' && typeof item.target_count === 'number' && item.target_count > 0) {
    return item.current_count >= item.target_count
  }

  return String(item.status || '').toLowerCase() === 'completed'
}

function summarizeWeeklyMissionProgress(mission) {
  const items = mission?.items ?? []
  const totalObjectives = items.length
  const completedObjectives = items.filter(isWeeklyItemComplete).length
  const percent = totalObjectives > 0 ? Math.round((completedObjectives / totalObjectives) * 100) : 0

  return {
    code: mission?.pattern_code || mission?.code || '',
    completedObjectives,
    totalObjectives,
    percent,
    isComplete: totalObjectives > 0 && completedObjectives >= totalObjectives,
  }
}

function App() {
  const toastTimersRef = useRef(new Map())
  const weeklyMissionSnapshotRef = useRef(null)
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
  const [vocabularyItems, setVocabularyItems] = useState([])
  const [dueFlashcards, setDueFlashcards] = useState([])

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
  const [questPendingById, setQuestPendingById] = useState({})
  const [suggestionPendingByKey, setSuggestionPendingByKey] = useState({})
  const [checkInSaving, setCheckInSaving] = useState(false)
  const [checkInFeedback, setCheckInFeedback] = useState(null)
  const [toastQueue, setToastQueue] = useState([])
  const [successQuestId, setSuccessQuestId] = useState(null)
  const [rewardPulseActive, setRewardPulseActive] = useState(false)
  const [weeklyPulseActive, setWeeklyPulseActive] = useState(false)
  const [weeklyClaimPending, setWeeklyClaimPending] = useState(false)

  const [statusOverlayReady, setStatusOverlayReady] = useState(false)
  const [questOverlayReady, setQuestOverlayReady] = useState(false)
  const [certificateOverlayReady, setCertificateOverlayReady] = useState(false)
  const [bossOverlayReady, setBossOverlayReady] = useState(false)

  const [currentView, setCurrentView] = useState('dashboard') // 'dashboard' | 'vocabulary'
  const [vocabularyWorkspaceReady, setVocabularyWorkspaceReady] = useState(false)

  const [examData, setExamData] = useState(null) // RankExamStartOut
  const [examSkill, setExamSkill] = useState(null)
  const [examResult, setExamResult] = useState(null)
  const [isExamOpen, setIsExamOpen] = useState(false)
  const [isExamResultOpen, setIsExamResultOpen] = useState(false)

  const navigate = useNavigate()
  const { logout, account } = useAuth()

  const handleLogout = useCallback(async () => {
    await logout()
    navigate('/login')
  }, [logout, navigate])

  const api = useCallback(
    async (path, options = {}) => {
      try {
        return await apiFetch(path, options)
      } catch (err) {
        if (err.status === 401) {
          await logout()
          navigate('/login')
          return
        }
        throw err
      }
    },
    [logout, navigate],
  )

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

  useEffect(() => {
    return () => {
      toastTimersRef.current.forEach((timer) => window.clearTimeout(timer))
      toastTimersRef.current.clear()
    }
  }, [])

  useEffect(() => {
    if (!successQuestId) return undefined

    const timer = window.setTimeout(() => {
      setSuccessQuestId(null)
    }, 1400)

    return () => window.clearTimeout(timer)
  }, [successQuestId])

  useEffect(() => {
    if (!rewardPulseActive) return undefined

    const timer = window.setTimeout(() => {
      setRewardPulseActive(false)
    }, 1200)

    return () => window.clearTimeout(timer)
  }, [rewardPulseActive])

  useEffect(() => {
    if (!weeklyPulseActive) return undefined

    const timer = window.setTimeout(() => {
      setWeeklyPulseActive(false)
    }, 1200)

    return () => window.clearTimeout(timer)
  }, [weeklyPulseActive])

  useEffect(() => {
    if (!checkInFeedback || checkInFeedback.tone === 'error') return undefined

    const timer = window.setTimeout(() => {
      setCheckInFeedback(null)
    }, 2200)

    return () => window.clearTimeout(timer)
  }, [checkInFeedback])

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
  const weeklyTouchpoint = useMemo(() => {
    if (!view?.weeklyMission && !weeklyMission) return null

    const fallbackMission = view?.weeklyMission
      ? {
          pattern_code: view.weeklyMission.code,
          title: view.weeklyMission.title,
          description: 'Pattern-derived weekly focus while the live mission feed is syncing.',
          reward_xp: view.weeklyMission.rewardXp,
          progress: view.weeklyMission.progress,
          items: view.weeklyMission.lines.map((line, index) => ({
            id: `fallback-${index}`,
            description: line,
            current_count: 0,
            target_count: 1,
            status: 'Pending',
          })),
        }
      : null

    const sourceMission = weeklyMission || fallbackMission

    if (!sourceMission) return null

    const items = (sourceMission.items ?? []).map((item, index) => {
      const statusLabel = String(item.status || 'Pending').replaceAll('_', ' ')
      const isComplete = isWeeklyItemComplete(item)

      return {
        ...item,
        id: item.id ?? `${sourceMission.pattern_code || sourceMission.code || 'weekly'}-${index}`,
        statusLabel,
        isComplete,
        progressLabel:
          typeof item.current_count === 'number' && typeof item.target_count === 'number'
            ? `${item.current_count}/${item.target_count}`
            : isComplete
              ? 'Done'
              : 'Tracking',
      }
    })

    const progressSummary = summarizeWeeklyMissionProgress({ ...sourceMission, items })
    const liveProgress = sourceMission.progress || `${progressSummary.completedObjectives}/${Math.max(progressSummary.totalObjectives, 1)}`

    return {
      ...sourceMission,
      id: sourceMission.id ?? null,
      code: sourceMission.pattern_code || sourceMission.code || '--',
      rewardXp: sourceMission.reward_xp ?? sourceMission.rewardXp ?? 0,
      rewardClaimed: Boolean(sourceMission.reward_claimed ?? sourceMission.rewardClaimed ?? false),
      rewardClaimedAt: sourceMission.reward_claimed_at ?? sourceMission.rewardClaimedAt ?? null,
      items,
      progressText: liveProgress,
      completedObjectives: progressSummary.completedObjectives,
      totalObjectives: progressSummary.totalObjectives,
      percent: progressSummary.percent,
      isComplete: progressSummary.isComplete,
      sourceLabel: weeklyMission ? 'Live weekly sync' : 'Pattern fallback',
      stateLabel: progressSummary.isComplete
        ? Boolean(sourceMission.reward_claimed ?? sourceMission.rewardClaimed ?? false)
          ? 'Reward secured'
          : 'Reward ready to claim'
        : `Objectives ${liveProgress}`,
      helperText: progressSummary.isComplete
        ? Boolean(sourceMission.reward_claimed ?? sourceMission.rewardClaimed ?? false)
          ? 'Weekly reward has been secured and folded into player progress.'
          : 'All conditions are complete. Claim the weekly reward to bank the XP.'
        : `${Math.max(progressSummary.totalObjectives - progressSummary.completedObjectives, 0)} objectives still need attention this week.`,
    }
  }, [view, weeklyMission])

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

  function commitState(update, transition = false) {
    if (transition) {
      startTransition(() => {
        update()
      })
      return
    }

    update()
  }

  function enqueueToast({ title, detail, tone = 'neutral' }) {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
    const nextToast = { id, title, detail, tone }

    setToastQueue((current) => [...current, nextToast])

    const timer = window.setTimeout(() => {
      setToastQueue((current) => current.filter((toast) => toast.id !== id))
      toastTimersRef.current.delete(id)
    }, 2600)

    toastTimersRef.current.set(id, timer)
  }

  function dismissToast(id) {
    const timer = toastTimersRef.current.get(id)
    if (timer) {
      window.clearTimeout(timer)
      toastTimersRef.current.delete(id)
    }
    setToastQueue((current) => current.filter((toast) => toast.id !== id))
  }

  function markQuestRewardClaimed(quest) {
    setSuccessQuestId(quest.id)
    setRewardPulseActive(true)
    enqueueToast({
      title: 'Reward claimed',
      detail: `${quest.title} banked +${quest.earnedXp ?? quest.earned_xp ?? 0} XP.`,
      tone: 'success',
    })
  }

  async function loadInitialData({ transition = false, silent = false } = {}) {
    try {
      if (!silent) {
        setAppLoading(true)
        setAppError('')
      }

      const [summaryData, profileData, questData, checkinData, vocabData, dueData] = await Promise.all([
        api('/summary'),
        api('/profile'),
        api('/quests'),
        api('/checkins'),
        api('/vocabulary').catch(() => []),
        api('/flashcards/due').catch(() => []),
      ])

      commitState(() => {
        setSummary(summaryData)
        setProfile(profileData)
        setQuests(questData)
        setCheckins(checkinData)
        setVocabularyItems(vocabData)
        setDueFlashcards(dueData)
      }, transition)
    } catch (error) {
      if (silent) throw error
      commitState(() => setAppError(error.message), transition)
    } finally {
      if (!silent) setAppLoading(false)
    }
  }

  async function loadMainQuestData({ transition = false, silent = false } = {}) {
    try {
      if (!silent) {
        setMainQuestLoading(true)
        setMainQuestError('')
      }

      const [weeksData, mainQuestData] = await Promise.all([api('/study-plan/weeks'), api('/main-quests')])

      commitState(() => {
        setStudyPlanWeeks(weeksData)
        setMainQuests(mainQuestData)
      }, transition)
    } catch (error) {
      if (silent) throw error
      commitState(() => setMainQuestError(error.message), transition)
    } finally {
      if (!silent) setMainQuestLoading(false)
    }
  }

  async function loadWeeklyMission({ transition = false, silent = false } = {}) {
    try {
      if (!silent) {
        setWeeklyLoading(true)
        setWeeklyError('')
      }

      const mission = await api('/weekly-mission/current')
      const nextSnapshot = summarizeWeeklyMissionProgress(mission)
      const previousSnapshot = weeklyMissionSnapshotRef.current

      weeklyMissionSnapshotRef.current = nextSnapshot

      if (previousSnapshot && previousSnapshot.code === nextSnapshot.code) {
        const advanced =
          nextSnapshot.completedObjectives > previousSnapshot.completedObjectives || nextSnapshot.percent > previousSnapshot.percent

        if (advanced) {
          setWeeklyPulseActive(true)
        }
      }

      commitState(() => setWeeklyMission(mission), transition)
    } catch (error) {
      if (silent) throw error
      commitState(() => setWeeklyError(error.message), transition)
    } finally {
      if (!silent) setWeeklyLoading(false)
    }
  }

  async function loadSuggestions({ transition = false, silent = false } = {}) {
    try {
      if (!silent) {
        setSuggestionsLoading(true)
        setSuggestionsError('')
      }

      const [rankData, weaknessData] = await Promise.all([api('/rank-suggestions'), api('/weakness-suggestions')])

      commitState(() => {
        setRankSuggestions(rankData)
        setWeaknessSuggestions(weaknessData)
      }, transition)
    } catch (error) {
      if (silent) throw error
      commitState(() => setSuggestionsError(error.message), transition)
    } finally {
      if (!silent) setSuggestionsLoading(false)
    }
  }

  async function loadCertificates({ transition = false, silent = false } = {}) {
    try {
      if (!silent) {
        setCertificatesLoading(true)
        setCertificatesError('')
      }

      const records = await api('/test-records')
      commitState(() => setTestRecords(records), transition)
    } catch (error) {
      if (silent) throw error
      commitState(() => setCertificatesError(error.message), transition)
    } finally {
      if (!silent) setCertificatesLoading(false)
    }
  }

  async function loadBossBattles({ transition = false, silent = false } = {}) {
    try {
      const data = await api('/boss-battles')
      commitState(() => setBossBattles(data), transition)
    } catch (error) {
      if (silent) throw error
    }
  }

  async function handleQuestAction(quest, action) {
    if (questPendingById[quest.id]) return

    setQuestPendingById((current) => ({ ...current, [quest.id]: action }))

    try {
      const updatedQuest = await api(`/quests/${quest.id}/${action}`, {
        method: 'POST',
      })

      if (action === 'claim') {
        markQuestRewardClaimed({
          ...quest,
          earned_xp: updatedQuest?.earned_xp ?? quest.earned_xp,
          earnedXp: updatedQuest?.earned_xp ?? quest.earnedXp,
        })
      } else if (action === 'complete') {
        enqueueToast({
          title: 'Quest completed',
          detail: `${quest.title} is ready for claim.`,
          tone: 'neutral',
        })
      }

      await Promise.all([
        loadInitialData({ transition: true, silent: true }),
        loadWeeklyMission({ transition: true, silent: true }),
        loadSuggestions({ transition: true, silent: true }),
        loadMainQuestData({ transition: true, silent: true }),
      ])
    } catch (error) {
      setSuccessQuestId((current) => (current === quest.id ? null : current))
      setRewardPulseActive(false)
      enqueueToast({
        title: 'Action failed',
        detail: error.message,
        tone: 'danger',
      })
    } finally {
      setQuestPendingById((current) => {
        const nextState = { ...current }
        delete nextState[quest.id]
        return nextState
      })
    }
  }

  async function handleClaimWeeklyMission(mission) {
    if (!mission?.id || weeklyClaimPending) return

    setWeeklyClaimPending(true)

    try {
      await api(`/weekly-missions/${mission.id}/claim`, {
        method: 'POST',
      })

      setWeeklyPulseActive(true)
      enqueueToast({
        title: 'Weekly reward claimed',
        detail: `${mission.title} banked +${mission.rewardXp} XP.`,
        tone: 'success',
      })

      await Promise.all([
        loadInitialData({ transition: true, silent: true }),
        loadWeeklyMission({ transition: true, silent: true }),
      ])
    } catch (error) {
      enqueueToast({
        title: 'Action failed',
        detail: error.message,
        tone: 'danger',
      })
    } finally {
      setWeeklyClaimPending(false)
    }
  }

  async function saveCheckIn() {
    if (checkInSaving) return

    setCheckInSaving(true)
    setCheckInFeedback(null)

    try {
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

      await loadInitialData({ transition: true, silent: true })
      setCheckInFeedback({ tone: 'success', message: "Check-in saved to today's status log." })
      enqueueToast({
        title: 'Check-in saved',
        detail: 'Daily condition updated.',
        tone: 'success',
      })
    } catch (error) {
      setCheckInFeedback({ tone: 'error', message: error.message })
      enqueueToast({
        title: 'Action failed',
        detail: error.message,
        tone: 'danger',
      })
    } finally {
      setCheckInSaving(false)
    }
  }

  async function handleSuggestionAction(item, action) {
    if (suggestionPendingByKey[item.key]) return

    const path =
      item.type === 'rank'
        ? `/rank-suggestions/${item.id}/${action}`
        : `/weakness-suggestions/${item.id}/${action}`

    setSuggestionPendingByKey((current) => ({ ...current, [item.key]: action }))

    try {
      await api(path, { method: 'POST' })
      await Promise.all([
        loadSuggestions({ transition: true, silent: true }),
        loadInitialData({ transition: true, silent: true }),
      ])

      enqueueToast({
        title: action === 'apply' ? 'Suggestion applied' : 'Suggestion dismissed',
        detail: item.title,
        tone: action === 'apply' ? 'success' : 'neutral',
      })
    } catch (error) {
      enqueueToast({
        title: 'Action failed',
        detail: error.message,
        tone: 'danger',
      })
    } finally {
      setSuggestionPendingByKey((current) => {
        const nextState = { ...current }
        delete nextState[item.key]
        return nextState
      })
    }
  }

  async function handleUnlockBoss(skill) {
    try {
      await unlockRankExam(skill.id)
      await loadInitialData({ transition: true, silent: true })
      enqueueToast({ title: 'Boss unlocked', detail: `${skill.name} exam is now available`, tone: 'success' })
    } catch (err) {
      enqueueToast({ title: 'Unlock failed', detail: err.message, tone: 'danger' })
    }
  }

  async function handleStartExam(skill) {
    try {
      const data = await startRankExam(skill.id)
      setExamData(data)
      setExamSkill(skill)
      setExamResult(null)
      setIsExamOpen(true)
      setIsExamResultOpen(false)
    } catch (err) {
      enqueueToast({ title: 'Exam start failed', detail: err.message, tone: 'danger' })
    }
  }

  // Inbox boss item action: route by state. eligible → unlock; otherwise start/resume exam.
  async function handleBossInboxAction(item) {
    if (suggestionPendingByKey[item.key]) return
    setSuggestionPendingByKey((current) => ({ ...current, [item.key]: 'apply' }))
    try {
      if (item.bossState === 'eligible') {
        await handleUnlockBoss(item.skillObj)
      } else {
        setIsInboxOpen(false)
        await handleStartExam(item.skillObj)
      }
    } finally {
      setSuggestionPendingByKey((current) => {
        const next = { ...current }
        delete next[item.key]
        return next
      })
    }
  }

  function handleExamResult(result) {
    setExamResult(result)
    setIsExamOpen(false)
    setIsExamResultOpen(true)
    loadInitialData({ transition: true, silent: true })
    loadSuggestions({ transition: true, silent: true })
  }

  function handleExamClose() {
    setIsExamOpen(false)
    setIsExamResultOpen(false)
    setExamData(null)
    setExamSkill(null)
    setExamResult(null)
    loadInitialData({ transition: true, silent: true })
  }

  async function handleCreateCertificate(payload) {
    await api('/test-records', {
      method: 'POST',
      body: JSON.stringify(payload),
    })

    await Promise.all([
      loadCertificates({ transition: true, silent: true }),
      loadSuggestions({ transition: true, silent: true }),
    ])
  }

  function handleCheckInDraftChange({ field, value }) {
    setCheckInFeedback(null)
    setCheckInDraft((current) => ({ ...current, [field]: value }))
  }

  function openStatus() {
    setStatusOverlayReady(true)
    startTransition(() => {
      setIsStatusOpen(true)
      setIsQuestOpen(false)
      setIsCertificateOpen(false)
      setIsBossOpen(false)
      setIsInboxOpen(false)
      setIsNavOpen(false)
    })
  }

  function openQuest(tab = 'main') {
    setQuestOverlayReady(true)
    startTransition(() => {
      setActiveQuestTab(tab)
      setIsQuestOpen(true)
      setIsStatusOpen(false)
      setIsCertificateOpen(false)
      setIsBossOpen(false)
      setIsNavOpen(false)
      setIsInboxOpen(false)
    })
  }

  function openCertificates() {
    setCertificateOverlayReady(true)
    startTransition(() => {
      setIsCertificateOpen(true)
      setIsStatusOpen(false)
      setIsQuestOpen(false)
      setIsBossOpen(false)
      setIsNavOpen(false)
      setIsInboxOpen(false)
    })
  }

  function openBoss() {
    setBossOverlayReady(true)
    startTransition(() => {
      setIsBossOpen(true)
      setIsStatusOpen(false)
      setIsQuestOpen(false)
      setIsCertificateOpen(false)
      setIsNavOpen(false)
      setIsInboxOpen(false)
    })
  }

  function openVocabulary() {
    setVocabularyWorkspaceReady(true)
    startTransition(() => {
      setCurrentView('vocabulary')
      setIsStatusOpen(false)
      setIsQuestOpen(false)
      setIsCertificateOpen(false)
      setIsBossOpen(false)
      setIsNavOpen(false)
      setIsInboxOpen(false)
    })
  }

  if (appLoading && !summary) {
    return <div className="boot-screen">SYSTEM LOADING...</div>
  }

  if (appError) {
    return <div className="boot-screen boot-screen--error">API ERROR: {appError}</div>
  }

  if (!view || !playerSnapshot) return null

  if (currentView === 'vocabulary' && vocabularyWorkspaceReady) {
    return (
      <main className="vocab-shell">
        <div className="app-shell__texture" />
        <Suspense fallback={<div className="boot-screen">LOADING WORKSPACE...</div>}>
          <VocabularyWorkspace
            onClose={() => {
              setCurrentView('dashboard')
              loadInitialData({ transition: true, silent: true })
            }}
            api={api}
            vocabularyItems={vocabularyItems}
            dueFlashcards={dueFlashcards}
            onLoadData={() => loadInitialData({ transition: true, silent: true })}
          />
        </Suspense>
        <ToastRack toasts={toastQueue} onDismiss={dismissToast} />
      </main>
    )
  }

  const mainQuestCleared = mainQuests.filter((quest) => quest.completed).length
  const pendingDailyClaims = view.quests.filter((quest) => quest.completed && !quest.rewardClaimed).length
  const pendingMainClaims = mainQuests.filter((quest) => quest.completed && !quest.reward_claimed).length
  const pendingWeeklyClaims = weeklyTouchpoint?.isComplete && !weeklyTouchpoint?.rewardClaimed ? 1 : 0
  const pendingClaimCount = pendingDailyClaims + pendingMainClaims + pendingWeeklyClaims

  const statCards = [
    {
      label: 'Streak',
      value: `${playerSnapshot.currentStreak} days`,
      detail: `Best ${playerSnapshot.bestStreak} days`,
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
        suggestionPendingByKey={suggestionPendingByKey}
        onToggleInbox={() => setIsInboxOpen((current) => !current)}
        onCloseInbox={() => setIsInboxOpen(false)}
        onApplySuggestion={(item) =>
          item.type === 'boss' ? handleBossInboxAction(item) : handleSuggestionAction(item, 'apply')
        }
        onDismissSuggestion={(item) => handleSuggestionAction(item, 'dismiss')}
        hasPendingClaims={pendingClaimCount > 0}
        onOpenNav={() => {
          setIsInboxOpen(false)
          setIsNavOpen(true)
        }}
        onOpenStatus={openStatus}
      />

      <section className="home-shell__surface">
        <RoadmapHero
          player={playerSnapshot}
          roadmap={roadmapTrack}
          mainQuestMap={mainQuestMap}
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
          <article className={`support-panel ${rewardPulseActive ? 'support-panel--reward-pulse' : ''}`}>
            <p>Today Sync</p>
            <strong>{view.commandDeck.activeCheckIn ? 'Check-in ready' : 'Need check-in'}</strong>
            <span>
              {view.summary.todayXp} XP banked today{pendingClaimCount > 0 ? ` / ${pendingClaimCount} reward${pendingClaimCount > 1 ? 's' : ''} waiting` : ''}
            </span>
          </article>

          <button
            className="support-panel support-panel--button"
            type="button"
            onClick={openVocabulary}
            aria-label="Open vocabulary support system"
          >
            <p>Vocabulary Today</p>
            <strong>
              {vocabularyItems.length} Words Codex
            </strong>
            <span>
              {dueFlashcards.length > 0 ? `${dueFlashcards.length} flashcards due` : 'All memory gates secured'}
            </span>
          </button>

          <button
            className={`support-panel support-panel--button ${weeklyPulseActive ? 'support-panel--reward-pulse' : ''}`}
            type="button"
            onClick={() => openQuest('weekly')}
            aria-label="Open weekly mission board"
          >
            <p>Weekly Mission</p>
            <strong>{weeklyLoading && !weeklyTouchpoint ? 'Loading...' : weeklyTouchpoint?.title || 'Mission sync issue'}</strong>
            <span>
              {weeklyLoading && !weeklyTouchpoint
                ? 'Loading weekly mission.'
                : weeklyTouchpoint
                  ? `${weeklyTouchpoint.stateLabel} / ${weeklyTouchpoint.sourceLabel}`
                  : weeklyError || 'No weekly mission loaded.'}
            </span>
          </button>

          <article className="support-panel">
            <p>Boss Status</p>
            <strong>{bossView.currentBoss?.title || 'No boss loaded'}</strong>
            <span>{bossView.currentBoss?.displayStatus || 'Pending'}</span>
          </article>
        </div>
      </section>

      <NavigationDrawer
        open={isNavOpen}
        onClose={() => setIsNavOpen(false)}
        onOpenQuestTab={openQuest}
        onOpenCertificates={openCertificates}
        onOpenBoss={openBoss}
        onOpenVocabulary={openVocabulary}
      />

      {statusOverlayReady ? (
        <Suspense fallback={isStatusOpen ? <OverlayShellFallback title="Status" /> : null}>
          <StatusModal
            open={isStatusOpen}
            onClose={() => setIsStatusOpen(false)}
            onLogout={handleLogout}
            player={playerSnapshot}
            activeCheckIn={view.commandDeck.activeCheckIn}
            checkInDraft={checkInDraft}
            onCheckInDraftChange={handleCheckInDraftChange}
            onSaveCheckIn={saveCheckIn}
            checkInSaving={checkInSaving}
            checkInFeedback={checkInFeedback}
            skills={view.skills}
            badges={view.badges}
            recentCheckins={view.commandDeck.recentCheckins}
            onProfileRefresh={() => loadInitialData({ silent: true })}
          />
        </Suspense>
      ) : null}

      {questOverlayReady ? (
        <Suspense fallback={isQuestOpen ? <OverlayShellFallback title="Quest Board" /> : null}>
          <QuestOverlay
            open={isQuestOpen}
            activeTab={activeQuestTab}
            onTabChange={(tab) => startTransition(() => setActiveQuestTab(tab))}
            onClose={() => setIsQuestOpen(false)}
            mainQuestMap={mainQuestMap}
            mainQuestLoading={mainQuestLoading}
            mainQuestError={mainQuestError}
            dailyQuests={view.todayQuests}
            allQuests={view.quests}
            commandDeck={view.commandDeck}
            skills={view.skills}
            onQuestAction={handleQuestAction}
            questPendingById={questPendingById}
            successQuestId={successQuestId}
            rewardPulseToken={rewardPulseActive}
            weeklyMission={weeklyTouchpoint}
            weeklyLoading={weeklyLoading && !weeklyTouchpoint}
            weeklyError={weeklyTouchpoint ? '' : weeklyError}
            weeklyPulseActive={weeklyPulseActive}
            weeklyClaimPending={weeklyClaimPending}
            onClaimWeeklyMission={handleClaimWeeklyMission}
          />
        </Suspense>
      ) : null}

      {certificateOverlayReady ? (
        <Suspense fallback={isCertificateOpen ? <OverlayShellFallback title="Certificate Records" /> : null}>
          <CertificateOverlay
            open={isCertificateOpen}
            loading={certificatesLoading}
            error={certificatesError}
            records={certificateRecords}
            onClose={() => setIsCertificateOpen(false)}
            onCreate={handleCreateCertificate}
          />
        </Suspense>
      ) : null}

      {bossOverlayReady ? (
        <Suspense fallback={isBossOpen ? <OverlayShellFallback title="Boss Battles" /> : null}>
          <BossOverlay open={isBossOpen} bossView={bossView} onClose={() => setIsBossOpen(false)} />
        </Suspense>
      ) : null}



      {account?.email === 'ad00000@gmail.com' && (
        <TestXpPanel
          hidden={isNavOpen || isExamOpen || isExamResultOpen || isStatusOpen || isQuestOpen || isBossOpen || isCertificateOpen}
          onXpChange={() => loadInitialData({ transition: true, silent: true })}
        />
      )}

      <RankExamScreen
        open={isExamOpen}
        examData={examData}
        skill={examSkill}
        onClose={handleExamClose}
        onResult={handleExamResult}
      />

      <RankExamResultScreen
        open={isExamResultOpen}
        result={examResult}
        skill={examSkill}
        onClose={handleExamClose}
        onRetry={() => examSkill && handleStartExam(examSkill)}
      />

      <ToastRack toasts={toastQueue} onDismiss={dismissToast} />
    </main>
  )
}

export default App
