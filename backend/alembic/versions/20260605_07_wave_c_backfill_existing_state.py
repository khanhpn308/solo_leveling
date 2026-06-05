"""backfill wave C existing campaign-scoped state

Revision ID: 20260605_07
Revises: 20260605_06
Create Date: 2026-06-05 22:40:00
"""

from alembic import op


revision = "20260605_07"
down_revision = "20260605_06"
branch_labels = None
depends_on = None


def backfill_daily_slot_code() -> None:
    op.execute(
        """
        UPDATE quests
        SET daily_slot_code = quest_role
        WHERE daily_slot_code IS NULL
          AND session_type = 'Daily Quest'
          AND quest_role IN ('core', 'support', 'mini')
        """
    )


def backfill_quest_typed_links() -> None:
    op.execute(
        """
        UPDATE quests q
        SET error_log_id = tracker_entry_id
        WHERE q.error_log_id IS NULL
          AND q.tracker_type = 'error_log'
          AND q.tracker_entry_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM error_logs e
              WHERE e.id = q.tracker_entry_id
          )
        """
    )
    op.execute(
        """
        UPDATE quests q
        SET writing_entry_id = tracker_entry_id
        WHERE q.writing_entry_id IS NULL
          AND q.tracker_type = 'writing_entry'
          AND q.tracker_entry_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM writing_entries w
              WHERE w.id = q.tracker_entry_id
          )
        """
    )
    op.execute(
        """
        UPDATE quests q
        SET speaking_entry_id = tracker_entry_id
        WHERE q.speaking_entry_id IS NULL
          AND q.tracker_type = 'speaking_entry'
          AND q.tracker_entry_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM speaking_entries s
              WHERE s.id = q.tracker_entry_id
          )
        """
    )
    op.execute(
        """
        UPDATE quests q
        SET mock_test_id = tracker_entry_id
        WHERE q.mock_test_id IS NULL
          AND q.tracker_type = 'mock_test'
          AND q.tracker_entry_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM mock_tests m
              WHERE m.id = q.tracker_entry_id
          )
        """
    )


def backfill_weakness_typed_sources() -> None:
    op.execute(
        """
        UPDATE weakness_suggestions ws
        SET source_test_record_id = source_ref_id
        WHERE ws.source_test_record_id IS NULL
          AND ws.source_type = 'test_record'
          AND ws.source_ref_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM test_records t
              WHERE t.id = ws.source_ref_id
          )
        """
    )
    op.execute(
        """
        UPDATE weakness_suggestions ws
        SET source_mock_test_id = source_ref_id
        WHERE ws.source_mock_test_id IS NULL
          AND ws.source_type = 'mock_test'
          AND ws.source_ref_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM mock_tests m
              WHERE m.id = ws.source_ref_id
          )
        """
    )
    op.execute(
        """
        UPDATE weakness_suggestions ws
        SET source_error_log_id = source_ref_id
        WHERE ws.source_error_log_id IS NULL
          AND ws.source_type = 'error_log'
          AND ws.source_ref_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM error_logs e
              WHERE e.id = ws.source_ref_id
          )
        """
    )
    op.execute(
        """
        UPDATE weakness_suggestions ws
        SET source_quest_id = source_ref_id
        WHERE ws.source_quest_id IS NULL
          AND ws.source_type IN ('quest', 'quest_pattern')
          AND ws.source_ref_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM quests q
              WHERE q.id = ws.source_ref_id
          )
        """
    )


def backfill_campaign_scope() -> None:
    op.execute(
        """
        UPDATE checkins c
        SET campaign_id = (
            SELECT MIN(cp.id)
            FROM campaigns cp
            WHERE cp.start_date <= c.checkin_date
              AND cp.end_date >= c.checkin_date
        )
        WHERE c.campaign_id IS NULL
          AND 1 = (
              SELECT COUNT(*)
              FROM campaigns cp2
              WHERE cp2.start_date <= c.checkin_date
                AND cp2.end_date >= c.checkin_date
          )
        """
    )
    op.execute(
        """
        UPDATE test_records t
        SET campaign_id = (
            SELECT MIN(cp.id)
            FROM campaigns cp
            WHERE cp.player_id = t.player_id
              AND cp.start_date <= t.test_date
              AND cp.end_date >= t.test_date
        )
        WHERE t.campaign_id IS NULL
          AND 1 = (
              SELECT COUNT(*)
              FROM campaigns cp2
              WHERE cp2.player_id = t.player_id
                AND cp2.start_date <= t.test_date
                AND cp2.end_date >= t.test_date
          )
        """
    )
    op.execute(
        """
        UPDATE test_records t
        SET campaign_id = (
            SELECT MIN(cp.id)
            FROM campaigns cp
            WHERE cp.player_id = t.player_id
        )
        WHERE t.campaign_id IS NULL
          AND 1 = (
              SELECT COUNT(*)
              FROM campaigns cp2
              WHERE cp2.player_id = t.player_id
          )
        """
    )
    op.execute(
        """
        UPDATE skill_rank_suggestions s
        JOIN test_records t
          ON t.id = s.source_test_record_id
        SET s.campaign_id = t.campaign_id
        WHERE s.campaign_id IS NULL
          AND t.campaign_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE skill_rank_history h
        JOIN test_records t
          ON t.id = h.source_test_record_id
        SET h.campaign_id = t.campaign_id
        WHERE h.campaign_id IS NULL
          AND t.campaign_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE weakness_suggestions ws
        JOIN test_records t
          ON t.id = ws.source_test_record_id
        SET ws.campaign_id = t.campaign_id
        WHERE ws.campaign_id IS NULL
          AND t.campaign_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE weakness_suggestions ws
        JOIN mock_tests m
          ON m.id = ws.source_mock_test_id
        SET ws.campaign_id = m.campaign_id
        WHERE ws.campaign_id IS NULL
          AND m.campaign_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE weakness_suggestions ws
        JOIN error_logs e
          ON e.id = ws.source_error_log_id
        SET ws.campaign_id = e.campaign_id
        WHERE ws.campaign_id IS NULL
          AND e.campaign_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE weakness_suggestions ws
        JOIN quests q
          ON q.id = ws.source_quest_id
        SET ws.campaign_id = q.campaign_id
        WHERE ws.campaign_id IS NULL
          AND q.campaign_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE weakness_suggestions ws
        SET campaign_id = (
            SELECT MIN(cp.id)
            FROM campaigns cp
            WHERE cp.status = 'active'
        )
        WHERE ws.campaign_id IS NULL
          AND ws.source_type IN ('last_practiced', 'quest_pattern')
          AND 1 = (
              SELECT COUNT(*)
              FROM campaigns cp2
              WHERE cp2.status = 'active'
          )
        """
    )


def seed_campaign_skill_states() -> None:
    op.execute(
        """
        INSERT INTO campaign_skill_states (
            campaign_id,
            skill_id,
            xp,
            `rank`,
            confirmed_rank,
            level,
            streak,
            last_practiced,
            weak_point,
            user_weakness_note,
            last_system_suggestion_at,
            created_at,
            updated_at
        )
        SELECT DISTINCT
            p.active_campaign_id,
            s.id,
            s.xp,
            s.`rank`,
            s.confirmed_rank,
            s.level,
            s.streak,
            s.last_practiced,
            s.weak_point,
            s.user_weakness_note,
            s.last_system_suggestion_at,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        FROM players p
        JOIN skills s
        LEFT JOIN campaign_skill_states css
          ON css.campaign_id = p.active_campaign_id
         AND css.skill_id = s.id
        WHERE p.active_campaign_id IS NOT NULL
          AND css.id IS NULL
        """
    )


def seed_badge_unlocks() -> None:
    op.execute(
        """
        INSERT INTO badge_unlocks (
            player_id,
            campaign_id,
            badge_id,
            source_boss_battle_id,
            unlocked_at
        )
        SELECT
            cp.player_id,
            bb.campaign_id,
            bb.badge_id,
            bb.id,
            COALESCE(bb.cleared_at, CURRENT_TIMESTAMP)
        FROM boss_battles bb
        JOIN campaigns cp
          ON cp.id = bb.campaign_id
        LEFT JOIN badge_unlocks bu
          ON bu.campaign_id = bb.campaign_id
         AND bu.badge_id = bb.badge_id
        WHERE bb.result_status = 'cleared'
          AND bb.badge_id IS NOT NULL
          AND bu.id IS NULL
        """
    )
    op.execute(
        """
        INSERT INTO badge_unlocks (
            player_id,
            campaign_id,
            badge_id,
            source_boss_battle_id,
            unlocked_at
        )
        SELECT
            p.id,
            p.active_campaign_id,
            b.id,
            NULL,
            COALESCE(b.unlocked_at, CURRENT_TIMESTAMP)
        FROM players p
        JOIN badges b
        LEFT JOIN badge_unlocks bu
          ON bu.campaign_id = p.active_campaign_id
         AND bu.badge_id = b.id
        WHERE b.unlocked = TRUE
          AND p.active_campaign_id IS NOT NULL
          AND bu.id IS NULL
          AND 1 = (
              SELECT COUNT(*)
              FROM players p2
              WHERE p2.active_campaign_id IS NOT NULL
          )
          AND 1 = (
              SELECT COUNT(*)
              FROM campaigns cp
              WHERE cp.status = 'active'
          )
        """
    )


def upgrade() -> None:
    backfill_daily_slot_code()
    backfill_quest_typed_links()
    backfill_weakness_typed_sources()
    backfill_campaign_scope()
    seed_campaign_skill_states()
    seed_badge_unlocks()


def downgrade() -> None:
    pass
