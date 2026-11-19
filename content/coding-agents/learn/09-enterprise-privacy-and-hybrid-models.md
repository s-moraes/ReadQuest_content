# Enterprise Privacy, Proxies & Hybrid Model Gateways

In regulated industries (fintech, healthcare, enterprise SaaS), developers cannot always point a CLI agent directly at public consumer APIs. Both **Google Antigravity** and **Claude Code** support enterprise routing, zero-data-retention (ZDR) endpoints, and strict network boundaries.

---

## 1. Enterprise Cloud Gateways (Vertex AI & Bedrock)

Instead of individual developer API keys, enterprise teams route agent traffic through their own cloud VPC/IAM boundary:
- **Claude Code:** Supports **Amazon Bedrock**, **Google Cloud Vertex AI**, and custom **LLM Gateways** (e.g., LiteLLM) via environment variables (`CLAUDE_CODE_USE_BEDROCK=1`, `CLAUDE_CODE_USE_VERTEX=1`, `ANTHROPIC_BASE_URL`).
- **Google Antigravity:** Integrates with Google Cloud **Vertex AI** endpoints and enterprise identity/policy controls.

Benefits for senior teams:
- Unified IAM/SSO auditing and per-team cost attribution.
- Data residency guarantees and zero training on proprietary source code.

---

## 2. Operating Behind Corporate Proxies & Air-Gapped Networks

When running on locked-down Linux workstations:
- Configure `HTTP_PROXY` / `HTTPS_PROXY` and custom corporate CA bundles (`NODE_EXTRA_CA_CERTS` / `SSL_CERT_FILE`) so CLI tool calls and MCP HTTPS transports trust internal TLS certificates.
- Set Antigravity's **Internet Access Policy** to `deny` (or restrict the **Browser Allowlist** to internal domains only) so agents cannot make unexpected outbound requests.

---

## 3. Secret & PII Hygiene Checklist

Even behind an enterprise gateway, maintain strict local hygiene:
- Block `.env*`, `~/.ssh/**`, `~/.aws/**`, and `*.pem` / `*.key` via `permissions.deny`.
- Scrub customer PII from production logs *before* piping them into `claude -p` or attaching them to an Antigravity chat canvas.
