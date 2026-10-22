# Memory Cycle

## Private and Shared Memory

The model-implement skills maintain private memory:

- `memory/init.jsonl`
- `memory/init-rules.md`
- `memory/model-implement.jsonl`
- `memory/model-implement-rules.md`
- `memory/executor.jsonl`
- `memory/executor-rules.md`
- `memory/fix.jsonl`
- `memory/fix-rules.md`
- `memory/review.jsonl`
- `memory/review-rules.md`
Shared memory is synthesized by `model-implement-init`:

- `memory/shared-memory.md`
- `memory/shared-rules.md`

Shared rules are filtered synthesis output, not a union of all private rules.

## What to Record

Record only compact, reusable facts:

- User-confirmed preferences.
- Repeated project conventions.
- Framework-specific implementation constraints.
- Database/schema design lessons.
- Mistakes that were corrected and should not recur.
- Acceptance criteria patterns that the user repeatedly asks for.

Do not record:

- Secrets, passwords, tokens, or connection strings.
- Raw production data.
- Large copied source snippets.
- One-time guesses that have not been confirmed or validated.

## Rule Promotion

Use this path:

1. Observation in JSONL.
2. Candidate rule when repeated or user-confirmed.
3. Private rule when stable for that skill.
4. Shared rule when useful across initialization, planning, implementation, issue fixing, or review.

Prefer conservative promotion. A user instruction such as "以后都按这个来" can be promoted faster.

When a private observation is clearly cross-phase, log it with `--shared-candidate` so the promoted private rule carries `shared_candidate=true`. Use this flag sparingly because it allows the entry to bypass the normal score threshold during private rule promotion:

```powershell
python .codex/skills/model-implement-init/scripts/memory_cycle.py log --stream .codex/model-implement/memory/init.jsonl --role init --kind rule_candidate --text "Rule text" --shared-candidate
```

## Synthesis

When synthesizing shared rules:

- Read the private rule files for initialization, planning, implementation, issue fixing, and review.
- Include a rule only when it appears in at least two skill contexts, or when a private rule explicitly carries `shared_candidate=true`.
- Do not treat `shared-rules.md` as a raw union of private rules.
- Keep initialization-only discovery habits in `init-rules.md` unless they affect planning or execution.
- Keep planning-only interpretation habits in `model-implement-rules.md` unless they affect initialization or execution.
- Keep executor-only workarounds in `executor-rules.md` unless they affect earlier phases.
- Keep fix-only local workaround habits in `fix-rules.md` unless they affect earlier phases or future implementations.
- Keep review-only local heuristics in `review-rules.md` unless they affect earlier phases or downstream execution.
- Put reusable implementation patterns into the knowledge library with `knowledge-library`; do not synthesize them through a deleted reuse private memory stream.
