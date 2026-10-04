# Handoff

`qa_gate.py` is the single machine decision for implementation QA. It checks the local run and evidence manifest, artifact bytes and PNG structure, selected source fingerprint, current implementation captures, viewport × DPR, run/iteration ownership, named regions, score evidence, check-result artifacts, preservation items, E comparison conditions, F dimension semantics, and serious-difference repair history.

A `verified` result means those machine-checkable conditions passed and the report declares sufficient human/agent observations and scores. It does not prove the capture came from an unmodified browser, that an observer actually assessed its content, that text/check claims are truthful, or that the design judgment is correct. Report checks run, route/scope, new files, statuses and unresolved limitations. Use `needs-repair` for measured regression or low scores; `unverified` for unavailable, stale, missing or unobserved evidence.

A Research task completes with traceable sources, observation limits and actionable design guidance. Implementation completes only when the relevant browser captures and preserved behaviors have been checked; E additionally requires a matched reference screenshot and F requires comparison with the adopted design intent. Publishing is only part of the handoff when the user requested it.
