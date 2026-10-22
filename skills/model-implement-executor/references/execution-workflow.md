# Execution Workflow

## Required Reading

Before editing code, read:

- `.codex/model-implement/reports/init-airead/shared-context.md`
- `.codex/model-implement/reports/init-airead/business-flows.md`
- `.codex/model-implement/reports/init-airead/db-assessment.md`
- `.codex/model-implement/reports/modules/<module-name>/module-readiness.md`
- `.codex/model-implement/reports/modules/<module-name>/module-relations.md`
- `.codex/model-implement/reports/modules/<module-name>/<screen-name>/frontend-plan.md`
- `.codex/model-implement/reports/modules/<module-name>/<screen-name>/backend-plan.md`
- `.codex/model-implement/prototypes/<module-name>/` prototype image or notes that match the target screen
- `.codex/model-implement/library/定义规则.md`
- matched knowledge-library paths under `.codex/model-implement/library/`
- `.codex/model-implement/memory/shared-rules.md`
- `.codex/model-implement/memory/executor-rules.md`

Use the reports as the implementation contract, but still inspect the target prototype image and similar existing pages as calibration sources. When style details are missing from `frontend-plan.md`, default to the current framework, design system, component library, and similar existing pages for colors, spacing, typography, density, and component styling. Use the prototype to calibrate layout structure, component grouping, relative positions, and explicit visual differences instead of inventing a new style.

Knowledge-library reading is mandatory before editing code. Read `library/定义规则.md`, identify all matched required and lookup-on-use entries for the implementation task, read those specific files, and obey them strictly. Do not treat the knowledge library as optional background. If `library/` exists but `定义规则.md` is missing, matched files cannot be read, or rule priority is unclear, stop before editing code.

## Steps

1. Confirm the target module readiness report allows implementation.
2. Confirm the target screen plans and the module relation plan allow implementation.
3. Enforce the knowledge-library gate: read `library/定义规则.md`, read all matched specific knowledge files, and record the actual paths used.
4. Locate the target screen prototype before editing UI code.
5. Inspect the relevant existing code paths named in the screen plans, including similar pages, shared components, and style files.
6. Implement the smallest coherent frontend and backend change that satisfies the chosen screen plans, follows the matched knowledge-library rules, follows current framework style where the plan is visually underspecified, uses the prototype for layout and explicit differences, and does not break module relations.
7. When style details are not explicitly specified, default to current framework/style-system consistency and do not invent replacement styling.
8. Preserve framework conventions discovered in the codebase.
9. If a plan and its prototype conflict on an implementation-relevant visual or interaction detail, stop and surface the conflict unless the user has already specified which source wins.
10. Run relevant checks or tests.
11. Update the relevant screen or module relation report only with durable facts when the user wants the reports kept in sync.
12. Append useful execution observations to `.codex/model-implement/memory/executor.jsonl`.
13. Promote stable implementation rules to `.codex/model-implement/memory/executor-rules.md` when repeated or user-confirmed.
14. Use `shared_candidate=true` only for execution lessons that should also constrain initialization or planning, because it can bypass the normal private-rule score threshold; otherwise keep them private to executor memory.

## Stop Conditions

Stop and ask for clarification when:

- the target module readiness report is `draft` or `blocked`,
- the target screen plan or module relation report is `draft` or `blocked`,
- `library/` exists but `library/定义规则.md` is missing,
- a matched required knowledge-library file is missing or unreadable,
- knowledge-library rules conflict with user instructions, project rules, or confirmed plans and priority cannot be determined,
- the implementation would contradict `shared-rules.md`,
- the plan depends on a missing API, schema, route decision, or initialization decision,
- the plan, prototype, and current framework style disagree on a material layout, style, interaction, or data-display behavior,
- the requested change risks overwriting unrelated user work.

