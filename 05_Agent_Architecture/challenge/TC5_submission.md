# TC5 submission

## What changed after critique

After Session 9 and the Nov 3 sponsor demo, three things changed. The agent now gets the vendor's document list before it may say a document is missing (false "missing" claims: 9 of 13 to 13 of 13). An answer now counts as good only if it passes all 4 checks: no false "missing", no other vendor, right date, real answer (12 of 13; the sponsor's bar is 9 of 10). The production question got a route: the Anthropic API under the existing agreement. The one remaining failure, another vendor named, is the sponsor's worst case, so it becomes a search filter next week.

## Bring it to work

**Capability:** the contract search (`search_chunks` and `list_documents`) that the contract agent wraps in an MCP server for Claude Desktop, so contract owners can ask about IT contracts from Claude instead of a separate app.

- **Data:** one search returns about 7,400 characters (7,367 measured, up to 4 sections of up to 1,000 characters, max 8). A one-search question needs 2 capability calls as a tool and 3 through MCP (*measured*). Real contracts are longer than the synthetic ones, so this grows.
- **Model or endpoint:** no contract API exists at work; the search is my code on the temporary VM. The model is the Anthropic API under the existing company agreement (decided Nov 10). IT holds the API credential, dedicated to the contract agent; no credential on laptops.
- **Access or approval:** IT to set up API credits for the agent and a way to watch cost (they rejected a separate workspace); a deployment target for the MCP server reachable from Claude Desktop (local over VPN, or a remote endpoint with TLS and company login: to settle with IT security); a sandbox for Code Mode later, if API cost needs cutting.

**Step 5 tokens (*measured*, one search, mean of 3 runs, `use_case/evals/runs/measure-step5-full-pages.json`):** tool 4,996 tokens; MCP 11,513 tokens.

## Step 7 answers

Shown to the sponsor (Head of IT infrastructure), Nov 10. Full row in `use_case/stakeholders.md`.

1. **What would you do differently on Monday?** No more spreadsheet for renewal dates; he checks the drafted vendor questions instead of writing them; copies the contracts mailbox so the agent learns from real threads; fewer people in the loop for routine renewals.
2. **What did I say that you did not believe?** Nothing. He wants to see Code Mode later, for API cost.
3. **What is the worst thing this could do?** Disclosure to a vendor (our discount, internal history, a competitor's name), then a wrong amount, duration or contract version. Next guardrail: a vendor filter in the search.
