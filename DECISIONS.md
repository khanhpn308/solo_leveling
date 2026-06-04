# Decisions Log

## 2026-06-04 - Home dashboard redesign stays frontend-only

- The completed home dashboard redesign is a frontend-only change.
- No API contract, database/schema, or Docker Compose changes were introduced for this redesign.
- Existing backend endpoints were reused for suggestion inbox actions and certificate records.
- The avatar picker is intentionally placeholder-only for now.

## 2026-06-04 - Home shell structure

- The home dashboard uses a compact shell instead of the previous larger dashboard layout.
- The primary landing area is the roadmap hero plus bottom stat cards.
- Secondary surfaces are exposed through the burger navigation and overlays.

## 2026-06-04 - Overlay behavior

- Quest is presented as a full overlay with Main, Daily, Weekly, and Archive tabs.
- The Main tab surfaces the current main quest first, followed by the rest of the roadmap map.
- Certificate and Boss are separate overlays so they do not clutter the home shell.

## 2026-06-04 - Existing APIs reused

- Suggestion inbox actions use the existing backend suggestion endpoints.
- Certificate creation uses the existing test-records API.
- No new data model was added for these surfaces in this task.
