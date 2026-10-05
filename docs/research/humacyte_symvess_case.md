# Case Study: Humacyte (HUMA) and Symvess, a Dissent That Preceded the Market

Date: 2026-10-05. First application of M15 (`docs/modules/long_form_media.md`).
Prompted by the investor watching the American Whistleblower Podcast episode
"Whistleblower Exposes FDA Approval of Dangerous Vascular Graft for Military Use". The
episode itself was not located by web search from this environment; its date and
speaker should be added to the dissent register by the investor.

## 1. Timeline (sources linked; evidence class in brackets)

| Date | Event | Class |
|---|---|---|
| 2024-08-10 | Original PDUFA goal date; FDA review extended about 19 more weeks | [F per company statement] |
| 2024-12-19 | FDA approves Symvess (acellular tissue engineered vessel-tyod) for extremity vascular trauma when urgent revascularization is needed and autologous vein is not feasible; no advisory committee | [F] |
| Before 2025-03-27 | New York Times reports concerns about the approval; Dr. Robert E. Lee, a vascular surgeon who consulted on the review, said reviewers were pressured to approve after he raised concerns and asked for a public advisory panel, and retired in protest | [U, press] |
| 2025-03-27 | Humacyte issues a statement responding to the NYT article (also filed with the SEC as an 8-K exhibit) | [F] |
| 2025 (reported) | Another FDA medical reviewer wrote that the two submitted studies did not meet "the usual criteria for an adequate and well-controlled trial"; trial complications reported included four deaths and four limb amputations | [U, press; confirm in FDA review documents] |
| 2025-04 | Faculty affiliated with Northeastern Law's Amy J. Reed Collaborative petition FDA to recall all Symvess products | [U, press] |
| 2025-12 | Reporting on promotion of off-label uses | [U, press] |
| 2026-10-05 | HUMA at USD 0.50, market cap about USD 84M, 52-week range 0.48 to 2.55 | [U: FMP profile] |

## 2. What the case teaches

1. **The best evidence was in the regulator's own documents.** The critical reviewer's
   language, if confirmed in the published review memos, was public record. M2 should
   ingest FDA review documents for every approval in the universe, not only the decision.
2. **No advisory committee is a feature to log.** A novel product approved without an
   AdCom after a long extension, over internal objections, is a measurable pattern.
   Candidate feature for P3 (FDA action model) and for the launch model: "contested
   approval".
3. **A government buyer is not product validation.** DoD procurement supported the story;
   it does not replace controlled evidence. Same lesson applies to MRLN's military
   contracts.
4. **Dissent arrived in stages:** internal objection, retirement in protest, press,
   academic petition, podcast. Each stage was a chance to act before the left tail.

## 3. Open work

- Get daily HUMA prices for 2024-12 to 2025-06 (FMP plan blocks price history; use EDGAR
  plus another vendor, or the local machine) and measure returns from each dissent stage
  to 90 days later, vs XBI.
- Pull the Symvess FDA review documents (CBER) and confirm or refute each press claim.
- Add every row above to `data/reference/dissent_register.csv` once confirmed.
- Find comparable cases (approvals with documented internal dissent) to start the H12
  labeled set, including cases where the product did fine.

## Sources

- [Northeastern: petition to FDA over Symvess](https://news.northeastern.edu/2025/04/23/fda-artificial-blood-vessel-petition/)
- [Northeastern Law: petition to recall all Symvess products](https://law.northeastern.edu/northeastern-law-faculty-affiliated-with-the-amy-j-reed-collaborative-petition-fda-to-recall-all-humacyte-symvess-products)
- [Bloomberg Law: FDA okayed device for wounded troops despite risks, surgeon says](https://news.bloombergtax.com/health-law-and-business/fda-okayed-device-for-wounded-troops-despite-risks-surgeon-says)
- [Humacyte statement on New York Times article](https://humacyte.gcs-web.com/news-releases/news-release-details/humacyte-statement-new-york-times-article/)
- [SEC 8-K exhibit with the statement](https://www.sec.gov/Archives/edgar/data/1818382/000110465925028830/tm2510708d1_ex99-1.htm)
- [Jacobin: off-label promotion reporting, 2025-12](https://jacobin.com/2025/12/lab-grown-blood-vessel-regulation)
