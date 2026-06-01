import hashlib
import hmac
import json
import os
import urllib.request
from datetime import datetime, timezone

# ── Submission fields ──────────────────────────────────────────────────────────
SUBMISSION = {
    "name": "Aria Zade",
    "email": "Aria.zade22@gmail.com",
    "resume_link": "https://github.com/tech-spectra",
    "repository_link": os.environ["REPOSITORY_LINK"],   # injected by CI
    "action_run_link": os.environ["ACTION_RUN_LINK"],   # injected by CI
}

ENDPOINT = "https://b12.io/apply/submission"
_SECRET   = os.environ.get("SIGNING_SECRET", "hello-there-from-b12").encode()

# ── Build payload ──────────────────────────────────────────────────────────────
payload = {
    **SUBMISSION,
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") +
                 f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z",
}

# Canonical form: keys sorted, no extra whitespace, UTF-8
body: bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

# ── Compute HMAC-SHA256 signature ──────────────────────────────────────────────
hex_digest = hmac.new(_SECRET, body, hashlib.sha256).hexdigest()
signature  = f"sha256={hex_digest}"

# ── POST ───────────────────────────────────────────────────────────────────────
req = urllib.request.Request(
    ENDPOINT,
    data=body,
    headers={
        "Content-Type": "application/json",
        "X-Signature-256": signature,
    },
    method="POST",
)

with urllib.request.urlopen(req) as resp:
    response_body = json.loads(resp.read().decode("utf-8"))

print("Submission receipt:", response_body["receipt"])
