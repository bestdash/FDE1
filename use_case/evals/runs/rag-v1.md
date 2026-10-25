# Run rag-v1

- Date: 2026-10-24
- Model: anthropic/claude-sonnet-5-5
- Settings: BM25 over ## sections; search_chunks k default 4, max 8; 1000 chars per chunk; max_turns 6
- Change in this run: baseline: S5 chunks, vendor name only in Parties

| # | Kind | Question | Pass | Cited all gold | Calls | Evidence chars | Latency s | Stopped |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | multi-hop | What's the cancellation period for the Vendor04 contract? | **no** | **no** | 4 | 11,884 | 7.06 | answer |
| 2 | multi-hop | What are the renewal terms of the Vendor10 contract? | **no** | **no** | 8 | 19,637 | 8.36 | max_turns |
| 3 | multi-hop | How much did we pay for the Vendor10 product last year? | yes | yes | 8 | 21,436 | 13.17 | answer |
| 4 | lookup | When does the Vendor05 contract end? | yes | yes | 5 | 7,549 | 10.01 | answer |
| 5 | lookup | When does the Vendor02 contract end? | yes | yes | 7 | 17,216 | 11.09 | answer |
| 6 | lookup | What is the price per user in the Vendor07 contract? | yes | yes | 1 | 981 | 4.24 | answer |
| 7 | lookup | Did we include SSO in the Vendor02 contract? | **no** | **no** | 9 | 15,038 | 8.76 | max_turns |
| 8 | lookup | What are my payment terms in the Vendor09 contract? | yes | **no** | 6 | 17,096 | 11.59 | answer |
| 9 | decline | What are the renewal terms of the Vendor03 contract? | yes | yes | 4 | 9,422 | 9.96 | answer |
| 10 | decline | Who is responsible for security in case of an incident with Vendor04, and on what terms? | yes | n/a | 8 | 25,863 | 16.65 | answer |

## Answers

### 1. What's the cancellation period for the Vendor04 contract?

- Gold: SYN-04-order.md#Terms, SYN-04-terms.md#8. Term and Termination
- Expected terms: 90 days
- Tool calls: search_chunks(Vendor04 cancellation period) → search_chunks(termination for convenience notice cancel order SY) → search_chunks(Vendor04 Security Ltd. term and termination renewa) → search_chunks(Vendor04 order form subscription term start date c)

The Vendor04 contract doesn't give a "cancellation period" in the sense of a right to cancel mid-term. It does set a notice period for stopping automatic renewal.

**Non-renewal notice: 60 days.** Each subscription renews automatically for successive 12-month periods. It doesn't renew if either party gives written notice of non-renewal at least 60 days before the end of the current term [SYN-04-terms.md#8. Term and Termination].

**Termination for breach.** Either party may terminate the Agreement or an affected Order Form by written notice if the other party materially breaches it. The breach must remain unremedied "within a reasonable period after being notified". No fixed number of days is stated [SYN-04-terms.md#8. Term and Termination].

**Not found.** In the sections I retrieved, I found no right to cancel for convenience and no cooling-off period. I also found no subscription term dates for Vendor04. The SYN-04 order excerpts I retrieved cover only the parties and the signature block [SYN-04-order.md#Parties] [SYN-04-order.md#Signatures]. So I can't work out the actual date by which a non-renewal notice would be due. If you need that date, check the full order form for the term. The notice deadline is 60 days before the term ends.

### 2. What are the renewal terms of the Vendor10 contract?

- Gold: SYN-10-renewal.md#Purchase Terms, SYN-10-terms.md#8. Term and Termination
- Expected terms: automatically, 90 days, Customer
- Tool calls: search_chunks(Vendor10 renewal terms) → search_chunks(Vendor10 term auto-renew notice of non-renewal) → search_chunks(Vendor10 Design renewal term start date end date f) → search_chunks(Vendor10 Design Ltd. order form subscription term) → search_chunks(SYN-10-terms term and termination renewal non-rene) → search_chunks(Vendor10 order form initial term fees) → search_chunks(Master Subscription Agreement Vendor10 Customer Co) → search_chunks(Vendor10 Master Subscription Agreement termination)

(max turns reached)

### 3. How much did we pay for the Vendor10 product last year?

- Gold: SYN-10-order.md#Products and Fees, SYN-10-renewal.md#Products and Fees
- Expected terms: 16,000
- Tool calls: search_chunks(Vendor10 fees payment) → search_chunks(Vendor10 order form subscription price) → search_chunks(SYN-10 fees annual amount term start date, 10) → search_chunks(Renewal Order Form renewal term fees price increas) → search_chunks(Vendor10 Design Products and Fees annual fee amoun) → search_chunks(SYN-10-order Subscription Term services start, 10) → search_chunks(introductory discount user licences first year fee) → search_chunks(Vendor10 order subscription term start date ends 1)

The contracts don't show what you actually paid. They only show the fees you agreed to pay. I found no invoices or payment records. I also can't tell which period "last year" means, because I don't know today's date.

**Original order (1 December 2025 to 30 November 2026)**
- You ordered 400 user licences at USD 40 per user per year, with an introductory discount. The annual fee is **USD 16,000**, exclusive of taxes [SYN-10-order.md#Products and Fees].
- The term runs from 1 December 2025 to 30 November 2026 (12 months) [SYN-10-order.md#Subscription Term].
- 400 × USD 40 = USD 16,000, which matches the stated fee.

**Renewal (1 December 2026 to 30 November 2027)**
- The fee is **USD 18,000**: 400 licences at USD 45 per user per year. The introductory discount no longer applies [SYN-10-renewal.md#Products and Fees].
- The renewal term runs from 1 December 2026 to 30 November 2027 [SYN-10-renewal.md#Renewal Term].
- The annual fee is invoiced in advance, with invoices due within 30 days of the invoice date [SYN-10-renewal.md#Payment Terms].

**What this means for "last year"**
- If "last year" means the term that began in December 2025, the contracted fee is USD 16,000 plus any applicable taxes. The renewal text doesn't say when the original order's fee is invoiced.
- Any taxes, and the amount and date of each payment, would be on the invoices or in your accounts payable records. The contracts don't include those.

### 4. When does the Vendor05 contract end?

- Gold: SYN-05-renewal.md#Renewal Term
- Expected terms: 30 June 2028
- Tool calls: search_chunks(Vendor05 contract term end date) → search_chunks(Vendor05 order form subscription term start date m) → search_chunks(Vendor05 renewal extends term new end date) → search_chunks(SYN-05 Renewal Order renewal term starts) → search_chunks(Renewal Order Vendor05 Collaboration subscription )

The Vendor05 subscription currently runs to **30 June 2028**, if the renewal order was signed. The copies I found are unsigned, so please confirm that.

- **Original order:** The term runs from 1 July 2025 to 30 June 2026 (12 months) [SYN-05-order.md#Subscription Term].
- **Renewal order:** The renewal term runs from 1 July 2026 to 30 June 2028 (24 months). It replaces the previous order form for that period [SYN-05-renewal.md#Renewal Term].
- **Signature status:** The renewal says it becomes binding only when both parties' authorised representatives sign it [SYN-05-renewal.md#Renewal Summary]. The signature blocks in the copies I found are blank, in both the renewal and the original order [SYN-05-renewal.md#Signatures] [SYN-05-order.md#Signatures]. If the renewal was never signed, the current term ends on 30 June 2026.
- **Auto-renewal:** Each order renews automatically for a period equal to its current term. This happens unless either party gives written notice of non-renewal at least 90 days before the term ends [SYN-05-terms.md#8. Term and Termination].
  - If the renewal is in force, a 24-month renewal would follow 30 June 2028 unless notice is given.
  - Counting back 90 days from 30 June 2028 puts the notice deadline at about 1 April 2028. That date is my own calculation.

I did not find the Master Subscription Agreement itself, which the renewal refers to. If you need to be certain, ask the vendor for the last signed copy of the renewal order.

### 5. When does the Vendor02 contract end?

- Gold: SYN-02-order.md#Subscription Term
- Expected terms: 1 March 2026, 36 months, 28 February 2029
- Tool calls: search_chunks(Vendor02 contract term end date) → search_chunks(Vendor02 effective date initial term renewal) → search_chunks(Vendor02 Cloud Ltd. order form subscription term s) → search_chunks(SYN-02 Master Services Agreement term and terminat) → search_chunks(SYN-02-order term commencement fees renewal Vendor) → search_chunks(services start and continue for months subscriptio) → search_chunks(Vendor02 Master Services Agreement renewal non-ren)

The Vendor02 order form says the initial subscription term ends on 28 February 2029. I computed that date, and the contract doesn't state it.

The order form says: "The subscription term starts on 1 March 2026 and runs for 36 months." [SYN-02-order.md#Subscription Term]

- **Calculation:** 36 months from 1 March 2026 runs to the end of 28 February 2029.
- **Renewal terms:** The search results include only the title and parties clause of the Vendor02 Master Services Agreement [SYN-02-terms.md#Master Services Agreement]. I couldn't find its term, renewal or termination clauses, so I can't say whether the subscription renews automatically or what notice is needed.
- **Other documents:** The renewal and notice terms I found in other documents belong to other vendors' contracts, so they don't apply here.
- **Signatures:** The Vendor02 order form's signature block is blank in the copy I found [SYN-02-order.md#Signatures]. I can't confirm from these results that it was signed.

To confirm whether the contract renews, ask the vendor for the last signed copy of the Vendor02 Master Services Agreement and the order form.

### 6. What is the price per user in the Vendor07 contract?

- Gold: SYN-07-order.md#Products and Fees
- Expected terms: USD 80
- Tool calls: search_chunks(Vendor07 price per user)

In the Vendor07 order (I'm taking "Vendor07" to mean document SYN-07), the price is **USD 80 per user per year**. That covers 250 user licences, which comes to USD 20,000 a year [SYN-07-order.md#Products and Fees].

The order also has two flat-fee add-ons that are not part of the per-user price [SYN-07-order.md#Products and Fees]:
- Security add-on: USD 5,000 per year.
- Support SLA add-on: USD 5,000 per year.

The total annual fee is USD 30,000. Dividing that by 250 users would give USD 120 per user, but that figure is my own calculation. The contract states the per-user price as USD 80.

The search results don't name the vendor in that document. I matched "Vendor07" to it only by the "SYN-07" file name. If you meant a different document, tell me and I'll look again.

### 7. Did we include SSO in the Vendor02 contract?

- Gold: SYN-02-order.md#Products and Fees
- Expected terms: SSO
- Tool calls: search_chunks(Vendor02 SSO single sign-on) → search_chunks(Vendor02 contract features included security authe) → search_chunks(SYN-02 order Products and Fees package ordered) → search_chunks(Vendor02 Cloud Ltd. order form term fee services) → search_chunks(subscription fee products ordered annual fee Vendo) → search_chunks(SYN-02 services description features subscription ) → search_chunks(Vendor02 Cloud order form Products and Fees user l) → search_chunk() → search_chunks(SYN-02-order Subscription Term and Products and Fe)

(max turns reached)

### 8. What are my payment terms in the Vendor09 contract?

- Gold: SYN-09-order.md#Payment Terms
- Expected terms: 30 days
- Tool calls: search_chunks(Vendor09 payment terms) → search_chunks(Vendor09 invoice due days fees payment) → search_chunks(Vendor09 Storage Inc. order form fees invoice, 10) → search_chunks(SYN-09 late payment interest taxes dispute, 10) → search_chunks(Vendor09 order form payment currency method bank t) → search_chunks(SYN-09-order Payment Terms invoiced annually in ad)

Your Vendor09 Storage Inc. contract says each invoice is due within 30 days of the invoice date.

- **Due date:** "The Vendor will invoice the Customer, and each invoice is due within 30 days of the invoice date." [SYN-09-terms.md#3. Fees and Payment]
- **Fees:** The Customer pays the fees in the applicable Order Form. Fees are non-cancellable except as the Agreement expressly states. [SYN-09-terms.md#3. Fees and Payment]
- **Amount:** The Order Form sets an annual fee of USD 12,000 for 5 TB of storage and standard support. [SYN-09-order.md#Products and Fees]
- **Taxes:** Fees exclude applicable taxes, duties and similar charges. You must pay these, except taxes based on the Vendor's income. [SYN-09-terms.md#3. Fees and Payment] The Order Form says taxes will be added to the invoice where the law requires. [SYN-09-order.md#Products and Fees]
- **Disputes:** You must tell the Vendor in writing about any good-faith invoice dispute. You must still pay the undisputed portion when it is due. [SYN-09-terms.md#3. Fees and Payment]

**Not found:** My searches did not return a "Payment Terms" section in the Vendor09 Order Form. I found nothing on payment method, currency, or invoice timing, such as whether you are billed annually in advance. I also found no late-payment or interest provision in the Vendor09 documents. Check the full signed Order Form for these points. If they aren't there, ask the vendor.

The signature blocks in the Vendor09 documents I saw are blank, so I can't confirm from these results that a signed copy exists.

### 9. What are the renewal terms of the Vendor03 contract?

- Gold: SYN-03-order.md#Terms
- Expected terms: (none)
- Tool calls: search_chunks(Vendor03 renewal terms) → search_chunks(Vendor03 term auto-renew notice of non-renewal) → search_chunks(Vendor03 Analytics order form term, subscription p) → search_chunks(SYN-03 order form terms governing agreement online)

I can't give you the renewal terms for the Vendor03 contract. The Vendor03 order form says nothing about renewal, and the document that would cover it isn't in the results.

**What the Vendor03 order form says**
- The order form is between Vendor03 Analytics Inc. and Customer Co [SYN-03-order.md#Parties].
- The subscription term runs from 1 February 2026 to 31 January 2027 [SYN-03-order.md#Subscription Term].
- The order is governed by the Vendor's online Terms of Service, as updated from time to time. These are not attached to the order form [SYN-03-order.md#Terms].
- If the order form and the online terms conflict, the order form prevails for the products and fees it describes [SYN-03-order.md#Terms].
- The order form has no renewal, auto-renewal or non-renewal notice provision in the sections I found.

**What's missing**
The Vendor03 online Terms of Service aren't in the results, so I can't tell you whether the subscription renews automatically or what notice is needed to stop a renewal. I also can't tell you the renewal length. The signature blocks in the order form are blank, so I can't confirm the order was signed either.

**Other documents to ignore**
Other documents in the set state renewal terms, such as 30, 60 or 90 days' notice and auto-renewal or no auto-renewal. These belong to other vendors' contracts, such as SYN-04, SYN-05, SYN-06, SYN-07, SYN-09 and SYN-10. Nothing links them to Vendor03, so don't rely on them for this contract.

**Suggested next step**
Ask Vendor03 Analytics for the last signed copy of its online Terms of Service, as in force when the order was signed. Ask for any signed renewal order form as well. The renewal terms will be in those documents.

### 10. Who is responsible for security in case of an incident with Vendor04, and on what terms?

- Gold: (none: decline)
- Expected terms: (none)
- Tool calls: search_chunks(Vendor04 security incident responsibility) → search_chunks(security breach notification obligations data prot) → search_chunks(SYN-04 security safeguards Vendor shall protect Cu) → search_chunks(SYN-04 liability, indemnity, incident, responsibil) → search_chunks(Vendor04 Customer Data confidentiality data protec) → search_chunks(Vendor04 order form security addendum, data proces) → search_chunks(SYN-04 terms Services Customer responsibilities te) → search_chunks(Vendor04 Section 5 Section 6 Customer Data securit)

**Short answer:** The Vendor04 contracts I found don't say who is responsible for security in an incident. They contain no security-incident, breach-notification, data-protection or security-responsibility clause.

**What the Vendor04 documents do say**
- **Services:** The Services are "hosted security software services described in an Order Form" [SYN-04-terms.md#1. Definitions]. The Order Form lists "the Business package with SSO, a security add-on and premium support" [SYN-04-order.md#Products and Fees]. Neither document says what the security add-on covers or who handles an incident.
- **Vendor's warranty:** The Vendor warrants only that it will provide the Services "with reasonable skill and care". All other warranties are disclaimed, and the Services are otherwise provided "as is" [SYN-04-terms.md#6. Warranties]. This is the only performance standard I found that could bear on an incident. It doesn't mention security.
- **Customer's warranty:** The Customer warrants that it has the right to submit the Customer Data [SYN-04-terms.md#6. Warranties].
- **Liability limits if an incident causes loss:**
  - Neither party is liable for indirect, incidental, special or consequential damages, or for loss of profits, revenue or data [SYN-04-terms.md#7. Limitation of Liability]. The exclusion of "loss of data" is especially relevant to a data incident.
  - Each party's total liability is capped at the Fees paid under the Order Form giving rise to the claim [SYN-04-terms.md#7. Limitation of Liability]. The Order Form states an annual fee of USD 40,000 [SYN-04-order.md#Products and Fees]. I haven't computed a cap from this, because the contract says "Fees paid", which may differ from the annual fee.
  - Liability that can't be limited by law, such as fraud, stays unlimited. The Customer's obligation to pay Fees isn't subject to the limits [SYN-04-terms.md#7. Limitation of Liability].
- **Confidential Information:** The definition covers non-public information marked or understood to be confidential [SYN-04-terms.md#1. Definitions]. Each party must return or delete the other's Confidential Information on request after termination [SYN-04-terms.md#8. Term and Termination]. The excerpts don't include a confidentiality section that sets security duties.

**What's missing**
I couldn't find a security schedule, data processing agreement or incident-response terms. The Order Form says it is issued under the Master Subscription Agreement and that capitalised terms take their meaning from it [SYN-04-order.md#Parties]. The agreement also says the governing law comes from the Order Form [SYN-04-terms.md#10. General]. Neither document refers to a separate security document.

If you expect incident duties, such as notification timelines, cooperation or cost allocation, ask Vendor04 for its last signed copy of any security or data-protection terms. Ask also for a description of the security add-on. Without those, the contracts leave incident responsibility unaddressed, and the liability limits above are the only terms I found that apply.
