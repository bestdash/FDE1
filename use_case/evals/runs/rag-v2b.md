# Run rag-v2b

- Date: 2026-10-25
- Model: anthropic/claude-sonnet-5-5 (price used: $2.0 in / $10.0 out per million tokens)
- Settings: BM25 over ## sections; search_chunks k default 4, max 8; 1000 chars per chunk; max_turns 6; CHUNK_PREFIX=True
- Change in this run: rag-v2 repeat, tokens logged

| # | Kind | Question | Pass | Cited all gold | Calls | Evidence chars | Tokens in | Tokens out | Cost $ | Latency s | Stopped |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | multi-hop | What's the cancellation period for the Vendor04 contract? | yes | yes | 4 | 13,097 | 8,591 | 1,004 | 0.027 | 9.04 | answer |
| 2 | multi-hop | What are the renewal terms of the Vendor10 contract? | yes | yes | 5 | 10,790 | 13,968 | 1,406 | 0.042 | 15.43 | answer |
| 3 | multi-hop | How much did we pay for the Vendor10 product last year? | yes | yes | 4 | 5,763 | 5,939 | 930 | 0.021 | 7.98 | answer |
| 4 | lookup | When does the Vendor05 contract end? | yes | yes | 3 | 5,726 | 5,196 | 856 | 0.019 | 10.83 | answer |
| 5 | lookup | When does the Vendor02 contract end? | yes | yes | 2 | 5,296 | 3,161 | 478 | 0.011 | 5.54 | answer |
| 6 | lookup | What is the price per user in the Vendor07 contract? | yes | yes | 1 | 1,135 | 1,762 | 223 | 0.006 | 3.76 | answer |
| 7 | lookup | Did we include SSO in the Vendor02 contract? | yes | yes | 2 | 3,520 | 2,680 | 291 | 0.008 | 3.88 | answer |
| 8 | lookup | What are my payment terms in the Vendor09 contract? | yes | yes | 2 | 3,685 | 2,815 | 556 | 0.011 | 9.02 | answer |
| 9 | decline | What are the renewal terms of the Vendor03 contract? | yes | yes | 3 | 6,257 | 5,821 | 658 | 0.018 | 8.54 | answer |
| 10 | decline | Who is responsible for security in case of an incident with Vendor04, and on what terms? | yes | n/a | 6 | 29,577 | 32,234 | 1,685 | 0.081 | 25.37 | answer |

## Answers

### 1. What's the cancellation period for the Vendor04 contract?

- Gold: SYN-04-order.md#Terms, SYN-04-terms.md#8. Term and Termination
- Expected terms: 90 days
- Tool calls: search_chunks(Vendor04 cancellation period) → search_chunks(termination for convenience notice cancel order) → search_chunks(Vendor04 Security Ltd. term termination renewal no) → search_chunks(Vendor04 Order Form subscription term fees, 10)

Vendor04 has no standalone cancellation period. It has a non-renewal notice period, and that period is **90 days**.

- **Order Form:** It says that "notwithstanding the Agreement, notice of non-renewal must be given at least 90 days before the end of the current term." It also says the Order Form prevails if it conflicts with the Master Subscription Agreement [SYN-04-order.md#Terms].
- **Master Subscription Agreement:** It sets a shorter 60-day non-renewal notice and renews automatically for successive 12-month periods [SYN-04-terms.md#8. Term and Termination]. The Order Form's 90 days overrides the 60 days.
- **Current term:** It runs from 1 April 2026 to 31 March 2027 [SYN-04-order.md#Subscription Term].
- **Notice deadline:** I counted 90 days back from 31 March 2027, which gives about 31 December 2026. Written notice should be given on or before that date to stop the automatic 12-month renewal. Confirm the exact date with the vendor.

**Other ways to end the contract:** Either party can terminate for material breach by written notice if the breach isn't remedied within a reasonable period [SYN-04-terms.md#8. Term and Termination]. The documents I found don't give a right to cancel early for convenience, and they don't give a cooling-off period.

The signature blocks in the Vendor04 order form appear blank in the copy I found [SYN-04-order.md#Signatures]. You may want to check that you hold a signed copy.

### 2. What are the renewal terms of the Vendor10 contract?

- Gold: SYN-10-renewal.md#Purchase Terms, SYN-10-terms.md#8. Term and Termination
- Expected terms: automatically, 90 days, Customer
- Tool calls: search_chunks(Vendor10 renewal terms) → search_chunks(Vendor10 contract term automatic renewal notice of) → search_chunks(Vendor10 Design Ltd. master agreement fees price i) → search_chunks(term, renewal, termination, subscription period, 1) → search_chunks(Vendor10 Order Form subscription term start date f)

The Vendor10 renewal is automatic for 12-month periods. The Customer can stop it by giving written notice at least 90 days before the term ends.

- **Renewal term:** The Renewal Order Form says the renewal runs from 1 December 2026 to 30 November 2027 (12 months) [SYN-10-renewal.md#Renewal Term]. It follows the original 12-month term, which runs from 1 December 2025 to 30 November 2026 [SYN-10-order.md#Subscription Term].
- **Automatic renewal:** The subscription renews automatically for successive 12-month periods. This is unless the Customer gives written notice of non-renewal at least 90 days before the end of the current term [SYN-10-renewal.md#Purchase Terms]. The text only gives the Customer this right. It doesn't say the Vendor can give notice of non-renewal.
- **Notice deadline (my calculation):** I counted 90 days back from the term end on 30 November 2026. That gives about 1 September 2026 as the latest date for notice to stop the renewal into December 2026. Allow a margin, because the contract doesn't say how the 90 days are counted or how notice must be delivered.
- **Amendments:** The Renewal Order Form can only be changed in writing signed by both parties [SYN-10-renewal.md#Purchase Terms].
- **Precedence:** The Agreement's terms continue to apply unless the renewal form says otherwise. If the two conflict, the renewal form prevails for the renewal [SYN-10-renewal.md#Renewal Summary].
- **Master agreement:** The Master Subscription Agreement's term clause has no renewal or non-renewal provisions. It says only that the agreement continues while any order is in effect. It also covers termination for material breach that isn't cured within 30 days of written notice [SYN-10-terms.md#8. Term and Termination].

The contracts I found don't state renewal pricing or any fee increase. I didn't search the "Products and Fees" section of the order form, so check it for fees. The signature blocks in the copies I saw are blank [SYN-10-renewal.md#Signatures]. If you need to rely on the renewal, ask the vendor for the last signed copy.

### 3. How much did we pay for the Vendor10 product last year?

- Gold: SYN-10-order.md#Products and Fees, SYN-10-renewal.md#Products and Fees
- Expected terms: 16,000
- Tool calls: search_chunks(Vendor10 fees payment) → search_chunks(Vendor10 order form price subscription) → search_chunks(Vendor10 annual fee amount products and fees) → search_chunks(Vendor10 renewal term fee increase)

The contracts don't say what you actually paid. They give the fees that were invoiced, and I don't know today's date, so I can't tell which term counts as "last year". Here is what they state.

- **Original term, 1 Dec 2025 to 30 Nov 2026:** The annual fee is USD 16,000. That is 400 user licences at USD 40 per user per year, with an introductory discount [SYN-10-order.md#Products and Fees] [SYN-10-order.md#Subscription Term]. The fee excludes applicable taxes [SYN-10-order.md#Products and Fees].
- **Renewal term, 1 Dec 2026 to 30 Nov 2027:** The annual fee is USD 18,000. That is 400 user licences at USD 45 per user per year, and the introductory discount no longer applies [SYN-10-renewal.md#Products and Fees] [SYN-10-renewal.md#Renewal Term]. It is invoiced annually in advance [SYN-10-renewal.md#Payment Terms]. It also excludes taxes.

If "last year" falls in the original term, the contracted fee is USD 16,000 before taxes. If it falls in the renewal term, it is USD 18,000 before taxes. If your fiscal or calendar year spans both terms, the amount would be a mix of the two. I haven't tried to work out that split.

Invoices are due within 30 days of the invoice date [SYN-10-order.md#Payment Terms]. The contracts don't include invoices, payment records, or the actual tax amounts. To confirm what was paid, check your accounts payable records or ask the vendor for an invoice and payment statement.

### 4. When does the Vendor05 contract end?

- Gold: SYN-05-renewal.md#Renewal Term
- Expected terms: 30 June 2028
- Tool calls: search_chunks(Vendor05 contract term end date) → search_chunks(Vendor05 Order start date initial term subscriptio) → search_chunks(SYN-05-order)

The Vendor05 contract currently ends on **30 June 2028**, unless it renews automatically.

- **Original order:** The term ran from 1 July 2025 to 30 June 2026 (12 months) [SYN-05-order.md#Subscription Term].
- **Renewal order:** The renewal term runs from 1 July 2026 to 30 June 2028 (24 months). It replaces the previous order form for that period [SYN-05-renewal.md#Renewal Term].
- **Master agreement:** The agreement continues for as long as any Order remains in effect [SYN-05-terms.md#8. Term and Termination]. So it ends when the last order ends, which is 30 June 2028 on the current documents.

**Automatic renewal:** Each order renews automatically for a period equal to its current term. That would be another 24 months. This doesn't happen if either party gives written notice of non-renewal at least 90 days before the end of the term [SYN-05-terms.md#8. Term and Termination]. Counting back 90 days from 30 June 2028 gives about 1 April 2028. That date is my calculation, so please check it. If no notice is given by then, the contract would probably run to 30 June 2030.

**Signatures:** The signature blocks in both the order form and the renewal order form appear blank in the search results [SYN-05-order.md#Signatures] [SYN-05-renewal.md#Signatures]. I can't confirm from these results that the renewal was signed. You may want to get the signed copies from the vendor.

### 5. When does the Vendor02 contract end?

- Gold: SYN-02-order.md#Subscription Term
- Expected terms: 1 March 2026, 36 months, 28 February 2029
- Tool calls: search_chunks(Vendor02 contract term end date) → search_chunks(Vendor02 effective date initial term renewal)

The Vendor02 subscription ends on **28 February 2029**.

- The Order Form says the subscription term starts on 1 March 2026 and runs for 36 months [SYN-02-order.md#Subscription Term].
- Adding 36 months to 1 March 2026 gives 1 March 2029. The last day of the term is therefore 28 February 2029. I calculated this date. The contract doesn't state it.
- The Master Services Agreement says the agreement continues for the term stated in the Order Form, unless it is terminated earlier [SYN-02-terms.md#8. Term and Termination].
- Renewal needs a new written agreement signed by both parties. Nothing renews automatically [SYN-02-terms.md#8. Term and Termination].
- Either party can give written notice of non-renewal at least 30 days before the end of the term [SYN-02-terms.md#8. Term and Termination].
- Either party can also terminate early for an uncured material breach [SYN-02-terms.md#8. Term and Termination].

I found no renewal order form for Vendor02 in the search results.

### 6. What is the price per user in the Vendor07 contract?

- Gold: SYN-07-order.md#Products and Fees
- Expected terms: USD 80
- Tool calls: search_chunks(Vendor07 price per user)

In the Vendor07 Order Form, the price is **USD 80 per user per year**. That covers 250 user licences, which comes to USD 20,000. [SYN-07-order.md#Products and Fees]

The order form lists two add-ons separately, so they aren't part of the per-user price:
- Security add-on: USD 5,000 per year
- Support SLA add-on: USD 5,000 per year

The total annual fee is USD 30,000. [SYN-07-order.md#Products and Fees]

### 7. Did we include SSO in the Vendor02 contract?

- Gold: SYN-02-order.md#Products and Fees
- Expected terms: SSO
- Tool calls: search_chunks(Vendor02 SSO single sign-on) → search_chunks(Vendor02 contract features included security authe)

Yes. The Vendor02 Order Form says the Customer is subscribing to "the Platform package including SSO, AI credits (50,000 per year) and unlimited projects" [SYN-02-order.md#Products and Fees].

The same section gives a total fee of USD 90,000 for the 36-month term. The order form doesn't list SSO as a separate line item or give it a separate price. I didn't find any Vendor02 master terms in the results, so I can't say whether other terms limit or qualify the SSO feature.

### 8. What are my payment terms in the Vendor09 contract?

- Gold: SYN-09-order.md#Payment Terms
- Expected terms: 30 days
- Tool calls: search_chunks(Vendor09 payment terms) → search_chunks(Vendor09 invoices payable within days fees)

Your Vendor09 contract sets these payment terms:

- **Due date:** The Vendor invoices you for the annual fee. Each invoice is due within 30 days of the invoice date. [SYN-09-order.md#Payment Terms] The Master Subscription Agreement says the same. [SYN-09-terms.md#3. Fees and Payment]
- **Currency and method:** You pay in USD by bank transfer to the account stated on the invoice. [SYN-09-order.md#Payment Terms]
- **Disputes:** If you dispute an invoice in good faith, tell the Vendor promptly. You must still pay the undisputed portion on time. [SYN-09-order.md#Payment Terms] The Master Subscription Agreement requires the dispute notice to be in writing. [SYN-09-terms.md#3. Fees and Payment]
- **Taxes:** Fees exclude applicable taxes, duties and similar charges. You pay these, except taxes based on the Vendor's income. [SYN-09-terms.md#3. Fees and Payment]
- **Non-cancellable fees:** Fees can't be cancelled except as the Agreement expressly states. [SYN-09-terms.md#3. Fees and Payment]

The Vendor09 documents I found don't mention late-payment charges or interest.

### 9. What are the renewal terms of the Vendor03 contract?

- Gold: SYN-03-order.md#Terms
- Expected terms: (none)
- Tool calls: search_chunks(Vendor03 renewal terms) → search_chunks(Vendor03 term auto-renew notice of non-renewal) → search_chunks(Vendor03 Analytics Order Form subscription term fe)

**The Vendor03 contract doesn't state any renewal terms in the documents I found.**

- The Vendor03 Order Form gives a fixed subscription term. It starts on 1 February 2026 and ends on 31 January 2027 [SYN-03-order.md#Subscription Term].
- The order form has no clause on automatic renewal, renewal length, renewal pricing, or notice of non-renewal.
- It says the order is governed by the Vendor's online Terms of Service, "as updated from time to time". It also says those terms "are not attached to this order form" [SYN-03-order.md#Terms]. Any renewal or non-renewal rules are probably in those terms.
- The order form prevails over the online terms only "with respect to the products and fees described above" [SYN-03-order.md#Terms]. That doesn't cover renewal.

**Missing document:** the Vendor03 online Terms of Service. I'd ask Vendor03 for the last signed or current copy, and for confirmation of the version that applied on 1 February 2026. Because the terms can be updated from time to time, it's worth getting that confirmation in writing.

I didn't apply the renewal terms of other vendors' contracts (for example Vendor06, Vendor09 and Vendor10), because they are separate agreements.

### 10. Who is responsible for security in case of an incident with Vendor04, and on what terms?

- Gold: (none: decline)
- Expected terms: (none)
- Tool calls: search_chunks(Vendor04 security incident responsibility, 8) → search_chunks(security breach notification obligations data prot) → search_chunks(Vendor04 terms Customer Data security measures, in) → search_chunks(SYN-04 liability, data processing, security addend) → search_chunks(Vendor04 Confidentiality Fees Term and Termination) → search_chunks(Vendor04 Agreement 5. Confidentiality receiving pa)

**Short answer:** The Vendor04 contracts don't say who is responsible for security in an incident. They have no security-incident, breach-notification or data-security clause. I can only point to the general provisions below.

**What the contracts do say**
- **Customer's responsibility:** The Customer is responsible for the acts of its authorised users and for keeping their access credentials secure. [SYN-04-terms.md#2. Services] The Customer also warrants that it has the right to submit the Customer Data to the Services. [SYN-04-terms.md#6. Warranties]
- **Vendor's responsibility:** The Vendor warrants that it will provide the Services with reasonable skill and care. [SYN-04-terms.md#6. Warranties] Apart from that, the Services are provided "as is", and other warranties are disclaimed to the extent the law permits. [SYN-04-terms.md#6. Warranties]
- **Confidentiality:** The receiving party must protect Confidential Information with at least reasonable care. It may disclose it only to personnel and advisers who need to know it and are bound by confidentiality duties. [SYN-04-terms.md#5. Confidentiality] "Customer Data" is defined as all data submitted to the Services. [SYN-04-terms.md#1. Definitions] The definition of Confidential Information is general. It does not say that Customer Data counts as Confidential Information. [SYN-04-terms.md#1. Definitions]

**Liability terms if an incident causes loss**
- Neither party is liable for indirect, incidental, special or consequential damages, or for loss of profits, revenue or data. [SYN-04-terms.md#7. Limitation of Liability]
- Each party's total liability is capped at the total Fees paid under the Order Form giving rise to the claim. [SYN-04-terms.md#7. Limitation of Liability] The Order Form sets an annual fee of USD 40,000. [SYN-04-order.md#Products and Fees] Whether that cap works out to USD 40,000 depends on how much has actually been paid.
- Liability that cannot be limited by law, such as fraud, is not limited. [SYN-04-terms.md#7. Limitation of Liability]
- Unlike some other vendors' terms, the Vendor04 liability section has no carve-out for confidentiality breaches. It excludes only the Customer's obligation to pay Fees from the limits. [SYN-04-terms.md#7. Limitation of Liability]

**Other points**
- Either party may terminate for a material breach that is not remedied within a reasonable period after notice. [SYN-04-terms.md#8. Term and Termination]
- The Order Form lists a "security add-on" and premium support. [SYN-04-order.md#Products and Fees] It gives no detail on what the add-on covers or on any incident-response duties. Nothing in the results defines its scope.
- The Agreement and each Order Form together are the entire agreement. [SYN-04-terms.md#10. General] No separate security terms are referenced in the results I found. If you expect a security addendum, data processing terms, SLA or support policy, ask the vendor for the last signed copy.
