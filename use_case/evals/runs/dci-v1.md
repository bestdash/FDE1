# Run dci-v1

- Date: 2026-10-25
- Model: anthropic/claude-sonnet-5-5 (price used: $2.0 in / $10.0 out per million tokens)
- Technique: dci
- Settings: contracts/index.md via list_pages; grep_wiki max 40 lines; read_page max 12000 chars; max_turns 6
- Change in this run: DCI: index + grep (40 lines) + read_page, no chunks

| # | Kind | Question | Pass | Cited all gold | Calls | Evidence chars | Tokens in | Tokens out | Cost $ | Latency s | Stopped |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | multi-hop | What's the cancellation period for the Vendor04 contract? | yes | yes | 4 | 18,648 | 14,624 | 717 | 0.036 | 7.08 | answer |
| 2 | multi-hop | What are the renewal terms of the Vendor10 contract? | yes | yes | 4 | 14,003 | 7,521 | 1,019 | 0.025 | 7.75 | answer |
| 3 | multi-hop | How much did we pay for the Vendor10 product last year? | yes | yes | 5 | 14,572 | 11,305 | 1,133 | 0.034 | 9.67 | answer |
| 4 | lookup | When does the Vendor05 contract end? | yes | yes | 5 | 16,004 | 11,715 | 755 | 0.031 | 6.64 | answer |
| 5 | lookup | When does the Vendor02 contract end? | yes | yes | 4 | 12,063 | 10,259 | 754 | 0.028 | 7.54 | answer |
| 6 | lookup | What is the price per user in the Vendor07 contract? | yes | yes | 4 | 12,275 | 10,220 | 355 | 0.024 | 6.81 | answer |
| 7 | lookup | Did we include SSO in the Vendor02 contract? | yes | yes | 3 | 7,785 | 9,313 | 538 | 0.024 | 5.92 | answer |
| 8 | lookup | What are my payment terms in the Vendor09 contract? | yes | yes | 4 | 13,265 | 10,597 | 828 | 0.029 | 8.79 | answer |
| 9 | decline | What are the renewal terms of the Vendor03 contract? | yes | yes | 3 | 6,084 | 8,111 | 628 | 0.023 | 16.73 | answer |
| 10 | decline | Who is responsible for security in case of an incident with Vendor04, and on what terms? | yes | n/a | 4 | 12,473 | 10,402 | 1,189 | 0.033 | 9.25 | answer |

## Answers

### 1. What's the cancellation period for the Vendor04 contract?

- Gold: SYN-04-order.md#Terms, SYN-04-terms.md#8. Term and Termination
- Expected terms: 90 days
- Tool calls: list_pages() → grep_wiki((?i)cancel|terminat|notice) → read_page(SYN-04-order.md) → read_page(SYN-04-terms.md)

The Vendor04 contract (SYN-04) has no general right to cancel for convenience. What it does have is a notice period for non-renewal, which is probably what you mean.

**Non-renewal notice: 90 days.**
- The Master Subscription Agreement says subscriptions renew automatically for successive 12-month periods unless a party gives written notice of non-renewal at least 60 days before the end of the current term [SYN-04-terms.md#8. Term and Termination].
- The Order Form overrides this. It says the order form prevails in a conflict, and that notice of non-renewal must be given at least 90 days before the end of the current term [SYN-04-order.md#Terms].
- The current term ends on 31 March 2027 [SYN-04-order.md#Subscription Term]. Counting back 90 days from that date, the notice deadline is about 1 January 2027. This is my own calculation, and you should confirm it.

**Other points:**
- Fees are non-cancellable and non-refundable, except as the Agreement expressly states otherwise [SYN-04-terms.md#3. Fees and Payment].
- Either party may terminate early only for a material breach that the other party fails to remedy within a reasonable period after written notice [SYN-04-terms.md#8. Term and Termination].
- Notices must be in writing and sent to the address or email address stated in the Order Form [SYN-04-terms.md#9. Notices]. The Order Form I reviewed doesn't list any notice addresses, so check where notices should go.

### 2. What are the renewal terms of the Vendor10 contract?

- Gold: SYN-10-renewal.md#Purchase Terms, SYN-10-terms.md#8. Term and Termination
- Expected terms: automatically, 90 days, Customer
- Tool calls: list_pages() → read_page(SYN-10-order.md) → read_page(SYN-10-renewal.md) → read_page(SYN-10-terms.md)

**Renewal terms for Vendor10 Design Ltd. (SYN-10)**

- **Renewal term:** The renewal runs from 1 December 2026 to 30 November 2027 (12 months). [SYN-10-renewal.md#Renewal Term] It follows the original subscription term, which ends on 30 November 2026. [SYN-10-order.md#Subscription Term]
- **Fees:** The renewal covers 400 user licences at USD 45 per user per year, which comes to USD 18,000 a year. The introductory discount no longer applies. [SYN-10-renewal.md#Products and Fees]
  - The original fee was USD 40 per user, or USD 16,000 a year, with an introductory discount. [SYN-10-order.md#Products and Fees]
  - By my calculation, the renewal is USD 2,000 a year higher than the original fee (18,000 − 16,000).
- **Automatic renewal:** The subscription renews automatically for successive 12-month periods. The Customer can stop this by giving written notice of non-renewal at least 90 days before the end of the current term. [SYN-10-renewal.md#Purchase Terms]
  - For the current renewal term, which ends 30 November 2027, I calculate that the notice deadline is about 1 September 2027 (90 days before the end date). Please check this date before you rely on it.
- **Payment:** The Vendor invoices the annual fee in advance. Invoices are due within 30 days of the invoice date. Fees exclude taxes, which the Customer pays. [SYN-10-renewal.md#Payment Terms]
- **Other terms:**
  - Licences are for the Customer's authorised users only and can't be shared with third parties. [SYN-10-renewal.md#Purchase Terms]
  - The renewal form can only be amended in a writing signed by both parties. [SYN-10-renewal.md#Purchase Terms]
  - The Master Subscription Agreement continues to apply unless the renewal form says otherwise. If the two conflict, the renewal form prevails for the renewal. [SYN-10-renewal.md#Renewal Summary]
  - The Master Subscription Agreement continues while any order is in effect. [SYN-10-terms.md#8. Term and Termination]
  - The Master Subscription Agreement has no renewal or non-renewal provisions of its own. The renewal form is the only source for those terms.

The signature blocks in the copies I reviewed are blank. Confirm that signed versions exist.

### 3. How much did we pay for the Vendor10 product last year?

- Gold: SYN-10-order.md#Products and Fees, SYN-10-renewal.md#Products and Fees
- Expected terms: 16,000
- Tool calls: list_pages() → grep_wiki(Vendor10) → read_page(SYN-10-order.md) → read_page(SYN-10-renewal.md) → read_page(SYN-10-terms.md)

The contracts don't show what you actually paid. They show only the fees that were agreed, and they contain no invoices or payment records. I also can't tell which year "last year" means, because I don't know today's date. Here is what the Vendor10 Design Ltd. documents say.

| Period | Fee | Source |
|---|---|---|
| 1 Dec 2025 – 30 Nov 2026 (original order) | USD 16,000 | [SYN-10-order.md#Products and Fees] |
| 1 Dec 2026 – 30 Nov 2027 (renewal) | USD 18,000 | [SYN-10-renewal.md#Products and Fees] |

- **Original order:** It covers 400 user licences at USD 40 per user per year, with an introductory discount. The annual fee is USD 16,000 [SYN-10-order.md#Products and Fees]. The term runs from 1 December 2025 to 30 November 2026 [SYN-10-order.md#Subscription Term].
- **Renewal:** It covers 400 licences at USD 45 per user per year, and the introductory discount no longer applies. The annual fee is USD 18,000 [SYN-10-renewal.md#Products and Fees]. The renewal term runs from 1 December 2026 to 30 November 2027 [SYN-10-renewal.md#Renewal Term]. Both figures check out: 400 × 40 = 16,000 and 400 × 45 = 18,000.
- **Timing:** The vendor invoices the annual fee, and invoices are due within 30 days of the invoice date [SYN-10-order.md#Payment Terms]. For the renewal, the invoice is issued in advance [SYN-10-renewal.md#Payment Terms]. The documents don't give invoice dates, so I can't say which calendar year a payment fell in. The first invoice could fall in 2025 or 2026.
- **Taxes:** The fees exclude applicable taxes, which are your responsibility [SYN-10-order.md#Products and Fees]. Any tax you paid would be on top of these amounts.

If "last year" means the first term, the contracted fee was USD 16,000 plus any taxes. To confirm what was actually paid, check the vendor's invoices and your payment records.

### 4. When does the Vendor05 contract end?

- Gold: SYN-05-renewal.md#Renewal Term
- Expected terms: 30 June 2028
- Tool calls: list_pages() → grep_wiki(Vendor05) → read_page(SYN-05-order.md) → read_page(SYN-05-renewal.md) → read_page(SYN-05-terms.md)

The Vendor05 contract currently ends on **30 June 2028**, provided the renewal order is signed and no one gives notice of non-renewal.

- **Original order:** The subscription term runs from 1 July 2025 to 30 June 2026 (12 months) [SYN-05-order.md#Subscription Term].
- **Renewal order:** The renewal term runs from 1 July 2026 to 30 June 2028 (24 months). It replaces the previous order form for that period [SYN-05-renewal.md#Renewal Term]. The renewal order says it becomes binding only when both parties' authorised representatives sign it [SYN-05-renewal.md#Renewal Summary]. The copies I have show blank signature lines, so I can't confirm it was signed. If it wasn't, the term ends 30 June 2026 unless the auto-renewal clause below applies.
- **Auto-renewal:** Each order renews automatically for a period equal to its current term. This doesn't happen if either party gives written notice of non-renewal at least 90 days before the end of the current term [SYN-05-terms.md#8. Term and Termination]. For the renewal term ending 30 June 2028, that deadline is about 1 April 2028. I counted back 90 days from 30 June 2028. Without notice, the contract would renew for another 24 months.
- **Master agreement:** The Master Subscription Agreement lasts as long as any order remains in effect [SYN-05-terms.md#8. Term and Termination].

I'd check that you hold a signed copy of the renewal order.

### 5. When does the Vendor02 contract end?

- Gold: SYN-02-order.md#Subscription Term
- Expected terms: 1 March 2026, 36 months, 28 February 2029
- Tool calls: list_pages() → grep_wiki(Vendor02) → read_page(SYN-02-order.md) → read_page(SYN-02-terms.md)

The Vendor02 Cloud Ltd. contract ends on **28 February 2026 + 36 months = 28 February 2029**. That is the last day of the term.

- The Order Form says the subscription term "starts on 1 March 2026 and runs for 36 months" [SYN-02-order.md#Subscription Term].
- I calculated the end date from that. 36 months from 1 March 2026 reaches 1 March 2029, so the last day of the term is 28 February 2029.
- The Master Services Agreement says the agreement continues "for the term stated in the applicable Order Form", unless it is terminated earlier [SYN-02-terms.md#8. Term and Termination]. So the Order Form's term sets the end date.

- **No automatic renewal:** A renewal needs a new written agreement signed by both parties [SYN-02-terms.md#8. Term and Termination].
- **Non-renewal notice:** Either party can give written notice of non-renewal at least 30 days before the end of the term [SYN-02-terms.md#8. Term and Termination]. For a 28 February 2029 end, that notice would be due by about 29 January 2029. I worked that date out myself.
- **Early termination:** Either party can terminate early for an uncured material breach [SYN-02-terms.md#8. Term and Termination].

The copies I have show blank signature lines. The Agreement begins "when signed by both parties" [SYN-02-terms.md#8. Term and Termination], and the Order Form says the platform is made available once both parties have signed [SYN-02-order.md#Order Summary]. I can't confirm from these copies that the contract was signed. If the signing date affects your answer, ask the vendor for the last signed copy.

### 6. What is the price per user in the Vendor07 contract?

- Gold: SYN-07-order.md#Products and Fees
- Expected terms: USD 80
- Tool calls: list_pages() → grep_wiki(Vendor07|Vendor 07) → read_page(SYN-07-order.md) → read_page(SYN-07-terms.md)

The Vendor07 contract prices user licences at **USD 80 per user per year**. The Order Form lists 250 user licences at that rate, which comes to USD 20,000 [SYN-07-order.md#Products and Fees].

That price covers user licences only. The order also includes a Security add-on at USD 5,000 per year and a Support SLA add-on at USD 5,000 per year. The total annual fee is USD 30,000 [SYN-07-order.md#Products and Fees].

### 7. Did we include SSO in the Vendor02 contract?

- Gold: SYN-02-order.md#Products and Fees
- Expected terms: SSO
- Tool calls: list_pages() → grep_wiki((?i)SSO|single sign|Vendor02) → read_page(SYN-02-order.md)

Yes. The Vendor02 Order Form includes SSO. It says the Customer is subscribing to "the Platform package including SSO, AI credits (50,000 per year) and unlimited projects" [SYN-02-order.md#Products and Fees]. The total fee for the 36-month term is USD 90,000 [SYN-02-order.md#Products and Fees].

- **No separate SSO charge:** SSO is listed as part of the package. The order form shows no separate price for it.
- **Signatures:** The copy I have shows blank signature lines for both parties [SYN-02-order.md#Signatures]. I can't confirm from this copy that it was signed. The order says it takes effect once both parties sign [SYN-02-order.md#Order Summary]. You may want to get the last signed copy from the vendor.
- **Master agreement:** The order is governed by the Master Services Agreement, and the order form prevails over it only for the products and fees it describes [SYN-02-order.md#Terms]. My search of the Master Services Agreement (SYN-02-terms.md) found no mention of SSO, so I didn't read it in full.

### 8. What are my payment terms in the Vendor09 contract?

- Gold: SYN-09-order.md#Payment Terms
- Expected terms: 30 days
- Tool calls: list_pages() → grep_wiki((?i)vendor ?09) → read_page(SYN-09-order.md) → read_page(SYN-09-terms.md)

Under the Vendor09 Storage Inc. contract, you pay each invoice within 30 days of the invoice date.

- **Fee and invoicing:** The annual fee is USD 12,000. The Vendor invoices you for it. [SYN-09-order.md#Products and Fees] [SYN-09-order.md#Payment Terms]
- **Due date:** Each invoice is due within 30 days of the invoice date. [SYN-09-order.md#Payment Terms] The Master Subscription Agreement says the same. [SYN-09-terms.md#3. Fees and Payment]
- **Payment method:** You pay in USD by bank transfer to the account stated on the invoice. [SYN-09-order.md#Payment Terms]
- **Taxes:** The fee does not include applicable taxes. These are added to the invoice where the law requires. [SYN-09-order.md#Products and Fees] Under the Master Subscription Agreement you pay these taxes, except taxes based on the Vendor's income. [SYN-09-terms.md#3. Fees and Payment]
- **Disputed invoices:** If you dispute an invoice in good faith, tell the Vendor promptly. The Master Subscription Agreement requires this notice to be in writing. You must still pay the undisputed portion on time. [SYN-09-order.md#Payment Terms] [SYN-09-terms.md#3. Fees and Payment]
- **Non-cancellable fees:** Fees can't be cancelled except as the Agreement expressly allows. [SYN-09-terms.md#3. Fees and Payment]

The contracts don't state an invoice date. They also don't state any late-payment interest or penalty. The subscription term runs from 1 May 2026 to 30 April 2027. [SYN-09-order.md#Subscription Term]

The copies I have show blank signature blocks. I can't confirm from them that the documents were signed.

### 9. What are the renewal terms of the Vendor03 contract?

- Gold: SYN-03-order.md#Terms
- Expected terms: (none)
- Tool calls: list_pages() → grep_wiki((?i)vendor ?0?3) → read_page(SYN-03-order.md)

The Vendor03 contract doesn't state any renewal terms in the documents I have.

- **What the order form says:** The subscription term runs from 1 February 2026 to 31 January 2027 [SYN-03-order.md#Subscription Term]. The order form says nothing about auto-renewal, a renewal term, a notice period for non-renewal, or renewal pricing.
- **Where renewal terms might be:** The order form says it is governed by the Vendor's online Terms of Service, "as updated from time to time." It also says those terms are "not attached to this order form" [SYN-03-order.md#Terms]. Any renewal or termination provisions would most likely be in those terms.
- **What's missing:** Vendor03's online Terms of Service aren't in the documents I searched. There is also no master agreement or renewal order form for Vendor03.

I'd ask Vendor03 for the last signed copy of its Terms of Service, and the version in force when this order was signed. Ask them to confirm in writing whether the subscription renews automatically and what notice you must give to stop a renewal.

The order form does say it prevails over the online terms on conflicts about "the products and fees described above" [SYN-03-order.md#Terms]. Renewal isn't clearly covered by that wording. The 300 licences at USD 60 per user per year (USD 18,000 annually) apply to the stated term [SYN-03-order.md#Products and Fees]. Don't assume those prices carry over to a renewal.

### 10. Who is responsible for security in case of an incident with Vendor04, and on what terms?

- Gold: (none: decline)
- Expected terms: (none)
- Tool calls: list_pages() → grep_wiki(Vendor04) → read_page(SYN-04-order.md) → read_page(SYN-04-terms.md)

The Vendor04 contracts don't say who is responsible for security in an incident, or on what terms. Neither document has a security incident, breach notification, or data protection clause. Neither mentions an incident response process, a security schedule or a data processing addendum.

What the documents do say that touches on security:

- **Customer:** The Customer is responsible for the acts of its authorised users and for keeping their access credentials secure [SYN-04-terms.md#2. Services]. The Customer also warrants that it has the right to submit the Customer Data to the Services [SYN-04-terms.md#6. Warranties].
- **Vendor:** The Vendor must provide the Services "with reasonable skill and care" [SYN-04-terms.md#6. Warranties]. Otherwise the Services are provided "as is", and other warranties are disclaimed to the extent the law permits [SYN-04-terms.md#6. Warranties].
- **Support:** The Vendor provides technical support during its normal business hours and uses reasonable efforts to respond promptly. It gives priority to issues that materially impair use of the Services [SYN-04-terms.md#4. Support]. The Customer must give reasonable information and cooperation to help diagnose problems [SYN-04-terms.md#4. Support]. The Order Form adds premium support and a security add-on, but it gives no detail on what they include, such as response times or incident handling [SYN-04-order.md#Products and Fees].
- **Confidentiality:** Each party must protect the other's Confidential Information with at least reasonable care [SYN-04-terms.md#5. Confidentiality].
- **Liability:** Neither party is liable for indirect or consequential damages, or for loss of profits, revenue or data [SYN-04-terms.md#7. Limitation of Liability]. Each party's total liability is capped at the Fees paid under the Order Form giving rise to the claim [SYN-04-terms.md#7. Limitation of Liability]. Liability that the law does not allow to be limited, such as fraud, is not capped [SYN-04-terms.md#7. Limitation of Liability].
- **Precedence:** If the Order Form and the Master Subscription Agreement conflict, the Order Form prevails [SYN-04-order.md#Terms]. The Order Form says nothing on incident responsibility.

The contracts don't say whether the Vendor must notify you of a breach or within what time. They also don't say who bears remediation costs, or whether the "security add-on" changes any of this. Because liability for data loss is excluded and total liability is capped at the Fees paid, your recovery after an incident would likely be limited. I'd treat that as a reading of the clauses rather than a confirmed outcome.

I'd ask Vendor04 for any security or data processing terms, and for the description of the security add-on and premium support. Those may sit in documents that aren't in this set.
