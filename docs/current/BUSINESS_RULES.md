# Business Rules

## Core Progression Model

- XP is awarded for completed study actions.
- Study time alone does not grant XP.
- Skills use ranks: `F`, `E`, `D`, `C`, `B`, `A`, `S`.
- Skills also track:
  - XP
  - level
  - last practiced date
  - weakness note

## Main Skills

- Listening
- Reading
- Writing
- Speaking
- Vocabulary
- Collocation
- Grammar

## Progression Loop

The intended loop is:

1. complete quests or study actions
2. claim rewards
3. gain XP and visible progression
4. surface weaknesses and suggestions
5. continue the campaign

## Reward Claim Rule

- Completing a quest does not automatically bank XP.
- XP is banked only after explicit reward claim.
- This applies to quest and weekly reward flow.

## Campaign Scope Rule

- Live progression surfaces are campaign-scoped.
- Test history remains player-wide.
- Campaign-scoped state now includes:
  - skill progression
  - badge ownership
  - check-ins
  - rank suggestions
  - weakness suggestions

## Check-In Rule

Each day can store:

- mood
- energy
- focus
- a short note

Check-ins are used for streak and weekly-support logic.

## Quest Model

The product currently uses:

- main quests
- daily quests
- weekly missions
- archived/completed history views

Daily quest roles include:

- `core`
- `support`
- `mini`

## Boss / Badge Rule

- Boss battles and badges are part of the motivation loop.
- Badge unlock state is now stored per campaign.
- Unlock criteria are preserved from the current backend logic and were not redesigned during the migration waves.
