const PLAYER_RANK_THRESHOLDS = [
  { minXp: 1800, rank: 'S' },
  { minXp: 1350, rank: 'A' },
  { minXp: 950, rank: 'B' },
  { minXp: 620, rank: 'C' },
  { minXp: 320, rank: 'D' },
  { minXp: 120, rank: 'E' },
  { minXp: 0, rank: 'F' },
]

const SKILL_XP_THRESHOLDS = [0, 200, 500, 1000, 1700, 2500, 3500]
const DATE_ONLY_RE = /^(\d{4})-(\d{2})-(\d{2})$/

export const RANK_ORDER = ['F', 'E', 'D', 'C', 'B', 'A', 'S']

export const SKILL_THEME = {
  Listening: { accent: 'cyan', label: 'Core' },
  Reading: { accent: 'amber', label: 'Core' },
  Writing: { accent: 'rose', label: 'Core' },
  Speaking: { accent: 'violet', label: 'Core' },
  Vocabulary: { accent: 'green', label: 'Support' },
  Collocation: { accent: 'orange', label: 'Support' },
  Grammar: { accent: 'steel', label: 'Support' },
}

export const TEST_EVIDENCE = [
  { exam: 'TOEIC', date: '2025-11-10', details: 'Listening 395 / Reading 270 / Speaking 95 / Writing 120' },
  { exam: 'Aptis', date: '2026-01-18', details: 'Overall B1 / Listening B2 / Reading B1 / Speaking B1 / Writing B1' },
]

export const TRACKER_MODULES = [
  {
    key: 'error-log',
    title: 'Error Log',
    status: 'Ready',
    description: 'Store reviewed and corrected mistakes, tagged to generate weakness suggestions.',
  },
  {
    key: 'writing',
    title: 'Writing Tracker',
    status: 'Preparing',
    description: 'Track prompts, drafts, feedback, and revised versions.',
  },
  {
    key: 'speaking',
    title: 'Speaking Tracker',
    status: 'Preparing',
    description: 'Track topics, cue cards, self notes, and transcript summaries.',
  },
  {
    key: 'mock-test',
    title: 'Mock Test Tracker',
    status: 'Preparing',
    description: 'Track full or partial tests, raw scores, and estimated bands.',
  },
]

export const CERTIFICATE_TYPES = ['IELTS', 'APTIS', 'TOEIC', 'TOEFL']

export const MAIN_QUEST_PHASES = [
  {
    code: 'P1',
    title: 'Month 1-3',
    subtitle: 'Foundation',
    weekStart: 1,
    weekEnd: 13,
  },
  {
    code: 'P2',
    title: 'Month 4-6',
    subtitle: 'Format Training',
    weekStart: 14,
    weekEnd: 26,
  },
  {
    code: 'P3',
    title: 'Month 7-9',
    subtitle: 'Band 6 Push',
    weekStart: 27,
    weekEnd: 39,
  },
  {
    code: 'P4',
    title: 'Month 10-12',
    subtitle: 'Partial Tests',
    weekStart: 40,
    weekEnd: 52,
  },
  {
    code: 'P5',
    title: 'Month 13-18',
    subtitle: 'Mock Arena',
    weekStart: 53,
    weekEnd: 78,
  },
]

const WEEKLY_MISSION_PATTERNS = [
  {
    code: 'A',
    title: 'Mission A · Reading Pressure',
    lines: [
      'Complete 4 core study sessions this week',
      'Finish at least 2 Reading quests on time',
      'Update 1 Error Log entry related to vocabulary or long sentences',
    ],
  },
  {
    code: 'B',
    title: 'Mission B · Grammar Relay',
    lines: [
      'Complete 4 core study sessions this week',
      'Submit 1 check-in with a clear study-status note',
      'Finish 1 overdue Grammar or Vocabulary quest',
    ],
  },
  {
    code: 'C',
    title: 'Mission C · Mixed Discipline',
    lines: [
      'Complete 4 core study sessions this week',
      'Finish at least 1 Writing or Speaking quest',
      'Keep overdue quests under 2 for the week',
    ],
  },
]

export function formatDate(value) {
  if (!value) return '--'

  if (typeof value === 'string') {
    const match = value.match(DATE_ONLY_RE)
    if (match) {
      const [, yyyy, mm, dd] = match
      return `${dd}/${mm}/${yyyy}`
    }
  }

  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(parseDateValue(value))
}

export function toIsoDate(value) {
  if (!value) return ''

  if (typeof value === 'string') {
    const match = value.match(DATE_ONLY_RE)
    if (match) return value
  }

  const dateValue = parseDateValue(value)
  if (Number.isNaN(dateValue.getTime())) return ''

  const yyyy = dateValue.getFullYear()
  const mm = String(dateValue.getMonth() + 1).padStart(2, '0')
  const dd = String(dateValue.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

export function parseDateValue(value) {
  if (value instanceof Date) return value

  if (typeof value === 'string') {
    const match = value.match(DATE_ONLY_RE)
    if (match) {
      const [, yyyy, mm, dd] = match
      return new Date(Number(yyyy), Number(mm) - 1, Number(dd), 12, 0, 0, 0)
    }
  }

  return new Date(value)
}

export function getCalendarDayOrdinal(value) {
  const isoDate = toIsoDate(value)
  const match = isoDate.match(DATE_ONLY_RE)

  if (!match) return Number.NaN

  const [, yyyy, mm, dd] = match
  return Math.floor(Date.UTC(Number(yyyy), Number(mm) - 1, Number(dd)) / 86400000)
}

export function getCalendarDayDiff(laterValue, earlierValue) {
  return getCalendarDayOrdinal(laterValue) - getCalendarDayOrdinal(earlierValue)
}

export function getTodayISO() {
  const today = new Date()
  const yyyy = today.getFullYear()
  const mm = String(today.getMonth() + 1).padStart(2, '0')
  const dd = String(today.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

export function splitSummaryItems(value) {
  if (!value) return []

  return value
    .split(';')
    .map((item) => item.trim())
    .filter(Boolean)
}

function uniqueItems(items) {
  return [...new Set(items.filter(Boolean))]
}

export function getMainQuestPhaseMeta(weekNo) {
  return MAIN_QUEST_PHASES.find((phase) => weekNo >= phase.weekStart && weekNo <= phase.weekEnd) ?? MAIN_QUEST_PHASES[0]
}

function getMainQuestStatusMeta(status) {
  if (status === 'completed') {
    return { label: 'Completed', tone: 'completed' }
  }

  if (status === 'overdue') {
    return { label: 'Overdue', tone: 'overdue' }
  }

  if (status === 'expired') {
    return { label: 'Expired', tone: 'expired' }
  }

  return { label: 'Pending', tone: 'pending' }
}

function getSessionIntegrity(matches) {
  if (matches.length === 0) {
    return {
      level: 'warning',
      label: 'Missing quest link',
      detail: 'This study session does not have a Main Quest linked by study_plan_session_id.',
    }
  }

  if (matches.length > 1) {
    return {
      level: 'warning',
      label: 'Duplicate quest link',
      detail: `${matches.length} Main Quests point to this session. Showing the first one for now.`,
    }
  }

  return null
}

function getSessionXpMeta(quest, integrity) {
  if (integrity?.level === 'warning' && !quest) {
    return {
      value: '--',
      label: 'XP unavailable',
      detail: 'Main Quest could not be resolved, so reward and earned XP are unavailable.',
    }
  }

  if (!quest) {
    return {
      value: '--',
      label: 'XP unavailable',
      detail: 'No XP data available for this session.',
    }
  }

  const rewardXp = quest.base_xp ?? quest.xp ?? null

  if (quest.completed) {
    return {
      value: quest.earned_xp ?? '--',
      label: 'Earned',
      detail: rewardXp != null ? `Reward ${rewardXp} XP` : 'No base reward returned by the API.',
    }
  }

  return {
    value: rewardXp ?? '--',
    label: 'Reward',
    detail: rewardXp != null ? 'Reward XP if completed.' : 'No reward XP returned by the API.',
  }
}

export function buildMainQuestMap(studyPlanWeeks, mainQuests, todayIso = getTodayISO()) {
  const weekList = [...(studyPlanWeeks ?? [])].sort((a, b) => a.week_no - b.week_no)
  const knownSessionIds = new Set(weekList.flatMap((week) => (week.sessions ?? []).map((session) => session.id)))
  const questsBySessionId = new Map()
  const orphanQuests = []

  ;(mainQuests ?? []).forEach((quest) => {
    const sessionId = quest.study_plan_session_id

    if (sessionId == null || !knownSessionIds.has(sessionId)) {
      orphanQuests.push(quest)
      return
    }

    const current = questsBySessionId.get(sessionId) ?? []
    current.push(quest)
    questsBySessionId.set(sessionId, current)
  })

  const weeks = weekList.map((week) => {
    const phase = getMainQuestPhaseMeta(week.week_no)
    const isCurrentWeek = todayIso >= toIsoDate(week.week_start) && todayIso <= toIsoDate(week.week_end)

    const sessions = [...(week.sessions ?? [])]
      .sort((a, b) => a.session_no - b.session_no)
      .map((session) => {
        const matches = questsBySessionId.get(session.id) ?? []
        const quest = matches[0] ?? null
        const integrity = getSessionIntegrity(matches)
        const materialItems = uniqueItems([
          ...splitSummaryItems(session.material_summary),
          ...splitSummaryItems(quest?.source),
        ])
        const status = integrity ? 'warning' : quest?.status ?? null
        const statusMeta = getMainQuestStatusMeta(status)
        const isCurrentSession = toIsoDate(session.study_date) === todayIso
        const xpMeta = getSessionXpMeta(quest, integrity)

        return {
          ...session,
          quest,
          duplicateQuestCount: matches.length > 1 ? matches.length : 0,
          integrity,
          materialItems,
          deliverableText: session.deliverable || 'No deliverable yet',
          status: status ?? 'pending',
          statusLabel: integrity?.label ?? statusMeta.label,
          statusTone: integrity?.level ?? statusMeta.tone,
          sourceText: quest?.source || session.material_summary || '',
          taskText: session.task_detail || quest?.details || '',
          skillText: session.skill_summary || quest?.skill_name || '',
          xpMeta,
          isCurrentSession,
        }
      })

    const warningSessions = sessions.filter((session) => session.integrity).length

    return {
      ...week,
      phase,
      isCurrentWeek,
      weekRangeLabel: `${formatDate(week.week_start)} - ${formatDate(week.week_end)}`,
      materials: uniqueItems(splitSummaryItems(week.material_summary)),
      sessions,
      completedSessions: sessions.filter((session) => session.status === 'completed').length,
      warningSessions,
      currentSessionId: sessions.find((session) => session.isCurrentSession)?.id ?? null,
    }
  })

  const currentWeek = weeks.find((week) => week.isCurrentWeek) ?? null
  const defaultOpenWeek = weeks[0] ?? null

  const phases = MAIN_QUEST_PHASES.map((phase) => {
    const phaseWeeks = weeks.filter((week) => week.week_no >= phase.weekStart && week.week_no <= phase.weekEnd)

    return {
      ...phase,
      weeks: phaseWeeks,
      totalWeeks: phaseWeeks.length,
      totalSessions: phaseWeeks.reduce((total, week) => total + week.sessions.length, 0),
      completedSessions: phaseWeeks.reduce((total, week) => total + week.completedSessions, 0),
      warningSessions: phaseWeeks.reduce((total, week) => total + week.warningSessions, 0),
      isCurrentPhase: currentWeek?.phase.code === phase.code,
    }
  })

  const missingSessions = weeks.reduce(
    (total, week) => total + week.sessions.filter((session) => session.integrity?.label === 'Missing quest link').length,
    0,
  )
  const duplicateSessions = weeks.reduce(
    (total, week) => total + week.sessions.filter((session) => session.integrity?.label === 'Duplicate quest link').length,
    0,
  )
  const defaultOpenPhase = phases.find((phase) => phase.weeks.length > 0) ?? null

  return {
    phases,
    totalWeeks: weeks.length,
    totalSessions: weeks.reduce((total, week) => total + week.sessions.length, 0),
    integrity: {
      missingSessions,
      duplicateSessions,
      orphanQuests: orphanQuests.length,
      totalWarnings: missingSessions + duplicateSessions + orphanQuests.length,
    },
    currentWeekNo: currentWeek?.week_no ?? null,
    currentPhaseCode: currentWeek?.phase.code ?? null,
    currentSessionId: currentWeek?.currentSessionId ?? null,
    defaultOpenWeekNo: defaultOpenWeek?.week_no ?? null,
    defaultOpenPhaseCode: defaultOpenPhase?.code ?? null,
  }
}

export function getQuestStatus(quest, todayIso = getTodayISO()) {
  if (quest.completed) return 'completed'

  const diffDays = getCalendarDayDiff(todayIso, quest.quest_date)

  if (diffDays <= 0) return 'pending'
  if (diffDays <= 3) return 'overdue'
  return 'expired'
}

export function getCompletionMode(quest, todayIso = getTodayISO()) {
  if (!quest.completed) return null

  return getCalendarDayDiff(todayIso, quest.quest_date) > 0 ? 'overdue' : 'on_time'
}

export function getQuestEarnedXp(quest, todayIso = getTodayISO()) {
  const mode = getCompletionMode(quest, todayIso)
  if (mode === 'overdue') return Math.ceil(quest.xp * 0.5)
  return quest.xp
}

export function getPlayerLevel(totalXp) {
  return Math.max(1, Math.floor(totalXp / 120) + 1)
}

export function getPlayerRank(totalXp) {
  return PLAYER_RANK_THRESHOLDS.find((item) => totalXp >= item.minXp)?.rank ?? 'F'
}

export function getSkillProgress(xp) {
  const next = SKILL_XP_THRESHOLDS.find((threshold) => threshold > xp) ?? SKILL_XP_THRESHOLDS.at(-1)
  const prev = [...SKILL_XP_THRESHOLDS].reverse().find((threshold) => threshold <= xp) ?? 0

  if (xp >= SKILL_XP_THRESHOLDS.at(-1)) return 100
  return Math.max(0, Math.min(100, Math.round(((xp - prev) / (next - prev)) * 100)))
}

function getCurrentWeekNo(quests, player) {
  const todayIso = getTodayISO()
  const startDate = player?.start_date ? player.start_date : null

  if (startDate && getCalendarDayDiff(todayIso, startDate) >= 0) {
    const diffDays = getCalendarDayDiff(todayIso, startDate)
    return Math.floor(diffDays / 7) + 1
  }

  const firstUpcoming = [...quests]
    .filter((quest) => !quest.completed)
    .sort((a, b) => getCalendarDayOrdinal(a.quest_date) - getCalendarDayOrdinal(b.quest_date))[0]

  return firstUpcoming?.week_no ?? 1
}

function getCurrentPhaseLabel(weekNo) {
  if (weekNo <= 13) return 'Month 1-3 / Foundation'
  if (weekNo <= 26) return 'Month 4-6 / Format Training'
  if (weekNo <= 39) return 'Month 7-9 / Band 6 Push'
  if (weekNo <= 52) return 'Month 10-12 / Partial Tests'
  return 'Month 13-18 / Mock Arena'
}

function getWeeklyPattern(weekNo) {
  return WEEKLY_MISSION_PATTERNS[(Math.max(weekNo, 1) - 1) % WEEKLY_MISSION_PATTERNS.length]
}

function getTodayQuests(quests, currentWeekNo) {
  const todayIso = getTodayISO()
  const todayQuests = quests.filter((quest) => quest.quest_date === todayIso)
  if (todayQuests.length > 0) return todayQuests

  return [...quests]
    .filter((quest) => !quest.completed && quest.week_no === currentWeekNo)
    .sort((a, b) => getCalendarDayOrdinal(a.quest_date) - getCalendarDayOrdinal(b.quest_date))
    .slice(0, 3)
}

function getBacklogQuests(quests) {
  return quests
    .filter((quest) => ['overdue', 'expired'].includes(getQuestStatus(quest)))
    .sort((a, b) => getCalendarDayOrdinal(a.quest_date) - getCalendarDayOrdinal(b.quest_date))
    .slice(0, 6)
}

function buildWeaknessSuggestions(skills, quests) {
  const overdueBySkill = new Map()
  quests.forEach((quest) => {
    const status = getQuestStatus(quest)
    if (status === 'overdue' || status === 'expired') {
      overdueBySkill.set(quest.skill_name, (overdueBySkill.get(quest.skill_name) ?? 0) + 1)
    }
  })

  return skills.flatMap((skill) => {
    const suggestions = []
    const staleDays = skill.last_practiced
      ? getCalendarDayDiff(getTodayISO(), skill.last_practiced)
      : 99

    if (skill.weak_point) {
      suggestions.push({
        id: `${skill.name}-weakness`,
        skill: skill.name,
        title: 'Main weakness reminder',
        detail: skill.weak_point,
        severity: 'medium',
      })
    }

    if (staleDays >= (['Listening', 'Reading', 'Writing', 'Speaking'].includes(skill.name) ? 7 : 5)) {
      suggestions.push({
        id: `${skill.name}-stale`,
        skill: skill.name,
        title: 'Inactive too long',
        detail: `${skill.name} has been inactive for ${staleDays} days. Bring it back into this week's rhythm.`,
        severity: 'high',
      })
    }

    if ((overdueBySkill.get(skill.name) ?? 0) >= 2) {
      suggestions.push({
        id: `${skill.name}-overdue`,
        skill: skill.name,
        title: 'Possible skill avoidance',
        detail: `Multiple ${skill.name} quests are overdue or expired. Prioritize backlog recovery.`,
        severity: 'high',
      })
    }

    return suggestions.slice(0, 2)
  })
}

export function buildDashboardView(summary, quests, checkins) {
  const player = summary?.player ?? {}
  const totalXp = player.total_xp ?? 0
  const currentWeekNo = getCurrentWeekNo(quests, player)
  const todayQuests = getTodayQuests(quests, currentWeekNo)
  const backlogQuests = getBacklogQuests(quests)
  const weekQuests = quests.filter((quest) => quest.week_no === currentWeekNo)
  const weeklyPattern = getWeeklyPattern(currentWeekNo)
  const completedWeekQuests = weekQuests.filter((quest) => quest.completed).length
  const completedToday = todayQuests.filter((quest) => quest.completed).length
  const todayIso = getTodayISO()
  const activeCheckIn = checkins.find((item) => item.checkin_date === todayIso) ?? null
  const startDate = player.start_date ? player.start_date : null
  const hasStarted = startDate ? getCalendarDayDiff(todayIso, startDate) >= 0 : true

  return {
    player: {
      ...player,
      level: getPlayerLevel(totalXp),
      rank: getPlayerRank(totalXp),
      totalXp,
      hasStarted,
      phaseLabel: getCurrentPhaseLabel(currentWeekNo),
      currentWeekNo,
      daysUntilStart: startDate ? Math.max(0, getCalendarDayDiff(startDate, todayIso)) : 0,
    },
    skills: (summary?.skills ?? []).map((skill) => ({
      ...skill,
      progress: getSkillProgress(skill.xp),
      theme: SKILL_THEME[skill.name] ?? { accent: 'cyan', label: 'Skill' },
    })),
    quests: quests.map((quest) => ({
      ...quest,
      status: getQuestStatus(quest),
      completionMode: getCompletionMode(quest),
      earnedXp: getQuestEarnedXp(quest),
    })),
    todayQuests: todayQuests.map((quest) => ({
      ...quest,
      status: getQuestStatus(quest),
      completionMode: getCompletionMode(quest),
      earnedXp: getQuestEarnedXp(quest),
    })),
    backlogQuests: backlogQuests.map((quest) => ({
      ...quest,
      status: getQuestStatus(quest),
      completionMode: getCompletionMode(quest),
      earnedXp: getQuestEarnedXp(quest),
    })),
    weeklyMission: {
      ...weeklyPattern,
      progress: `${completedWeekQuests}/${Math.max(weekQuests.length, 1)}`,
      completedWeekQuests,
      totalWeekQuests: weekQuests.length,
      rewardXp: 50,
    },
    commandDeck: {
      completedToday,
      totalToday: todayQuests.length,
      backlogCount: backlogQuests.length,
      activeCheckIn,
      recentCheckins: checkins.slice(0, 5),
    },
    summary: {
      totalCompletedQuests: summary?.total_completed_quests ?? 0,
      totalQuests: summary?.total_quests ?? 0,
      todayXp: summary?.today_xp ?? 0,
      weekXp: summary?.week_xp ?? 0,
      currentStreak: summary?.current_streak ?? 0,
    },
    badges: summary?.badges ?? [],
    bosses: summary?.boss_battles ?? [],
    suggestions: buildWeaknessSuggestions(summary?.skills ?? [], quests),
  }
}

export function getPlayerXpProgress(totalXp, level = getPlayerLevel(totalXp)) {
  const currentFloor = Math.max(0, (level - 1) * 120)
  const nextLevelXp = level * 120
  const currentXp = Math.max(0, totalXp - currentFloor)
  const neededXp = Math.max(1, nextLevelXp - currentFloor)

  return {
    currentXp,
    nextLevelXp,
    percent: Math.max(0, Math.min(100, Math.round((currentXp / neededXp) * 100))),
    remainingXp: Math.max(0, nextLevelXp - totalXp),
  }
}

export function buildPlayerSnapshot(summaryPlayer = {}, profile = {}) {
  const totalXp = profile.player_xp ?? summaryPlayer.total_xp ?? 0
  const level = profile.player_level ?? summaryPlayer.player_level ?? getPlayerLevel(totalXp)
  const rank = profile.player_rank ?? summaryPlayer.player_rank ?? getPlayerRank(totalXp)

  return {
    displayName: profile.display_name || summaryPlayer.name || 'Hunter',
    title: summaryPlayer.title || 'Quest Runner',
    target: profile.target_overall_band || summaryPlayer.target || '',
    currentLevelLabel: profile.current_estimated_level || summaryPlayer.current_level || '',
    strongestSkill: profile.strongest_skill || '',
    weakestSkill: profile.weakest_skill || '',
    studyDaysPerWeek: profile.study_days_per_week ?? 0,
    sessionMinutes: profile.session_minutes ?? 0,
    miniStudyMinutes: profile.daily_mini_study_minutes ?? 0,
    totalXp,
    level,
    rank,
    currentStreak: profile.current_streak ?? 0,
    bestStreak: profile.best_streak ?? 0,
    shieldCount: profile.shield_count ?? summaryPlayer.shield_count ?? 0,
    shieldRegenProgress: profile.shield_regen_progress ?? 0,
    perfectDayCount: profile.perfect_day_count ?? summaryPlayer.perfect_day_count ?? 0,
    xpProgress: getPlayerXpProgress(totalXp, level),
  }
}

function getPhaseState(code, currentPhaseCode) {
  const currentIndex = MAIN_QUEST_PHASES.findIndex((phase) => phase.code === currentPhaseCode)
  const phaseIndex = MAIN_QUEST_PHASES.findIndex((phase) => phase.code === code)

  if (phaseIndex === -1 || currentIndex === -1) return 'upcoming'
  if (phaseIndex < currentIndex) return 'cleared'
  if (phaseIndex === currentIndex) return 'current'
  return 'upcoming'
}

export function buildRoadmapPhaseTrack(map) {
  if (!map?.phases?.length) return []

  return map.phases.map((phase) => {
    const firstWeek = phase.weeks[0] ?? null
    const lastWeek = phase.weeks.at(-1) ?? null
    const totalSessions = phase.totalSessions || 0
    const progress = totalSessions > 0 ? Math.round((phase.completedSessions / totalSessions) * 100) : 0

    return {
      code: phase.code,
      title: phase.title,
      subtitle: phase.subtitle,
      dateLabel:
        firstWeek && lastWeek
          ? `${formatDate(firstWeek.week_start)} - ${formatDate(lastWeek.week_end)}`
          : `Week ${phase.weekStart}-${phase.weekEnd}`,
      weekLabel: `Week ${phase.weekStart}-${phase.weekEnd}`,
      totalSessions,
      completedSessions: phase.completedSessions,
      progress,
      state: getPhaseState(phase.code, map.currentPhaseCode),
      isCurrent: phase.code === map.currentPhaseCode,
    }
  })
}

export function buildRoadmapBounds(studyPlanWeeks = []) {
  if (!studyPlanWeeks.length) return null

  const orderedWeeks = [...studyPlanWeeks].sort((left, right) => left.week_no - right.week_no)
  const firstWeek = orderedWeeks[0]
  const lastWeek = orderedWeeks.at(-1)

  return {
    startDate: firstWeek?.week_start ?? null,
    endDate: lastWeek?.week_end ?? null,
  }
}

export function buildSuggestionInbox(rankSuggestions = [], weaknessSuggestions = [], skills = []) {
  const skillNameById = new Map(skills.map((skill) => [skill.id, skill.name]))

  const rankItems = rankSuggestions.map((item) => ({
    key: `rank-${item.id}`,
    id: item.id,
    type: 'rank',
    skillId: item.skill_id,
    skillName: skillNameById.get(item.skill_id) || `Skill ${item.skill_id}`,
    title: `Update rank ${item.current_rank} -> ${item.suggested_rank}`,
    detail:
      item.direction === 'up'
        ? 'Suggested rank increase based on the latest test result.'
        : 'Suggested rank adjustment to reflect current ability more accurately.',
    severity: item.direction === 'down' ? 'high' : 'medium',
    createdAt: item.created_at,
    status: item.status,
  }))

  const weaknessItems = weaknessSuggestions.map((item) => ({
    key: `weakness-${item.id}`,
    id: item.id,
    type: 'weakness',
    skillId: item.skill_id,
    skillName: skillNameById.get(item.skill_id) || `Skill ${item.skill_id}`,
    title: item.title,
    detail: item.detail,
    severity: item.severity || 'medium',
    createdAt: item.created_at,
    status: item.status,
  }))

  return [...rankItems, ...weaknessItems]
    .filter((item) => item.status === 'pending')
    .sort((left, right) => new Date(right.createdAt).getTime() - new Date(left.createdAt).getTime())
}

export function filterCertificateRecords(records = []) {
  return records.filter((record) =>
    CERTIFICATE_TYPES.some((type) => record.test_type?.toUpperCase().includes(type)),
  )
}

function normalizeBossState(status = '') {
  const value = String(status).toLowerCase()
  if (['cleared', 'completed', 'won'].includes(value)) return 'cleared'
  if (['active', 'current', 'ongoing'].includes(value)) return 'current'
  if (['underprepared', 'failed', 'lost', 'missed'].includes(value)) return 'locked'
  return 'locked'
}

export function buildBossView(bosses = [], todayIso = getTodayISO()) {
  const orderedBosses = [...bosses].sort(
    (left, right) => getCalendarDayOrdinal(left.battle_date) - getCalendarDayOrdinal(right.battle_date),
  )

  const currentBoss =
    orderedBosses.find((boss) => {
      const state = normalizeBossState(boss.result_status || boss.status)
      return state === 'current' || (state !== 'cleared' && toIsoDate(boss.battle_date) >= todayIso)
    }) ??
    orderedBosses.find((boss) => normalizeBossState(boss.result_status || boss.status) !== 'cleared') ??
    orderedBosses[0] ??
    null

  return {
    currentBoss: currentBoss
      ? {
          ...currentBoss,
          uiStatus: normalizeBossState(currentBoss.result_status || currentBoss.status),
          displayStatus: currentBoss.result_status || currentBoss.status,
        }
      : null,
    timeline: orderedBosses.map((boss) => ({
      ...boss,
      uiStatus: normalizeBossState(boss.result_status || boss.status),
      displayStatus: boss.result_status || boss.status,
    })),
  }
}
