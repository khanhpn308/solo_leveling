import test from 'node:test'
import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'

import {
  buildDashboardView,
  buildMainQuestMap,
  getCalendarDayDiff,
  getCompletionMode,
  getQuestEarnedXp,
  getQuestStatus,
  getTodayISO,
} from './dashboard-data.js'

function withMockedNow(isoString, callback) {
  const RealDate = Date

  class MockDate extends RealDate {
    constructor(...args) {
      if (args.length === 0) {
        super(isoString)
        return
      }

      super(...args)
    }

    static now() {
      return new RealDate(isoString).getTime()
    }
  }

  globalThis.Date = MockDate

  try {
    return callback()
  } finally {
    globalThis.Date = RealDate
  }
}

function createSession(id, sessionNo, studyDate, overrides = {}) {
  return {
    id,
    session_no: sessionNo,
    study_date: studyDate,
    deliverable: `Deliverable ${id}`,
    material_summary: 'Cambridge 17; Notebook',
    skill_summary: 'Reading',
    task_detail: `Task ${id}`,
    ...overrides,
  }
}

function runInTimezone(timezone, script) {
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', script], {
    cwd: new URL('..', import.meta.url),
    env: { ...process.env, TZ: timezone },
    encoding: 'utf8',
    timeout: 5000,
  })

  assert.ifError(result.error)
  assert.equal(result.status, 0, result.stderr || result.stdout)
}

test('buildMainQuestMap flags missing, duplicate, and orphan quest links while keeping week/session ordering stable', () => {
  const studyPlanWeeks = [
    {
      week_no: 2,
      week_start: '2026-04-13',
      week_end: '2026-04-19',
      material_summary: 'Week 2 Pack; Week 2 Pack',
      sessions: [
        createSession(202, 2, '2026-04-15', { material_summary: 'Notebook; Cambridge 17' }),
        createSession(201, 1, '2026-04-14'),
        createSession(203, 3, '2026-04-16'),
      ],
    },
    {
      week_no: 1,
      week_start: '2026-04-06',
      week_end: '2026-04-12',
      material_summary: 'Week 1 Pack',
      sessions: [createSession(101, 1, '2026-04-07')],
    },
  ]

  const mainQuests = [
    {
      id: 1,
      study_plan_session_id: 101,
      status: 'completed',
      completed: true,
      earned_xp: 20,
      base_xp: 20,
      reward_claimed: true,
      source: 'Week 1 Pack; Audio Lab',
      details: 'Quest 101',
      skill_name: 'Listening',
    },
    {
      id: 2,
      study_plan_session_id: 201,
      status: 'pending',
      completed: false,
      xp: 25,
      source: 'Cambridge 17; Notebook',
      details: 'Quest 201',
      skill_name: 'Reading',
    },
    {
      id: 3,
      study_plan_session_id: 202,
      status: 'pending',
      completed: false,
      xp: 30,
      source: 'Grammar in Use',
      details: 'Quest 202A',
      skill_name: 'Grammar',
    },
    {
      id: 4,
      study_plan_session_id: 202,
      status: 'pending',
      completed: false,
      xp: 35,
      source: 'Grammar in Use',
      details: 'Quest 202B',
      skill_name: 'Grammar',
    },
    {
      id: 5,
      study_plan_session_id: 999,
      status: 'pending',
      completed: false,
      xp: 40,
      source: 'Orphan Source',
      details: 'Orphan quest',
      skill_name: 'Writing',
    },
  ]

  const questMap = buildMainQuestMap(studyPlanWeeks, mainQuests, '2026-04-15')

  assert.equal(questMap.totalWeeks, 2)
  assert.equal(questMap.totalSessions, 4)
  assert.equal(questMap.currentWeekNo, 2)
  assert.equal(questMap.currentSessionId, 202)
  assert.equal(questMap.defaultOpenWeekNo, 1)
  assert.equal(questMap.defaultOpenPhaseCode, 'P1')
  assert.deepEqual(questMap.integrity, {
    missingSessions: 1,
    duplicateSessions: 1,
    orphanQuests: 1,
    totalWarnings: 3,
  })

  const phaseOne = questMap.phases[0]
  assert.equal(phaseOne.totalWeeks, 2)
  assert.equal(phaseOne.totalSessions, 4)
  assert.equal(phaseOne.completedSessions, 1)
  assert.equal(phaseOne.warningSessions, 2)
  assert.equal(phaseOne.isCurrentPhase, true)

  const [weekOne, weekTwo] = phaseOne.weeks
  assert.deepEqual(
    weekTwo.sessions.map((session) => session.id),
    [201, 202, 203],
  )

  const linkedSession = weekTwo.sessions[0]
  assert.equal(linkedSession.status, 'pending')
  assert.equal(linkedSession.statusTone, 'pending')
  assert.deepEqual(linkedSession.materialItems, ['Cambridge 17', 'Notebook'])
  assert.deepEqual(linkedSession.xpMeta, {
    value: 25,
    label: 'Reward',
    detail: 'Reward XP if completed.',
  })

  const duplicateSession = weekTwo.sessions[1]
  assert.equal(duplicateSession.duplicateQuestCount, 2)
  assert.equal(duplicateSession.status, 'warning')
  assert.equal(duplicateSession.statusLabel, 'Duplicate quest link')
  assert.equal(duplicateSession.statusTone, 'warning')
  assert.equal(duplicateSession.integrity?.detail.includes('Showing the first one for now.'), true)
  assert.deepEqual(duplicateSession.materialItems, ['Notebook', 'Cambridge 17', 'Grammar in Use'])

  const missingSession = weekTwo.sessions[2]
  assert.equal(missingSession.quest, null)
  assert.equal(missingSession.statusLabel, 'Missing quest link')
  assert.deepEqual(missingSession.xpMeta, {
    value: '--',
    label: 'XP unavailable',
    detail: 'Main Quest could not be resolved, so reward and earned XP are unavailable.',
  })

  assert.equal(weekTwo.warningSessions, 2)
  assert.equal(weekTwo.completedSessions, 0)
  assert.equal(weekTwo.currentSessionId, 202)

  const completedSession = weekOne.sessions[0]
  assert.deepEqual(completedSession.xpMeta, {
    value: 20,
    label: 'Earned',
    detail: 'Reward 20 XP secured.',
  })
})

test('daily quest helpers classify pending, overdue, expired, and earned XP consistently', () => {
  const pendingQuest = { quest_date: '2026-04-15', completed: false, xp: 25 }
  const overdueQuest = { quest_date: '2026-04-14', completed: false, xp: 25 }
  const expiredQuest = { quest_date: '2026-04-11', completed: false, xp: 25 }
  const completedTodayQuest = { quest_date: '2026-04-15', completed: true, xp: 25 }
  const completedLateQuest = { quest_date: '2026-04-13', completed: true, xp: 25 }

  assert.equal(getQuestStatus(pendingQuest, '2026-04-15'), 'pending')
  assert.equal(getQuestStatus(overdueQuest, '2026-04-15'), 'expired')
  assert.equal(getQuestStatus(expiredQuest, '2026-04-15'), 'expired')
  assert.equal(getQuestStatus(completedTodayQuest, '2026-04-15'), 'completed')

  assert.equal(getCompletionMode(pendingQuest, '2026-04-15'), null)
  assert.equal(getCompletionMode(completedTodayQuest, '2026-04-15'), 'on_time')
  assert.equal(getCompletionMode(completedLateQuest, '2026-04-15'), 'on_time')

  assert.equal(getQuestEarnedXp(completedTodayQuest, '2026-04-15'), 25)
  assert.equal(getQuestEarnedXp({ ...completedLateQuest, xp: 21 }, '2026-04-15'), 21)
})

test('buildDashboardView derives currentWeekNo, daysUntilStart, and stale skill suggestions from calendar-safe dates', () => {
  const summary = {
    player: {
      total_xp: 240,
      start_date: '2026-04-20',
    },
    skills: [
      { name: 'Listening', xp: 220, last_practiced: '2026-04-08', weak_point: '' },
      { name: 'Grammar', xp: 140, last_practiced: '2026-04-10', weak_point: '' },
    ],
    total_completed_quests: 1,
    total_quests: 3,
    today_xp: 0,
    week_xp: 40,
    current_streak: 2,
    badges: [],
    boss_battles: [],
  }

  const quests = [
    { id: 1, week_no: 3, quest_date: '2026-04-20', completed: false, xp: 30, skill_name: 'Listening' },
    { id: 2, week_no: 2, quest_date: '2026-04-14', completed: false, xp: 25, skill_name: 'Grammar' },
    { id: 3, week_no: 2, quest_date: '2026-04-10', completed: true, xp: 20, skill_name: 'Grammar' },
  ]

  const checkins = [{ checkin_date: '2026-04-15', mood: 'steady' }]

  const view = withMockedNow('2026-04-15T10:30:00', () => buildDashboardView(summary, quests, checkins))

  assert.equal(view.player.currentWeekNo, 2)
  assert.equal(view.player.daysUntilStart, 5)
  assert.equal(view.player.hasStarted, false)
  assert.equal(view.todayQuests.length, 1)
  assert.equal(view.todayQuests[0].quest_date, '2026-04-14')
  assert.equal(view.todayQuests[0].status, 'expired')
  assert.equal(view.commandDeck.activeCheckIn?.mood, 'steady')

  const staleSuggestion = view.suggestions.find((item) => item.id === 'Listening-stale')
  assert.ok(staleSuggestion)
  assert.equal(staleSuggestion.severity, 'high')
  assert.equal(staleSuggestion.detail.includes('7'), true)

  const grammarStaleSuggestion = view.suggestions.find((item) => item.id === 'Grammar-stale')
  assert.ok(grammarStaleSuggestion)
  assert.equal(grammarStaleSuggestion.detail.includes('5'), true)
})

test('calendar day diff ignores DST-shortened elapsed hours', () => {
  assert.equal(getCalendarDayDiff('2026-03-08', '2026-03-07'), 1)
})

test('date logic remains stable in America/Los_Angeles across the DST boundary', () => {
  const script = `
    import assert from 'node:assert/strict';
    import { buildDashboardView, getCalendarDayDiff, getQuestStatus, getTodayISO } from './src/dashboard-data.js';

    const RealDate = Date;
    class MockDate extends RealDate {
      constructor(...args) {
        if (args.length === 0) {
          super('2026-03-09T00:30:00');
          return;
        }
        super(...args);
      }
      static now() {
        return new RealDate('2026-03-09T00:30:00').getTime();
      }
    }

    globalThis.Date = MockDate;

    try {
      assert.equal(getTodayISO(), '2026-03-09');
      assert.equal(getCalendarDayDiff('2026-03-08', '2026-03-07'), 1);
      assert.equal(getQuestStatus({ quest_date: '2026-03-08', completed: false, xp: 20 }), 'expired');
      assert.equal(getQuestStatus({ quest_date: '2026-03-07', completed: false, xp: 20 }), 'expired');
      const view = buildDashboardView(
        {
          player: { total_xp: 0, start_date: '2026-03-02' },
          skills: [{ name: 'Reading', xp: 0, last_practiced: '2026-03-02', weak_point: '' }],
          badges: [],
          boss_battles: [],
        },
        [{ id: 1, week_no: 2, quest_date: '2026-03-09', completed: false, xp: 20, skill_name: 'Reading' }],
        [],
      );
      assert.equal(view.player.currentWeekNo, 2);
      assert.equal(view.player.daysUntilStart, 0);
      assert.equal(view.player.hasStarted, true);
      assert.equal(view.todayQuests[0].quest_date, '2026-03-09');
      assert.ok(view.suggestions.some((item) => item.id === 'Reading-stale'));

      const futureView = buildDashboardView(
        {
          player: { total_xp: 0, start_date: '2026-03-10' },
          skills: [],
          badges: [],
          boss_battles: [],
        },
        [{ id: 2, week_no: 2, quest_date: '2026-03-10', completed: false, xp: 20, skill_name: 'Reading' }],
        [],
      );
      assert.equal(futureView.player.daysUntilStart, 1);
      assert.equal(futureView.player.hasStarted, false);
    } finally {
      globalThis.Date = RealDate;
    }
  `

  runInTimezone('America/Los_Angeles', script)
})
