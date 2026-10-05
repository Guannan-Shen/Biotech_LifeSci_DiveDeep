# Runbook: Local Setup and Data-Access Check

Goal: run the project on your own computer, where sec.gov, data.sec.gov, api.fda.gov
and clinicaltrials.gov are usually reachable (the cloud environment blocks them).

## 1. Clone

```bash
git clone https://github.com/Guannan-Shen/Biotech_LifeSci_DiveDeep.git
cd Biotech_LifeSci_DiveDeep
# main holds the latest merged work
```

GitHub Desktop works too: File > Clone repository > URL.

## 2. Check data access (no install needed)

macOS / Linux:

```bash
export SEC_USER_AGENT="Your Name your@email"
python3 scripts/check_data_access.py --save
```

Windows PowerShell:

```powershell
$env:SEC_USER_AGENT = "Your Name your@email"
python scripts\check_data_access.py --save
```

Expected: one `[OK  ]` line per source and exit code 0. `--save` writes sample payloads
to `data/raw/_access_check/` (git-ignored) so the next session can build parsers and
test fixtures from real responses.

| Symptom | Likely cause | Fix |
|---|---|---|
| SEC lines show HTTP 403 | Missing or anonymous User-Agent | Set `SEC_USER_AGENT` with a real name and email |
| `CERTIFICATE_VERIFY_FAILED` | Corporate or university TLS inspection | Point `SSL_CERT_FILE` at your organization's CA bundle |
| Timeouts on everything | Proxy required | Set `HTTPS_PROXY` (urllib honors it) |
| openFDA HTTP 429 | Rate limit without key | Get a free key and set `OPENFDA_API_KEY` |
| ClinicalTrials.gov 403 | Some networks block it | Try another network; it is a public API |

Optional: set `X_BEARER_TOKEN` to test the X API (M13); USAspending is checked for the
adjacent sleeve but does not fail the run.

## 3. Full development install

```bash
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev,data]"
python -m pytest
```

## 4. Share results back

Paste the script's output into the next session, or commit nothing and just report
which lines failed. Sample payloads stay local (git-ignored).
