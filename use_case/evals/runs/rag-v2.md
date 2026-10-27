# Run rag-v2

- Date: 2026-10-24
- Model: anthropic/claude-sonnet-5-5
- Settings: BM25 over ## sections; search_chunks k default 4, max 8; 1000 chars per chunk; max_turns 6
- Change in this run: file, vendor and title prefixed to every chunk

| # | Kind | Question | Pass | Cited all gold | Calls | Evidence chars | Latency s | Stopped |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | multi-hop | What's the cancellation period for the Vendor04 contract? | yes | yes | 3 | 6,133 | 8.64 | answer |
| 2 | multi-hop | What are the renewal terms of the Vendor10 contract? | yes | yes | 5 | 8,647 | 14.21 | answer |
| 3 | multi-hop | How much did we pay for the Vendor10 product last year? | yes | yes | 4 | 5,663 | 7.52 | answer |
| 4 | lookup | When does the Vendor05 contract end? | yes | yes | 3 | 6,561 | 6.84 | answer |
| 5 | lookup | When does the Vendor02 contract end? | yes | yes | 2 | 5,296 | 3.96 | answer |
| 6 | lookup | What is the price per user in the Vendor07 contract? | yes | yes | 1 | 1,135 | 2.69 | answer |
| 7 | lookup | Did we include SSO in the Vendor02 contract? | yes | yes | 2 | 3,520 | 2.93 | answer |
| 8 | lookup | What are my payment terms in the Vendor09 contract? | yes | yes | 2 | 3,777 | 4.88 | answer |
| 9 | decline | What are the renewal terms of the Vendor03 contract? | yes | yes | 3 | 6,258 | 6.98 | answer |
| 10 | decline | Who is responsible for security in case of an incident with Vendor04, and on what terms? | yes | n/a | 9 | 25,801 | 13.82 | answer |

## Answers

### 1. What's the cancellation period for the Vendor04 contract?

- Gold: SYN-04-order.md#Terms, SYN-04-terms.md#8. Term and Termination
- Expected terms: 90 days
- Tool calls: search_chunks(Vendor04 cancellation period) → search_chunks(termination for convenience notice cancel order Ve) → search_chunks(Vendor04 Order Form subscription term start date f)

The Vendor04 contract has no general cancellation period. What it has is a notice period for non-renewal, and that period is **90 days**.

- **Order Form:** It says that, "Notwithstanding the Agreement, notice of non-renewal must be given at least 90 days before the end of the current term." It also says the order form prevails if it conflicts with the Master Subscription Agreement [SYN-04-order.md#Terms].
- **Master Subscription Agreement:** Clause 8.2 sets a 60-day non-renewal notice [SYN-04-terms.md#8. Term and Termination]. The order form overrides this, so 90 days applies.
- **Current term:** It runs from 1 April 2026 to 31 March 2027 (12 months) [SYN-04-order.md#Subscription Term]. Subscriptions renew automatically for successive 12-month periods unless notice is given [SYN-04-terms.md#8. Term and Termination].
- **Deadline:** Counting back 90 days from 31 March 2027 gives **31 December 2026**. This is my own calculation from the stated dates. Written notice should reach the vendor by then to avoid renewal.
- **Early termination:** The only right I found is termination for material breach that isn't remedied within a reasonable period after written notice (clause 8.3). I found no right to cancel for convenience mid-term. I also found nothing on refunds.

If you meant something else by "cancellation", such as a cooling-off period or early exit, the documents I searched don't cover it.

### 2. What are the renewal terms of the Vendor10 contract?

- Gold: SYN-10-renewal.md#Purchase Terms, SYN-10-terms.md#8. Term and Termination
- Expected terms: automatically, 90 days, Customer
- Tool calls: search_chunks(Vendor10 renewal terms) → search_chunks(Vendor10 term auto-renew notice of non-renewal) → search_chunks(Vendor10 Design Ltd. renewal fees price increase A) → search_chunks(Vendor10 Master Subscription Agreement term and te) → search_chunks(Vendor10 Order Form subscription term start date f)

The Vendor10 renewal terms are in the Renewal Order Form. The Master Subscription Agreement has no renewal clause of its own.

- **Automatic renewal:** The subscription renews automatically for successive 12-month periods. This does not happen if the Customer gives written notice of non-renewal at least 90 days before the end of the current term. [SYN-10-renewal.md#Purchase Terms]
- **Who can give notice:** The clause only mentions notice from the Customer. It doesn't give the Vendor a matching right. [SYN-10-renewal.md#Purchase Terms]
- **Current renewal term:** It runs from 1 December 2026 to 30 November 2027 (12 months). [SYN-10-renewal.md#Renewal Term] This follows the original order term of 1 December 2025 to 30 November 2026. [SYN-10-order.md#Subscription Term]
- **Notice deadlines (my calculation, counting back 90 days from each end date):**
  - To stop the 1 December 2026 renewal, notice is due by about 1 September 2026.
  - To stop a further renewal after 30 November 2027, notice is due by about 1 September 2027.
- **Precedence:** If the Renewal Order Form conflicts with the Agreement, the Renewal Order Form prevails for the renewal. Otherwise the Agreement's terms continue to apply. [SYN-10-renewal.md#Renewal Summary]
- **Amendments:** The Renewal Order Form can only be amended in writing signed by both parties. [SYN-10-renewal.md#Purchase Terms]
- **Master Subscription Agreement:** Its term clause says the Agreement continues while any order is in effect. It also covers termination for uncured material breach (30 days' notice) and payment of fees due on expiry. It says nothing about renewal or non-renewal notice. [SYN-10-terms.md#8. Term and Termination]

**Caveats:**
- The signature blocks in the copies I found are blank. [SYN-10-renewal.md#Signatures] Ask the vendor for the last signed copy to confirm the renewal form was executed.
- I found nothing on renewal pricing or fee increases in the results. I did not review the "Products and Fees" section of the order.

### 3. How much did we pay for the Vendor10 product last year?

- Gold: SYN-10-order.md#Products and Fees, SYN-10-renewal.md#Products and Fees
- Expected terms: 16,000
- Tool calls: search_chunks(Vendor10 fees payment) → search_chunks(Vendor10 order form subscription price) → search_chunks(Vendor10 annual fee amount USD products and fees) → search_chunks(Vendor10 renewal term fee price increase)

The contracts don't show what you actually paid. They only state the fees that were agreed, and I don't know what "last year" means in terms of today's date. Nothing in the results covers invoices or payment records.

**What the contracts say**
- **Original Order Form:** The subscription term is 1 December 2025 to 30 November 2026. You ordered 400 user licences at USD 40 per user per year, with an introductory discount. The annual fee is **USD 16,000**, exclusive of taxes. [SYN-10-order.md#Subscription Term] [SYN-10-order.md#Products and Fees]
- **Renewal Order Form:** The renewal term is 1 December 2026 to 30 November 2027. It covers 400 licences at USD 45 per user per year, because the introductory discount no longer applies. The annual fee is **USD 18,000**, invoiced in advance. [SYN-10-renewal.md#Renewal Term] [SYN-10-renewal.md#Products and Fees] [SYN-10-renewal.md#Payment Terms]

**Which figure applies**
- If "last year" means the 2025–26 term, the contracted fee is USD 16,000 plus any applicable taxes.
- If it means the 2026–27 renewal term, the contracted fee is USD 18,000 plus any applicable taxes.
- Taxes are the Customer's responsibility, so the amount actually paid could be higher. [SYN-10-terms.md#3. Fees and Payment]

To confirm what was actually paid, check the Vendor10 invoices and your payment records. That would also show whether any amounts were disputed or adjusted.

### 4. When does the Vendor05 contract end?

- Gold: SYN-05-renewal.md#Renewal Term
- Expected terms: 30 June 2028
- Tool calls: search_chunks(Vendor05 contract term end date) → search_chunks(Vendor05 effective date initial term renewal) → search_chunks(Vendor05 Order Form subscription term start date)

The current term of the Vendor05 contract ends on **30 June 2028**, if the renewal order form is in force.

- The original Order Form ran from 1 July 2025 to 30 June 2026 (12 months) [SYN-05-order.md#Subscription Term].
- The Renewal Order Form replaces it for 1 July 2026 to 30 June 2028 (24 months) [SYN-05-renewal.md#Renewal Term].
- The Master Subscription Agreement has no fixed end date. It continues for as long as any Order remains in effect [SYN-05-terms.md#8. Term and Termination].
- Each order renews automatically for a period equal to its current term. That would be another 24 months, to 30 June 2030. Automatic renewal doesn't happen if either party gives written notice of non-renewal at least 90 days before the term ends [SYN-05-terms.md#8. Term and Termination].
- I computed the notice deadline from that 90-day rule. For a 30 June 2028 end date, notice would be due around 1 April 2028.

I can't tell from the documents whether the renewal order form has been signed. If it hasn't, the original term would end on 30 June 2026. Please check that you have the signed copy.

### 5. When does the Vendor02 contract end?

- Gold: SYN-02-order.md#Subscription Term
- Expected terms: 1 March 2026, 36 months, 28 February 2029
- Tool calls: search_chunks(Vendor02 contract term end date) → search_chunks(Vendor02 effective date initial term renewal)

The Vendor02 subscription ends on **28 February 2029**.

- The Order Form says the subscription term starts on 1 March 2026 and runs for 36 months [SYN-02-order.md#Subscription Term].
- I counted 36 months from 1 March 2026. That gives 1 March 2029 as the first day after the term, so the last day is 28 February 2029.
- The Master Services Agreement continues for the term stated in the Order Form, unless it is terminated earlier [SYN-02-terms.md#8. Term and Termination].

Other terms that affect the end date:
- A renewal needs a new written agreement signed by both parties. The subscription does not renew automatically [SYN-02-terms.md#8. Term and Termination].
- Either party can give written notice of non-renewal at least 30 days before the end of the term [SYN-02-terms.md#8. Term and Termination].
- Either party can end the agreement early for an unremedied material breach [SYN-02-terms.md#8. Term and Termination].

### 6. What is the price per user in the Vendor07 contract?

- Gold: SYN-07-order.md#Products and Fees
- Expected terms: USD 80
- Tool calls: search_chunks(Vendor07 price per user)

In the Vendor07 Order Form, the price is USD 80 per user per year. That covers 250 user licences, which comes to USD 20,000. [SYN-07-order.md#Products and Fees]

The order form also lists two add-ons that are priced separately, not per user:
- Security add-on: USD 5,000 per year
- Support SLA add-on: USD 5,000 per year

The total annual fee is USD 30,000. [SYN-07-order.md#Products and Fees]

### 7. Did we include SSO in the Vendor02 contract?

- Gold: SYN-02-order.md#Products and Fees
- Expected terms: SSO
- Tool calls: search_chunks(Vendor02 SSO single sign-on) → search_chunks(Vendor02 contract features included security authe)

Yes. The Vendor02 Order Form includes SSO. It says the Customer is subscribing to "the Platform package including SSO, AI credits (50,000 per year) and unlimited projects." The total fee for the 36-month term is USD 90,000 [SYN-02-order.md#Products and Fees].

I only found the order form. I didn't search for Vendor02's master terms, so I can't say whether they add conditions on SSO.

### 8. What are my payment terms in the Vendor09 contract?

- Gold: SYN-09-order.md#Payment Terms
- Expected terms: 30 days
- Tool calls: search_chunks(Vendor09 payment terms) → search_chunks(Vendor09 invoices due net days fees)

Under the Vendor09 contract, each invoice is due within 30 days of the invoice date.

- **Invoicing:** The Vendor invoices you for the annual fee. [SYN-09-order.md#Payment Terms] The Master Subscription Agreement says the same about the 30-day due date. [SYN-09-terms.md#3. Fees and Payment]
- **Payment method:** Pay in USD by bank transfer to the account stated on the invoice. [SYN-09-order.md#Payment Terms]
- **Disputes:** If you dispute an invoice in good faith, tell the Vendor. The Master Subscription Agreement requires this notice to be in writing. You must still pay the undisputed portion on time. [SYN-09-order.md#Payment Terms] [SYN-09-terms.md#3. Fees and Payment]
- **Taxes:** Fees exclude applicable taxes, duties and similar charges. You pay these, except for taxes based on the Vendor's income. [SYN-09-terms.md#3. Fees and Payment]
- **Non-cancellable fees:** Fees can't be cancelled except as the Agreement expressly states. [SYN-09-terms.md#3. Fees and Payment]

The Vendor09 documents I found don't mention late-payment charges or interest. I can't say whether any apply.

### 9. What are the renewal terms of the Vendor03 contract?

- Gold: SYN-03-order.md#Terms
- Expected terms: (none)
- Tool calls: search_chunks(Vendor03 renewal terms) → search_chunks(Vendor03 term auto-renew non-renewal notice) → search_chunks(SYN-03 Vendor03 Analytics subscription term fees o)

The Vendor03 contract doesn't state any renewal terms in the documents I can see.

- **Term:** The subscription runs from 1 February 2026 to 31 January 2027 [SYN-03-order.md#Subscription Term].
- **Renewal:** The order form has no clause on renewal, auto-renewal or notice of non-renewal. Its Terms section says only that the order is governed by the Vendor's online Terms of Service, "as updated from time to time", and that these "are not attached to this order form" [SYN-03-order.md#Terms].
- **Conflicts:** The order form prevails over the online terms only "with respect to the products and fees described above" [SYN-03-order.md#Terms]. The order form says nothing about renewal, so any renewal provisions would probably sit in the online terms.

**Missing document:** The Vendor03 Terms of Service aren't in the results, so I can't say whether the subscription renews automatically, what the renewal length is, or what notice period applies. I suggest asking Vendor03 for the last signed copy, or the version of the Terms of Service in force at 1 February 2026. Because those terms can be updated from time to time, you should also ask how changes apply to this order.

The other renewal clauses in the results belong to different vendors (Vendor05, Vendor06, Vendor09 and Vendor10). They don't apply to Vendor03.

### 10. Who is responsible for security in case of an incident with Vendor04, and on what terms?

- Gold: (none: decline)
- Expected terms: (none)
- Tool calls: search_chunks(Vendor04 security incident responsibility) → search_chunks(security breach notification obligations data prot) → search_chunks(Vendor shall maintain security measures; Customer ) → search_chunks(SYN-04 terms liability indemnity confidentiality) → search_chunks(SYN-04 security addendum or incident response term) → search_chunks(Vendor04 Customer Data protection safeguards breac) → search_chunks(Vendor04 Master Subscription Agreement data proces) → search_chunks(Vendor04 5. Confidentiality obligations protect Co) → search_chunks(Vendor04 order form terms support security add-on )

The Vendor04 contracts don't say who is responsible for security in an incident. They have no security-incident, breach-notification, or data-protection terms.

I searched the Vendor04 Master Subscription Agreement and Order Form. I found only these provisions that bear on security:

- **Customer's responsibility:** The Customer is responsible for the acts of its authorised users and for keeping their access credentials secure [SYN-04-terms.md#2. Services].
- **Vendor's service standard:** The Vendor warrants that it will provide the Services "with reasonable skill and care". Apart from what the Agreement expressly states, the Services are provided "as is" [SYN-04-terms.md#6. Warranties]. This is a general performance standard. It doesn't mention security or incidents.
- **Confidential Information:** Each party must protect the other's Confidential Information with at least reasonable care. It may disclose that information only to personnel and advisers who need to know it and are bound by confidentiality duties. It may also disclose it where the law requires, after giving notice where legally permitted [SYN-04-terms.md#5. Confidentiality]. "Customer Data" is defined separately as all data submitted to the Services [SYN-04-terms.md#1. Definitions]. The Agreement doesn't say Customer Data counts as Confidential Information.
- **Liability limits:** Neither party is liable for indirect or consequential damages, or for loss of profits, revenue or data. Each party's total liability is capped at the Fees paid under the Order Form giving rise to the claim. Liability that can't be limited by law, such as fraud, is not limited. The Customer's obligation to pay Fees is not subject to these limits [SYN-04-terms.md#7. Limitation of Liability].
- **The order:** The Order Form lists a "security add-on" and premium support at a USD 40,000 annual fee [SYN-04-order.md#Products and Fees]. It doesn't describe what the add-on covers or any incident-response commitments.

In practice, the Vendor's incident duties are unspecified beyond reasonable skill and care. The Customer is responsible for credentials. Any claim would likely be capped at the Fees paid under the relevant Order Form, and loss of data is excluded.

I found no security schedule, data-processing terms, or support or service-level terms for Vendor04. If any exist, they weren't in the results. I'd suggest asking the vendor for the last signed copy of any security or data-processing addendum, and for the scope of the "security add-on" and "premium support". Both copies of the signature blocks are also unsigned in what I saw.
