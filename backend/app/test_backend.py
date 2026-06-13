import os
# Test-only env: app.auth_utils hard-fails without JWT_SECRET_KEY. Must be set
# before importing app.* below. Throwaway values, never used in production.
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("ENABLE_DEV_ENDPOINTS", "true")

import unittest
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.database import Base
from app.models import (
    Player, Campaign, Skill, CampaignSkillState, Badge, BadgeUnlock, CheckIn, Quest,
    BossBattle, SkillXpTransaction, PlayerXpTransaction,
    Account, AccountSession, AccountPreference, PlayerLearningProfile, AccountSecurityEvent,
    RankExamPool, RankExamVersion, RankExamQuestion, RankExamAttempt, SkillRankHistory,
    CollocationCollection, CollocationSection, CollocationTopic, CollocationItem,
    CampaignCollocationLink, PlayerCollocationProgress, CollocationFlashcard,
)
from fastapi.testclient import TestClient
from app.main import app, get_db, get_current_player, get_current_campaign
from app.services import (
    ensure_campaign_skill_states,
    get_campaign_skill_state_map,
    recompute_badges,
    recompute_player_progress,
)

class TestWaveDAndE(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for testing
        from sqlalchemy.pool import StaticPool
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()

        # Seed initial core data (Skills, Badges)
        self.skills = [
            Skill(name="Listening", icon="🎧"),
            Skill(name="Reading", icon="📖"),
            Skill(name="Writing", icon="✍️"),
            Skill(name="Speaking", icon="🗣️"),
            Skill(name="Vocabulary", icon="📔"),
        ]
        self.badges = [
            Badge(name="Vocabulary Hunter", icon="🏆", description="300 Vocabulary XP."),
            Badge(name="Listening Warrior", icon="🎧", description="Reach 500 Listening XP."),
            Badge(name="Error Killer", icon="⚔️", description="Defeat 10 error monsters."),
        ]
        self.db.add_all(self.skills)
        self.db.add_all(self.badges)
        self.db.commit()

        # Create mock player and campaign
        self.player = Player(
            name="Test Player",
            start_date=date.today(),
            total_xp=0,
            setup_completed=True
        )
        self.db.add(self.player)
        self.db.commit()

        self.campaign = Campaign(
            player_id=self.player.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            status="active"
        )
        self.db.add(self.campaign)
        self.db.commit()

        # Link player active campaign
        self.player.active_campaign_id = self.campaign.id
        self.db.commit()

        # Override auth dependencies so routes resolve to this test's player/campaign
        player_ref = self.player
        campaign_ref = self.campaign
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[get_current_player] = lambda: player_ref
        app.dependency_overrides[get_current_campaign] = lambda: campaign_ref
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.pop(get_current_player, None)
        app.dependency_overrides.pop(get_current_campaign, None)
        app.dependency_overrides.pop(get_db, None)
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_campaign_scoped_skill_state(self):
        """Test that campaign-scoped skill states are seeded and managed per campaign."""
        # Seeding skill states for the campaign
        states = ensure_campaign_skill_states(self.db, self.campaign)
        self.assertEqual(len(states), 5)
        for s in states:
            self.assertEqual(s.campaign_id, self.campaign.id)
            self.assertEqual(s.xp, 0)

        # Retrieve map
        state_map = get_campaign_skill_state_map(self.db, self.campaign)
        self.assertIn("Listening", [s.skill.name for s in state_map.values()])

        # Create a second campaign for the same player
        campaign2 = Campaign(
            player_id=self.player.id,
            start_date=date.today() + timedelta(days=91),
            end_date=date.today() + timedelta(days=180),
            status="pending"
        )
        self.db.add(campaign2)
        self.db.commit()

        # Seed second campaign
        states2 = ensure_campaign_skill_states(self.db, campaign2)
        self.assertEqual(len(states2), 5)
        for s in states2:
            self.assertEqual(s.campaign_id, campaign2.id)

        # Modify first campaign's Listening XP
        listening_skill = next(s for s in self.skills if s.name == "Listening")
        listening_state1 = self.db.query(CampaignSkillState).filter_by(campaign_id=self.campaign.id, skill_id=listening_skill.id).first()
        listening_state1.xp = 150
        self.db.commit()

        # Verify second campaign's Listening XP remains 0
        listening_state2 = self.db.query(CampaignSkillState).filter_by(campaign_id=campaign2.id, skill_id=listening_skill.id).first()
        self.assertEqual(listening_state2.xp, 0)
        self.assertEqual(listening_state1.xp, 150)

    def test_badge_unlock_read_path(self):
        """Test badge recomputation and unlocks are scoped to the campaign."""
        state_map = get_campaign_skill_state_map(self.db, self.campaign)
        
        # Initially no badges unlocked
        recompute_badges(self.db, self.player, self.campaign, state_map)
        unlocks = self.db.query(BadgeUnlock).filter_by(campaign_id=self.campaign.id).all()
        self.assertEqual(len(unlocks), 0)

        # Give player 350 Vocabulary XP in campaign skill state
        vocab_skill = next(s for s in self.skills if s.name == "Vocabulary")
        state_map[vocab_skill.id].xp = 350
        self.db.commit()

        # Recompute should unlock "Vocabulary Hunter"
        recompute_badges(self.db, self.player, self.campaign, state_map)
        unlocks = self.db.query(BadgeUnlock).filter_by(campaign_id=self.campaign.id).all()
        self.assertEqual(len(unlocks), 1)
        self.assertEqual(unlocks[0].badge.name, "Vocabulary Hunter")

        # Create a second campaign
        campaign2 = Campaign(
            player_id=self.player.id,
            start_date=date.today() + timedelta(days=91),
            end_date=date.today() + timedelta(days=180),
            status="pending"
        )
        self.db.add(campaign2)
        self.db.commit()
        state_map2 = get_campaign_skill_state_map(self.db, campaign2)

        # Under campaign2, vocab XP is 0, so no badges should unlock
        recompute_badges(self.db, self.player, campaign2, state_map2)
        unlocks2 = self.db.query(BadgeUnlock).filter_by(campaign_id=campaign2.id).all()
        self.assertEqual(len(unlocks2), 0)

    def test_checkin_upsert_behavior(self):
        """Test check-in upserts and campaign-scoped check-in uniqueness."""
        checkin_date = date.today()
        
        # Insert checkin for campaign 1
        checkin1 = CheckIn(
            campaign_id=self.campaign.id,
            checkin_date=checkin_date,
            mood=4,
            energy=4,
            focus=5,
            note="Good day"
        )
        self.db.add(checkin1)
        self.db.commit()

        # Attempting to insert duplicate checkin on same campaign + same date should raise IntegrityError
        checkin_dup = CheckIn(
            campaign_id=self.campaign.id,
            checkin_date=checkin_date,
            mood=3,
            energy=3,
            focus=3,
            note="Duplicate"
        )
        self.db.add(checkin_dup)
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()

        # Insert checkin for campaign 2 on same date should succeed (campaign-scoped checkin uniqueness)
        campaign2 = Campaign(
            player_id=self.player.id,
            start_date=date.today() + timedelta(days=91),
            end_date=date.today() + timedelta(days=180),
            status="pending"
        )
        self.db.add(campaign2)
        self.db.commit()

        checkin2 = CheckIn(
            campaign_id=campaign2.id,
            checkin_date=checkin_date,
            mood=2,
            energy=2,
            focus=2,
            note="Campaign 2 checkin"
        )
        self.db.add(checkin2)
        self.db.commit() # Should succeed without error

        self.assertEqual(self.db.query(CheckIn).count(), 2)

    def test_daily_slot_invariants(self):
        """Test that daily quests have slot uniqueness constraints per campaign."""
        quest_date = date.today()
        listening_skill = next(s for s in self.skills if s.name == "Listening")

        # Create daily quest in slot 'core'
        quest1 = Quest(
            campaign_id=self.campaign.id,
            quest_date=quest_date,
            week_no=1,
            stage="Foundation",
            title="Quest 1",
            skill_id=listening_skill.id,
            source="System",
            details="Listen to podcast",
            session_type="Daily Quest",
            quest_role="core",
            daily_slot_code="core"
        )
        self.db.add(quest1)
        self.db.commit()

        # Creating another quest with same campaign_id, quest_date, and daily_slot_code 'core' should raise IntegrityError
        quest_dup = Quest(
            campaign_id=self.campaign.id,
            quest_date=quest_date,
            week_no=1,
            stage="Foundation",
            title="Quest Duplicate",
            skill_id=listening_skill.id,
            source="System",
            details="Another listen",
            session_type="Daily Quest",
            quest_role="mini",
            daily_slot_code="core" # Duplicate slot code
        )
        self.db.add(quest_dup)
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()

        # Creating quest for different campaign with same date and daily_slot_code 'core' should succeed
        campaign2 = Campaign(
            player_id=self.player.id,
            start_date=date.today() + timedelta(days=91),
            end_date=date.today() + timedelta(days=180),
            status="pending"
        )
        self.db.add(campaign2)
        self.db.commit()

        quest2 = Quest(
            campaign_id=campaign2.id,
            quest_date=quest_date,
            week_no=1,
            stage="Foundation",
            title="Quest 2",
            skill_id=listening_skill.id,
            source="System",
            details="Listen to podcast",
            session_type="Daily Quest",
            quest_role="core",
            daily_slot_code="core"
        )
        self.db.add(quest2)
        self.db.commit() # Should succeed

        self.assertEqual(self.db.query(Quest).count(), 2)

    def test_boss_reward_routing(self):
        """Boss claim with reward_skill_id routes to SkillXpTransaction; a skill-less boss awards nothing (player has no direct XP accrual)."""
        # Get Vocabulary skill
        vocab_skill = next(s for s in self.skills if s.name == "Vocabulary")
        ensure_campaign_skill_states(self.db, self.campaign)

        # 1. Test Skill-specific boss reward routing
        vocab_boss = BossBattle(
            stage="Foundation",
            battle_date=date.today(),
            title="Vocabulary Boss Battle",
            source="System",
            goal="Defeat vocabulary boss",
            status="Cleared",
            campaign_id=self.campaign.id,
            reward_xp=200,
            cleared_at=datetime.utcnow(),
            boss_scope="skill",
            reward_skill_id=vocab_skill.id,
            reward_claimed=False
        )
        self.db.add(vocab_boss)
        self.db.commit()

        # Claim reward via HTTP client
        resp = self.client.post(f"/api/boss-battles/{vocab_boss.id}/claim")
        self.assertEqual(resp.status_code, 200)

        # Reload boss
        self.db.refresh(vocab_boss)
        self.assertTrue(vocab_boss.reward_claimed)
        self.assertIsNotNone(vocab_boss.reward_claimed_at)

        # Check that SkillXpTransaction was created
        skill_tx = self.db.query(SkillXpTransaction).filter_by(
            campaign_id=self.campaign.id,
            skill_id=vocab_skill.id,
            idempotency_key=f"boss_claim:{vocab_boss.id}"
        ).first()
        self.assertIsNotNone(skill_tx)
        self.assertEqual(skill_tx.xp, 200)
        self.assertEqual(skill_tx.transaction_type, "boss")

        # Check that CampaignSkillState XP was increased
        vocab_state = self.db.query(CampaignSkillState).filter_by(
            campaign_id=self.campaign.id,
            skill_id=vocab_skill.id
        ).first()
        self.assertEqual(vocab_state.xp, 200)

        # Verify no PlayerXpTransaction was created for this claim
        player_tx_count = self.db.query(PlayerXpTransaction).count()
        self.assertEqual(player_tx_count, 0)

        # 2. Test Player-scoped boss reward routing (reward_skill_id is None).
        # Per redesign (ielts_xp_policy_rank_quest_spec.md §1.2 / §4): the player
        # never accrues XP directly. A boss with no reward_skill_id awards NOTHING —
        # no PlayerXpTransaction, and player_xp stays the average of the 5 matrix skills.
        player_boss = BossBattle(
            stage="Foundation",
            battle_date=date.today(),
            title="Overall Phase Boss Battle",
            source="System",
            goal="Defeat overall boss",
            status="Cleared",
            campaign_id=self.campaign.id,
            reward_xp=500,
            cleared_at=datetime.utcnow(),
            boss_scope="player",
            reward_skill_id=None,
            reward_claimed=False
        )
        self.db.add(player_boss)
        self.db.commit()

        # Save current player XP (derived from skill average; not a raw accumulator)
        initial_player_xp = self.player.player_xp or 0

        # Claim reward via HTTP client
        resp2 = self.client.post(f"/api/boss-battles/{player_boss.id}/claim")
        self.assertEqual(resp2.status_code, 200)

        # Reload boss — still marked claimed even though no XP is granted
        self.db.refresh(player_boss)
        self.assertTrue(player_boss.reward_claimed)

        # No PlayerXpTransaction is ever created (player has no direct accrual)
        player_tx_count_after = self.db.query(PlayerXpTransaction).count()
        self.assertEqual(player_tx_count_after, 0)

        # Player XP is unchanged: no matrix skill gained XP from a skill-less boss
        self.db.refresh(self.player)
        self.assertEqual(self.player.player_xp, initial_player_xp)

        # Verify no additional SkillXpTransaction was created
        vocab_state_after = self.db.query(CampaignSkillState).filter_by(
            campaign_id=self.campaign.id,
            skill_id=vocab_skill.id
        ).first()
        self.assertEqual(vocab_state_after.xp, 200)

    def test_check_constraints(self):
        """Test that CheckConstraint limits only one tracker for Quests and only one source for WeaknessSuggestions."""
        listening_skill = next(s for s in self.skills if s.name == "Listening")

        # 1. Test Quest only one tracker constraint
        invalid_quest = Quest(
            campaign_id=self.campaign.id,
            quest_date=date.today(),
            week_no=1,
            stage="Foundation",
            title="Invalid Quest",
            skill_id=listening_skill.id,
            source="System",
            details="Invalid Details",
            session_type="Daily Quest",
            quest_role="mini",
            error_log_id=1,
            mock_test_id=1,
        )
        self.db.add(invalid_quest)
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()

        # 2. Test WeaknessSuggestion only one source constraint
        from app.models import WeaknessSuggestion
        invalid_suggestion = WeaknessSuggestion(
            skill_id=listening_skill.id,
            campaign_id=self.campaign.id,
            source_test_record_id=1,
            source_mock_test_id=1,
            title="Invalid Suggestion",
            detail="Details",
            severity="medium",
            status="pending",
        )
        self.db.add(invalid_suggestion)
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()

    def test_vocabulary_anti_farm_cap(self):
        """Test that vocabulary data-entry XP is capped at 40 per word, with mastery score counted separately on top."""
        from app.services import compute_vocabulary_xp
        from app.models import VocabularyItem, VocabularyExample, VocabularyRelation

        # Clear any existing items to run a clean test
        self.db.query(VocabularyItem).filter_by(player_id=self.player.id).delete()
        self.db.query(VocabularyExample).filter_by(player_id=self.player.id).delete()
        self.db.query(VocabularyRelation).filter_by(player_id=self.player.id).delete()
        self.db.commit()

        # 1. Test standard word under the 40 XP cap
        # base (2) + meaning_en (2) + meaning_vi (2) + part_of_speech (2) + pronunciation_ipa (3) = 11 XP
        item1 = VocabularyItem(
            player_id=self.player.id,
            word="diligent",
            meaning_en="showing care and effort in your work or studies",
            meaning_vi="siêng năng, cần cù",
            part_of_speech="adjective",
            pronunciation_ipa="/ˈdɪl.ɪ.dʒənt/",
            mastery_score=0
        )
        self.db.add(item1)
        self.db.commit()

        self.assertEqual(compute_vocabulary_xp(self.db, self.player.id), 11)

        # 2. Test word with examples and relations that goes over the cap
        # We add 6 examples (+5 each = 30 XP) and 1 relation (+5 XP)
        # Total data entry XP: 11 (base) + 30 (examples) + 5 (relation) = 46 XP
        # This should be capped at 40 XP.
        for i in range(6):
            ex = VocabularyExample(
                vocabulary_item_id=item1.id,
                player_id=self.player.id,
                example_sentence=f"Example sentence {i}"
            )
            self.db.add(ex)
        
        relation = VocabularyRelation(
            player_id=self.player.id,
            source_word_id=item1.id,
            relation_type="word_family"
        )
        self.db.add(relation)
        self.db.commit()

        # Cap is 40.
        self.assertEqual(compute_vocabulary_xp(self.db, self.player.id), 40)

        # 3. Test that mastery score is added ON TOP of the 40 XP cap separately.
        # Let's update mastery score to 30. Total should be 40 (capped data-entry) + 30 = 70 XP.
        item1.mastery_score = 30
        self.db.commit()
        self.assertEqual(compute_vocabulary_xp(self.db, self.player.id), 70)

        # Let's update mastery score to 80. Mastery is capped at 50, so total should be 40 + 50 = 90 XP.
        item1.mastery_score = 80
        self.db.commit()
        self.assertEqual(compute_vocabulary_xp(self.db, self.player.id), 90)


class TestAuthEndpoints(unittest.TestCase):
    def setUp(self):
        # Setup memory database for auth tests with StaticPool for multi-threaded sharing
        from sqlalchemy.pool import StaticPool
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()

        # Seed static dependencies (Skills)
        self.skills = [
            Skill(name="Listening", icon="🎧"),
            Skill(name="Reading", icon="📖"),
            Skill(name="Writing", icon="✍️"),
            Skill(name="Speaking", icon="🗣️"),
            Skill(name="Vocabulary", icon="📔"),
        ]
        self.db.add_all(self.skills)
        self.db.commit()

        # FastAPI dependency override
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_register_success(self):
        payload = {
            "email": "user@example.com",
            "password": "testpassword123",
            "display_name": "Test User"
        }
        response = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("ielts_rt", response.cookies)

        # Check database objects created
        account = self.db.query(Account).filter_by(email="user@example.com").first()
        self.assertIsNotNone(account)
        self.assertEqual(account.display_name, "Test User")
        self.assertFalse(account.onboarding_completed)

        player = self.db.query(Player).filter_by(account_id=account.id).first()
        self.assertIsNotNone(player)
        self.assertEqual(player.name, "Test User")

        pref = self.db.query(AccountPreference).filter_by(account_id=account.id).first()
        self.assertIsNotNone(pref)
        self.assertEqual(pref.locale, "vi")

        profile = self.db.query(PlayerLearningProfile).filter_by(player_id=player.id).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.preferred_learning_style, "mixed")

        # Check security event
        event = self.db.query(AccountSecurityEvent).filter_by(account_id=account.id, event_type="register").first()
        self.assertIsNotNone(event)
        self.assertTrue(event.success)

    def test_register_duplicate(self):
        payload = {
            "email": "user@example.com",
            "password": "testpassword123"
        }
        # First registration
        self.client.post("/api/auth/register", json=payload)
        
        # Duplicate registration
        response = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Email already registered")

    def test_login_success(self):
        # Register first
        payload = {
            "email": "user@example.com",
            "password": "testpassword123"
        }
        self.client.post("/api/auth/register", json=payload)

        # Login
        login_payload = {
            "email": "user@example.com",
            "password": "testpassword123"
        }
        response = self.client.post("/api/auth/login", json=login_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("ielts_rt", response.cookies)

        # Check login success security event
        account = self.db.query(Account).filter_by(email="user@example.com").first()
        event = self.db.query(AccountSecurityEvent).filter_by(account_id=account.id, event_type="login_success").first()
        self.assertIsNotNone(event)
        self.assertTrue(event.success)

    def test_login_failed(self):
        # Register first
        payload = {
            "email": "user@example.com",
            "password": "testpassword123"
        }
        self.client.post("/api/auth/register", json=payload)

        # Login with incorrect password
        login_payload = {
            "email": "user@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post("/api/auth/login", json=login_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid email or password")

        # Check login failed security event
        account = self.db.query(Account).filter_by(email="user@example.com").first()
        event = self.db.query(AccountSecurityEvent).filter_by(account_id=account.id, event_type="login_failed").first()
        self.assertIsNotNone(event)
        self.assertFalse(event.success)

    def test_login_locked(self):
        # Register first
        payload = {
            "email": "user@example.com",
            "password": "testpassword123"
        }
        self.client.post("/api/auth/register", json=payload)

        # 5 failed login attempts
        login_payload = {
            "email": "user@example.com",
            "password": "wrongpassword"
        }
        for _ in range(5):
            response = self.client.post("/api/auth/login", json=login_payload)
            self.assertEqual(response.status_code, 401)

        # Check account is locked in DB
        account = self.db.query(Account).filter_by(email="user@example.com").first()
        self.assertEqual(account.status, "locked")
        self.assertIsNotNone(account.locked_until)

        # 6th attempt should return 403 Forbidden
        response = self.client.post("/api/auth/login", json=login_payload)
        self.assertEqual(response.status_code, 403)
        self.assertIn("Account is locked", response.json()["detail"])

    def test_refresh_token(self):
        # Register first
        payload = {
            "email": "user@example.com",
            "password": "testpassword123"
        }
        reg_response = self.client.post("/api/auth/register", json=payload)
        refresh_token = reg_response.cookies.get("ielts_rt").strip('"')

        # Refresh token
        refresh_payload = {
            "refresh_token": refresh_token
        }
        response = self.client.post("/api/auth/refresh", json=refresh_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("ielts_rt", response.cookies)
        self.assertNotEqual(response.cookies.get("ielts_rt").strip('"'), refresh_token)

    def test_refresh_invalid(self):
        # Refresh with fake token
        refresh_payload = {
            "refresh_token": "fake-refresh-token"
        }
        response = self.client.post("/api/auth/refresh", json=refresh_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid or expired refresh token")

    def test_logout(self):
        # Register first
        payload = {
            "email": "user@example.com",
            "password": "testpassword123"
        }
        reg_response = self.client.post("/api/auth/register", json=payload)
        refresh_token = reg_response.cookies.get("ielts_rt").strip('"')

        # Logout
        logout_payload = {
            "refresh_token": refresh_token
        }
        response = self.client.post("/api/auth/logout", json=logout_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "Successfully logged out")

        # Verify session is revoked in DB
        import hashlib
        token_hash = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()
        session = self.db.query(AccountSession).filter_by(refresh_token_hash=token_hash).first()
        self.assertIsNotNone(session)
        self.assertIsNotNone(session.revoked_at)

        # Refreshing with the logged out token should fail
        refresh_payload = {
            "refresh_token": refresh_token
        }
        refresh_response = self.client.post("/api/auth/refresh", json=refresh_payload)
        self.assertEqual(refresh_response.status_code, 401)

    def test_get_me_success(self):
        # Register first
        payload = {
            "email": "user@example.com",
            "password": "testpassword123"
        }
        reg_response = self.client.post("/api/auth/register", json=payload)
        access_token = reg_response.json()["access_token"]

        # Get me
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["account"]["email"], "user@example.com")
        self.assertIsNotNone(data["player"])

    def test_get_me_unauthorized(self):
        # Get me without headers
        response = self.client.get("/api/auth/me")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Missing authorization header")

        # Get me with invalid header
        headers = {
            "Authorization": "Bearer invalidtoken"
        }
        response = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid or expired access token")


class TestOnboardingEndpoints(unittest.TestCase):
    def setUp(self):
        # Setup memory database for onboarding tests with StaticPool for multi-threaded sharing
        from sqlalchemy.pool import StaticPool
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()

        # Seed static dependencies (Skills)
        self.skills = [
            Skill(name="Listening", icon="🎧"),
            Skill(name="Reading", icon="📖"),
            Skill(name="Writing", icon="✍️"),
            Skill(name="Speaking", icon="🗣️"),
            Skill(name="Vocabulary", icon="🧠"),
            Skill(name="Collocation", icon="🔗"),
            Skill(name="Grammar", icon="⚙️"),
        ]
        self.db.add_all(self.skills)
        self.db.commit()

        # FastAPI dependency override
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

        # Register a test user and obtain tokens
        payload = {
            "email": "onboard@example.com",
            "password": "password123",
            "display_name": "Onboard User"
        }
        response = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.access_token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_get_status_initial(self):
        response = self.client.get("/api/onboarding/status", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["onboarding_completed"])
        self.assertFalse(data["has_certificate"])

    def test_get_status_with_certificate(self):
        from app.models import CertificateRecord
        # Find player
        player = self.db.query(Player).first()
        self.assertIsNotNone(player)

        # Create certificate record
        cert = CertificateRecord(
            player_id=player.id,
            certificate_type="IELTS",
            overall_score=6.5,
            listening_score=7.0,
            reading_score=6.5,
            writing_score=6.0,
            speaking_score=6.5,
            input_method="manual",
            status="submitted"
        )
        self.db.add(cert)
        self.db.commit()

        response = self.client.get("/api/onboarding/status", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["onboarding_completed"])
        self.assertTrue(data["has_certificate"])

    def test_activate_campaign_success(self):
        from app.models import CampaignSetting, VocabularySetting, CampaignSkillQuestQuota, Campaign
        
        # Activate campaign
        response = self.client.post("/api/onboarding/activate-campaign", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "Campaign activated successfully")

        # Verify onboarding completed in Account
        account = self.db.query(Account).filter_by(email="onboard@example.com").first()
        self.assertTrue(account.onboarding_completed)
        self.assertIsNotNone(account.onboarding_completed_at)

        # Verify player setup completed
        player = self.db.query(Player).filter_by(account_id=account.id).first()
        self.assertTrue(player.setup_completed)
        self.assertIsNotNone(player.active_campaign_id)

        # Verify campaign setup completed
        campaign = self.db.query(Campaign).filter_by(id=player.active_campaign_id).first()
        self.assertIsNotNone(campaign)
        self.assertTrue(campaign.setup_completed)
        self.assertEqual(campaign.status, "active")

        # Verify campaign setting exists
        setting = self.db.query(CampaignSetting).filter_by(campaign_id=campaign.id).first()
        self.assertIsNotNone(setting)
        self.assertEqual(setting.current_english_level, "B1")

        # Verify vocabulary settings exist
        vocab_setting = self.db.query(VocabularySetting).filter_by(campaign_id=campaign.id).first()
        self.assertIsNotNone(vocab_setting)

        # Verify quest quotas exist
        quotas = self.db.query(CampaignSkillQuestQuota).filter_by(campaign_id=campaign.id).all()
        self.assertTrue(len(quotas) > 0)

        # Verify some quests are generated
        quests = self.db.query(Quest).filter_by(campaign_id=campaign.id).all()
        self.assertTrue(len(quests) > 0)

        # Get status again
        status_response = self.client.get("/api/onboarding/status", headers=self.headers)
        self.assertEqual(status_response.status_code, 200)
        self.assertTrue(status_response.json()["onboarding_completed"])

    def test_activate_campaign_unauthorized(self):
        # Without headers
        response = self.client.post("/api/onboarding/activate-campaign")
        self.assertEqual(response.status_code, 401)

        # Invalid token
        headers = {"Authorization": "Bearer invalid"}
        response = self.client.post("/api/onboarding/activate-campaign", headers=headers)
        self.assertEqual(response.status_code, 401)


class TestCertificateAndSuggestionEndpoints(unittest.TestCase):
    def setUp(self):
        # Setup memory database for onboarding/suggestions tests with StaticPool
        from sqlalchemy.pool import StaticPool
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()

        # Seed static dependencies (Skills)
        self.skills = [
            Skill(name="Listening", icon="🎧"),
            Skill(name="Reading", icon="📖"),
            Skill(name="Writing", icon="✍️"),
            Skill(name="Speaking", icon="🗣️"),
            Skill(name="Vocabulary", icon="🧠"),
            Skill(name="Collocation", icon="🔗"),
            Skill(name="Grammar", icon="⚙️"),
        ]
        self.db.add_all(self.skills)
        self.db.commit()

        # FastAPI dependency override
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

        # Register a test user and obtain tokens
        payload = {
            "email": "cert@example.com",
            "password": "password123",
            "display_name": "Cert User"
        }
        response = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.access_token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_manual_certificate_creation_pre_campaign(self):
        # Submit manual certificate scores before campaign exists
        payload = {
            "overall_score": 6.5,
            "listening_score": 7.0,
            "reading_score": 6.5,
            "writing_score": 6.0,
            "speaking_score": 6.5
        }
        response = self.client.post("/api/certificates/manual", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        cert = response.json()
        self.assertEqual(cert["overall_score"], 6.5)
        self.assertEqual(cert["listening_score"], 7.0)

        # Ensure no suggestions are generated yet (as no campaign exists)
        from app.models import SkillRankSuggestion
        suggestions = self.db.query(SkillRankSuggestion).all()
        self.assertEqual(len(suggestions), 0)

        # Now, activate the campaign
        act_response = self.client.post("/api/onboarding/activate-campaign", headers=self.headers)
        self.assertEqual(act_response.status_code, 200)

        # Ensure suggestions are generated post-campaign activation
        suggestions = self.db.query(SkillRankSuggestion).filter(
            SkillRankSuggestion.source_certificate_record_id != None
        ).all()
        # Should generate suggestions for the 5 matrix skills only (Grammar + Collocation removed from inferred)
        self.assertEqual(len(suggestions), 5)

    def test_manual_certificate_creation_post_campaign(self):
        # 1. Activate campaign first
        act_response = self.client.post("/api/onboarding/activate-campaign", headers=self.headers)
        self.assertEqual(act_response.status_code, 200)

        # 2. Submit manual certificate scores after campaign exists
        payload = {
            "overall_score": 6.0,
            "listening_score": 6.5,
            "reading_score": 6.0,
            "writing_score": 5.5,
            "speaking_score": 6.0
        }
        response = self.client.post("/api/certificates/manual", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)

        # Ensure suggestions are generated immediately
        from app.models import SkillRankSuggestion
        suggestions = self.db.query(SkillRankSuggestion).filter(
            SkillRankSuggestion.source_certificate_record_id != None
        ).all()
        self.assertEqual(len(suggestions), 5)

        # Verify mapping (5 matrix skills only; Grammar + Collocation excluded):
        # Listening (6.5) -> A
        # Reading (6.0) -> B
        # Writing (5.5) -> C
        # Speaking (6.0) -> B
        # Vocabulary (overall 6.0) -> B
        mapped_ranks = {s.skill.name: s.suggested_rank for s in suggestions}
        self.assertEqual(mapped_ranks["Listening"], "A")
        self.assertEqual(mapped_ranks["Reading"], "B")
        self.assertEqual(mapped_ranks["Writing"], "C")
        self.assertEqual(mapped_ranks["Speaking"], "B")
        self.assertEqual(mapped_ranks["Vocabulary"], "B")
        self.assertNotIn("Grammar", mapped_ranks)
        self.assertNotIn("Collocation", mapped_ranks)

        # Get list of certificates
        get_response = self.client.get("/api/certificates", headers=self.headers)
        self.assertEqual(get_response.status_code, 200)
        certs = get_response.json()
        self.assertEqual(len(certs), 1)
        self.assertEqual(certs[0]["overall_score"], 6.0)

    def test_apply_suggestion_direct_promotion(self):
        # Activate campaign first
        self.client.post("/api/onboarding/activate-campaign", headers=self.headers)

        # Submit manual certificate
        payload = {
            "overall_score": 6.5,
            "listening_score": 7.0,
            "reading_score": 6.5,
            "writing_score": 6.0,
            "speaking_score": 6.5
        }
        self.client.post("/api/certificates/manual", json=payload, headers=self.headers)

        # Find suggestion for Listening
        from app.models import SkillRankSuggestion, CampaignSkillState, SkillRankHistory
        listening_skill = self.db.query(Skill).filter_by(name="Listening").first()
        suggestion = self.db.query(SkillRankSuggestion).filter_by(
            skill_id=listening_skill.id,
            status="pending"
        ).first()
        self.assertIsNotNone(suggestion)
        # Verify fetching suggestions works via both endpoints
        get_suggestions_resp = self.client.get("/api/skill-rank-suggestions", headers=self.headers)
        self.assertEqual(get_suggestions_resp.status_code, 200)
        self.assertTrue(len(get_suggestions_resp.json()) > 0)

        # Setup state to have promotion boss pending first to check clean-up
        state = self.db.query(CampaignSkillState).filter_by(skill_id=listening_skill.id).first()
        state.pending_rank = "E"
        state.promotion_status = "boss_required"
        self.db.commit()

        # Apply suggestion
        apply_response = self.client.post(f"/api/skill-rank-suggestions/{suggestion.id}/apply", headers=self.headers)
        self.assertEqual(apply_response.status_code, 200)

        # Verify suggestion status is applied
        suggestion_after = self.db.query(SkillRankSuggestion).filter_by(id=suggestion.id).first()
        self.assertEqual(suggestion_after.status, "applied")

        # Verify state ranks are updated and exam state cleared
        state_after = self.db.query(CampaignSkillState).filter_by(skill_id=listening_skill.id).first()
        self.assertEqual(state_after.confirmed_rank, "S")
        self.assertEqual(state_after.rank, "S") # updated since 'F' -> 'S' is 'up'
        self.assertIsNone(state_after.pending_rank)
        self.assertEqual(state_after.promotion_status, "none")

        # Verify history is logged
        history = self.db.query(SkillRankHistory).filter_by(skill_id=listening_skill.id).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_rank, "F")
        self.assertEqual(history.new_rank, "S")
        self.assertEqual(history.source_certificate_record_id, suggestion.source_certificate_record_id)

    def test_dismiss_suggestion(self):
        # Activate campaign first
        self.client.post("/api/onboarding/activate-campaign", headers=self.headers)

        # Submit manual certificate
        payload = {
            "overall_score": 6.5,
            "listening_score": 7.0,
            "reading_score": 6.5,
            "writing_score": 6.0,
            "speaking_score": 6.5
        }
        self.client.post("/api/certificates/manual", json=payload, headers=self.headers)

        # Find suggestion for Listening
        from app.models import SkillRankSuggestion
        listening_skill = self.db.query(Skill).filter_by(name="Listening").first()
        suggestion = self.db.query(SkillRankSuggestion).filter_by(
            skill_id=listening_skill.id,
            status="pending"
        ).first()
        self.assertIsNotNone(suggestion)

        # Dismiss suggestion
        dismiss_response = self.client.post(f"/api/skill-rank-suggestions/{suggestion.id}/dismiss", headers=self.headers)
        self.assertEqual(dismiss_response.status_code, 200)

        # Verify status
        suggestion_after = self.db.query(SkillRankSuggestion).filter_by(id=suggestion.id).first()
        self.assertEqual(suggestion_after.status, "dismissed")


    def test_patch_player_targets(self):
        # Activate campaign first
        self.client.post("/api/onboarding/activate-campaign", headers=self.headers)

        # PATCH all 5 target bands
        payload = {
            "target_overall_band": "7.0",
            "target_listening_band": "7.5",
            "target_reading_band": "6.5",
            "target_writing_band": "6.0",
            "target_speaking_band": "7.0",
        }
        response = self.client.patch("/api/player/targets", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        profile = response.json()
        self.assertEqual(profile["target_overall_band"], "7.0")
        self.assertEqual(profile["target_listening_band"], "7.5")
        self.assertEqual(profile["target_reading_band"], "6.5")
        self.assertEqual(profile["target_writing_band"], "6.0")
        self.assertEqual(profile["target_speaking_band"], "7.0")

        # PATCH only one field — others must remain unchanged
        response2 = self.client.patch("/api/player/targets", json={"target_overall_band": "8.0"}, headers=self.headers)
        self.assertEqual(response2.status_code, 200)
        profile2 = response2.json()
        self.assertEqual(profile2["target_overall_band"], "8.0")
        self.assertEqual(profile2["target_listening_band"], "7.5")

        # PATCH must never create suggestions
        from app.models import SkillRankSuggestion
        suggestions = self.db.query(SkillRankSuggestion).all()
        self.assertEqual(len(suggestions), 0)


class TestDailyQuestQuotaGenerator(unittest.TestCase):
    def setUp(self):
        from sqlalchemy.pool import StaticPool
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()

        # Seed static dependencies (Skills)
        self.skills = [
            Skill(name="Listening", icon="🎧"),
            Skill(name="Reading", icon="📖"),
            Skill(name="Writing", icon="✍️"),
            Skill(name="Speaking", icon="🗣️"),
            Skill(name="Vocabulary", icon="🧠"),
            Skill(name="Collocation", icon="🔗"),
            Skill(name="Grammar", icon="⚙️"),
        ]
        self.db.add_all(self.skills)
        self.db.commit()

        # FastAPI dependency override
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

        # Register a test user
        payload = {
            "email": "quota@example.com",
            "password": "password123",
            "display_name": "Quota User"
        }
        response = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.access_token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_default_quotas_generation(self):
        # 1. Activate campaign
        response = self.client.post("/api/onboarding/activate-campaign", headers=self.headers)
        self.assertEqual(response.status_code, 200)

        # 2. Check total daily quests generated
        from app.models import Quest, Campaign
        campaign = self.db.query(Campaign).first()
        self.assertIsNotNone(campaign)

        # Check total daily quests for start_date
        start_date = campaign.start_date
        daily_quests = self.db.query(Quest).filter(
            Quest.campaign_id == campaign.id,
            Quest.quest_date == start_date,
            Quest.session_type == "Daily Quest"
        ).all()

        # Vocabulary (2) + Reading (1) + Listening (1) + Grammar (2) + Collocation (1) + Writing (1) + Speaking (1) = 9 quests
        self.assertEqual(len(daily_quests), 9)

        # Verify skill distribution
        skill_counts = {}
        for q in daily_quests:
            skill_counts[q.skill.name] = skill_counts.get(q.skill.name, 0) + 1
        self.assertEqual(skill_counts.get("Vocabulary", 0), 2)  # Flashcard Gate, Codex Entry
        self.assertEqual(skill_counts.get("Reading", 0), 1)     # Reading Daily
        self.assertEqual(skill_counts.get("Listening", 0), 1)    # Listening Daily
        self.assertEqual(skill_counts.get("Grammar", 0), 2)      # Grammar Review, Grammar Exercise
        self.assertEqual(skill_counts.get("Collocation", 0), 1)  # Collocation Forge
        self.assertEqual(skill_counts.get("Writing", 0), 1)      # Writing Daily
        self.assertEqual(skill_counts.get("Speaking", 0), 1)      # Speaking Daily

    def test_custom_quotas_generation(self):
        # 1. Activate campaign
        self.client.post("/api/onboarding/activate-campaign", headers=self.headers)

        # 2. Clear existing daily quests to regenerate
        from app.models import Quest, Campaign, CampaignSkillQuestQuota, Skill
        campaign = self.db.query(Campaign).first()
        self.db.query(Quest).filter(
            Quest.campaign_id == campaign.id,
            Quest.session_type == "Daily Quest"
        ).delete()
        self.db.commit()

        # 3. Modify quotas
        # Set Vocabulary to 4 (should generate vocab_flashcard, vocab_codex, vocab_collocation)
        vocab_skill = self.db.query(Skill).filter_by(name="Vocabulary").first()
        vocab_quota = self.db.query(CampaignSkillQuestQuota).filter_by(campaign_id=campaign.id, skill_id=vocab_skill.id).first()
        vocab_quota.daily_quota = 4

        # Set Writing to 1
        writing_skill = self.db.query(Skill).filter_by(name="Writing").first()
        writing_quota = self.db.query(CampaignSkillQuestQuota).filter_by(campaign_id=campaign.id, skill_id=writing_skill.id).first()
        writing_quota.daily_quota = 1
        writing_quota.is_active = True

        # Set Listening to inactive
        listening_skill = self.db.query(Skill).filter_by(name="Listening").first()
        listening_quota = self.db.query(CampaignSkillQuestQuota).filter_by(campaign_id=campaign.id, skill_id=listening_skill.id).first()
        listening_quota.is_active = False

        self.db.commit()

        # 4. Regenerate daily quests
        from app.seed import ensure_quest_instances, ensure_roadmap_phases, ensure_templates, ensure_materials
        from app.models import StudyMaterial, RoadmapPhase
        skill_by_name = {s.name: s for s in self.db.query(Skill).all()}
        material_by_title = {m.title: m for m in self.db.query(StudyMaterial).all()}
        phase_by_code = {f"phase-{p.id}": p for p in self.db.query(RoadmapPhase).filter_by(campaign_id=campaign.id).all()}
        template_by_title = ensure_templates(self.db, skill_by_name, phase_by_code, material_by_title)

        ensure_quest_instances(self.db, campaign, skill_by_name, template_by_title, phase_by_code)
        self.db.commit()

        # 5. Check daily quests generated for start_date
        daily_quests = self.db.query(Quest).filter(
            Quest.campaign_id == campaign.id,
            Quest.quest_date == campaign.start_date,
            Quest.session_type == "Daily Quest"
        ).all()

        skill_counts = {}
        for q in daily_quests:
            skill_counts[q.skill.name] = skill_counts.get(q.skill.name, 0) + 1

        self.assertEqual(skill_counts.get("Vocabulary", 0), 2)  # Flashcard Gate, Codex Entry
        self.assertEqual(skill_counts.get("Collocation", 0), 1) # Collocation Forge
        self.assertEqual(skill_counts.get("Writing", 0), 1)
        self.assertEqual(skill_counts.get("Listening", 0), 0)

        # Verify vocab slot codes (should not include vocab_error)
        vocab_slots = {q.daily_slot_code for q in daily_quests if q.daily_slot_code in {"vocab_flashcard", "vocab_codex", "vocab_collocation"}}
        self.assertEqual(vocab_slots, {"vocab_flashcard", "vocab_codex", "vocab_collocation"})

    def test_preference_ordering_rotation(self):
        # 1. Activate campaign
        self.client.post("/api/onboarding/activate-campaign", headers=self.headers)

        # 2. Clear existing daily quests to regenerate
        from app.models import Quest, Campaign, CampaignSkillQuestQuota, Skill
        campaign = self.db.query(Campaign).first()
        self.db.query(Quest).filter(
            Quest.campaign_id == campaign.id,
            Quest.session_type == "Daily Quest"
        ).delete()
        self.db.commit()

        # 3. Modify Vocabulary quota to set daily_quota = 2 and preferred_activity_types
        vocab_skill = self.db.query(Skill).filter_by(name="Vocabulary").first()
        vocab_quota = self.db.query(CampaignSkillQuestQuota).filter_by(campaign_id=campaign.id, skill_id=vocab_skill.id).first()
        vocab_quota.daily_quota = 2
        vocab_quota.preferred_activity_types = ["codex_create", "flashcard_review"]
        self.db.commit()

        # 4. Regenerate daily quests
        from app.seed import ensure_quest_instances, ensure_roadmap_phases, ensure_templates, ensure_materials
        from app.models import StudyMaterial, RoadmapPhase
        skill_by_name = {s.name: s for s in self.db.query(Skill).all()}
        material_by_title = {m.title: m for m in self.db.query(StudyMaterial).all()}
        phase_by_code = {f"phase-{p.id}": p for p in self.db.query(RoadmapPhase).filter_by(campaign_id=campaign.id).all()}
        template_by_title = ensure_templates(self.db, skill_by_name, phase_by_code, material_by_title)

        ensure_quest_instances(self.db, campaign, skill_by_name, template_by_title, phase_by_code)
        self.db.commit()

        # 5. Check Vocabulary daily quests for start_date
        vocab_quests = self.db.query(Quest).filter(
            Quest.campaign_id == campaign.id,
            Quest.quest_date == campaign.start_date,
            Quest.session_type == "Daily Quest",
            Quest.skill_id == vocab_skill.id
        ).order_by(Quest.id).all()

        # Quota is 2, so exactly 2 quests should be generated
        self.assertEqual(len(vocab_quests), 2)

        # Codex Entry (vocab_codex) should be first because "codex_create" was first in preference
        # Memory Gate (vocab_flashcard) should be second because "flashcard_review" was second
        slot_codes = [q.daily_slot_code for q in vocab_quests]
        self.assertEqual(slot_codes, ["vocab_codex", "vocab_flashcard"])

    def test_nine_daily_slots_generation_and_routing(self):
        # 1. Activate campaign
        self.client.post("/api/onboarding/activate-campaign", headers=self.headers)

        from app.models import Quest, Campaign, CampaignSkillState, Skill
        campaign = self.db.query(Campaign).first()

        # 2. Retrieve generated quests
        quests = self.db.query(Quest).filter_by(
            campaign_id=campaign.id,
            quest_date=campaign.start_date,
            session_type="Daily Quest"
        ).all()

        # 3. Assert exactly 9 quests
        self.assertEqual(len(quests), 9)

        # 4. Check base_xp for each slot code
        slot_xps = {q.daily_slot_code: q.base_xp for q in quests}
        self.assertEqual(slot_xps.get("vocab_flashcard"), 4)
        self.assertEqual(slot_xps.get("vocab_codex"), 5)
        self.assertEqual(slot_xps.get("vocab_collocation"), 5)
        self.assertEqual(slot_xps.get("listening"), 10)
        self.assertEqual(slot_xps.get("reading"), 10)
        self.assertEqual(slot_xps.get("writing"), 12)
        self.assertEqual(slot_xps.get("speaking"), 12)
        self.assertEqual(slot_xps.get("grammar_review"), 5)
        self.assertEqual(slot_xps.get("grammar_exercise"), 7)

        # 5. Complete and claim a Grammar Review quest
        grammar_review_quest = next(q for q in quests if q.daily_slot_code == "grammar_review")
        grammar_review_quest.completed = True
        grammar_review_quest.status = "completed"
        grammar_review_quest.earned_xp = grammar_review_quest.base_xp
        self.db.commit()

        resp = self.client.post(f"/api/quests/{grammar_review_quest.id}/claim", headers=self.headers)
        self.assertEqual(resp.status_code, 200)

        # 6. Complete and claim a Collocation Forge quest
        collocation_quest = next(q for q in quests if q.daily_slot_code == "vocab_collocation")
        collocation_quest.completed = True
        collocation_quest.status = "completed"
        collocation_quest.earned_xp = collocation_quest.base_xp
        self.db.commit()

        resp = self.client.post(f"/api/quests/{collocation_quest.id}/claim", headers=self.headers)
        self.assertEqual(resp.status_code, 200)

        # 7. Verify routing to parent matrix skills (Grammar -> Writing, Collocation -> Vocabulary)
        self.db.expire_all()
        writing_skill = self.db.query(Skill).filter_by(name="Writing").first()
        writing_state = self.db.query(CampaignSkillState).filter_by(campaign_id=campaign.id, skill_id=writing_skill.id).first()
        # Writing Daily was not completed, so Writing XP should come entirely from Grammar Review (+5 XP)
        self.assertEqual(writing_state.xp, 5)

        vocab_skill = self.db.query(Skill).filter_by(name="Vocabulary").first()
        vocab_state = self.db.query(CampaignSkillState).filter_by(campaign_id=campaign.id, skill_id=vocab_skill.id).first()
        # Collocation Forge is completed (+5 XP) and vocab_xp (based on empty vocabulary list) is 0
        self.assertEqual(vocab_state.xp, 5)


class TestRankExamPhase9(unittest.TestCase):
    """Integration tests for Phase 9: Rank Boss exam flow, XP block, retry limit, and XP penalty."""

    def setUp(self):
        from sqlalchemy.pool import StaticPool
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()

        self.skills = [
            Skill(name="Listening", icon="🎧"),
            Skill(name="Reading", icon="📖"),
            Skill(name="Writing", icon="✍️"),
            Skill(name="Speaking", icon="🗣️"),
            Skill(name="Vocabulary", icon="🧠"),
            Skill(name="Collocation", icon="🔗"),
            Skill(name="Grammar", icon="⚙️"),
        ]
        self.db.add_all(self.skills)
        self.db.commit()

        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

        # Register and activate campaign
        reg = self.client.post("/api/auth/register", json={
            "email": "ranktest@example.com",
            "password": "password123",
            "display_name": "Rank Tester",
        })
        self.assertEqual(reg.status_code, 200)
        self.access_token = reg.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        self.client.post("/api/onboarding/activate-campaign", headers=self.headers)

        # Grab skill and campaign references (seed.py populates pools via activate-campaign)
        from app.models import Campaign, RankExamPool, RankExamVersion, RankExamQuestion
        self.campaign = self.db.query(Campaign).first()
        self.vocab_skill = self.db.query(Skill).filter_by(name="Vocabulary").first()

        # Use the pool seeded by activate-campaign (Vocabulary F→E)
        self.pool = self.db.query(RankExamPool).filter_by(
            skill_id=self.vocab_skill.id,
            from_rank="F",
            to_rank="E",
            is_active=True,
        ).first()
        if not self.pool:
            # Seed a minimal pool if seed.py didn't create one (failsafe)
            self.pool = RankExamPool(
                skill_id=self.vocab_skill.id,
                from_rank="F",
                to_rank="E",
                title="Vocabulary F->E",
                pass_percent=80,
                default_time_limit_minutes=30,
                max_attempts_per_day=2,
                xp_threshold=500,
                is_active=True,
            )
            self.db.add(self.pool)
            self.db.flush()
            self.version = RankExamVersion(
                pool_id=self.pool.id,
                title="Version 1",
                version_code="v1",
                total_questions=2,
                total_points=2,
                difficulty="normal",
                is_active=True,
            )
            self.db.add(self.version)
            self.db.flush()
            self.db.add(RankExamQuestion(
                exam_version_id=self.version.id,
                question_type="multiple_choice",
                prompt="What does 'abundant' mean?",
                options_json=["plentiful", "scarce", "limited"],
                correct_answer_json="plentiful",
                points=1,
                order_index=0,
            ))
            self.db.add(RankExamQuestion(
                exam_version_id=self.version.id,
                question_type="multiple_choice",
                prompt="What does 'acquire' mean?",
                options_json=["obtain", "lose", "avoid"],
                correct_answer_json="obtain",
                points=1,
                order_index=1,
            ))
            self.db.commit()
        else:
            self.version = self.db.query(RankExamVersion).filter_by(
                pool_id=self.pool.id,
                is_active=True,
            ).first()

        # Cache correct answers from actual questions for use in submit tests
        self.questions = self.db.query(RankExamQuestion).filter_by(
            exam_version_id=self.version.id,
        ).order_by(RankExamQuestion.order_index).all()

        # Put vocab skill into eligible state
        self.vocab_state = self.db.query(CampaignSkillState).filter_by(
            campaign_id=self.campaign.id,
            skill_id=self.vocab_skill.id,
        ).first()
        self.vocab_state.xp = 600
        self.vocab_state.confirmed_rank = "F"
        self.vocab_state.pending_rank = "E"
        self.vocab_state.promotion_status = "eligible"
        self.db.commit()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    # ------------------------------------------------------------------
    # unlock endpoint
    # ------------------------------------------------------------------

    def test_unlock_transitions_eligible_to_boss_required(self):
        resp = self.client.post("/api/rank-exams/unlock", json={"skill_id": self.vocab_skill.id}, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.db.refresh(self.vocab_state)
        self.assertEqual(self.vocab_state.promotion_status, "boss_required")

    def test_unlock_fails_when_not_eligible(self):
        self.vocab_state.promotion_status = "none"
        self.db.commit()
        resp = self.client.post("/api/rank-exams/unlock", json={"skill_id": self.vocab_skill.id}, headers=self.headers)
        self.assertEqual(resp.status_code, 400)

    def test_unlock_fails_when_already_boss_required(self):
        self.vocab_state.promotion_status = "boss_required"
        self.db.commit()
        resp = self.client.post("/api/rank-exams/unlock", json={"skill_id": self.vocab_skill.id}, headers=self.headers)
        self.assertEqual(resp.status_code, 400)

    # ------------------------------------------------------------------
    # start endpoint
    # ------------------------------------------------------------------

    def _unlock(self):
        self.client.post("/api/rank-exams/unlock", json={"skill_id": self.vocab_skill.id}, headers=self.headers)
        self.db.refresh(self.vocab_state)

    def test_start_creates_attempt_and_sets_in_progress(self):
        self._unlock()
        resp = self.client.post("/api/rank-exams/start", json={"skill_id": self.vocab_skill.id}, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("attempt_id", data)
        self.assertEqual(data["from_rank"], "F")
        self.assertEqual(data["to_rank"], "E")
        self.assertGreaterEqual(len(data["questions"]), 1)
        self.db.refresh(self.vocab_state)
        self.assertEqual(self.vocab_state.promotion_status, "in_progress")

    def test_start_fails_when_not_boss_required(self):
        # still eligible, not unlocked
        resp = self.client.post("/api/rank-exams/start", json={"skill_id": self.vocab_skill.id}, headers=self.headers)
        self.assertEqual(resp.status_code, 400)

    def test_start_enforces_two_per_day_cap(self):
        from app.models import RankExamAttempt as REA
        # Seed 2 already-started attempts today
        for _ in range(2):
            self.db.add(REA(
                campaign_id=self.campaign.id,
                skill_id=self.vocab_skill.id,
                from_rank="F",
                to_rank="E",
                pool_id=self.pool.id,
                exam_version_id=self.version.id,
                status="failed",
                total_points=2,
                pass_percent=80,
                time_limit_minutes=30,
                started_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=30),
            ))
        self.db.commit()
        self._unlock()
        resp = self.client.post("/api/rank-exams/start", json={"skill_id": self.vocab_skill.id}, headers=self.headers)
        self.assertEqual(resp.status_code, 429)

    # ------------------------------------------------------------------
    # get attempt endpoint
    # ------------------------------------------------------------------

    def test_get_attempt(self):
        self._unlock()
        start_resp = self.client.post("/api/rank-exams/start", json={"skill_id": self.vocab_skill.id}, headers=self.headers)
        attempt_id = start_resp.json()["attempt_id"]
        resp = self.client.get(f"/api/rank-exams/{attempt_id}", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], attempt_id)
        self.assertEqual(resp.json()["status"], "in_progress")

    def test_get_attempt_not_found(self):
        resp = self.client.get("/api/rank-exams/99999", headers=self.headers)
        self.assertEqual(resp.status_code, 404)

    # ------------------------------------------------------------------
    # submit: pass
    # ------------------------------------------------------------------

    def _start_exam(self):
        self._unlock()
        resp = self.client.post("/api/rank-exams/start", json={"skill_id": self.vocab_skill.id}, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        return resp.json()

    def _correct_answers(self, exam):
        """Build all-correct answers list using actual questions from the DB."""
        return [
            {"question_id": q["id"], "answer_json": self.questions[i].correct_answer_json}
            for i, q in enumerate(exam["questions"])
            if i < len(self.questions)
        ]

    def test_submit_pass_promotes_rank(self):
        exam = self._start_exam()
        answers = self._correct_answers(exam)
        resp = self.client.post(f"/api/rank-exams/{exam['attempt_id']}/submit", json={"answers": answers}, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["passed"])
        self.assertGreaterEqual(data["score_percent"], 80.0)
        self.assertEqual(data["confirmed_rank"], "E")
        self.db.refresh(self.vocab_state)
        self.assertEqual(self.vocab_state.confirmed_rank, "E")
        self.assertEqual(self.vocab_state.promotion_status, "none")
        self.assertIsNone(self.vocab_state.pending_rank)

    def test_submit_pass_logs_rank_history(self):
        exam = self._start_exam()
        answers = self._correct_answers(exam)
        self.client.post(f"/api/rank-exams/{exam['attempt_id']}/submit", json={"answers": answers}, headers=self.headers)
        history = self.db.query(SkillRankHistory).filter_by(
            skill_id=self.vocab_skill.id,
            campaign_id=self.campaign.id,
        ).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_rank, "F")
        self.assertEqual(history.new_rank, "E")

    # ------------------------------------------------------------------
    # submit: fail, first attempt → back to boss_required
    # ------------------------------------------------------------------

    def test_submit_fail_first_attempt_returns_to_boss_required(self):
        exam = self._start_exam()
        answers = [{"question_id": q["id"], "answer_json": "wrong"} for q in exam["questions"]]
        resp = self.client.post(f"/api/rank-exams/{exam['attempt_id']}/submit", json={"answers": answers}, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()["passed"])
        self.db.refresh(self.vocab_state)
        self.assertEqual(self.vocab_state.promotion_status, "boss_required")

    # ------------------------------------------------------------------
    # submit: fail second attempt → -50 XP penalty → eligible
    # ------------------------------------------------------------------

    def test_submit_fail_second_attempt_applies_penalty_and_resets_eligible(self):
        from app.models import RankExamAttempt as REA
        # Pre-seed one failed attempt today so this submit is the 2nd
        self.db.add(REA(
            campaign_id=self.campaign.id,
            skill_id=self.vocab_skill.id,
            from_rank="F",
            to_rank="E",
            pool_id=self.pool.id,
            exam_version_id=self.version.id,
            status="failed",
            total_points=2,
            pass_percent=80,
            time_limit_minutes=30,
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=30),
        ))
        self.db.commit()

        exam = self._start_exam()
        answers = [
            {"question_id": q["id"], "answer_json": "wrong"}
            for q in exam["questions"]
        ]
        resp = self.client.post(f"/api/rank-exams/{exam['attempt_id']}/submit", json={"answers": answers}, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()["passed"])
        self.db.expire_all()
        state_after = self.db.query(CampaignSkillState).filter_by(
            campaign_id=self.campaign.id, skill_id=self.vocab_skill.id,
        ).first()
        self.assertEqual(state_after.promotion_status, "eligible")
        # Penalty applied: xp after recompute is max(0, recomputed_xp - 50)
        # In test: no quests claimed → recomputed_xp = 0 → penalty floored at 0
        self.assertGreaterEqual(state_after.xp, 0)

    def test_xp_penalty_floored_at_zero(self):
        from app.models import RankExamAttempt as REA
        # Set XP below 50 to test floor
        self.vocab_state.xp = 30
        self.db.commit()

        self.db.add(REA(
            campaign_id=self.campaign.id,
            skill_id=self.vocab_skill.id,
            from_rank="F",
            to_rank="E",
            pool_id=self.pool.id,
            exam_version_id=self.version.id,
            status="failed",
            total_points=2,
            pass_percent=80,
            time_limit_minutes=30,
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=30),
        ))
        self.db.commit()

        exam = self._start_exam()
        answers = [{"question_id": q["id"], "answer_json": "wrong"} for q in exam["questions"]]
        self.client.post(f"/api/rank-exams/{exam['attempt_id']}/submit", json={"answers": answers}, headers=self.headers)
        self.db.refresh(self.vocab_state)
        self.assertEqual(self.vocab_state.xp, 0)  # floor, not negative

    # ------------------------------------------------------------------
    # XP block on quest claim
    # ------------------------------------------------------------------

    def test_quest_claim_suppresses_xp_when_boss_required(self):
        from app.models import Quest
        self.vocab_state.promotion_status = "boss_required"
        self.vocab_state.xp = 0
        self.db.commit()

        quest = Quest(
            quest_date=date.today(),
            week_no=1,
            stage="Foundation",
            title="Vocab Quest",
            skill_id=self.vocab_skill.id,
            source="Test",
            details="Test vocab quest",
            xp=20,
            base_xp=20,
            earned_xp=20,
            completed=True,
            reward_claimed=False,
            session_type="Daily Quest",
            campaign_id=self.campaign.id,
            status="completed",
            quest_role="mini",
        )
        self.db.add(quest)
        self.db.commit()

        resp = self.client.post(f"/api/quests/{quest.id}/claim", headers=self.headers)
        self.assertEqual(resp.status_code, 200)

        # XP must NOT increase — block active
        self.db.expire_all()
        state_after = self.db.query(CampaignSkillState).filter_by(
            campaign_id=self.campaign.id, skill_id=self.vocab_skill.id,
        ).first()
        self.assertEqual(state_after.xp, 0)

    def test_quest_claim_awards_xp_normally_when_eligible(self):
        from app.models import Quest
        self.vocab_state.promotion_status = "eligible"
        self.vocab_state.xp = 0
        self.db.commit()

        quest = Quest(
            quest_date=date.today(),
            week_no=1,
            stage="Foundation",
            title="Vocab Quest",
            skill_id=self.vocab_skill.id,
            source="Test",
            details="Test vocab quest",
            xp=20,
            base_xp=20,
            earned_xp=20,
            completed=True,
            reward_claimed=False,
            session_type="Daily Quest",
            campaign_id=self.campaign.id,
            status="completed",
            quest_role="mini",
            reward_skill_id=self.vocab_skill.id,
        )
        self.db.add(quest)
        self.db.commit()

        resp = self.client.post(f"/api/quests/{quest.id}/claim", headers=self.headers)
        self.assertEqual(resp.status_code, 200)

        # XP must increase when eligible (not blocked)
        self.db.expire_all()
        state_after = self.db.query(CampaignSkillState).filter_by(
            campaign_id=self.campaign.id,
            skill_id=self.vocab_skill.id,
        ).first()
        self.assertGreater(state_after.xp, 0)

    def test_double_submit_rejected(self):
        exam = self._start_exam()
        answers = self._correct_answers(exam)
        self.client.post(f"/api/rank-exams/{exam['attempt_id']}/submit", json={"answers": answers}, headers=self.headers)
        # Second submit same attempt must be rejected
        resp = self.client.post(f"/api/rank-exams/{exam['attempt_id']}/submit", json={"answers": answers}, headers=self.headers)
        self.assertEqual(resp.status_code, 400)


class TestCollocationMasterData(unittest.TestCase):
    def setUp(self):
        from sqlalchemy.pool import StaticPool
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()

        # Seed skills
        self.skills = [
            Skill(name="Vocabulary", icon="📔"),
            Skill(name="Listening", icon="🎧"),
            Skill(name="Reading", icon="📖"),
            Skill(name="Writing", icon="✍️"),
            Skill(name="Speaking", icon="🗣️"),
        ]
        self.db.add_all(self.skills)
        self.db.commit()

        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

        # Register user and activate campaign
        payload = {
            "email": "colloc@example.com",
            "password": "password123",
            "display_name": "Colloc User"
        }
        resp = self.client.post("/api/auth/register", json=payload)
        self.access_token = resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

        # Activate campaign
        self.client.post("/api/onboarding/activate-campaign", headers=self.headers)
        
        # Get player and campaign
        self.player = self.db.query(Player).first()
        self.campaign = self.db.query(Campaign).first()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_collocation_flow(self):
        # Clear existing links to keep test isolated
        self.db.query(CampaignCollocationLink).delete()
        self.db.commit()

        # 1. Create a collection
        collection_payload = {
            "code": "eciu-inter",
            "title": "English Collocations in Use",
            "description": "Intermediate collocations",
            "source_book": "Cambridge",
            "level": "Intermediate",
            "is_active": True
        }
        resp = self.client.post("/api/collocation-collections", json=collection_payload)
        self.assertEqual(resp.status_code, 200)
        collection_id = resp.json()["id"]

        # 2. Add Section, Topic, and Items directly to DB
        section = CollocationSection(collection_id=collection_id, title="Section 1", section_order=1)
        self.db.add(section)
        self.db.commit()

        topic = CollocationTopic(section_id=section.id, title="Topic 1", topic_number=1, topic_order=1)
        self.db.add(topic)
        self.db.commit()

        item = CollocationItem(
            topic_id=topic.id,
            collocation="heavy rain",
            pronunciation_us="/ˈhɛvi reɪn/",
            meaning_vi="mưa nặng hạt",
            example_en="We got caught in heavy rain.",
            example_vi="Chúng tôi bị kẹt trong cơn mưa lớn.",
            collocation_type="adj + noun",
            item_order=1
        )
        self.db.add(item)
        self.db.commit()

        # 3. Link collection to campaign
        link_resp = self.client.post(f"/api/campaigns/current/collocation-collections/{collection_id}/link?display_order=1", headers=self.headers)
        self.assertEqual(link_resp.status_code, 200)

        # Verify linked collections
        get_links = self.client.get("/api/campaigns/current/collocation-collections", headers=self.headers)
        self.assertEqual(get_links.status_code, 200)
        self.assertEqual(len(get_links.json()), 1)
        self.assertEqual(get_links.json()[0]["code"], "eciu-inter")

        # 4. Fetch outline outline with progress
        progress_outline = self.client.get(f"/api/collocation-collections/{collection_id}/progress", headers=self.headers)
        self.assertEqual(progress_outline.status_code, 200)
        outline_data = progress_outline.json()
        self.assertEqual(outline_data["sections"][0]["topics"][0]["items"][0]["collocation"], "heavy rain")
        self.assertIsNone(outline_data["sections"][0]["topics"][0]["items"][0]["progress"])

        # 5. Get practice collocations
        practice_resp = self.client.get("/api/vocabulary/practice/collocations", headers=self.headers)
        self.assertEqual(practice_resp.status_code, 200)
        practice_data = practice_resp.json()
        self.assertEqual(len(practice_data["matches"]), 1)
        self.assertEqual(practice_data["matches"][0]["collocation"], "heavy rain")

        # 6. Update progress
        progress_resp = self.client.post(
            f"/api/collocation-items/{item.id}/progress?correct=true",
            headers=self.headers
        )
        self.assertEqual(progress_resp.status_code, 200)
        self.assertEqual(progress_resp.json()["status"], "learning")

        # Master the item by marking it correct 2 more times
        self.client.post(f"/api/collocation-items/{item.id}/progress?correct=true", headers=self.headers)
        self.client.post(f"/api/collocation-items/{item.id}/progress?correct=true", headers=self.headers)
        
        # Verify status is mastered
        check_progress = self.client.get(f"/api/collocation-collections/{collection_id}/progress", headers=self.headers)
        progress_info = check_progress.json()["sections"][0]["topics"][0]["items"][0]["progress"]
        self.assertEqual(progress_info["status"], "mastered")

        # 7. Verify vocabulary boss checkpoints with collocations
        from app.services import challenge_vocabulary_boss
        
        # boss 3: collocations only
        boss_3_exam = challenge_vocabulary_boss(self.db, self.player.id, 3)
        self.assertTrue(len(boss_3_exam["questions"]) > 0)
        self.assertEqual(boss_3_exam["questions"][0]["question_type"], "collocation")
        self.assertEqual(boss_3_exam["questions"][0]["correct_answer"], "heavy")
        
        # boss 4: mixed (includes collocations)
        boss_4_exam = challenge_vocabulary_boss(self.db, self.player.id, 4)
        self.assertTrue(len(boss_4_exam["questions"]) > 0)
        col_qs = [q for q in boss_4_exam["questions"] if q["question_type"] == "collocation"]
        self.assertTrue(len(col_qs) > 0)
        self.assertEqual(col_qs[0]["correct_answer"], "heavy")

    def test_main_quest_xp_and_routing(self):
        from app.seed import infer_main_quest_xp
        from app.models import Quest, Skill, CampaignSkillState
        from datetime import date
        
        # 1. Test infer_main_quest_xp values
        self.assertEqual(infer_main_quest_xp(3, "Writing + Grammar"), 45)
        self.assertEqual(infer_main_quest_xp(1, "Listening + Speaking"), 35)
        self.assertEqual(infer_main_quest_xp(2, "Reading + Vocabulary"), 35)
        self.assertEqual(infer_main_quest_xp(4, "Review + Mini test", "Review errors"), 25)
        self.assertEqual(infer_main_quest_xp(4, "Review + Mini test", "Focus: Mini mock test"), 60)
        self.assertEqual(infer_main_quest_xp(4, "Review + Mini test", "Speaking mock exam"), 60)
        self.assertEqual(infer_main_quest_xp(4, "Review + Mini test", "Sectional test"), 60)

        # Ensure skill states are initialized
        from app.services import ensure_campaign_skill_states, get_campaign_skill_state_map
        ensure_campaign_skill_states(self.db, self.campaign)

        # Get skill entities
        skills = self.db.query(Skill).all()
        skill_by_name = {s.name: s for s in skills}
        
        # 2. Test S2 Main Quest claim (routes to Reading + Vocabulary)
        s2_quest = Quest(
            quest_date=date.today(),
            week_no=1,
            stage="Foundation",
            title="Main Quest W01 - S2",
            skill_id=skill_by_name["Reading"].id,
            source="Test S2",
            details="Test S2 Main Quest",
            xp=35,
            base_xp=35,
            earned_xp=35,
            completed=True,
            reward_claimed=False,
            session_type="Main Quest",
            campaign_id=self.campaign.id,
            status="completed",
            quest_role="main",
        )
        self.db.add(s2_quest)
        self.db.commit()

        # Claim the S2 quest
        resp = self.client.post(f"/api/quests/{s2_quest.id}/claim", headers=self.headers)
        self.assertEqual(resp.status_code, 200)

        # Verify skill XP balances
        state_map = {state.skill.name: state for state in ensure_campaign_skill_states(self.db, self.campaign)}
        self.assertEqual(state_map["Reading"].xp, 35)
        self.assertEqual(state_map["Vocabulary"].xp, 35)
        # S2 shouldn't credit Listening, Speaking, or Writing
        self.assertEqual(state_map["Listening"].xp, 0)
        self.assertEqual(state_map["Speaking"].xp, 0)
        self.assertEqual(state_map["Writing"].xp, 0)

        # 3. Test S1 Main Quest claim (routes to Listening + Speaking)
        s1_quest = Quest(
            quest_date=date.today(),
            week_no=1,
            stage="Foundation",
            title="Main Quest W01 - Session 1",
            skill_id=skill_by_name["Listening"].id,
            source="Test S1",
            details="Test S1 Main Quest",
            xp=35,
            base_xp=35,
            earned_xp=35,
            completed=True,
            reward_claimed=False,
            session_type="Main Quest",
            campaign_id=self.campaign.id,
            status="completed",
            quest_role="main",
        )
        self.db.add(s1_quest)
        self.db.commit()

        # Claim the S1 quest
        resp2 = self.client.post(f"/api/quests/{s1_quest.id}/claim", headers=self.headers)
        self.assertEqual(resp2.status_code, 200)

        # Verify skill XP balances updated
        self.db.expire_all()
        state_map = {state.skill.name: state for state in ensure_campaign_skill_states(self.db, self.campaign)}
        self.assertEqual(state_map["Listening"].xp, 35)
        self.assertEqual(state_map["Speaking"].xp, 35)

    def test_non_boss_gated_skills(self):
        from app.models import Quest, Skill, CampaignSkillState
        from app.services import ensure_campaign_skill_states, get_campaign_skill_state_map
        from datetime import date

        # Ensure skill states are initialized
        ensure_campaign_skill_states(self.db, self.campaign)

        # Get skill entities
        skills = self.db.query(Skill).all()
        skill_by_name = {s.name: s for s in skills}

        # 1. Assert seeding was correct
        self.assertFalse(skill_by_name["Writing"].boss_gated)
        self.assertFalse(skill_by_name["Speaking"].boss_gated)
        self.assertTrue(skill_by_name["Listening"].boss_gated)
        self.assertTrue(skill_by_name["Reading"].boss_gated)
        self.assertTrue(skill_by_name["Vocabulary"].boss_gated)

        # 2. Complete and claim a Writing quest of 1000 XP
        writing_quest = Quest(
            quest_date=date.today(),
            week_no=1,
            stage="Foundation",
            title="Writing Quest",
            skill_id=skill_by_name["Writing"].id,
            source="Test",
            details="Test writing quest",
            xp=1000,
            base_xp=1000,
            earned_xp=1000,
            completed=True,
            reward_claimed=False,
            session_type="Daily Quest",
            campaign_id=self.campaign.id,
            status="completed",
            quest_role="core",
        )
        self.db.add(writing_quest)
        self.db.commit()

        # Claim the quest
        resp = self.client.post(f"/api/quests/{writing_quest.id}/claim", headers=self.headers)
        self.assertEqual(resp.status_code, 200)

        # 3. Verify rank promotion
        self.db.expire_all()
        state_map = {state.skill.name: state for state in ensure_campaign_skill_states(self.db, self.campaign)}
        writing_state = state_map["Writing"]
        self.assertEqual(writing_state.xp, 1000)
        self.assertEqual(writing_state.rank, "E")
        # Direct confirmed_rank auto-promotion (since Writing is non-boss-gated)
        self.assertEqual(writing_state.confirmed_rank, "E")
        self.assertEqual(writing_state.promotion_status, "none")
        self.assertIsNone(writing_state.pending_rank)

        # 4. Attempt to unlock rank exam for Writing (should be blocked with 400)
        unlock_resp = self.client.post(
            "/api/rank-exams/unlock",
            json={"skill_id": skill_by_name["Writing"].id},
            headers=self.headers
        )
        self.assertEqual(unlock_resp.status_code, 400)
        self.assertIn("does not require a boss exam", unlock_resp.json()["detail"])

    def test_collocation_parser_and_seed(self):
        from app.seed import collocations_file_path, parse_collocations_file, ensure_collocations
        from app.models import CollocationCollection, CollocationSection, CollocationTopic, CollocationItem, CampaignCollocationLink, PlayerCollocationProgress
        from app.services import compute_vocabulary_xp, ensure_campaign_skill_states, update_player_collocation_progress
        
        # 1. Test parser on the real file
        try:
            filepath = collocations_file_path()
        except FileNotFoundError:
            self.skipTest("Collocation campaign file not found in test environment.")
            
        data = parse_collocations_file(filepath)
        self.assertEqual(data["code"], "intermediate-collocations")
        self.assertEqual(data["title"], "English Collocations in Use Intermediate")

        # C-1: polished file has 10 real sections (not 60)
        self.assertEqual(len(data["sections"]), 10,
            f"Parser must produce exactly 10 sections from _Section: labels; got {len(data['sections'])}")

        # C-1: total topics across all sections must be 60
        total_topics = sum(len(sec["topics"]) for sec in data["sections"])
        self.assertEqual(total_topics, 60,
            f"Parser must produce exactly 60 topics from ## N. headings; got {total_topics}")

        # C-1: topic_number must reflect the ## N value (not section_order)
        # Topic "What is a collocation?" is ## 1 → topic_number=1
        first_sec = data["sections"][0]
        self.assertEqual(first_sec["topics"][0]["topic_number"], 1)

        # C-1: verify a known section name and its topic grouping
        section_titles = [sec["title"] for sec in data["sections"]]
        self.assertIn("Learning about collocations", section_titles)
        self.assertIn("Travel and the environment", section_titles)

        # Count all parsed items
        total_items = 0
        found_ancient_monument = False
        for sec in data["sections"]:
            for top in sec["topics"]:
                for item in top["items"]:
                    total_items += 1
                    if item["collocation"] == "ancient monument":
                        found_ancient_monument = True
                        self.assertEqual(item["pronunciation_us"], "/ˈeɪn.ʃənt/ /ˈmɑːn.jə.mənt/")
                        self.assertEqual(item["meaning_vi"], "di tích cổ")
                        self.assertEqual(item["example_en"], "We visited an ancient monument in the city center.")
                        self.assertEqual(item["example_vi"], "Chúng tôi đến thăm một di tích cổ ở trung tâm thành phố.")

        self.assertGreaterEqual(total_items, 1000,
            f"Parsed item count should be at least 1000; got {total_items}")
        self.assertTrue(found_ancient_monument, "'ancient monument' must be found in the parsed data")
        
        # 2. Test seeding is idempotent
        # Clear existing collocation models first (in SQLite memory DB)
        self.db.query(PlayerCollocationProgress).delete()
        self.db.query(CampaignCollocationLink).delete()
        self.db.query(CollocationItem).delete()
        self.db.query(CollocationTopic).delete()
        self.db.query(CollocationSection).delete()
        self.db.query(CollocationCollection).delete()
        self.db.commit()
        
        # Run seeding first time
        ensure_collocations(self.db, self.campaign)
        self.db.commit()
        
        # Assert collection, campaign link, and items were created
        # C-2: global dedup means count < raw row count in file; still expect ≥1000
        col_count_first = self.db.query(CollocationItem).count()
        self.assertGreaterEqual(col_count_first, 1000)
        
        link_exists = self.db.query(CampaignCollocationLink).filter_by(
            campaign_id=self.campaign.id
        ).first()
        self.assertIsNotNone(link_exists)
        
        # Run seeding second time
        ensure_collocations(self.db, self.campaign)
        self.db.commit()
        
        # Assert count is exactly the same (idempotent)
        col_count_second = self.db.query(CollocationItem).count()
        self.assertEqual(col_count_first, col_count_second)

        # 3. Verify that collocation progress increases Vocabulary XP
        item = self.db.query(CollocationItem).first()
        self.assertIsNotNone(item)
        
        # Get baseline Vocabulary XP (should be 0 or small depending on seeded test profile)
        baseline_xp = compute_vocabulary_xp(self.db, self.player.id)
        
        # Advance collocation progress to "learning"
        update_player_collocation_progress(
            self.db,
            player_id=self.player.id,
            campaign_id=self.campaign.id,
            collocation_item_id=item.id,
            status="learning"
        )
        self.db.commit()
        
        new_xp = compute_vocabulary_xp(self.db, self.player.id)
        self.assertEqual(new_xp, baseline_xp + 5)

    def test_gap1_support_breakdown_excludes_main_quest_xp(self):
        """GAP-1: support_breakdown query must filter session_type != 'Main Quest'.
        Grammar Main Quest XP must NOT appear in Writing support_breakdown.
        Only Grammar Daily Quest XP should be counted."""
        from app.main import get_campaign_skill_outputs
        from app.models import Quest, Skill

        grammar_skill = self.db.query(Skill).filter(Skill.name == "Grammar").first()
        self.assertIsNotNone(grammar_skill, "Grammar skill must exist")

        # Insert a Grammar Main Quest (completed + claimed) — should be EXCLUDED
        main_quest = Quest(
            campaign_id=self.campaign.id,
            skill_id=grammar_skill.id,
            session_type="Main Quest",
            quest_date=date.today(),
            week_no=1,
            stage="Foundation",
            title="Grammar Main Quest",
            source="test",
            details="",
            daily_slot_code="grammar_main_1",
            status="completed",
            completed=True,
            reward_claimed=True,
            earned_xp=100,
        )
        self.db.add(main_quest)

        # Insert a Grammar Daily Quest (completed + claimed) — should be INCLUDED
        daily_quest = Quest(
            campaign_id=self.campaign.id,
            skill_id=grammar_skill.id,
            session_type="Daily Quest",
            quest_date=date.today(),
            week_no=1,
            stage="Foundation",
            title="Grammar Daily Quest",
            source="test",
            details="",
            daily_slot_code="grammar_daily_1",
            status="completed",
            completed=True,
            reward_claimed=True,
            earned_xp=30,
        )
        self.db.add(daily_quest)
        self.db.commit()

        skill_outputs = get_campaign_skill_outputs(self.db, self.campaign)

        # Find Writing skill output (Grammar routes into Writing)
        writing_out = next((s for s in skill_outputs if s.name == "Writing"), None)
        self.assertIsNotNone(writing_out, "Writing must appear in skill outputs")

        grammar_breakdown = next(
            (item for item in (writing_out.support_breakdown or []) if item.source == "Grammar"),
            None,
        )
        self.assertIsNotNone(grammar_breakdown, "Grammar must appear in Writing support_breakdown")

        # Must be 30 (Daily only), NOT 130 (Daily + Main)
        self.assertEqual(
            grammar_breakdown.xp,
            30,
            f"support_breakdown should count only Daily Quest XP (30), got {grammar_breakdown.xp}",
        )

    def test_c2_global_dedup_collocation_seed(self):
        """C-2 (reverses GAP-2): ensure_collocations global dedup — a collocation
        phrase appearing in multiple topics is seeded only once (first occurrence wins).
        A phrase appearing twice in the same topic is also deduplicated to 1.
        Idempotent: re-running seed does not change the count.

        NOTE: GAP-2 previously asserted that same-string items at different
        item_order positions were BOTH seeded. That decision has been reversed:
        owner decision 2026-06-10 adopts global dedup (first-wins) to avoid
        duplicate flashcard entries across the polished collocation file.
        """
        from app.seed import ensure_collocations
        from app.models import (
            CollocationCollection, CollocationSection,
            CollocationTopic, CollocationItem, CampaignCollocationLink,
        )
        from unittest.mock import patch

        # Fixture: "make progress" appears in Topic X (order 1) AND Topic Y (order 1).
        # "learn fast" appears twice in Topic X (orders 1 and 2) — same topic dup.
        # Expected after global dedup: 3 unique phrases total (make progress, learn fast, find a way).
        fixture = {
            "code": "test-global-dedup",
            "title": "Test Global Dedup Collection",
            "description": "Test only",
            "source_book": "Test Book",
            "level": "Intermediate",
            "sections": [
                {
                    "title": "Section A",
                    "section_order": 1,
                    "topics": [
                        {
                            "title": "Topic X",
                            "topic_number": 1,
                            "topic_order": 1,
                            "items": [
                                {
                                    "item_order": 1,
                                    "collocation": "make progress",
                                    "pronunciation_us": "/meɪk/",
                                    "meaning_vi": "tiến bộ",
                                    "example_en": "We make progress daily.",
                                    "example_vi": "Chúng tôi tiến bộ hàng ngày.",
                                },
                                {
                                    "item_order": 2,
                                    "collocation": "make progress",  # duplicate in same topic → skip
                                    "pronunciation_us": "/meɪk/",
                                    "meaning_vi": "đạt tiến bộ",
                                    "example_en": "Teams make progress together.",
                                    "example_vi": "Các nhóm cùng tiến bộ.",
                                },
                                {
                                    "item_order": 3,
                                    "collocation": "learn fast",
                                    "pronunciation_us": "/lɜːrn/",
                                    "meaning_vi": "học nhanh",
                                    "example_en": "Children learn fast.",
                                    "example_vi": "Trẻ em học nhanh.",
                                },
                            ],
                        },
                        {
                            "title": "Topic Y",
                            "topic_number": 2,
                            "topic_order": 2,
                            "items": [
                                {
                                    "item_order": 1,
                                    "collocation": "make progress",  # cross-topic dup → skip
                                    "pronunciation_us": "/meɪk/",
                                    "meaning_vi": "tiến bộ",
                                    "example_en": "She made progress quickly.",
                                    "example_vi": "Cô ấy tiến bộ nhanh chóng.",
                                },
                                {
                                    "item_order": 2,
                                    "collocation": "find a way",
                                    "pronunciation_us": "/faɪnd/",
                                    "meaning_vi": "tìm ra cách",
                                    "example_en": "They found a way.",
                                    "example_vi": "Họ tìm ra cách.",
                                },
                            ],
                        },
                    ],
                }
            ],
        }

        # Clean slate
        self.db.query(CampaignCollocationLink).delete()
        self.db.query(CollocationItem).delete()
        self.db.query(CollocationTopic).delete()
        self.db.query(CollocationSection).delete()
        self.db.query(CollocationCollection).delete()
        self.db.commit()

        with patch("app.seed.collocations_file_path", return_value="/fake/path"), \
             patch("app.seed.parse_collocations_file", return_value=fixture):
            ensure_collocations(self.db, self.campaign)
            self.db.commit()

        seeded_count = self.db.query(CollocationItem).count()
        self.assertEqual(
            seeded_count,
            3,
            f"Global dedup: 3 unique phrases (make progress×1, learn fast, find a way); got {seeded_count}",
        )

        # Verify "make progress" seeded only once
        make_progress_count = self.db.query(CollocationItem).filter_by(collocation="make progress").count()
        self.assertEqual(make_progress_count, 1, "Global dedup: 'make progress' must appear exactly once")

        # Idempotency: re-run → count stays at 3
        with patch("app.seed.collocations_file_path", return_value="/fake/path"), \
             patch("app.seed.parse_collocations_file", return_value=fixture):
            ensure_collocations(self.db, self.campaign)
            self.db.commit()

        seeded_count_second = self.db.query(CollocationItem).count()
        self.assertEqual(seeded_count_second, 3, "Idempotent re-seed must not change count")


class TestPolicyTables(unittest.TestCase):
    """Task 15: Verify 4 XP policy tables are seeded and quest XP reads from them."""

    def setUp(self):
        from sqlalchemy.pool import StaticPool
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()

        # Seed all 7 skills (matrix + support)
        for name, icon in [
            ("Vocabulary", "📔"), ("Listening", "🎧"), ("Reading", "📖"),
            ("Writing", "✍️"), ("Speaking", "🗣️"),
            ("Grammar", "📝"), ("Collocation", "🔗"),
        ]:
            self.db.add(Skill(name=name, icon=icon))
        self.db.commit()

        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

        resp = self.client.post("/api/auth/register", json={
            "email": "policy@example.com",
            "password": "password123",
            "display_name": "Policy User",
        })
        self.access_token = resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        self.client.post("/api/onboarding/activate-campaign", headers=self.headers)
        self.campaign = self.db.query(Campaign).first()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_rank_xp_thresholds_seeded(self):
        from app.models import RankXpThreshold
        rows = self.db.query(RankXpThreshold).order_by(RankXpThreshold.min_xp).all()
        rank_map = {r.rank_name: (r.min_xp, r.first_level) for r in rows}
        # Spec §2.3 values
        expected = {
            "F": (0, 1), "E": (862, 11), "D": (2460, 21),
            "C": (4604, 31), "B": (7212, 41), "A": (10234, 51), "S": (13279, 60),
        }
        for rank, (min_xp, first_level) in expected.items():
            self.assertIn(rank, rank_map, f"Missing RankXpThreshold for {rank}")
            self.assertEqual(rank_map[rank][0], min_xp, f"{rank} min_xp mismatch")
            self.assertEqual(rank_map[rank][1], first_level, f"{rank} first_level mismatch")

    def test_quest_xp_policies_seeded(self):
        from app.models import QuestXpPolicy
        rows = self.db.query(QuestXpPolicy).all()
        pol = {r.activity_code: (r.skill_code, r.xp_reward) for r in rows}
        # Spec §5.1 selected values
        self.assertEqual(pol.get("listening"), ("Listening", 10))
        self.assertEqual(pol.get("reading"), ("Reading", 10))
        self.assertEqual(pol.get("writing"), ("Writing", 12))
        self.assertEqual(pol.get("speaking"), ("Speaking", 12))
        self.assertEqual(pol.get("grammar_exercise"), ("Writing", 7))   # Grammar → Writing
        self.assertEqual(pol.get("grammar_review"), ("Writing", 5))
        self.assertEqual(pol.get("vocab_flashcard"), ("Vocabulary", 4))
        self.assertEqual(pol.get("vocab_codex"), ("Vocabulary", 5))
        self.assertEqual(pol.get("vocab_collocation"), ("Vocabulary", 5))

    def test_weekly_mission_xp_policies_seeded(self):
        from app.models import WeeklyMissionXpPolicy
        rows = self.db.query(WeeklyMissionXpPolicy).all()
        pol = {r.mission_type: (r.reward_target_skill, r.xp_reward) for r in rows}
        # Spec §7
        self.assertEqual(pol.get("vocab_weekly"),    ("Vocabulary", 55))
        self.assertEqual(pol.get("listening_weekly"), ("Listening", 40))
        self.assertEqual(pol.get("reading_weekly"),  ("Reading", 40))
        self.assertEqual(pol.get("writing_weekly"),  ("Writing", 45))
        self.assertEqual(pol.get("speaking_weekly"), ("Speaking", 45))
        self.assertEqual(pol.get("grammar_weekly"),  ("Writing", 45))   # Grammar → Writing

    def test_main_quest_xp_policies_seeded(self):
        from app.models import MainQuestXpPolicy
        rows = self.db.query(MainQuestXpPolicy).all()
        pol = {r.tier_code: r.xp_reward for r in rows}
        # Spec §6
        self.assertEqual(pol.get("light_intro"), 25)
        self.assertEqual(pol.get("standard"), 35)
        self.assertEqual(pol.get("heavy_output"), 45)
        self.assertEqual(pol.get("review_error_logging"), 25)
        self.assertEqual(pol.get("mock"), 60)

    def test_policy_idempotent(self):
        """Running ensure_policy_tables twice must not create duplicates."""
        from app.models import RankXpThreshold, QuestXpPolicy, WeeklyMissionXpPolicy, MainQuestXpPolicy
        from app.seed import ensure_policy_tables

        count_before = (
            self.db.query(RankXpThreshold).count()
            + self.db.query(QuestXpPolicy).count()
            + self.db.query(WeeklyMissionXpPolicy).count()
            + self.db.query(MainQuestXpPolicy).count()
        )
        ensure_policy_tables(self.db)
        self.db.commit()
        count_after = (
            self.db.query(RankXpThreshold).count()
            + self.db.query(QuestXpPolicy).count()
            + self.db.query(WeeklyMissionXpPolicy).count()
            + self.db.query(MainQuestXpPolicy).count()
        )
        self.assertEqual(count_before, count_after, "Second ensure_policy_tables must not insert duplicates")

    def test_daily_quest_xp_from_policy(self):
        """Daily quests seeded via ensure_templates + ensure_quest_instances must carry
        XP values sourced from QuestXpPolicy, not hard-coded defaults."""
        from app.models import Quest, QuestXpPolicy

        # Map activity_code → expected xp from policy
        pol_rows = self.db.query(QuestXpPolicy).all()
        xp_by_code = {r.activity_code: r.xp_reward for r in pol_rows}

        # Slot-code ↔ activity_code are the same in this codebase
        slot_to_xp = {code: xp for code, xp in xp_by_code.items()}

        quests = self.db.query(Quest).filter(
            Quest.campaign_id == self.campaign.id,
            Quest.session_type == "Daily Quest",
        ).limit(200).all()

        self.assertGreater(len(quests), 0, "No daily quests seeded")

        mismatches = []
        for q in quests:
            if q.daily_slot_code and q.daily_slot_code in slot_to_xp:
                expected = slot_to_xp[q.daily_slot_code]
                if q.base_xp != expected:
                    mismatches.append(f"{q.daily_slot_code}: base_xp={q.base_xp} expected={expected}")

        self.assertEqual(
            mismatches, [],
            "Quest base_xp mismatch with QuestXpPolicy:\n" + "\n".join(mismatches),
        )


class TestGap151MainQuestReadsPolicy(unittest.TestCase):
    """GAP-15-1: infer_main_quest_xp must read MainQuestXpPolicy when db= is passed.
    Proves policy is source of truth (mutating policy row changes quest XP)."""

    def setUp(self):
        from sqlalchemy.pool import StaticPool
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()

        # Seed all 7 skills
        for name, icon in [
            ("Vocabulary", "📔"), ("Listening", "🎧"), ("Reading", "📖"),
            ("Writing", "✍️"), ("Speaking", "🗣️"),
            ("Grammar", "📝"), ("Collocation", "🔗"),
        ]:
            self.db.add(Skill(name=name, icon=icon))
        self.db.commit()

        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

        resp = self.client.post("/api/auth/register", json={
            "email": "gap151@example.com",
            "password": "password123",
            "display_name": "Gap151 User",
        })
        self.access_token = resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        self.client.post("/api/onboarding/activate-campaign", headers=self.headers)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_main_quest_xp_reads_policy_not_hardcode(self):
        """infer_main_quest_xp with db= must read MainQuestXpPolicy, not hard-code.
        Mutate 'standard' 35→40, call with db=, assert result=40."""
        from app.models import MainQuestXpPolicy
        from app.seed import infer_main_quest_xp

        # Mutate the 'standard' policy row to 40
        policy = self.db.query(MainQuestXpPolicy).filter_by(tier_code="standard").first()
        self.assertIsNotNone(policy, "MainQuestXpPolicy 'standard' not seeded")
        policy.xp_reward = 40
        self.db.commit()

        # infer_main_quest_xp with db= should read the policy table (standard = session_no=1 or 2)
        xp_with_db = infer_main_quest_xp(1, "Reading and Vocabulary focus", db=self.db)
        self.assertEqual(
            xp_with_db, 40,
            f"infer_main_quest_xp returned {xp_with_db} (expected 40 from policy). "
            "Policy not being read — hard-code fallback used instead.",
        )

        # Without db= must still return hard-coded 35 (fallback path unchanged)
        xp_no_db = infer_main_quest_xp(1, "Reading and Vocabulary focus")
        self.assertEqual(xp_no_db, 35, "Hard-code fallback should return 35 when db=None")


class TestGap153WeeklyPolicyAllRowsReachable(unittest.TestCase):
    """GAP-15-3: All seeded WeeklyMissionXpPolicy rows must be reachable via
    map_weekly_pattern_to_mission_type from at least one seeded weekly pattern."""

    def setUp(self):
        from sqlalchemy.pool import StaticPool
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()

        for name, icon in [
            ("Vocabulary", "📔"), ("Listening", "🎧"), ("Reading", "📖"),
            ("Writing", "✍️"), ("Speaking", "🗣️"),
            ("Grammar", "📝"), ("Collocation", "🔗"),
        ]:
            self.db.add(Skill(name=name, icon=icon))
        self.db.commit()

        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

        resp = self.client.post("/api/auth/register", json={
            "email": "gap153@example.com",
            "password": "password123",
            "display_name": "Gap153 User",
        })
        self.access_token = resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        self.client.post("/api/onboarding/activate-campaign", headers=self.headers)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_all_weekly_policy_mission_types_reachable(self):
        """Every WeeklyMissionXpPolicy.mission_type for the 6 regular weekly types
        (non-onboarding) is mapped by at least one pattern_code in weekly_mission_patterns
        via map_weekly_pattern_to_mission_type.
        Note: 'onboarding' is a special-case row used by ensure_weekly_mission_instances
        directly (not through weekly_mission_patterns), so it is excluded here."""
        from app.models import WeeklyMissionXpPolicy, WeeklyMission
        from app.seed import map_weekly_pattern_to_mission_type, weekly_mission_patterns

        # Collect all seeded policy mission types — exclude 'onboarding' (special-case)
        SPECIAL_CASE_TYPES = {"onboarding"}
        policy_types = {
            r.mission_type
            for r in self.db.query(WeeklyMissionXpPolicy).all()
            if r.mission_type not in SPECIAL_CASE_TYPES
        }
        self.assertGreater(len(policy_types), 0, "No WeeklyMissionXpPolicy rows seeded")

        # Collect all mapped mission types from all patterns across all phase indices
        mapped_types = set()
        for phase_idx in range(1, 7):  # phases 1-6
            for pattern in weekly_mission_patterns(phase_idx):
                mapped_type = map_weekly_pattern_to_mission_type(pattern["pattern_code"])
                mapped_types.add(mapped_type)

        dead_rows = policy_types - mapped_types
        self.assertEqual(
            dead_rows, set(),
            f"WeeklyMissionXpPolicy rows with no reader in any pattern: {dead_rows}. "
            "Add pattern_code entries or remove the dead policy rows.",
        )

    def test_speaking_weekly_missions_seeded(self):
        """After activate-campaign, speaking-focus weekly missions must exist.
        WeeklyMission stores pattern_code (e.g. '1-speaking-focus'), not mission_type."""
        from app.models import WeeklyMission
        from sqlalchemy import func
        # pattern_code contains 'speaking' for speaking-focus missions
        speaking_missions = self.db.query(WeeklyMission).filter(
            func.lower(WeeklyMission.pattern_code).contains("speaking")
        ).all()
        self.assertGreater(
            len(speaking_missions), 0,
            "No speaking-focus weekly missions seeded (pattern_code contains 'speaking'). "
            "Check weekly_mission_patterns adds speaking-focus patterns.",
        )

    def test_grammar_weekly_missions_seeded(self):
        """After activate-campaign, grammar-focus weekly missions must exist.
        WeeklyMission stores pattern_code (e.g. '1-grammar-focus'), not mission_type."""
        from app.models import WeeklyMission
        from sqlalchemy import func
        # pattern_code contains 'grammar' for grammar-focus missions
        grammar_missions = self.db.query(WeeklyMission).filter(
            func.lower(WeeklyMission.pattern_code).contains("grammar")
        ).all()
        self.assertGreater(
            len(grammar_missions), 0,
            "No grammar-focus weekly missions seeded (pattern_code contains 'grammar'). "
            "Check weekly_mission_patterns adds grammar-focus patterns.",
        )


class TestCollocationFlashcards(unittest.TestCase):
    def setUp(self):
        from sqlalchemy.pool import StaticPool
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()

        # Seed skills
        self.skills = [
            Skill(name="Vocabulary", icon="📔"),
            Skill(name="Listening", icon="🎧"),
            Skill(name="Reading", icon="📖"),
            Skill(name="Writing", icon="✍️"),
            Skill(name="Speaking", icon="🗣️"),
            Skill(name="Grammar", icon="📝"),
            Skill(name="Collocation", icon="🔗"),
        ]
        self.db.add_all(self.skills)
        self.db.commit()

        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

        # Register user and activate campaign
        payload = {
            "email": "colloc_fc@example.com",
            "password": "password123",
            "display_name": "Colloc FC User"
        }
        resp = self.client.post("/api/auth/register", json=payload)
        self.access_token = resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

        # Activate campaign
        self.client.post("/api/onboarding/activate-campaign", headers=self.headers)
        
        # Get player and campaign
        self.player = self.db.query(Player).first()
        self.campaign = self.db.query(Campaign).first()

        # Create collocation setup
        collection = CollocationCollection(
            code="test-coll",
            title="Test Collection",
            description="",
            source_book="",
            level="Intermediate",
            is_active=True
        )
        self.db.add(collection)
        self.db.commit()

        self.section = CollocationSection(collection_id=collection.id, title="Section 1", section_order=1)
        self.db.add(self.section)
        self.db.commit()

        self.topic = CollocationTopic(section_id=self.section.id, title="Topic 1", topic_number=1, topic_order=1)
        self.db.add(self.topic)
        self.db.commit()

        self.item = CollocationItem(
            topic_id=self.topic.id,
            collocation="heavy rain",
            pronunciation_us="/ˈhɛvi reɪn/",
            meaning_vi="mưa nặng hạt",
            example_en="We got caught in heavy rain.",
            example_vi="Chúng tôi bị kẹt trong cơn mưa lớn.",
            collocation_type="adj + noun",
            item_order=1
        )
        self.db.add(self.item)
        self.db.commit()

        # Link collection to campaign
        self.client.post(f"/api/campaigns/current/collocation-collections/{collection.id}/link?display_order=1", headers=self.headers)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_effective_familiarity_decay(self):
        from app.services import effective_familiarity
        now = datetime.utcnow()
        # good -> good at 0d
        self.assertEqual(effective_familiarity("good", now, now), "good")
        # good -> hard at 8d
        self.assertEqual(effective_familiarity("good", now - timedelta(days=8), now), "hard")
        # good -> again at 15d
        self.assertEqual(effective_familiarity("good", now - timedelta(days=15), now), "again")
        # hard -> again at 8d
        self.assertEqual(effective_familiarity("hard", now - timedelta(days=8), now), "again")
        # again stays again
        self.assertEqual(effective_familiarity("again", now - timedelta(days=8), now), "again")
        # easy stays easy (graduated, never decays)
        self.assertEqual(effective_familiarity("easy", now - timedelta(days=100), now), "easy")

    def test_add_flashcard_idempotent(self):
        resp = self.client.post(f"/api/collocations/{self.item.id}/flashcard", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["detail"], "flashcard added")

        # Second POST
        resp2 = self.client.post(f"/api/collocations/{self.item.id}/flashcard", headers=self.headers)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json()["detail"], "flashcard exists")

    def test_add_graduated_resets_to_again(self):
        self.client.post(f"/api/collocations/{self.item.id}/flashcard", headers=self.headers)
        # Review to easy
        review_resp = self.client.post(
            f"/api/collocations/{self.item.id}/flashcard/review",
            json={"result": "easy"},
            headers=self.headers
        )
        self.assertEqual(review_resp.status_code, 200)
        
        # Verify it is easy
        fc = self.db.query(CollocationFlashcard).filter(CollocationFlashcard.collocation_item_id == self.item.id).first()
        self.assertEqual(fc.familiarity, "easy")

        # Re-add flashcard
        readd_resp = self.client.post(f"/api/collocations/{self.item.id}/flashcard", headers=self.headers)
        self.assertEqual(readd_resp.status_code, 200)
        self.assertEqual(readd_resp.json()["familiarity"], "again")
        
        # Verify in DB it has reset to again
        self.db.refresh(fc)
        self.assertEqual(fc.familiarity, "again")

    def test_review_easy_graduates(self):
        # Add flashcard
        self.client.post(f"/api/collocations/{self.item.id}/flashcard", headers=self.headers)
        
        # Check it is in flashcard topics and items
        resp_topics = self.client.get("/api/collocations/flashcard/topics", headers=self.headers)
        self.assertEqual(len(resp_topics.json()), 1)
        
        resp_items = self.client.get(f"/api/collocations/flashcard/topics/{self.topic.id}", headers=self.headers)
        self.assertEqual(len(resp_items.json()), 1)

        # Review easy
        self.client.post(
            f"/api/collocations/{self.item.id}/flashcard/review",
            json={"result": "easy"},
            headers=self.headers
        )

        # Check it is excluded from flashcard topics and items
        resp_topics = self.client.get("/api/collocations/flashcard/topics", headers=self.headers)
        self.assertEqual(len(resp_topics.json()), 0)
        
        resp_items = self.client.get(f"/api/collocations/flashcard/topics/{self.topic.id}", headers=self.headers)
        self.assertEqual(len(resp_items.json()), 0)

        # Check it is still present (yellow) in browse read
        resp_browse = self.client.get(f"/api/collocations/topics/{self.topic.id}/items", headers=self.headers)
        self.assertEqual(len(resp_browse.json()), 1)
        self.assertEqual(resp_browse.json()[0]["effective_familiarity"], "easy")

    def test_autocomplete_collocation_forge_5_distinct(self):
        # Reuse the quest seeded during campaign activation (avoid UNIQUE constraint on vocab_collocation slot)
        quest = self.db.query(Quest).filter(
            Quest.campaign_id == self.campaign.id,
            Quest.daily_slot_code == "vocab_collocation",
            Quest.quest_date == date.today(),
        ).first()
        if quest is None:
            # Fallback: create quest only if seed didn't produce one for today
            colloc_skill = self.db.query(Skill).filter(Skill.name == "Collocation").first()
            quest = Quest(
                campaign_id=self.campaign.id,
                skill_id=colloc_skill.id,
                session_type="Daily Quest",
                quest_date=date.today(),
                week_no=1,
                stage="Foundation",
                title="Collocation Forge",
                source="test",
                details="",
                daily_slot_code="vocab_collocation",
                status="active",
                completed=False,
                reward_claimed=False,
                base_xp=5,
            )
            self.db.add(quest)
            self.db.commit()
        else:
            # Reset to active/not-completed in case seed marked it otherwise
            quest.completed = False
            quest.status = "active"
            self.db.commit()

        items = []
        for i in range(1, 6):
            item = CollocationItem(
                topic_id=self.topic.id,
                collocation=f"heavy rain {i}",
                collocation_type="adj + noun",
                item_order=i
            )
            self.db.add(item)
            items.append(item)
        self.db.commit()

        for item in items:
            self.client.post(f"/api/collocations/{item.id}/flashcard", headers=self.headers)

        for i in range(4):
            resp = self.client.post(
                f"/api/collocations/{items[i].id}/flashcard/review",
                json={"result": "good"},
                headers=self.headers
            )
            self.assertEqual(resp.status_code, 200)
            self.assertFalse(resp.json()["collocation_forge_autocompleted"])
        
        # Verify quest is still not completed
        self.db.refresh(quest)
        self.assertFalse(quest.completed)

        # Review the 5th one
        resp = self.client.post(
            f"/api/collocations/{items[4].id}/flashcard/review",
            json={"result": "good"},
            headers=self.headers
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["collocation_forge_autocompleted"])

        # Verify quest is now completed
        self.db.refresh(quest)
        self.assertTrue(quest.completed)
        self.assertEqual(quest.status, "completed")

    def test_autocomplete_collocation_forge_same_card_no_complete(self):
        # Reuse the quest seeded during campaign activation (avoid UNIQUE constraint on vocab_collocation slot)
        quest = self.db.query(Quest).filter(
            Quest.campaign_id == self.campaign.id,
            Quest.daily_slot_code == "vocab_collocation",
            Quest.quest_date == date.today(),
        ).first()
        if quest is None:
            colloc_skill = self.db.query(Skill).filter(Skill.name == "Collocation").first()
            quest = Quest(
                campaign_id=self.campaign.id,
                skill_id=colloc_skill.id,
                session_type="Daily Quest",
                quest_date=date.today(),
                week_no=1,
                stage="Foundation",
                title="Collocation Forge",
                source="test",
                details="",
                daily_slot_code="vocab_collocation",
                status="active",
                completed=False,
                reward_claimed=False,
                base_xp=5,
            )
            self.db.add(quest)
            self.db.commit()
        else:
            quest.completed = False
            quest.status = "active"
            self.db.commit()

        self.client.post(f"/api/collocations/{self.item.id}/flashcard", headers=self.headers)

        # Review it 5 times today
        for i in range(5):
            resp = self.client.post(
                f"/api/collocations/{self.item.id}/flashcard/review",
                json={"result": "good"},
                headers=self.headers
            )
            self.assertEqual(resp.status_code, 200)
            self.assertFalse(resp.json()["collocation_forge_autocompleted"])
        
        self.db.refresh(quest)
        self.assertFalse(quest.completed)


if __name__ == "__main__":
    unittest.main()
