# MARKET_DATA — Sourced inputs for TAM / SAM / SOM, pricing, competitors

Prepared 2026-11-06 for the IEEE RAG Hackathon (Bethlehem University / BinX Tech).

**Rules used in this file**
- Every number has a URL that was opened (or seen in the search results) while preparing this file. Anything else is marked **ASSUMPTION**.
- "Vendor estimate" means a figure from a market-research firm's press release (MarketsandMarkets, Grand View Research and similar). These are paid-report headlines, not official statistics. Say so on the slide.
- "Derived" means we did arithmetic on official figures (for example, a share computed from quarterly PCBS tables). Show the formula if asked.
- Gaza data after Oct 2023 is often missing or not comparable. PCBS itself flags this. Use the West Bank as the realistic SAM for most problems.

---

## 0. Cross-cutting: Palestine basics

| Metric | Value | Year | Source (title + URL) | Note |
|---|---|---|---|---|
| Population, State of Palestine | ~5.56 M (West Bank 3.43 M; Gaza 2.13 M) | end-2025 | PCBS, Palestinians at the end of 2025 — https://www.pcbs.gov.ps/portals/_pcbs/PressRelease/Press_En_PalPeopleEnd2025E.pdf | Gaza down ~254k (−10.6%) vs pre-war estimate |
| Children under 15 | 36% (WB 35%, Gaza 39%) | end-2025 | same PCBS release | |
| Under 30 (youth proxy) | 64% of population | end-2025 | same PCBS release | Use as "share of youth" |
| Aged 65+ | "less than 4%" | end-2025 | same PCBS release | |
| Aged 60+ | ~336,000 (6%); WB ~228k, Gaza >108k | mid-2025 | PCBS, Int'l Day of Older Persons 2025 — https://www.pcbs.gov.ps/portals/_pcbs/PressRelease/Press_En_IntDayOlderP2025E.pdf | |
| Unemployment | 46% overall (WB 28%, Gaza 78%) | 2025 | PCBS end-2025 release (above) | |
| Households with internet at home | 93.5% | 2023 | PCBS, Main ICT indicators 2017–2023 — https://pcbs.gov.ps/Portals/_Rainbow/Documents/CITPal2017-2023MI_E.htm | National figure only |
| Individuals 18+ using internet | 87.8% | 2023 | same PCBS table | |
| Individuals 18+ owning a smartphone | 85.7% | 2023 | same PCBS table | Households with smartphone: 94.0% |
| Households with a computer | 29.1% | 2023 | same PCBS table | Mobile first: design for phone / WhatsApp |
| Internet users | 4.80 M (86.6% of pop.) | start-2025 | DataReportal, Digital 2025: Palestine — https://datareportal.com/reports/digital-2025-palestine | Secondary aggregator |
| Social media user identities | 2.30 M (41.5%) | start-2025 | same DataReportal page | Identities are not unique people |
| Facebook / Instagram ad reach | 2.30 M / 1.65 M | start-2025 | same DataReportal page | WhatsApp user count: **not found** |
| Mobile connections | 4.41 M (79.7%) | start-2025 | same DataReportal page | |
| GDP per capita (current US$) | $3,028 (2024); $3,171 (2025); $3,607 (2023) | 2023–25 | World Bank via FRED, NYGDPPCAPCDPSE — https://fred.stlouisfed.org/data/NYGDPPCAPCDPSE | |
| GDP change 2024 vs 2023 | about −27% | 2024 | PCBS Quarterly National Accounts Q4 2024 — https://pcbs.gov.ps/portals/_pcbs/PressRelease/Press_En_QNAQ42024E.pdf | Preliminary |
| GDP per capita (constant prices), Q3 2025 | $578 per quarter, −29% vs Q3 2023 | Q3 2025 | PCBS QNA Q3 2025 — https://www.pcbs.gov.ps/portals/_pcbs/PressRelease/Press_En_QNAQ32025E.docx | Quarterly figure, not annual |
| Avg real daily wage, private sector (West Bank) | ~122 NIS/day (121 in 2023) | 2024 | PCBS via Al-Quds — https://alquds.com/en/posts/159473 ; and PNN — https://english.pnn.ps/news/47456 | Highest: transport & communication 166 NIS; lowest: agriculture 79 NIS |
| West Bank employed (excluding workers abroad) | ~681,000 | 2024 | same Al-Quds/PCBS article | Down 20% vs 2023 |

---

## 1. Smart academic advisor

| Metric | Value | Year | Source | Note |
|---|---|---|---|---|
| Students in universities + university colleges (Palestine) | 212,569 | 2022/23 | PCBS, Education 1994–2024 — https://www.pcbs.gov.ps/Portals/_Rainbow/Documents/Education-1994-2024-E.html | Latest full-Palestine year. 2023/24 onward marked ".." |
| Students in community colleges (Palestine) | 12,849 | 2022/23 | same | |
| Students in universities + univ. colleges (West Bank) | 130,827 | 2023/24 | PCBS, Selected Education Indicators 2024 (WB) — https://www.pcbs.gov.ps/Portals/_Rainbow/Documents/Education2024_E.html | No Gaza data since Oct 2023 |
| Community-college students (West Bank) | 5,650 | 2023/24 | same | |
| Graduates (WB universities + univ. colleges) | 26,486 | 2022/23 | same | |
| Number of institutions | 13 universities, 9 university colleges, 11 community colleges | 2024 article | US ITA, West Bank higher education system — https://www.trade.gov/market-intelligence/west-bank-palestinian-higher-education-system-and-study-abroad-us | Secondary source (US government) |
| New enrolments | >36,000 | 2023 | same ITA page | |
| Student-to-advisor ratio benchmark (US) | median 296:1 (small inst. 233, large 600) | 2011 survey | NACADA, Advisor Load — https://nacada.ksu.edu/Resources/Clearinghouse/View-Articles/Advisor-Load.aspx | No Palestine ratio found |

**Competitors / alternatives:** university registrar portals and SIS systems (for example Banner or in-house systems), human advisors, student Facebook and WhatsApp groups, general chatbots (ChatGPT/Gemini). Specific Palestinian advising products: **not found**.

**TAM / SAM / SOM (annual)**
- TAM = all Palestinian higher-education students × price = (212,569 + 12,849) = 225,418 × **$2/student/yr (ASSUMPTION, B2B licence paid by the university)** ≈ **$451k/yr**
- SAM = West Bank students reachable now = (130,827 + 5,650) = 136,477 × $2 ≈ **$273k/yr**
- SOM (year 1–2) = **2 universities ≈ 10% of SAM (ASSUMPTION)** ≈ 13,650 students ≈ **$27k/yr**
- Pitch angle: at 296:1 (US median) one advisor serves about 296 students. A 20,000-student university would need about 68 advisors. **ASSUMPTION:** Palestinian ratios are likely worse (no data found).

---

## 2. Legal & procedural assistant (citizens + small businesses)

| Metric | Value | Year | Source | Note |
|---|---|---|---|---|
| Al-Muqtafi legislation records | >14,000 items, covering ~150 years (Ottoman, Mandate, Jordanian/Egyptian, military orders, PA laws) | page undated | Birzeit Univ., Institute of Law — https://www.birzeit.edu/en/news/institute-law-staff-showcases-new-legal-database-features-developments-workshop | The ready-made RAG corpus |
| Al-Muqtafi court judgments | ~40,000 rulings of high courts since 1994 | same | same | |
| Employed in private & non-govt enterprises | 505,182 (WB 331,161; Gaza 174,021) | 2020 | PCBS "Reality of Private and Non-government Enterprises 2020", via MarketScreener — https://ca.marketscreener.com/news/latest/PCBS-The-Reality-of-the-Private-and-Non-government-Enterprises-in-Palestine-2020-36793163/ | Total number of enterprises: not stated |
| Number of registered companies / SMEs (total) | **not found** | — | MoNE monthly example: 162 new companies registered in the WB in April 2019 — https://www.palestineeconomy.ps/en/Article/14784 | Monthly flow only |
| Global legal-technology market | $45.73 B by 2030, CAGR 9.1% (2023–30) | 2023 release | Grand View Research press release — https://prnewswire.com/news-releases/legal-technology-market-to-be-worth-45-73-billion-by-2030-grand-view-research-inc-301855205.html | Vendor estimate |
| Palestinian legal services market size | **not found** | — | — | |
| Adult internet users (proxy for B2C reach) | 87.8% of 18+; 4.80 M internet users | 2023 / 2025 | PCBS ICT table; DataReportal (Sec. 0) | |

**Competitors:** Al-Muqtafi itself (search, not Q&A), lawyers and the bar association, government e-services portals, ChatGPT (generic, no Palestinian law grounding). Our edge: RAG grounded on Palestinian legislation, with citations.

**TAM / SAM / SOM**
- TAM (global context) = legal-tech market ≈ $45.7 B by 2030 (vendor estimate).
- SAM (Palestine B2C) = 4.80 M internet users × **10% with a legal or procedural question per year (ASSUMPTION)** = 480k users.
- SOM = 480k × **5% adopt in year 1–2 (ASSUMPTION)** = 24k free users × 3–5% freemium conversion (Lenny/OpenView benchmark, Sec. 12) ≈ 720–1,200 payers × **$3/month (ASSUMPTION)** ≈ **$26k–43k/yr**.
- B2B variant: law firms and NGOs as subscribers. Number of law firms: **not found**.

---

## 3. Farmer assistant

| Metric | Value | Year | Source | Note |
|---|---|---|---|---|
| Agricultural holdings | 140,568 (plant 103,143; animal 19,909; mixed 17,516) | 2020/21 | PCBS Agricultural Census 2021 — https://pcbs.gov.ps/portals/_pcbs/PressRelease/Press_En_AgriCensus2021E.pdf | 82.4% WB, 17.6% Gaza. 2010: 111,310 |
| Agricultural holders | 137,985 (92.3% male) | 2020/21 | same | |
| Cultivated area | 1,096.3 thousand dunums | 2020/21 | same | |
| Olive area | 575.2 thousand dunums = 85.0% of horticultural-tree area | 2020/21 | same | |
| Olive trees | ~10 million (pre-Oct 2023) | 2025 article | Al Jazeera, Palestine's olives: visual guide — https://www.aljazeera.com/features/longform/2025/11/6/palestines-olives-a-visual-guide-to-the-annual-harvest-and-traditions | Journalistic. Older: 7.8 M fruit-bearing trees (2011, UNCTAD, cited in https://en.wikipedia.org/wiki/Olive_cultivation_in_Palestine) |
| Olive oil produced | ~39,600 t (from ~177,000 t olives) | 2019 | PCBS data cited by Al Jazeera (above) | Good-year baseline |
| Olive oil produced | ~24,700 t | 2014 | PCBS olive-press survey, cited on Wikipedia (above) | |
| Olive oil expected | ~7,000 t ("sharp drop") | 2025 | ARIJ, Palestinian Olive 2025 — https://www.arij.org/latest/palestinian_olive_2025/ | Conflict + climate |
| Families relying on olive income | >100,000 | 2025 article | Al Jazeera (above) | |
| Agriculture share of GDP | ~6.0% (WB ~6.1%) | 2024 | **Derived** from PCBS QNA Q4 2024 quarterly tables — https://pcbs.gov.ps/portals/_pcbs/PressRelease/Press_En_QNAQ42024E.pdf | Sum of quarters, constant 2015 prices |
| Agriculture value added | −16% vs Q3 2023 (Gaza −93%) | Q3 2025 | PCBS QNA Q3 2025 (Sec. 0) | |
| FAO figures | **not fetched / not verified** | — | — | Use PCBS census instead |

**Competitors:** Ministry of Agriculture extension officers, NGOs (for example PARC and UAWC; names only, not verified here), agri-input dealers, generic chatbots, WhatsApp farmer groups.

**TAM / SAM / SOM**
- TAM = 140,568 holdings × **$24/yr (ASSUMPTION: $2/month or donor-paid per farmer)** ≈ **$3.37 M/yr**
- SAM = West Bank holdings = 140,568 × 82.4% ≈ 115,828 × $24 ≈ **$2.78 M/yr**
- SOM = **2% of SAM (ASSUMPTION; via one cooperative or NGO partner)** ≈ 2,300 farmers ≈ **$56k/yr**. Realistic model: B2G or NGO-sponsored, free for farmers.

---

## 4. Safe primary health guidance

| Metric | Value | Year | Source | Note |
|---|---|---|---|---|
| Population | 5.56 M | end-2025 | PCBS (Sec. 0) | |
| Aged 60+ | ~336,000 (6%) | mid-2025 | PCBS Older Persons 2025 (Sec. 0) | |
| Smartphone ownership 18+ | 85.7% | 2023 | PCBS ICT (Sec. 0) | |
| Primary health care centres | 765 | 2021 | PCBS, World Health Day 2023 — https://www.pcbs.gov.ps/portals/_pcbs/PressRelease/Press_En_WorldHealthDay2023e.pdf | |
| Hospitals / beds | 89 hospitals (WB 54, Gaza 35); 7,296 beds | 2021 | same | Pre-war. Gaza capacity since largely destroyed |
| Registered physicians / nurses | 14,054 / 22,478 | 2021 | same | |
| Community pharmacies | ~500 (West Bank) | data in 2003 paper | An-Najah Univ. J. Res., Community pharmacy practice in Palestine — https://journals.najah.edu/media/journals/full_texts/descriptive-study-community-pharmacy-practice-palestine-analysis-and-future-look.pdf | **Outdated.** Current count not found |
| WB health system stress | Available medicine types fell from 1,260 to 260; >400 govt clinics limited to emergencies | 2026 | Al-Quds, citing MoH — https://alquds.com/en/posts/242624 | Shows the need |
| Adults who looked online for health info (US) | 59%; 35% "online diagnosers" | 2012 survey (published 2013) | Pew Research — https://www.pewresearch.org/short-reads/2013/02/01/majority-of-adults-look-online-for-health-information/ | No Palestine/MENA figure found |
| WHO data | **not fetched / not verified** | — | — | |

**Competitors:** Ministry of Health hotlines, pharmacists (de facto first contact), Google/"Dr Google", ChatGPT, regional apps (for example Altibbi, a name only, not verified here). Safety framing: triage plus "see a doctor" escalation, not diagnosis.

**TAM / SAM / SOM**
- TAM = adults with smartphones ≈ 5.56 M × 64% (aged 15+; from PCBS 36% under 15) × 85.7% ≈ **3.05 M people** (derived; mixes 15+ with an 18+ rate, so slightly overstated)
- SAM = West Bank share: 3.43 M × 64% × 85.7% ≈ **1.88 M**
- SOM = **1% of SAM in year 1–2 (ASSUMPTION)** ≈ 18.8k users. Monetise B2B2C (insurers, pharmacies or NGOs) at **$0.50/user/month (ASSUMPTION)** ≈ **$113k/yr**.

---

## 5. Customer-support assistant for a software company

| Metric | Value | Year | Source | Note |
|---|---|---|---|---|
| Global AI for customer service market | $12.06 B (2024) → $47.82 B (2030), CAGR 25.8% | 2024–30 | MarketsandMarkets press release — https://marketsandmarkets.com/PressReleases/ai-for-customer-service.asp | Vendor estimate |
| Cost per contact: live channel vs self-service | ~$8.01 vs ~$0.10 | 2019 | Gartner press release — https://www.gartner.com/en/newsroom/press-releases/2019-09-25-gartner-says-only-9--of-customers-report-solving-thei | Only 9% fully resolve via self-service: quality matters |
| IT/desktop support cost per ticket | avg $62 (range $27–$490) | 2010 NA data | MetricNet/HDI, Metric of the Month: Cost per Ticket — https://www.thinkhdi.com/~/media/HDICorp/Files/Library-Archive/Insider%20Articles/Cost%20per%20Ticket.pdf | Old, desktop support (higher than L1 service desk) |
| Palestinian tech companies | ~450 companies; ~9,558 professionals | 2022 data | US ITA, West Bank tech sector (2024-09-03) — https://www.trade.gov/market-intelligence/west-banks-palestinian-tech-sector | |
| ICT share of GDP | 3.1% (~$482 M) | 2022 | same ITA page | PCBS-derived 2024 "information & communication" ≈ 3.4% (QNA Q4 2024, derived) |
| IT graduates | >2,500/yr from 13 universities | 2024 article | same ITA page | |
| Older baseline | ~250 ICT companies, ~5,000 direct jobs | 2007 | PITA, ICT Sector Profile — https://www.pita.ps/en/Article/104/ICT-Sector-Profile | Historic |

**Competitors:** Intercom Fin, Zendesk AI, Freshdesk Freddy, Ada, Salesforce Einstein (global). Edge: Arabic dialect support plus low price for local and MENA SMB software firms.

**TAM / SAM / SOM**
- TAM (global) = $12.06 B (2024) AI-for-customer-service (vendor estimate).
- SAM (Palestine) = 450 tech companies × **40% sell software with end-customer support (ASSUMPTION)** = 180 × **$100/month (ASSUMPTION)** ≈ **$216k/yr**
- SOM = **10 customers in year 1–2 (ASSUMPTION)** × $1,200 ≈ **$12k/yr**. MENA expansion is the real upside.
- ROI line: using Gartner's ~$8 live vs ~$0.10 self-service, deflecting 1,000 tickets/month saves ≈ $7,900/month (derived; ASSUMPTION on volume).

---

## 6. Internal HR knowledge assistant

| Metric | Value | Year | Source | Note |
|---|---|---|---|---|
| HR time on routine employee calls/emails | 36% of the day | 2013 | HR Review, Transversal/Vanson Bourne survey (UK, orgs >500 staff) — https://hrreview.co.uk/hr-news/strategy-news/hr-professionals-waste-a-third-of-their-day-answering-trivial-questions/44599 | Vendor-commissioned, old |
| Knowledge-management software market | $20.15 B (2024) → $62.15 B (2033), CAGR 13.6% | 2024–33 | Grand View Research (via GII) — https://www.giikorea.co.kr/report/grvi1814134-knowledge-management-software-market-size-share.html | Vendor estimate |
| Employed in private & non-govt enterprises | 505,182 | 2020 | PCBS via MarketScreener (Sec. 2) | |
| WB wage employees; private-sector share | ~447,000; ~65% private (~290k) | 2024 | PCBS via PNN — https://english.pnn.ps/news/47456 | 447k includes those working in Israel/settlements |
| Private-sector contract types | 67k permanent, 128k temporary, 101k no contract | 2024 | PCBS via Al-Quds — https://alquds.com/en/posts/159473 | Shows HR policy ambiguity |
| Firms with 50+ employees in Palestine | **not found** | — | — | Needed for SAM. Treat as ASSUMPTION |

**Competitors:** Moveworks, Leena AI, Microsoft Copilot / SharePoint, Notion AI, Guru, local HR systems (for example Menalytics, listed as a top-funded Palestinian startup by Startup Genome).

**TAM / SAM / SOM**
- TAM (global) = KM software $20.15 B (2024).
- SAM (Palestine) = ~290k WB private wage employees × **30% work in firms with 50+ staff (ASSUMPTION)** ≈ 87k employees × **$1/employee/month (ASSUMPTION)** ≈ **$1.04 M/yr**
- SOM = **5 mid-size firms × 200 employees (ASSUMPTION)** = 1,000 seats ≈ **$12k/yr**
- ROI line: if one HR officer spends 36% of time on routine questions at 122 NIS/day × ~22 days, about 966 NIS/month of their time goes to repeat Q&A (derived; uses the private-sector average wage as a proxy).

---

## 7. Contract analyzer for small businesses / freelancers

| Metric | Value | Year | Source | Note |
|---|---|---|---|---|
| Legal-technology market (global) | $45.73 B by 2030, CAGR 9.1% | 2023 release | Grand View Research — https://prnewswire.com/news-releases/legal-technology-market-to-be-worth-45-73-billion-by-2030-grand-view-research-inc-301855205.html | Vendor estimate |
| Contract management software (global) | $1.5 B (2019) → $2.9 B (2024), CAGR 13.5% | 2019 report | MarketsandMarkets — https://www.marketsandmarkets.com/PressReleases/contract-management-software.asp | Old vendor estimate |
| Palestinian freelancers on platforms | ~3,000 Freelancer.com, ~2,000 Upwork, ~7,000 Mostaql (registered) | 2018 | UNDP PAPP, Freelancing in the State of Palestine — https://www.undp.org/papp/news/freelancing-state-palestine | Registrations overlap. UNDP says the true total is hard to estimate |
| Registered on Freelancer+PeoplePerHour+Guru | 5,830, of which ~10% active | 2023 | ETF, Platform work in SEMED: Palestine — https://www.etf.europa.eu/sites/default/files/2023-12/New%20forms%20of%20work%20and%20platform%20work%20in%20SEMED%20-%20Country%20profile%20Palestine%20%281%29.pdf | Palestine ≈ 0.18% of global online labour |
| MENA freelancing intent | 70% of employers plan to hire freelancers; ~78% of workers intend to freelance more | 2022 | Arab News (Bayt survey, 1,764 respondents) — https://www.arabnews.com/middle-east/how-freelancing-is-reshaping-post-pandemic-middle-easts-world-of-work-2210736 | |
| Saudi freelance work documents issued | 1.85 M | ~2022 | same Arab News article | MENA TAM signal |
| Global freelancers | ~1.56 B (industry studies) | 2022 | same Arab News article | Weak source. Use carefully |

**Competitors:** Spellbook, Ironclad, DocuSign CLM, Juro, LegalOn (global, English-first); generic ChatGPT. Gap: Arabic contracts plus Palestinian/Jordanian law context.

**TAM / SAM / SOM**
- TAM (global) = contract-management software ≈ $2.9 B (2024, vendor estimate).
- SAM (Palestine) = **~12,000 freelancers (ASSUMPTION; based on UNDP 2018 platform registrations, assuming overlap ≈ new growth)** + SMEs (count not found) → freelancer-only SAM = 12,000 × **$5/month (ASSUMPTION)** ≈ **$720k/yr**
- SOM = 3–5% freemium conversion (Sec. 12) of **2,000 sign-ups (ASSUMPTION)** = 60–100 payers ≈ **$3.6k–6k/yr**. The MENA (Saudi 1.85 M freelance permits) expansion is the story.

---

## 8. Tourism & heritage guide (Bethlehem / Palestine)

| Metric | Value | Year | Source | Note |
|---|---|---|---|---|
| WB hotels / rooms / beds | 132 hotels; 7,279 rooms; 15,946 beds | June 2019 | PCBS, World Tourism Day 2019 — https://www.pcbs.gov.ps/portals/_pcbs/PressRelease/Press_En_26-9-2019-tour-en.docx | Pre-COVID baseline |
| WB hotel guests H1 2019; Bethlehem share | 363,385; Bethlehem = 64% of guests | H1 2019 | same | |
| WB hotel nights H1 2019 | 1,021,567 | H1 2019 | same | |
| Visits to WB tourist sites; Bethlehem share | 1,726,560 (excl. Jerusalem); Bethlehem 38% | H1 2019 | same | |
| WB hotel guests (H1) | 2022: 144,755; 2023: 379,735; 2024: 59,899 | H1 | PCBS, World Tourism Day 2024 — https://pcbs.gov.ps/portals/_pcbs/PressRelease/Press_En_WorldTourismDay2024E.pdf | |
| Bethlehem hotel guests (H1) | 2022: 48,805; 2023: 221,377; 2024: 6,187; 2025: 24,034 | H1 | PCBS, World Tourism Day 2025 — https://pcbs.gov.ps/portals/_pcbs/PressRelease/Press_En_WorldTourismDay2025E.pdf | A 97% collapse in 2024 |
| WB hotel guests H1 2025 | 121.4k (text) vs 90,421 (table) | H1 2025 | same | **PCBS internal inconsistency.** Quote both or the text figure |
| Same-day visitors WB H1 2025 | 2.626 M (1.584 M from 1948 territories; 1.042 M from abroad) | H1 2025 | same | |
| Tourism employment WB | 33.4k = 5.3% of WB employees | Q1 2025 | same | |
| Gaza tourism destruction | 4,992 establishments destroyed (173 accommodation); 15,265 jobs lost | 2025 | same | |
| International tourist arrivals | 688,000 (2019); 93,000 (2020); 2021+ no data | 2019–20 | World Bank API ST.INT.ARVL — https://api.worldbank.org/v2/country/PSE/indicator/ST.INT.ARVL?format=json&date=2010:2024 | Different definition from ministry |
| "Tourists" 2019 per Ministry | >3 million | 2019 | The Citizen, quoting Minister Rula Maayah — https://www.thecitizen.co.tz/news/More-than-3-million-tourists-visited-Palestine-in-2019/1840386-5398040-y79bfvz/index.html | Likely counts visits, not unique arrivals |
| Accommodation & food services share of GDP | ~1.0% | 2024 | **Derived** from PCBS QNA Q4 2024 | Tourism-satellite share of GDP: **not found** |

**Competitors:** Visit Palestine / Ministry of Tourism portals, TripAdvisor, Google Maps, GetYourGuide, human guides, the Bethlehem Peace Center. Edge: RAG over verified heritage text, Arabic/English, offline-friendly.

**TAM / SAM / SOM**
- TAM = WB visitors (2019 baseline): 688k international arrivals (WB) **plus** ~3.45 M site visits/yr (**ASSUMPTION:** H1 2019 1,726,560 × 2).
- SAM = Bethlehem: 38% of site visits ≈ 1.31 M visits/yr (derived from 2019 H1 × 2) × **5% would use a digital guide (ASSUMPTION)** ≈ 66k users × **$3 per visit (ASSUMPTION)** ≈ **$197k/yr** (2019-level demand)
- SOM (2025–26 recovery) = scale by the Bethlehem recovery ratio 24,034 / 221,377 ≈ 11% of the 2023 level (derived) → ≈ **$21k/yr**, or B2B to hotels/municipality at **$50/month × 20 hotels (ASSUMPTION)** = $12k/yr.

---

## 9. Grants & funding assistant

| Metric | Value | Year | Source | Note |
|---|---|---|---|---|
| Registered NGOs / CSOs | ~3,729 (WB ~2,800; Gaza 929) | 2022 | ICNL Civic Freedom Monitor: Palestine (citing Ministry of Interior 2022) — https://www.icnl.org/?p=20969 | |
| Net ODA received, West Bank & Gaza | $3.62 B (2023); $2.24 B (2022); $2.30 B (2019) | 2019–23 | World Bank API DT.ODA.ODAT.CD — https://api.worldbank.org/v2/country/PSE/indicator/DT.ODA.ODAT.CD?format=json&date=2018:2024 | 2024 not yet published |
| Aid to Palestinians 1994–2020 | >$40 B cumulative | 1994–2020 | OECD figure cited on Wikiwand "Foreign aid to Palestinians" — https://wikiwand.com/en/Foreign_aid_to_Palestinians | Secondary |
| Active startups | 241 | early 2017 | World Bank report via CTech/Calcalist — https://www.calcalistech.com/ctech/articles/0,7340,L-3742164,00.html | Old |
| Tech startups supported by hubs/incubators | ~200 | 2024 article | US ITA tech sector — https://www.trade.gov/market-intelligence/west-banks-palestinian-tech-sector | |
| VC funding (Seed to B+) | $8.6 M total, 2021–2025; early-stage $1.6 M (H2 2023–2025) | 2021–25 | Startup Genome, Palestine — https://startupgenome.com/ecosystems/palestine | Startup Genome's own figures look internally inconsistent (median Series A $11M) |

**Competitors:** Instrumentl, GrantStation, Candid/Foundation Directory (US-centric); fundsforNGOs (listings); donor portals (EU F&T portal, USAID was a major donor). Edge: Arabic proposal drafting plus matching to MENA/EU calls.

**TAM / SAM / SOM**
- TAM (money flow) = $3.62 B ODA (2023) flowing into Palestine. Tool value = better access to a share of it.
- SAM = 3,729 NGOs + ~200 startups ≈ 3,929 orgs × **$20/month (ASSUMPTION)** ≈ **$943k/yr**
- SOM = **3% of SAM in year 1–2 (ASSUMPTION)** ≈ 118 orgs ≈ **$28k/yr**. Alternatively, success fee **1% of grants won (ASSUMPTION)**.

---

## 10. Cybersecurity & compliance assistant for SMEs

| Metric | Value | Year | Source | Note |
|---|---|---|---|---|
| Ransomware in SMB breaches vs large orgs | 88% vs 39% | DBIR 2025 | Verizon DBIR 2025 via Infosecurity Magazine — https://infosecurity-magazine.com/news/verizon-dbir-smb-ransomware-attacks | |
| Ransomware share of all breaches | 44% (up from 32%); 12,195 breaches analysed | DBIR 2025 | same | |
| Median ransom paid / % refusing to pay | $115,000 / 64% | DBIR 2025 | same | |
| UK businesses with a breach or attack (last 12 months) | 43% overall; 67% of medium firms | 2025 | UK DSIT, Cyber Security Breaches Survey 2025 — https://www.gov.uk/government/statistics/cyber-security-breaches-survey-2025/cyber-security-breaches-survey-2025 | Phishing in 85% of breached firms. Small firms: 42% saw phishing |
| eGRC market (global) | $72.42 B (2025) → $203.65 B (2033), CAGR 13.7% | 2025–33 | Grand View Research (via GII) — https://www.giiresearch.com/report/grvi1678680-enterprise-governance-risk-compliance-market-size.html | Vendor estimate. Broad definition (includes services) |
| NIST CSF 2.0 | Released 26 Feb 2024. 6 functions: Govern (new), Identify, Protect, Detect, Respond, Recover. Includes small-business quick-start guides | 2024 | NIST news release — https://www.nist.gov/news-events/news/2024/02/nist-releases-version-20-landmark-cybersecurity-framework | The RAG corpus (public domain) |
| Palestinian SME cyber stats | **not found** | — | — | |

**Competitors:** Vanta, Drata, Secureframe (compliance automation, priced for funded startups); CyberSmart (UK SMEs); MSSPs. Edge: Arabic plain-language NIST CSF checklist for SMEs at local prices.

**TAM / SAM / SOM**
- TAM (global) = eGRC $72.42 B (2025, vendor estimate).
- SAM (Palestine) = 450 tech firms (ITA) + **~1,500 other digitised SMEs (ASSUMPTION; total enterprise count not found)** ≈ 1,950 × **$30/month (ASSUMPTION)** ≈ **$702k/yr**
- SOM = **2% (ASSUMPTION)** ≈ 39 firms ≈ **$14k/yr**. Upsell to banks/insurers who need vendor-risk evidence.

---

## 11. AI / infrastructure pricing (verified on official pages, 2026-11-06)

| Item | Price | Source | Note |
|---|---|---|---|
| Claude Sonnet 5.5 | $2 input / $10 output per 1M tokens (cache hit $0.10) | Anthropic pricing — https://platform.claude.com/docs/en/about-claude/pricing | Batch: 50% off ($1 / $5) |
| Claude Sonnet 4.6 / 4.5 | $3 / $15 per 1M | same | |
| Claude Haiku 5.5 | $0.10 / $0.50 per 1M (prompts ≤100k tokens); $0.50 / $2.50 (>100k) | same | Cheapest Claude option for RAG answers |
| Claude Haiku 4.5 | $1 / $5 per 1M | same | |
| Claude Opus 5.5 | $4 / $20 per 1M | same | |
| OpenAI text-embedding-3-small | $0.02 per 1M tokens | OpenAI model page — https://developers.openai.com/api/docs/models/text-embedding-3-small | |
| OpenAI gpt-4o-mini | $0.15 in / $0.075 cached / $0.60 out per 1M; **marked deprecated** | https://developers.openai.com/api/docs/models/gpt-4o-mini | |
| OpenAI gpt-6-luna (current small model) | $0.10 / $0.50 per 1M | OpenAI pricing — https://developers.openai.com/api/docs/pricing | |
| Gemini 2.5 Flash-Lite | $0.10 / $0.40 per 1M; free tier available | Google Gemini API pricing — https://ai.google.dev/gemini-api/docs/pricing | Free-tier data may be used to improve Google products (mind privacy for health/legal) |
| Gemini 2.5 Flash | $0.30 / $2.50 per 1M; free tier | same | |
| Gemini 3.1 Flash-Lite | $0.25 / $1.50 per 1M; free tier | same | |
| gemini-embedding-001 | $0.15 per 1M; free tier | same | |
| Hetzner Cloud CPX22 (2 vCPU, 4 GB, 80 GB) | €19.99/month excl. VAT; CPX12 (1 vCPU / 2 GB) €11.99; CPX02 €6.49 (listed as unavailable) | Hetzner — https://www.hetzner.com/cloud/regular-performance | EU locations |
| Render web service | Free $0 (512 MB); $7/month (512 MB); $25/month (1 CPU, 2 GB); Postgres from $6/month (free tier exists) | Render pricing — https://render.com/pricing | |

**Unit-cost example (derived):** one RAG answer with 3,000 input + 400 output tokens on Haiku 5.5 = 3,000 × $0.10/1M + 400 × $0.50/1M = $0.0003 + $0.0002 = **$0.0005/answer**. 10,000 answers per month ≈ $5, plus about $7–25 hosting. Embedding 1 M tokens of corpus once with text-embedding-3-small ≈ $0.02.

---

## 12. SaaS benchmarks

| Benchmark | Value | Source | Note |
|---|---|---|---|
| LTV:CAC | "3:1 or better" is the standard benchmark | Geckoboard KPI guide — https://www.geckoboard.com/resources/kpi-examples/ltv-cac-ratio/ | |
| Freemium → paid (self-serve) | Good 3–5%, great 6–8% | Lenny's Newsletter (Poyar/OpenView, Pendo; 1,000+ products) — https://lennysnewsletter.com/p/what-is-a-good-free-to-paid-conversion | Supports the "2–5%" rule of thumb (OpenView data says 3–5% is good) |
| Free trial → paid | Good 8–12%, great 15–25% | same | |
| Monthly churn (median) | Overall 5.6%; B2B 4.91%; B2C 6.77% (voluntary 3.95%, involuntary 1.38%) | Recurly churn benchmarks (data Jan 2021–Jul 2022) — https://www-prod.recurly.com/research/churn-rate-benchmarks/ | |

---

## 13. Not found / not verified (say so if judges ask)

- Total number of registered companies or SMEs in Palestine (MoNE registry total); total establishment count from the 2017 Establishment Census (the PCBS metadata page opened but gave no totals).
- Palestinian legal services market size; number of lawyers or law firms.
- Student-to-advisor ratio at Palestinian universities; full-Palestine higher-ed enrolment after 2022/23.
- Current number of pharmacies (only a ~500 West Bank figure from a 2003 paper).
- WHO and FAO datasets were not opened. Olive tree count (~10 M) comes from Al Jazeera, not PCBS/FAO.
- WhatsApp user count for Palestine; Palestine/MENA online-health-seeking rate.
- Tourism share of GDP (only accommodation & food ≈ 1.0%, derived); full-year 2023–2025 hotel guests (PCBS publishes H1 figures in these releases).
- Firms with 50+ employees; Palestinian SME cyberattack statistics; Palestinian freelancer total (only platform registrations).
- PCBS H1 2025 hotel guests is inconsistent inside the source (121.4k in text vs 90,421 in table).
- Market sizes from MarketsandMarkets and Grand View Research are vendor headline estimates. Definitions differ between firms; don't add them together.
