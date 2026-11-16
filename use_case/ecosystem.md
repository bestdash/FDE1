# The ecosystem you deploy into

Where your application would actually run, inside your actual firm.

> **Week 1 starts this file. Week 9 finishes it.**
> TC1 Step 10 asks eight questions. The full Week 9 checklist has around thirty,
> and the eight are a strict subset — so nothing here gets thrown away.

Describe patterns, not specifics. "On-prem OpenShift, images from an internal
registry, no public egress" is useful to everyone and identifies nobody. Never
put real hostnames, IPs, or architecture diagrams in this file.

---

## Week 1 — the first eight questions

<!-- Answered in TC1 Step 10. Bring these back from a real conversation. -->

**Who did you ask?** (role, not name)

The IT cloud engineer who runs our Azure setup, with the Head of IT infrastructure (the sponsor) and the IT security and platform admin in copy (email thread, Oct 1 to Oct 12).

| # | Question | Answer |
| :---: | --- | --- |
| 1 | Where do internal apps run? (k8s, ECS, App Service, a VM someone maintains) | Planned: an AKS dev cluster in a dedicated resource group. The cluster could not be created: every subnet in the IT VNet gave the same error. A Linux VM was given instead (Oct 7), admin access through Azure Bastion only. The VM is a temporary step (answer Oct 12): fixing the AKS subnet issue may take more time, so the pilot starts on the VM and moves to AKS later. |
| 2 | Which cloud? AWS, Azure, GCP, on-prem, several? | Azure, US region. The first VM attempt failed on Azure capacity in the region; another European region was the fallback, but it needs a new resource group and elevated permissions. |
| 3 | Is there an internal container registry? | No (answer Oct 12): there is no internal registry; IT pulls images directly from Docker Hub. So the image is built on the VM (outbound to the package and image registries), or pushed to a private Docker Hub repository with a company account. Open: which one IT accepts. |
| 4 | How do users log in? (Okta, Entra ID, Ping, SAML, homegrown) | Entra ID. Pilot users connect from Claude Desktop over the corporate network. |
| 5 | Can the app reach the internet? Egress proxy? Allowlist? | Deny by default, inbound and outbound. Each port and host is opened by a ticket to the Network team. I sent the list: inbound HTTPS from the corporate network only; outbound HTTPS to the model API and the identity and file services; DNS; the database port to the managed database. IT is opening the ticket and needs the endpoint name for the inbound HTTPS first. |
| 6 | Where do secrets come from? (Vault, Secrets Manager, Key Vault) | Keeper (VM credentials were shared through it). How secrets reach the running app is not decided yet: IT is checking with the IT SOC team for the way that fits SOC guidelines (Oct 12). |
| 7 | Who approves a deployment, and what review does it need? | Clean secret, dependency and code scans on the private company repo; registration in the authorized-apps registry; the sponsor's written sign-off. |
| 8 | Is there an approved internal LLM endpoint already? | No (answer Oct 12): there is no approved internal LLM, no Azure OpenAI instance and no approved Anthropic API. The network can be opened to the model API, but no model provider is approved. This is the main blocker for the pilot: a model route has to be approved first. |


**What surprised you?**

The rules did not surprise me: the sponsor (Head of IT infrastructure) set them before the build started: Azure US, deny-by-default network with an allowlist by ticket, Entra ID, Keeper for secrets. What surprised me was the platform. The sponsor asked for a Kubernetes cluster (AKS) with a managed PostgreSQL database, so that failed jobs restart on their own and the database is backed up and patched by Azure. The cluster could not be created: every subnet of the IT VNet gave the same error. The first VM attempt then failed on Azure capacity in the region. The app was never expected to run on a single VM, but that is what is available, so the pilot starts as a proof of concept (POC) on a VM. The VM is confirmed as a temporary step until the cluster works (Oct 12). The second surprise came with the same answer: there is no approved model route at all, so the network can be opened to the model API, but the app still has no approved provider to call.

**What would you have to change about your app to deploy there?**

On the planned cluster: nothing. The Kubernetes manifests are written and rehearsed locally; the daily job runs as a CronJob that restarts on failure, and the app connects to the managed database by configuration only.

On the VM (POC, temporary until the cluster works), the code stays the same but how it runs changes:
- Daily job: a systemd timer with restart on failure instead of a CronJob, plus an alert when a daily run does not finish (a missed run means a missed deadline alert, the exact failure the app exists to prevent).
- MCP server: a service with an automatic restart instead of a Kubernetes Deployment.
- Database: the Azure managed PostgreSQL server (PaaS, confirmed), reached from the VM on the database port. No PostgreSQL on the VM.
- Secrets: the method the IT SOC team approves (Keeper Secrets Manager, Key Vault or a restricted file), never `--env-file` from a laptop.
- Image: no internal registry. Built on the VM, or pulled from a private Docker Hub repository (open question).
- 443: IT provides the internal DNS name and the TLS certificate; I give them the endpoint name (the certificate Common Name).
- Model: no model route is approved yet. Once one is, it is a configuration change only (`LLM_MODEL`, and `LLM_API_BASE` for a gateway), because the model call is provider-agnostic.

If the cluster becomes available, the app moves back with the same manifests and no code change.

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

- **Split tunnel.** The VPN routes the private ranges plus a set of
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

## Week 2 — can a local model run here?

Downloading open weights works: `LiquidAI/LFM2.5-350M` downloaded from Hugging Face and ran on my laptop CPU (Intel Core Ultra 5 335, 15 GiB RAM in WSL): 15.13 s for 80 tokens. Plausible at the firm only if: the model vendor passes a vendor review (security certification, third-party risk review), the licence fits (this one becomes paid above a company revenue threshold), and the pilot VM has enough CPU or a GPU for a 4 to 8B model. The expert's preference (Oct 16) is a capable hosted model through an approved route instead.

## Week 3: what retrieval needs approved

BM25 needs no model and no index service, so the retrieval step needs no approval. Dense was measured with a local embedding model (bge-small-en-v1.5 through fastembed): embedding tokens 0, measured, nothing sent. At work it would need the same vendor review as any local model (Week 2). Still blocked: the answer model route (Week 1, question 8). New this week: retrieval sends contract sections to the answer model, not only structured fields, so the route request must cover contract text. Open with the sponsor and IT security after about Nov 4: may contract text go to a private endpoint in our own cloud under an SLA?

## Week 6: who can write to what the app reads

| Source | Where it enters the app | Who can write there | Trusted? |
| --- | --- | --- | --- |
| The user's question | `answer_contract_question` in `app.py`, and tool arguments from Claude Desktop | Any contract owner with a Claude license. Only contract owners should get access to the app | Partly: internal users, but they may paste vendor text. Separate gap: any owner can ask about another owner's contracts, and so can anyone who reaches the MCP server. Needs the permission filter (search only the contracts this user may see). |
| The contract files `SYN-*.md` | loaded into `PAGES` in `retrieval.py` | Whoever curates the corpus; in the real app, vendors write the contracts | No: vendors write them. Impact low: a planted instruction is unlikely (bad for the vendor's reputation), an attacker who replaces a file must know the app exists, and nothing leaves without the owner's approval (the app cannot send email). |
| `index.md` | read by `list_documents` | Whoever curates the corpus | Partly: built by my code from the contract files, so its titles carry the same small risk as the contract files. |
| The tool descriptions | `RAG_TOOLS` in `retrieval.py`, also served over MCP | You, and anyone who can edit the MCP server or the app source code | Yes, if every change goes through review in the private repo. Impact high if not: the model follows tool descriptions without question. |
| Real app: shared contracts mailbox | the watcher reads new emails and attachments | Anyone who can send an email to it, inside or outside the company: a vendor can hide an instruction in the message or an attachment | No: anyone can email it. Impact low, as for the contract files: the owner approves every draft. |
| Real app: database fields | values the app stores and later puts into a prompt (extracted terms, owner notes, dialogue replies) | The app itself (extraction from contracts and emails), contract owners through the dialogue, database admins | Partly: written by my code and by internal owners, but text extracted from contracts and emails is No (stored injection). Impact low, as for the contract files. |

### Doors

- Indirect injection: tested. A hidden instruction in a contract, 0 of 8 on the local model, 0 of 8 on a deliberately weakened copy. The real failure was cross-vendor retrieval, found with no attacker: the fix is the vendor filter in the search. The note did reach the model: a traced run on Nov 14 retrieved the poisoned section (Vendor04 Products and Fees).
- Tool description: tested. Two poisoned descriptions of the search tool (the same words the MCP server serves), run through the local agent loop: 0 of 16 leaks, the same as with no poison. But the descriptions changed the model's tool calls in every run, so they must stay in the reviewed private repo. `leaked()` reads only the answer, not the tool arguments. In the course app the only tool searches our own contracts, so an argument cannot take data out; in Claude Desktop with other connectors it could.
- Sandbox escape: closed. The app never runs code the model writes.
- The hosted model through Claude Desktop: not tested. The course rule and the providers' policies forbid attack prompts on the hosted model. The vendor filter in the search protects this path too.
- The internet: closed. The app has no web tool.
- Shared contracts mailbox (real app): not tested, because the course app has no mailbox. Planned controls: email text is data, never instructions; the owner approves every draft before it is sent (the human step in the ladder).

Week 6 finding (Level 0): the approved model route is a closed API, so there is no logit access and constrained decoding is not available in production. The one closed-set output (`message_type`) is picked by code instead.

---

## Week 9 — the full checklist

<!--
  TC9 extends this same file. Do not start a new one: the point is that the git
  history shows one continuous piece of work from Week 1 to Week 9.
-->

<!-- Week 9 -->
