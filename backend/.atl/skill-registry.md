# Skill Registry

**Delegator use only.** Any agent that launches sub-agents reads this registry to resolve compact rules, then injects them directly into sub-agent prompts. Sub-agents do NOT read this registry or individual SKILL.md files.

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| When creating a pull request, opening a PR, or preparing changes for review. | branch-pr | /home/arturoa-dev/.config/opencode/skills/branch-pr/SKILL.md |
| When writing Go tests, using teatest, or adding test coverage. | go-testing | /home/arturoa-dev/.config/opencode/skills/go-testing/SKILL.md |
| When creating a GitHub issue, reporting a bug, or requesting a feature. | issue-creation | /home/arturoa-dev/.config/opencode/skills/issue-creation/SKILL.md |
| When user says "judgment day", "judgment-day", "review adversarial", "dual review", "doble review", "juzgar", "que lo juzguen". | judgment-day | /home/arturoa-dev/.config/opencode/skills/judgment-day/SKILL.md |
| When user asks to create a new skill, add agent instructions, or document patterns for AI. | skill-creator | /home/arturoa-dev/.config/opencode/skills/skill-creator/SKILL.md |
| creating Django models/views/serializers/APIs, ORM/migration debugging, performance, auth, tests, DRF tasks | django-expert | /home/arturoa-dev/Desktop/Tesis Project/.agents/skills/django-expert/SKILL.md |

## Compact Rules

### branch-pr
- Every PR MUST link an approved issue (`Closes/Fixes/Resolves #N`).
- Every PR MUST have exactly one `type:*` label.
- Branch names MUST match `^(feat|fix|chore|docs|style|refactor|perf|test|build|ci|revert)\/[a-z0-9._-]+$`.
- Follow conventional commits: `type(scope): description` (or `type: description`).
- Run shellcheck on modified scripts before opening PR.
- Include summary bullets, changes table, and test plan in PR body.

### go-testing
- Prefer table-driven tests for pure/branching logic.
- Test Bubbletea state transitions via direct `Model.Update()` assertions.
- Use `teatest.NewTestModel()` for interactive TUI flows.
- Use golden-file tests for rendered output and keep them in `testdata/`.
- Mock side effects via interfaces; use `t.TempDir()` for filesystem isolation.
- Cover success/error paths explicitly and include edge-case inputs.

### issue-creation
- Always use issue templates (blank issues disabled).
- New issues must start with `status:needs-review`; PR work waits for `status:approved`.
- Classify correctly: bug → bug template, feature → feature template, questions → Discussions.
- Fill all required fields and pre-flight checks before submit.
- Search duplicates before creating new issue.
- Keep repro steps and expected vs actual behavior explicit.

### judgment-day
- Run two independent blind judges in parallel for adversarial review.
- Synthesize as Confirmed/Suspect/Contradiction; only confirmed blockers gate approval.
- Classify warnings as real vs theoretical; theoretical ones are INFO-only.
- After fixes, re-judge in parallel; do not commit/push before re-judgment completes.
- Ask user before applying confirmed fixes after Round 1.
- Escalate only after user decision when issues persist after two iterations.

### skill-creator
- Create skills only for reusable, non-trivial patterns.
- Use `skills/{skill-name}/SKILL.md` with complete frontmatter.
- Keep critical patterns explicit and actionable; examples minimal.
- Prefer local references over web links in `references/`.
- Follow naming conventions (`{technology}`, `{action}-{target}`, etc.).
- Register new skills in project agent instructions/index.

### django-expert
- Keep business rules out of views; move to services/managers/selectors.
- Use `select_related`/`prefetch_related` proactively to avoid N+1 queries.
- Use serializers/forms as single source of input validation.
- Enforce auth/permissions explicitly on DRF endpoints.
- Keep migrations clean and reversible; never edit applied migrations.
- Add deterministic tests for models, serializers, permissions, and API contracts.

## Project Conventions

| File | Path | Notes |
|------|------|-------|
| — | — | No convention index files detected in `/home/arturoa-dev/Desktop/Tesis Project/backend` (`AGENTS.md`, `agents.md`, `CLAUDE.md`, `.cursorrules`, `GEMINI.md`, `copilot-instructions.md`). |
