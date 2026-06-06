# Sổ tay Codex dùng chung và thư viện prompt

Đây là bản generic tiếng Việt cho workflow Codex.

Dùng khi:

- anh muốn một khung dùng chung cho nhiều repo
- repo chưa có workflow nội bộ rõ
- anh muốn lấy prompt trung tính rồi mới chỉnh theo project

Nếu repo đã có workflow riêng rõ ràng, nên ưu tiên bản repo-first.

## 1. Quy trình phiên làm việc dùng chung

### Bước 1. Đọc rules trước

Bắt đầu bằng:

1. file rules của repo
2. README hoặc mô tả project
3. task tracker hoặc issue hiện tại
4. decision log hoặc note kiến trúc
5. sau đó mới đến file theo task

Nếu repo không có rules file rõ ràng, cần nói rõ điều đó trước khi làm.

### Bước 2. Ground codebase

Trước khi plan hay code:

- xác định subsystem liên quan
- đọc các file liên quan
- tìm một pattern sẵn có để bám theo
- xác định task thuộc loại planning, implementation, debugging, review, documentation, hay migration

### Bước 3. Khóa contract của task

Phải nêu rõ:

- goal
- success criteria
- scope
- constraints
- risks

Không được tự bù requirements quan trọng một cách im lặng.

### Bước 4. Plan nếu task không còn trivial

Nên plan trước nếu task:

- chạm nhiều file
- đổi behavior
- đổi API hoặc schema
- cần thứ tự thực hiện rõ
- cần validation không đơn giản

### Bước 5. Thực thi theo lát cắt bounded

- giữ slice nhỏ
- tránh thay đổi ngoài lề
- bám convention hiện có
- validate từng slice trước khi chốt

### Bước 6. Xác minh

Thứ tự nên là:

1. syntax hoặc type checks
2. focused tests hoặc smoke checks
3. review rộng hơn nếu rủi ro đủ cao

### Bước 7. Ghi lại ngữ cảnh cho phiên sau

Cập nhật tracker, validation notes, và changelog theo mô hình docs của repo hiện tại.

### Bước 8. Kết thúc phiên sạch

Luôn ghi lại:

- đã đổi gì
- validate ra sao
- còn gì mở
- next step là gì

## 2. Ma trận chọn skill dùng chung

### Bắt đầu phiên

- `context-engineering`
- `agent-skills:using-agent-skills`

### Lên plan

- `agent-skills:planning-and-task-breakdown`
- `codex-orchestrator`

### Làm backend

- `backend-development`
- `fastapi-templates` nếu dùng FastAPI
- `agent-skills:api-and-interface-design` nếu đụng contract công khai
- `mysql` nếu đụng MySQL schema hoặc query

### Làm frontend

- `frontend-design`
- `agent-skills:frontend-ui-engineering`
- `web-design-guidelines`

### Debug

- `agent-skills:debugging-and-error-recovery`
- `agent-skills:test-driven-development`

### Review

- `codex-reviewer`
- `agent-skills:code-review-and-quality`

### Documentation

- `agent-skills:documentation-and-adrs`

### Migration / deprecation

- `agent-skills:deprecation-and-migration`
- `mysql`
- `backend-development`

## 3. Prompt mẫu dùng chung

### A. Prompt mở phiên

```text
Use $context-engineering and $agent-skills:using-agent-skills.
Ground yourself in this repository before proposing changes.

Read the repository rules, README, active task tracker, and decision log first.
Then inspect only the files relevant to this task: [insert task].

Return:
- current objective
- key constraints
- likely files involved
- recommended skill stack
- next step
```

### B. Prompt lên plan

```text
Use $agent-skills:planning-and-task-breakdown and $codex-orchestrator.
Do a read-only exploration first, then write a decision-complete plan for: [insert task].

Include:
- goal
- success criteria
- assumptions
- implementation order
- validation plan
```

### C. Prompt implement

```text
Use the skills best matched to this task.
Implement this bounded change: [insert task].

Requirements:
- follow existing project patterns
- keep scope tight
- validate the changed behavior
- update the local task and documentation files before closing
```

### D. Prompt review

```text
Use $codex-reviewer and $agent-skills:code-review-and-quality.
Review this change in findings-first order.

Focus on:
- regressions
- behavior bugs
- missing validation
- contract drift
```

### E. Prompt closeout

```text
Use $agent-skills:documentation-and-adrs.
Close this session cleanly.

Record:
- what changed
- validation
- remaining issues
- next recommended step
```

## 4. Prompt tệ -> Prompt tốt hơn

Tệ:

```text
Fix it.
```

Tốt hơn:

```text
Use the skills that match this task.
First inspect the relevant code and identify the root issue for: [insert bug].
Then implement the smallest safe fix, validate it, and update the repo docs/tracker.
```

Tệ:

```text
Refactor everything.
```

Tốt hơn:

```text
Refactor only [insert subsystem] to improve [insert concrete goal].

Constraints:
- no unrelated cleanup
- no public contract changes unless explicitly approved
- run focused validation
```

## 5. Checklist dùng chung

### Bắt đầu

- đọc rules của project
- chỉ đọc file liên quan
- xác định loại task
- chọn skill stack
- nêu assumptions

### Thực thi

- giữ scope bounded
- bám pattern của project
- validate thay đổi

### Kết thúc

- cập nhật task tracking
- cập nhật validation notes
- cập nhật changelog/history
- ghi next step
