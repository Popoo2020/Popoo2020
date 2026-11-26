# Contributing

Start with one reproducible case. Explain the workforce event, the observed assignment, the expected decision and why the existing result is wrong. Use synthetic identifiers and provider-shaped fixtures; remove credentials, employee information and real tenant/account identifiers.

From this project directory:

```bash
python -m unittest discover -s tests -v
python -m identity_governance demo --output build/contributor-review
python -m identity_governance verify --bundle build/contributor-review/mover
```

Add a regression that demonstrates a meaningful failure before fixing it. Keep provider-specific interpretation in `providers.py` or `imports.py`; do not relax the planner's completeness or approval checks to accommodate an unresolved export.

Document whether a change has been checked against synthetic fixtures, sanitized real exports or an authorized live environment. Unit tests cannot establish that an API permission, pagination flow or cloud mutation works. A future live connector needs approved test resources, provider references and sanitized collection/read-back evidence.

Pull requests should explain the problem, resulting behaviour, validation and remaining limitations. Do not replace the committed example outputs without regenerating and checking them from the supplied scenario.
