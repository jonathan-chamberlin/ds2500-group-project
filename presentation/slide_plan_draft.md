# DS2500 Presentation — Slide Plan (Final)

## Slide 1: Title & Introduction
**Speaker:** Min Yu Huang (30 seconds)
**Title:** What Drives Chronic Disease Across U.S. States?
**Subtitle:** Predicting Heart Disease, Diabetes, Cancer & Mental Health from CDC Data
**Content:**
- Team: Jonathan Chamberlin, Min Yu Huang, Anuhya Mandava, Tsion Teklaeb
- DS2500 Section 1 — Spring 2026
**Image:** None (clean title slide)

**Speaker notes:**
"Heart disease kills more Americans than anything else, but the rate varies dramatically from state to state. Mississippi's heart disease mortality rate is nearly double Colorado's. We wanted to know why. Our team used CDC data covering all 50 states and DC to figure out which health and lifestyle factors actually predict where chronic disease hits hardest. Each of us focused on a different disease area. Jonathan will walk you through our data."

---

## Slide 2: The Problem & Dataset
**Speaker:** Jonathan Chamberlin (45 seconds)
**Title:** Can We Predict Where Chronic Disease Hits Hardest?
**Content:**
- Question: which factors (smoking, obesity, poverty, food insecurity) best predict state-level disease rates?
- Data: CDC Chronic Disease Indicators — 51 observations (50 states + DC), 27 health metrics per state
- Source: data.cdc.gov — federal government's official chronic disease tracking system
- Why it matters: helps public health officials target interventions where they'll have the most impact
**Image:** `fig_choropleth_heart_disease.png` — geographic map showing heart disease mortality clustering in the Southeast

**Speaker notes:**
"We pulled our data from the CDC's U.S. Chronic Disease Indicators database. It's the federal government's official chronic disease tracking system, so the data is well-documented and covers every state. Each row is one state. Each column is a health metric, either a disease outcome like heart disease mortality or a risk factor like smoking or poverty rates. This map shows heart disease mortality by state. The Southeast has the highest rates. The question is, what's driving that pattern? Is it smoking? Obesity? Or something else? Anuhya will explain our approach."

---

## Slide 3: Our Approach
**Speaker:** Anuhya Mandava (45 seconds)
**Title:** How We Analyzed the Data
**Content:**
- Each team member analyzed a different disease pair: CVD, diabetes, cancer, mental health
- First: correlation analysis to identify which factors move together across states
- Then: two types of prediction models — one assumes direct linear relationships, one captures more complex patterns
- Validated by predicting each state using only the other 50
**Image:** `fig_06.png` — correlation heatmap showing how all variables relate to each other

**Speaker notes:**
"We divided the work by disease. Jonathan took cardiovascular disease. Min Yu handled diabetes and obesity. I covered mental health and alcoholism. Tsion analyzed cancer and COPD. For each disease, we started with correlation analysis. This heatmap shows how all our variables relate. Dark red means a strong positive correlation. You can see poverty, obesity, and physical inactivity all cluster together with heart disease mortality. Then we built two types of prediction models: one that assumes simple direct relationships, and one that captures more complex patterns. Both gave similar results, which made us more confident in our findings. We validated by predicting each state using only data from the other 50. Tsion will share what we found."

---

## Slide 4: Results & Key Insights
**Speaker:** Tsion Teklaeb (60 seconds)
**Title:** Poverty Predicts Heart Disease More Than Smoking or Obesity
**Content:**
- Our best model explains 65% of state-level variation in heart disease mortality
- Poverty is the single strongest predictor — its effect is nearly 4x larger than smoking's
- States above median poverty have significantly higher heart disease mortality (p < 0.0001)
- Diabetes tells a different story: obesity, not poverty, is the top driver
**Image:** `fig_11.png` — side-by-side standardized coefficients comparing heart disease vs diabetes models

**Speaker notes:**
"Here's our most important finding. When we look at what predicts heart disease mortality across states, poverty is the strongest factor. It's not close. The red bars show standardized coefficients for heart disease. Poverty's effect is nearly four times larger than smoking's. That matters because public health campaigns focus heavily on individual behavior, like quitting smoking. But our data suggests the economic environment matters more at the state level. Diabetes tells a different story. The blue bars show that obesity is the dominant driver for diabetes, not poverty. Different diseases, different drivers. Min Yu will wrap us up with conclusions."

---

## Slide 5: Conclusions & Impact
**Speaker:** Min Yu Huang (45 seconds)
**Title:** Conclusions
**Content:**
- Social and economic factors predict chronic disease at the state level as strongly as lifestyle factors
- The Southeast concentration of high heart disease, poverty, and smoking is not coincidence — these factors reinforce each other
- Implication: public health strategies that only target individual behavior miss the larger picture
- Limitation: state-level data (n=51) can't tell us about individuals (ecological fallacy)
**Image:** `fig_choropleth_poverty.png` — poverty prevalence map, side by side visually with heart disease map from slide 2

**Speaker notes:**
"So what does this mean? The biggest takeaway is that where you live matters. States with high poverty consistently have high heart disease mortality. The maps make this obvious: the Southeast has the highest rates of both heart disease and poverty. That pattern held up in our models too. For public health policy, this suggests that economic interventions could reduce chronic disease as much as traditional health campaigns. One important caveat: our data is at the state level, so we can't say poverty causes heart disease in individuals. We can say that states with more poverty have more heart disease, and that relationship is strong and consistent."

---

## Time Budget
| Slide | Speaker | Time |
|-------|---------|------|
| 1 | Min Yu | 0:30 |
| 2 | Jonathan | 0:45 |
| 3 | Anuhya | 0:45 |
| 4 | Tsion | 1:00 |
| 5 | Min Yu | 0:45 |
| Q&A buffer | — | 0:15 |
| **Total** | | **4:00** |

## Delivery Notes
- **Slide 1:** Min Yu — pause after "Mississippi's rate is nearly double Colorado's." Let it land.
- **Slide 2:** Jonathan — point to the Southeast on the map when you say "highest rates." End with the three questions to build tension.
- **Slide 3:** Anuhya — point to the dark red cluster in the heatmap. Slow down on "both gave similar results" — that's the credibility moment.
- **Slide 4:** Tsion — this is the money slide. Pause after "It's not close." Point to the poverty bar vs smoking bar. Emphasize "different diseases, different drivers" — it's the most memorable line.
- **Slide 5:** Min Yu — gesture back toward the two maps. End strong on "that relationship is strong and consistent."

## Transitions (each speaker says this to hand off)
- Min Yu → Jonathan: "Jonathan will walk you through our data."
- Jonathan → Anuhya: "Anuhya will explain our approach."
- Anuhya → Tsion: "Tsion will share what we found."
- Tsion → Min Yu: "Min Yu will wrap us up with what this means."

## Q&A Protocol
- Jonathan fields data/dataset questions
- Tsion fields results/model questions
- Anuhya and Min Yu field methodology/interpretation questions

## Rehearsal Plan
- 4/13 1:30pm team meeting: full run-through, timed
- If over 4:30, cut the ecological fallacy bullet from Slide 5 (speaker can mention it only if time allows)
- If over 5:00, cut the diabetes comparison from Slide 4 (keep poverty as sole focus)

## Image Selection Summary
| Slide | Image File | Why |
|-------|-----------|-----|
| 1 | None | Clean title |
| 2 | fig_choropleth_heart_disease.png | Immediately shows the geographic pattern — hooks audience |
| 3 | fig_06.png | Single clean heatmap, shows correlation structure at a glance |
| 4 | fig_11.png | THE key finding — poverty vs other predictors side by side |
| 5 | fig_choropleth_poverty.png | Visual parallel with slide 2 map — audience sees the overlap |
