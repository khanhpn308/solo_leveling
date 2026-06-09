# Migration History

This file summarizes the backend migration rollout that introduced campaign-scoped state and final constraint hardening.

## Status

Waves `A-E` are complete.

## Wave A - Nullable scope and typed-link columns

Goal:

- add campaign scope columns safely
- add typed quest tracker links
- add typed weakness source links

Result:

- new nullable columns added
- compatibility preserved
- no destructive schema rewrite

## Wave B - Additive state tables

Goal:

- introduce campaign-scoped mutable state tables without cutting over reads/writes yet

Result:

- added `campaign_skill_states`
- added `badge_unlocks`

## Wave C - Backfill existing data

Goal:

- fill legacy rows into the new campaign-scoped and typed-link shape

Result:

- campaign scope backfilled
- typed-link fields backfilled
- campaign skill state seeded
- qualifying badge unlock rows seeded

## Wave D - Application cutover

Goal:

- make the backend use the new state model without changing public response shapes

Result:

- skill reads/writes moved to `campaign_skill_states`
- badge reads moved to `badge_unlocks`
- campaign-scoped reads enforced for live progression surfaces
- typed quest completion dual-write implemented

## Wave E - Constraint hardening

Goal:

- enforce the data guarantees assumed by the cutover

Result:

- target `campaign_id` fields made `NOT NULL`
- check-in uniqueness became campaign-scoped
- daily quest slot uniqueness added
- migration includes fail-fast preflight checks

## Deferred Cleanup

Completed:

- removed legacy tracker fields from `quests` (Alembic migration `75dc49c5ae91`)
- removed legacy source fields from `weakness_suggestions` (Alembic migration `75dc49c5ae91`)
- removed global mutable state fields from `skills` (Alembic migration `75dc49c5ae91`)
- removed global unlock-state fields from `badges` (Alembic migration `75dc49c5ae91`)
- added stricter typed-link check constraints (Alembic migration `089adadeddde`)

