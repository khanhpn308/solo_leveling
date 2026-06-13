# ADR-003: Deploy Target — Managed PaaS (Render/Railway) + GitHub Student Credit

## Status

**Superseded (2026-06-11)** — owner dropped the public-SaaS direction (see
[`../SMALL_GROUP_PLAN.md`](../SMALL_GROUP_PLAN.md)). The app runs as a small-group tool on one shared
server; managed-PaaS deploy is no longer a committed decision. Retained for history.

## Date

2026-06-11

## Context

The app needs a real production deploy target. The current `docker-compose.yml` is dev-grade
(uvicorn `--reload`, `./backend:/app` volume mount, no reverse proxy, no HTTPS, no backend
healthcheck). A previous attempt used a bare **EC2** instance (the now-off IP `18.141.232.235`),
where the single developer had to hand-manage HTTPS, DB backups, monitoring, OS patching, and
restart-on-crash — an ongoing operational burden with real failure modes (an expired cert takes the
site down; no backup means total data loss).

The owner has a **GitHub Student** pack, which typically provides credits for managed providers
(DigitalOcean, Render, Heroku, Azure for Students) and a free domain (Namecheap), turning otherwise
pricier managed services nearly free during the early phase.

The app has stateful **MySQL** plus a long-running uvicorn process and a heavy startup seed, which
makes "long-running service + attached DB" platforms (Render/Railway) a better fit than edge/global
platforms where stateful DBs are more complex (Fly.io). Serverless was rejected outright for the
same stateful reasons.

## Decision

Deploy to a **Managed PaaS — Render or Railway** — and use **GitHub Student credit** to cover the
early-phase cost. The PaaS provides automatic HTTPS, a managed MySQL with automatic backups,
restart-on-crash, and git-push auto-deploy out of the box.

Note: the exact Student offer changes over time — **confirm the current Student benefit before
locking the provider**. Choosing the specific provider (Render vs Railway vs DigitalOcean App
Platform) is itself a Phase 1 step with explicit criteria (HTTPS + DB backup + restart + Student
credit applicability).

## Consequences

Positive:

- Offloads the exact operational tasks that made the EC2 attempt burdensome (HTTPS, backups,
  restart, deploy).
- Nearly free early on via Student credit.
- git-push auto-deploy doubles as lightweight CD (see ADR on CI), avoiding a hand-built pipeline.

Tradeoffs:

- Less OS-level control than a self-managed VPS.
- Higher raw cost than a bare VPS once Student credit runs out — revisit at Phase 3 if scale/cost
  becomes a real constraint.
