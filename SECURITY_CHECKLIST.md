# Security Checklist

- [x] Authentication checked
- [x] Authorization checked
- [x] Role escalation checked
- [x] IDOR checked
- [x] SQL injection checked
- [x] XSS checked
- [x] CSRF checked
- [x] SSTI checked
- [x] SSRF checked
- [x] Path traversal checked
- [x] File uploads checked — no upload surface exists
- [x] Sessions checked
- [x] Cookies checked
- [x] Secrets checked
- [x] Dependencies checked
- [x] Flask configuration checked
- [x] HTTP headers checked
- [x] Bandit checked — required full-tree run reached a formatter error on the surrogate regression fixture; production scan has only the intentional `0.0.0.0` LAN bind
- [ ] pip-audit completed — attempted, but `pypi.org` access failed with `WinError 10013`; advisory result unavailable
- [ ] Semgrep completed — attempted, but rule configuration load failed on this host; no valid findings report
- [x] Codex Security Deep Scan completed — sealed canonical result has 13 findings reconciled in `SECURITY_REPORT.md`
- [x] Repeat current-tree Standard Scan completed — scan `8bf38005-df71-4df8-8fd3-ff554bc45847` sealed with 3 documented findings
- [x] OWASP ZAP checked where possible — unavailable locally; safe localhost baseline completed
- [x] Login throttling checked — known and missing usernames now use the same account bucket and return the same limit response
- [x] Login-attempt storage is bounded — blocked clients cannot allocate fresh username rows; hard row cap and expiry cleanup are covered by tests
- [x] Account-wide login budget checked — rotating client addresses cannot bypass the normalized username limit
- [x] Archived ledger mutation checked — Admin/Cashier delete/cancel paths require active funds
- [x] Request-time authorization revalidation checked — write operations reload session/token/user state inside the transaction
- [x] Expired/revoked session retention checked — 30-day cleanup is covered by regression tests

## Release gate

- [x] No confirmed Critical vulnerabilities
- [x] No confirmed High vulnerabilities after fixes
- [x] Medium findings fixed or documented with deployment constraints
- [x] False positives manually validated and recorded
- [x] Existing business flows preserved by the full test suite
- [x] Super Admin can view/revoke active sessions
- [x] Browser sessions expire absolutely after 24 hours
- [x] Logout revokes copied-cookie access
- [x] API tokens expire and are revoked by password reset
- [x] Full regression suite passes — 219 tests
- [x] Codex Security Deep canonical report attached and reconciled
- [x] Repeat current-tree Standard canonical report attached and reconciled
