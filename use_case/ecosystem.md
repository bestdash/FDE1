# Someone else's ecosystem

Where your application would actually run, inside your actual firm.

> **Week 1 starts this file. Week 9 finishes it.**
> TC1 Step 6 asks eight questions. The full Week 9 checklist has around thirty,
> and the eight are a strict subset — so nothing here gets thrown away.

Describe patterns, not specifics. "On-prem OpenShift, images from an internal
registry, no public egress" is useful to everyone and identifies nobody. Never
put real hostnames, IPs, or architecture diagrams in this file.

---

## Week 1 — the first eight questions

<!-- Answered in TC1 Step 6. Bring these back from a real conversation. -->

**Who did you ask?** (role, not name)

<!-- your answer here -->

| # | Question | Answer |
| :---: | --- | --- |
| 1 | Where do internal apps run? (k8s, ECS, App Service, a VM someone maintains) | <!-- --> |
| 2 | Which cloud? AWS, Azure, GCP, on-prem, several? | <!-- --> |
| 3 | Is there an internal container registry? | <!-- --> |
| 4 | How do users log in? (Okta, Entra ID, Ping, SAML, homegrown) | <!-- --> |
| 5 | Can the app reach the internet? Egress proxy? Allowlist? | <!-- --> |
| 6 | Where do secrets come from? (Vault, Secrets Manager, Key Vault) | <!-- --> |
| 7 | Who approves a deployment, and what review does it need? | <!-- --> |
| 8 | Is there an approved internal LLM endpoint already? | <!-- --> |

**What surprised you?**

<!-- your answer here -->

**What would you have to change about your app to deploy there?**

<!-- your answer here -->

---

## Week 1 — what your machine told you

<!--
  Paste the egress probe output from Session 1 here. It is evidence, and it
  frequently disagrees with what people believe about their own network.
-->

### Probe run — 2026-10-07 (WSL2 dev machine)

| host | status | signed by | why it matters |
| --- | --- | --- | --- |
| pypi.org | OK | GlobalSign nv-sa | Python packages |
| files.pythonhosted.org | OK | GlobalSign nv-sa | the actual wheel downloads |
| api.openai.com | OK | Google Trust Services | the model API |
| cdn.jsdelivr.net | OK | GlobalSign nv-sa | the CDN the Week 1 frontend uses |
| huggingface.co | OK | Amazon | open weights, Weeks 2 and 8 |
| registry-1.docker.io | OK | Amazon | container images |
| github.com | OK | Sectigo Limited | this repository |

**Verdict:** Open network, public CAs, no proxy. Nothing here will bite you.

### Probe run — 2026-10-11 (WSL2 dev machine, corporate VPN connected)

| host | status | signed by | why it matters |
| --- | --- | --- | --- |
| pypi.org | OK | GlobalSign nv-sa | Python packages |
| files.pythonhosted.org | OK | GlobalSign nv-sa | the actual wheel downloads |
| api.openai.com | OK | Google Trust Services | the model API |
| cdn.jsdelivr.net | OK | Sectigo Limited | the CDN the Week 1 frontend uses |
| huggingface.co | OK | Amazon | open weights, Weeks 2 and 8 |
| registry-1.docker.io | OK | Amazon | container images |
| github.com | OK | Sectigo Limited | this repository |

**Verdict:** Open network, public CAs, no proxy. Same as the run without the VPN.

**What the VPN actually changed:**

- **Split tunnel.** The VPN routes the private 10.0.0.0/8 range plus a few hundred
  specific routes, many of them public addresses. The default route stays on the
  home network. All seven hosts above route over home Wi-Fi, not the VPN.
- **DNS goes corporate.** The VPN pushes the company's resolvers onto every
  adapter. They resolved all seven hosts normally, so there is no DNS filtering of
  anything the course needs.
- **No proxy anywhere.** No proxy environment variables, no WinHTTP proxy, no
  system proxy, no PAC file. The browser goes direct too.
- **jsDelivr's issuer changed** from GlobalSign to Sectigo. That is jsDelivr's
  multi-CDN rotating edges, not interception: both are public CAs.

So this run measures the home network with corporate DNS on top. It does not show
what the corporate network allows outbound. That needs a probe from inside the
deployment environment, or a full-tunnel VPN profile, or the answer to question 5
above.

**Does this match what you were told in the table above?** Where it doesn't, that
gap is worth chasing — it usually means a proxy nobody documented.

---

## Week 9 — the full checklist

<!--
  TC9 extends this same file. Do not start a new one: the point is that the git
  history shows one continuous piece of work from Week 1 to Week 9.
-->

<!-- Week 9 -->
