# Run dense-v1

- Date: 2026-10-25
- Model: anthropic/claude-sonnet-5-5 (price used: $2.0 in / $10.0 out per million tokens)
- Technique: dense
- Settings: bge-small-en-v1.5 via fastembed (local, 384 dims, embedding tokens 0: nothing sent); same ## chunks with prefix as rag (173); cosine; search_chunks k default 4, max 8; 1000 chars shown; max_turns 6
- Change in this run: dense: bge-small-en-v1.5 local, same chunks, cosine

| # | Kind | Question | Pass | Cited all gold | Calls | Evidence chars | Tokens in | Tokens out | Cost $ | Latency s | Stopped |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | multi-hop | What's the cancellation period for the Vendor04 contract? | yes | yes | 2 | 11,682 | 5,333 | 596 | 0.017 | 12.68 | answer |
| 2 | multi-hop | What are the renewal terms of the Vendor10 contract? | yes | **no** | 2 | 2,229 | 2,397 | 803 | 0.013 | 6.28 | answer |
| 3 | multi-hop | How much did we pay for the Vendor10 product last year? | yes | yes | 4 | 5,324 | 5,849 | 1,010 | 0.022 | 8.76 | answer |
| 4 | lookup | When does the Vendor05 contract end? | yes | yes | 2 | 3,061 | 2,582 | 568 | 0.011 | 6.04 | answer |
| 5 | lookup | When does the Vendor02 contract end? | yes | yes | 3 | 5,194 | 5,664 | 593 | 0.017 | 7.12 | answer |
| 6 | lookup | What is the price per user in the Vendor07 contract? | yes | yes | 1 | 1,341 | 1,918 | 303 | 0.007 | 10.68 | answer |
| 7 | lookup | Did we include SSO in the Vendor02 contract? | yes | yes | 4 | 11,047 | 8,335 | 685 | 0.024 | 6.42 | answer |
| 8 | lookup | What are my payment terms in the Vendor09 contract? | yes | yes | 2 | 4,484 | 3,203 | 603 | 0.012 | 4.77 | answer |
| 9 | decline | What are the renewal terms of the Vendor03 contract? | yes | yes | 5 | 8,317 | 9,482 | 829 | 0.027 | 14.53 | answer |
| 10 | decline | Who is responsible for security in case of an incident with Vendor04, and on what terms? | **no** | n/a | 9 | 30,094 | 34,982 | 962 | 0.080 | 11.71 | max_turns |

## Answers

### 1. What's the cancellation period for the Vendor04 contract?

- Gold: SYN-04-order.md#Terms, SYN-04-terms.md#8. Term and Termination
- Expected terms: 90 days
- Tool calls: search_chunks(Vendor04 cancellation period termination notice, 8) → search_chunks(SYN-04 cancel contract notice days, 8)

The Vendor04 contract has no fixed cancellation period. It has a notice period for non-renewal, and that period is **90 days**.

- **Order Form:** It says "Notwithstanding the Agreement, notice of non-renewal must be given at least 90 days before the end of the current term." It also says the Order Form prevails if it conflicts with the Master Subscription Agreement. [SYN-04-order.md#Terms]
- **Master Subscription Agreement:** Subscriptions renew automatically for successive 12-month periods unless a party gives written notice of non-renewal at least 60 days before the end of the current term. [SYN-04-terms.md#8. Term and Termination] The Order Form overrides this 60-day period, so 90 days applies.

**Termination for breach:** Either party can end the agreement or an affected Order Form by written notice if the other party materially breaches it. The breaching party must also have failed to fix the breach "within a reasonable period after being notified." The contract sets no number of days for this. [SYN-04-terms.md#8. Term and Termination]

I found nothing that lets either party cancel early for convenience in the middle of a term.

I also didn't see the term's start and end dates in the Order Form excerpts I retrieved. So I can't give you the actual last date to send a non-renewal notice.

### 2. What are the renewal terms of the Vendor10 contract?

- Gold: SYN-10-renewal.md#Purchase Terms, SYN-10-terms.md#8. Term and Termination
- Expected terms: automatically, 90 days, Customer
- Tool calls: search_chunks(Vendor10 renewal terms) → search_chunks(Vendor10 contract term auto-renew notice of non-re)

The Vendor10 renewal order form sets these renewal terms:

- **Renewal term:** It runs from 1 December 2026 to 30 November 2027, which is 12 months. [SYN-10-renewal.md#Renewal Term]
- **Automatic renewal:** The subscription renews automatically for successive 12-month periods. This doesn't happen if the Customer gives written notice of non-renewal at least 90 days before the end of the current term. [SYN-10-renewal.md#Purchase Terms]
- **Notice deadline for this term:** Counting 90 days back from 30 November 2027 gives about 1 September 2027. This is my own calculation, so confirm the exact day-count convention. Only the Customer is given the right to give non-renewal notice. [SYN-10-renewal.md#Purchase Terms]
- **Payment:** The Vendor invoices the annual fee in advance. Invoices are due within 30 days of the invoice date. Fees exclude taxes. [SYN-10-renewal.md#Payment Terms]
- **Amendments:** The form can only be changed in writing signed by both parties. [SYN-10-renewal.md#Purchase Terms]

The form says it renews the Customer's subscription "under the agreement already in place" between Vendor10 Design Ltd. and Customer Co. [SYN-10-renewal.md#Parties] That underlying agreement isn't in the results. It may contain other renewal-related terms, such as price changes or termination rights, that I can't see. I'd ask the vendor for the last signed copy.

### 3. How much did we pay for the Vendor10 product last year?

- Gold: SYN-10-order.md#Products and Fees, SYN-10-renewal.md#Products and Fees
- Expected terms: 16,000
- Tool calls: search_chunks(Vendor10 fees payment) → search_chunks(Vendor10 order form pricing subscription) → search_chunks(Vendor10 renewal term dates fees annual fee) → search_chunks(Vendor10 order effective date start date term)

The contracts don't show what you actually paid. They only give the invoiced fees, and I can't tell which year "last year" means because I don't know today's date. Here is what the Vendor10 documents say.

**Original order (1 December 2025 – 30 November 2026)**
- The order covers 400 user licences at USD 40 per user per year, with an introductory discount. The annual fee is **USD 16,000** (400 × USD 40). [SYN-10-order.md#Products and Fees]
- The term runs from 1 December 2025 to 30 November 2026. [SYN-10-order.md#Subscription Term]
- The fee excludes applicable taxes, which are your responsibility. [SYN-10-order.md#Products and Fees]
- Invoices are due within 30 days of the invoice date. [SYN-10-order.md#Payment Terms]

**Renewal (1 December 2026 – 30 November 2027)**
- The renewal has 400 licences at USD 45 per user per year, and the introductory discount no longer applies. The annual fee is **USD 18,000**. [SYN-10-renewal.md#Products and Fees]
- The renewal term runs from 1 December 2026 to 30 November 2027. [SYN-10-renewal.md#Renewal Term]
- The renewal fee is invoiced annually in advance. [SYN-10-renewal.md#Payment Terms]

**What this means for "last year"**
- If you mean the first term, which began in December 2025, the contracted fee is USD 16,000 plus any applicable taxes.
- If you mean the renewal term, the contracted fee is USD 18,000 plus any applicable taxes.
- The order form doesn't say when the first invoice is issued, so I can't tell which calendar year the payment falls in.
- The actual amounts paid, including taxes, any disputed or adjusted invoices, and payment dates, would be in your invoices or accounts-payable records. The contracts don't include those.

### 4. When does the Vendor05 contract end?

- Gold: SYN-05-renewal.md#Renewal Term
- Expected terms: 30 June 2028
- Tool calls: search_chunks(Vendor05 contract term end date) → search_chunks(Vendor05 order effective date renewal termination)

The Vendor05 contract currently ends on **30 June 2028**, based on the renewal order form. That date could move if the contract auto-renews.

- The original order ran from 1 July 2025 to 30 June 2026 (12 months) [SYN-05-order.md#Subscription Term].
- A renewal order form then set a 24-month renewal term from 1 July 2026 to 30 June 2028. It replaces the previous order form for that period [SYN-05-renewal.md#Renewal Term].
- The Master Subscription Agreement says each order renews automatically for a period equal to its current term. That doesn't happen if either party gives written notice of non-renewal at least 90 days before the term ends [SYN-05-terms.md#8. Term and Termination].
- Applying that to the current term, a non-renewal notice would be due by about 1 April 2028. That is 90 days before 30 June 2028, and it's my calculation. Without notice, the contract would renew for another 24 months, to 30 June 2030. The search results don't say whether the renewal form keeps this auto-renewal clause, so that follows from the master terms alone.
- The agreement also continues for as long as any order remains in effect [SYN-05-terms.md#8. Term and Termination]. Either party can end it earlier for an uncured material breach [SYN-05-terms.md#8. Term and Termination].

### 5. When does the Vendor02 contract end?

- Gold: SYN-02-order.md#Subscription Term
- Expected terms: 1 March 2026, 36 months, 28 February 2029
- Tool calls: search_chunks(Vendor02 contract term end date) → search_chunks(Vendor02 order form start date initial term renewa) → search_chunks(SYN-02-order Vendor02 Order Form subscription term)

The Vendor02 contract ends on 28 February 2029.

- The Order Form says the subscription term starts on 1 March 2026 and runs for 36 months [SYN-02-order.md#Subscription Term].
- I computed the end date by adding 36 months to 1 March 2026. That reaches 1 March 2029, so the last day of the term is 28 February 2029. The order form doesn't state an end date itself.
- The Master Services Agreement says the agreement continues for the term stated in the Order Form, unless it is terminated earlier [SYN-02-terms.md#8. Term and Termination].
- Renewal needs a new written agreement signed by both parties, so the contract does not renew automatically [SYN-02-terms.md#8. Term and Termination].
- Either party can give written notice of non-renewal at least 30 days before the end of the term [SYN-02-terms.md#8. Term and Termination]. For a 28 February 2029 end, that is by about 29 January 2029.
- Either party can end the agreement early for a material breach that isn't remedied after a reasonable opportunity [SYN-02-terms.md#8. Term and Termination].

### 6. What is the price per user in the Vendor07 contract?

- Gold: SYN-07-order.md#Products and Fees
- Expected terms: USD 80
- Tool calls: search_chunks(Vendor07 price per user)

The Vendor07 Order Form sets the price at **USD 80 per user per year**. That covers 250 user licences, which comes to USD 20,000 per year [SYN-07-order.md#Products and Fees].

The order form also lists two add-ons that are not priced per user:
- Security add-on: USD 5,000 per year.
- Support SLA add-on: USD 5,000 per year.

The total annual fee is USD 30,000 [SYN-07-order.md#Products and Fees]. Dividing that total by 250 users would give USD 120 per user, but the contract doesn't state that figure. The stated per-user price is USD 80.

### 7. Did we include SSO in the Vendor02 contract?

- Gold: SYN-02-order.md#Products and Fees
- Expected terms: SSO
- Tool calls: search_chunks(Vendor02 SSO single sign-on, 8) → search_chunks(Vendor02 order form features included, 8) → search_chunks(Vendor02 Products and Fees package subscription, 8) → search_chunks(Vendor02 Cloud Ltd. services authentication securi)

Yes. The Vendor02 Order Form includes SSO. It says the Customer is subscribing to "the Platform package including SSO, AI credits (50,000 per year) and unlimited projects." The total fee for the 36-month term is USD 90,000 [SYN-02-order.md#Products and Fees].

- **Term:** The subscription starts on 1 March 2026 and runs for 36 months. It applies to the products listed in "Products and Fees" [SYN-02-order.md#Subscription Term].
- **Master agreement:** The Vendor02 Master Services Agreement defines the Services as those "described in an Order Form" [SYN-02-terms.md#1. Definitions]. It doesn't mention SSO itself, so the Order Form is the only place SSO appears.
- **Signatures:** The copies I found have blank signature blocks [SYN-02-order.md#Signatures]. The MSA defines an Order Form as a document signed by both parties [SYN-02-terms.md#1. Definitions]. Check that you hold a fully signed copy.

### 8. What are my payment terms in the Vendor09 contract?

- Gold: SYN-09-order.md#Payment Terms
- Expected terms: 30 days
- Tool calls: search_chunks(Vendor09 payment terms) → search_chunks(Vendor09 invoices due net days fees)

Under the Vendor09 contract, each invoice is due within 30 days of the invoice date. The Master Subscription Agreement and the Order Form say the same thing.

- **Due date:** The Vendor invoices you, and each invoice is due within 30 days of the invoice date [SYN-09-terms.md#3. Fees and Payment]. The Order Form repeats this for the annual fee [SYN-09-order.md#Payment Terms].
- **Payment method:** Payment must be made in USD by bank transfer to the account stated on the invoice [SYN-09-order.md#Payment Terms].
- **Fees:** The fees are the ones in the applicable Order Form. They are non-cancellable except as the Agreement expressly states [SYN-09-terms.md#3. Fees and Payment].
- **Taxes:** Fees exclude applicable taxes, duties and similar charges, and you must pay those. The exception is taxes based on the Vendor's income [SYN-09-terms.md#3. Fees and Payment].
- **Disputes:** If you dispute an invoice in good faith, you must notify the Vendor in writing. You must still pay the undisputed portion when it is due [SYN-09-terms.md#3. Fees and Payment]. The Order Form says to notify the Vendor "promptly" [SYN-09-order.md#Payment Terms].

I found no late-payment interest or penalty clause in the sections returned. I also found no early-payment discount.

### 9. What are the renewal terms of the Vendor03 contract?

- Gold: SYN-03-order.md#Terms
- Expected terms: (none)
- Tool calls: search_chunks(Vendor03 renewal terms) → search_chunks(Vendor03 auto-renew term notice of non-renewal) → search_chunks(SYN-03 order form Vendor03) → search_chunks(Vendor03 subscription term end date renew) → search_chunks(Vendor03 Analytics terms renewal governed by agree)

The Vendor03 contract doesn't state any renewal terms. The documents I found don't say whether it renews, for how long, or how much notice is needed to stop a renewal.

- **Term:** The subscription runs from 1 February 2026 to 31 January 2027 [SYN-03-order.md#Subscription Term].
- **Renewal:** The Vendor03 order form has no renewal or non-renewal clause in the sections I found. Its only terms section says the order is governed by the Vendor's online Terms of Service, "as updated from time to time." It also says those terms "are not attached to this order form" [SYN-03-order.md#Terms].
- **Conflicts:** If the order form and the online terms conflict, the order form prevails, but only for "the products and fees described above" [SYN-03-order.md#Terms]. The order form says nothing on renewal, so any renewal rules would most likely sit in the online terms.

**Missing document:** The Vendor03 online Terms of Service are not in the results. I can't confirm any auto-renewal, renewal length or notice deadline without them. I'd ask Vendor03 Analytics Inc. for the last signed copy, or the version of the Terms of Service in force on the order date. Because the terms can be updated from time to time, you should also ask which version applies.

Other vendors' renewal terms, such as the 90-day notice in the Vendor05 and Vendor10 documents, don't apply to Vendor03.

### 10. Who is responsible for security in case of an incident with Vendor04, and on what terms?

- Gold: (none: decline)
- Expected terms: (none)
- Tool calls: search_chunks(Vendor04 security incident responsibility) → search_chunks(security breach notification data protection oblig) → search_chunks(Vendor shall maintain security measures; Customer ) → search_chunks(SYN-04 security addendum, data processing, liabili) → search_chunks(Vendor04 Master Subscription Agreement security, C) → search_chunks(Vendor04 Order Form fees term services ordered sec) → search_chunks(Vendor04 terms confidentiality limitation of liabi) → search_chunks(Vendor04 Master Subscription Agreement 5. Confiden) → search_chunks(Vendor04 Security Ltd. Order Form governing law te)

(max turns reached)
