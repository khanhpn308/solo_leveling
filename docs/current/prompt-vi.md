# Sổ tay phiên làm việc Codex và thư viện prompt

Đây là hướng dẫn tiếng Việt, ưu tiên cho repo `IELTS Quest Dashboard`.

Dùng file này khi anh muốn:

- bắt đầu một phiên làm việc đúng cách
- viết prompt hiệu quả hơn
- chọn đúng skill theo task
- kết thúc phiên gọn và dễ resume

## 1. Quy trình phiên làm việc

### Bước 1. Nạp ngữ cảnh đúng thứ tự

Trong repo này, luôn bắt đầu bằng:

1. `AGENTS.md`
2. `README.md`
3. `TASKS.md`
4. `DECISIONS.md`
5. `docs/current/CONTEXT_INDEX.md`

Sau đó chỉ đọc thêm các file thật sự liên quan đến task hiện tại.

Không nên bắt đầu bằng:

- changelog lịch sử dài
- note cũ không liên quan
- cả cây source không phục vụ task

### Bước 1A. Mở rộng ngữ cảnh theo loại task

Sau base load order, chỉ đọc thêm đúng phần nhỏ nhất cần cho task.

#### Với task backend

Đọc tiếp:

- các entrypoint backend liên quan trong `backend/app/`
- file service, schema, model tương ứng
- `docs/current/DATABASE_SCHEMA.md` nếu behavior phụ thuộc vào dữ liệu lưu trữ
- `docs/current/SCHEMA_SEMANTICS.md` nếu ý nghĩa field quan trọng

Ví dụ thường gặp:

- đổi endpoint:
  - route file
  - service file
  - schema file
- đổi behavior dữ liệu / state:
  - service file
  - model file
  - schema snapshot / semantics docs

#### Với task migration hoặc database

Đọc tiếp:

- các Alembic revision gần nhất có liên quan
- `backend/app/models.py`
- `docs/current/DATABASE_SCHEMA.md`
- `docs/current/SCHEMA_SEMANTICS.md`
- `docs/history/MIGRATION_HISTORY.md` nếu task nối tiếp các wave rollout trước

Không nên bắt đầu viết migration trước khi kiểm tra:

- invariant hiện tại
- rollout pattern đang dùng
- kỳ vọng validation

#### Với task frontend

Đọc tiếp:

- component mục tiêu
- các file data/utility liên quan trực tiếp
- một component lân cận để bám visual/state pattern hiện tại
- `docs/current/PROJECT_CONTEXT.md` nếu task ảnh hưởng đến cách thể hiện sản phẩm

Nếu task chạm UI state lấy từ backend, đọc thêm API consumer hoặc view-model path tương ứng.

#### Với task documentation

Đọc tiếp:

- canonical doc cần trở thành source of truth
- history docs tương ứng chỉ khi cần bằng chứng thực tế
- `DECISIONS.md` nếu thay đổi này ghi lại một rule hoặc workflow lâu dài

Ưu tiên update canonical docs từ trạng thái thật hiện tại của repo, không copy máy móc từ log cũ.

#### Với task review

Đọc tiếp:

- các file đã đổi hoặc diff
- một file lân cận để so pattern nếu cần
- `TASKS.md` và `DECISIONS.md` nếu intent của behavior chưa rõ
- `docs/history/TEST_REPORT.md` nếu cần kiểm tra claim về validation

#### Với task debugging

Đọc tiếp:

- code path đang fail
- test gần nhất có liên quan, nếu có
- runtime error chính xác hoặc output của lệnh đang fail

Không mở rộng sang history quá sớm. Phải reproduce và localize trước.

### Bước 1B. Quy tắc dừng nạp ngữ cảnh

Dừng đọc thêm khi cả 4 điều này đã đúng:

- đã biết loại task
- đã biết file nào có khả năng phải sửa
- đã có một pattern sẵn có để bám theo
- đã nói rõ được goal, constraints, và next step

Nếu sau đó vẫn tiếp tục nạp thêm file, rất có thể anh đang tăng noise thay vì signal.

### Bước 2. Ground repo trước khi làm

Trước khi plan hay code, làm một lượt xác nhận ngắn:

- task hiện tại trong `TASKS.md` là gì
- decision nào đã chốt trong `DECISIONS.md`
- code path nào thực sự liên quan
- task này thuộc loại nào:
  - planning
  - implementation
  - debugging
  - review
  - documentation
  - migration

### Bước 3. Khóa contract của task

Luôn nói rõ:

- mục tiêu
- tiêu chí hoàn thành
- trong scope
- ngoài scope
- ràng buộc
- rủi ro

Nếu còn ambiguity ảnh hưởng lớn đến cách làm, phải hỏi lại trước.

### Bước 4. Lên plan trước khi làm task rộng

Nên plan trước nếu task:

- chạm nhiều file
- đổi backend behavior
- đổi schema hoặc API contract
- liên quan migration
- cần sequencing hoặc validation rõ

Plan tốt phải:

- bounded
- decision complete
- testable
- đủ nhỏ để thực thi trong một phiên tập trung hoặc một worker slice

### Bước 5. Thực thi theo lát cắt nhỏ

Khi implement:

- chỉ chạm phần task cần
- bám pattern có sẵn trong repo
- không cleanup ngoài phạm vi
- mỗi lát cắt phải kiểm chứng được

### Bước 6. Xác minh

Thứ tự ưu tiên:

1. syntax / type checks
2. focused smoke checks
3. test cho behavior vừa đổi
4. review nếu task mức medium hoặc high risk

Không được coi task là xong nếu chưa có bằng chứng xác minh.

### Bước 7. Cập nhật docs và tracker

Sau khi hoàn thành một thay đổi có ý nghĩa, cập nhật:

1. `TASKS.md`
2. `docs/history/TEST_REPORT.md`
3. `docs/history/AGENT_NOTES.md`
4. `docs/history/changelogs.md`
5. `DECISIONS.md` hoặc ADR nếu đó là quyết định lâu dài

### Bước 8. Kết thúc phiên gọn

Trước khi kết thúc phiên, luôn ghi lại:

- đã thay đổi gì
- đã validate gì
- còn mở gì
- phiên sau nên đọc gì trước

Mục tiêu là phiên sau không phải ghép lại trạng thái từ chat history.

## 2. Ma trận chọn skill

Chỉ dùng bộ skill nhỏ nhất nhưng đủ đúng.

### Bắt đầu phiên / reset ngữ cảnh

- Chính:
  - `context-engineering`
- Hỗ trợ:
  - `agent-skills:using-agent-skills`

### Lên plan

- Chính:
  - `agent-skills:planning-and-task-breakdown`
- Hỗ trợ:
  - `codex-orchestrator`

### Ghi chép docs / rationale

- Chính:
  - `agent-skills:documentation-and-adrs`

### Làm backend

- Chính:
  - `backend-development`
- Hỗ trợ:
  - `fastapi-templates`
  - `agent-skills:api-and-interface-design`
  - `mysql` nếu đụng schema, query, migration

### Làm frontend

- Chính:
  - `frontend-design` hoặc `agent-skills:frontend-ui-engineering`
- Hỗ trợ:
  - `web-design-guidelines`
  - `agent-skills:browser-testing-with-devtools`

### Debug

- Chính:
  - `agent-skills:debugging-and-error-recovery`
- Hỗ trợ:
  - `agent-skills:test-driven-development`

### Review

- Chính:
  - `codex-reviewer`
- Hỗ trợ:
  - `agent-skills:code-review-and-quality`

### Migration / deprecation

- Chính:
  - `agent-skills:deprecation-and-migration`
- Hỗ trợ:
  - `mysql`
  - `backend-development`

### Kết thúc phiên

- Chính:
  - `agent-skills:documentation-and-adrs`
- Hỗ trợ:
  - `codex-orchestrator`

## 3. Prompt mẫu

### A. Prompt bắt đầu phiên

Khi dùng:

- mở phiên mới
- resume sau quãng nghỉ

Skills:

- `context-engineering`
- `agent-skills:using-agent-skills`

Prompt:

```text
Use $context-engineering and $agent-skills:using-agent-skills.
Ground yourself in this repo before proposing changes.

Read in this order:
1. AGENTS.md
2. README.md
3. TASKS.md
4. DECISIONS.md
5. docs/current/CONTEXT_INDEX.md

Then inspect only the files relevant to this task: [insert task].

Return:
- current objective
- constraints
- files likely involved
- recommended skill stack
- next step
```

### B. Prompt lên plan

Khi dùng:

- task medium/high risk
- task nhiều bước
- cần implementation order rõ

Skills:

- `agent-skills:planning-and-task-breakdown`
- `codex-orchestrator`

Prompt:

```text
Use $agent-skills:planning-and-task-breakdown and $codex-orchestrator.
Do a read-only exploration first, then produce a decision-complete plan for: [insert task].

Include:
- goal and success criteria
- assumptions
- implementation order
- validation steps
- docs/tracker updates required
```

### C. Prompt làm backend

Skills:

- `backend-development`
- `fastapi-templates`
- `agent-skills:api-and-interface-design`
- `mysql` nếu cần

Prompt:

```text
Use $backend-development $fastapi-templates $agent-skills:api-and-interface-design.
If this task touches schema, queries, or migrations, also use $mysql.

Implement this bounded backend task: [insert task].

Requirements:
- follow existing backend patterns
- keep API response shapes stable unless explicitly requested
- run focused validation
- update TASKS.md, docs/history/TEST_REPORT.md, docs/history/AGENT_NOTES.md, and docs/history/changelogs.md
```

### D. Prompt làm frontend

Skills:

- `frontend-design` hoặc `agent-skills:frontend-ui-engineering`
- `web-design-guidelines`

Prompt:

```text
Use $frontend-design and $web-design-guidelines.
Implement this bounded frontend task: [insert task].

Requirements:
- preserve the current visual language unless this task is a redesign
- verify responsive behavior
- avoid generic UI output
- update relevant docs/history files after implementation
```

### E. Prompt debug

Skills:

- `agent-skills:debugging-and-error-recovery`
- `agent-skills:test-driven-development`

Prompt:

```text
Use $agent-skills:debugging-and-error-recovery and $agent-skills:test-driven-development.
Reproduce, localize, fix, and guard this issue: [insert bug].

Return:
- root cause
- minimal fix
- validation proof
- regression guard
```

### F. Prompt review

Skills:

- `codex-reviewer`
- `agent-skills:code-review-and-quality`

Prompt:

```text
Use $codex-reviewer and $agent-skills:code-review-and-quality.
Review this change in findings-first order.

Focus on:
- regressions
- logic bugs
- migration/data risks
- missing tests
- contract drift
```

### G. Prompt cập nhật docs

Skills:

- `agent-skills:documentation-and-adrs`

Prompt:

```text
Use $agent-skills:documentation-and-adrs.
Update repository documentation for this change: [insert change].

Requirements:
- capture decisions and rationale, not just edits
- keep canonical docs concise
- keep history docs factual
- preserve the root -> current -> history documentation model
```

### H. Prompt kết thúc phiên

Skills:

- `agent-skills:documentation-and-adrs`
- `codex-orchestrator`

Prompt:

```text
Use $agent-skills:documentation-and-adrs and $codex-orchestrator.
Close this session cleanly.

Do all of the following:
- summarize what changed
- record validation
- update TASKS.md
- update docs/history/TEST_REPORT.md
- update docs/history/AGENT_NOTES.md
- update docs/history/changelogs.md
- list the next best task
```

## 4. Prompt tệ -> Prompt tốt hơn

### Ví dụ 1. Bug fix quá mơ hồ

Tệ:

```text
Fix backend bug.
```

Tốt hơn:

```text
Use $agent-skills:debugging-and-error-recovery and $agent-skills:test-driven-development.
Investigate why `/api/checkins` returns inconsistent results after recent migration work.

First reproduce and isolate the cause.
Then implement the smallest safe fix.
Run focused validation and update the repo history docs.
```

### Ví dụ 2. Backend change quá rộng

Tệ:

```text
Refactor the backend.
```

Tốt hơn:

```text
Use $backend-development $fastapi-templates $agent-skills:api-and-interface-design.
Refactor only the quest completion flow so typed tracker writes are easier to maintain.

Constraints:
- no API response shape changes
- no schema changes
- keep current behavior intact
- run focused smoke checks
```

### Ví dụ 3. Migration request quá chung

Tệ:

```text
Update the database.
```

Tốt hơn:

```text
Use $mysql $backend-development $agent-skills:planning-and-task-breakdown.
Explore the current schema and write a decision-complete migration plan for: [insert migration goal].

Do not implement yet.
Include:
- data risks
- ordering
- rollback expectations
- validation checklist
```

### Ví dụ 4. Docs request quá mơ hồ

Tệ:

```text
Update docs.
```

Tốt hơn:

```text
Use $agent-skills:documentation-and-adrs.
Update the canonical docs to reflect the new backend behavior for [insert feature].

Keep:
- source-of-truth docs concise
- rationale explicit
- history docs updated separately
```

## 5. Checklist theo phiên

### Checklist bắt đầu phiên

- đọc root entrypoints
- đọc đúng canonical docs liên quan
- xác định loại task
- chọn skill stack
- nói rõ assumptions

### Checklist trong lúc thực thi

- giữ scope bounded
- bám pattern hiện có
- validate trước khi chốt
- cập nhật tracker ngay sau progress lớn

### Checklist kết thúc phiên

- update `TASKS.md`
- update `docs/history/TEST_REPORT.md`
- update `docs/history/AGENT_NOTES.md`
- update `docs/history/changelogs.md`
- ghi next best task

## 6. Ma trận validation tối thiểu theo loại task

Dùng phần này như baseline tối thiểu trước khi coi task là xong.

### Task backend

Tối thiểu:

- syntax check cho các file backend đã chạm
- một focused API hoặc service smoke check cho behavior vừa đổi
- update `docs/history/TEST_REPORT.md`

Bổ sung thêm nếu cần:

- schema-aware checks nếu response shape hoặc state interpretation thay đổi
- targeted regression test nếu bug cũ dễ quay lại

### Task migration hoặc database

Tối thiểu:

- syntax check cho migration file và backend files liên quan
- chạy migration upgrade trên local target database
- SQL hoặc schema inspection chứng minh thay đổi cấu trúc đã đúng
- một post-migration smoke check cho behavior bị ảnh hưởng
- update `docs/history/TEST_REPORT.md`

Bổ sung thêm nếu cần:

- duplicate/null audits trước khi hardening
- downgrade verification nếu rollback safety là một phần của task

### Task frontend

Tối thiểu:

- build hoặc syntax validation cho frontend code đã chạm
- một runtime hoặc visual verification cho surface bị đổi
- update `docs/history/TEST_REPORT.md`

Bổ sung thêm nếu cần:

- browser walkthrough nếu task đổi layout hoặc interaction
- targeted component hoặc view-model test nếu repo có

### Task debugging

Tối thiểu:

- reproduce issue hoặc xác định rõ failing condition
- validate rằng fix đã loại bỏ lỗi
- validate thêm một path lân cận có thể bị regression
- update `docs/history/TEST_REPORT.md`

### Task review-only

Tối thiểu:

- inspect diff hoặc changed files trực tiếp
- verify validation evidence nếu nó là phần quan trọng của review
- output theo findings-first

### Task documentation-only

Tối thiểu:

- kiểm tra doc đã phản ánh đúng repo truth hiện tại
- kiểm tra links hoặc references nếu có đổi path
- update `docs/history/changelogs.md`

### Task chỉ để close session

Tối thiểu:

- `TASKS.md` phản ánh đúng trạng thái hiện tại
- validation notes đã current
- changelog đã update
- next recommended step đã rõ

## 7. Glossary ngắn

### Platform-level protocol

Đây là các rule do chính nền tảng hoặc runtime của agent áp đặt.

Ví dụ:

- có những channel nào
- khi nào được gọi tool
- rule về approval hoặc sandbox
- ràng buộc input/output của tool
- hạn chế giữa plan mode và execution mode

Project docs có thể mô tả chúng, nhưng không điều khiển được chúng.

### Repo operating standard

Đây là workflow chuẩn dùng riêng trong repository này.

Ví dụ trong repo này:

- phải đọc doc nào trước
- phải update tracker file nào
- nên dùng prompt guide nào
- nên đóng phiên và ghi chép ra sao

Đây là guidance ở mức project, không phải enforcement ở mức nền tảng.

### Skill

Là một gói workflow hoặc instruction có thể tái dùng cho một loại task.

Ví dụ:

- `context-engineering`
- `backend-development`
- `mysql`
- `agent-skills:documentation-and-adrs`

### Harness

Là môi trường chạy agent bao quanh phiên làm việc, cung cấp tool, mode, channel, và runtime controls.

### Orchestrator

Là agent điều phối:

- đọc context
- chốt scope
- tạo plan
- delegate hoặc sắp thứ tự công việc
- kiểm tra hoàn thành

### Worker

Là agent hoặc session slice tập trung vào việc thực thi một task bounded.

## 8. Default khuyến nghị cho repo này

- Nếu task là backend, migration, hoặc multi-file thì nên plan trước.
- Đụng schema, index, query, migration thì gọi `mysql`.
- Nếu thay đổi dễ làm phiên sau bị mất ngữ cảnh thì phải gọi `documentation-and-adrs`.
- Ưu tiên task nhỏ, bounded, testable thay vì prompt kiểu “sửa hết”.
- Giữ canonical docs ngắn và current; giữ history docs factual.
