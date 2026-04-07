# Jonathan Chamberlin — DS2500 Project Check-In

**What is your project trying to accomplish? (in 1 or 2 sentences)**

We're predicting chronic disease rates at the state level using the CDC's U.S. Chronic Disease Indicators dataset. Each team member is analyzing a different disease pair (mine is cardiovascular disease and social determinants like poverty and insurance) to figure out which risk factors actually drive state-level variation.

**What does your final dataset look like?**

**Rows:** 51 rows. Each row is one U.S. state (all 50 states plus DC).

**Columns:** 29 columns. Two are identifiers (state abbreviation and full name). The other 27 are numeric health indicators covering disease outcomes (heart disease mortality rate, stroke mortality rate, diabetes prevalence, cancer incidence, COPD prevalence, etc.) and risk factors (smoking, obesity, physical inactivity, poverty, food insecurity, high school completion, insurance status, flu vaccination, binge drinking, etc.). All values are rates or prevalences per state.

**What are you currently working on? (in 1 or 2 sentences)**

I'm building the presentation slides for milestone 4 (due 4/13) and finishing the cross-disease comparison, testing whether the same features that predict heart disease mortality also predict diabetes prevalence.

**What challenges are you facing?**

The insurance variable has too much missing data (16 out of 51 states are blank), and it was supposed to be central to the social determinants angle. I'm working around it by running two parallel analyses: one on all 51 states without insurance, one on the 35-state subset that has it. Stroke mortality is also poorly predicted by these features (R² = 0.11), so I need to figure out what's actually driving stroke versus heart disease at the state level.

**Any specific questions?**

With only 51 observations (one per state), is leave-one-out cross-validation the right evaluation strategy, or should I also report 5-fold or 10-fold CV for comparison?
