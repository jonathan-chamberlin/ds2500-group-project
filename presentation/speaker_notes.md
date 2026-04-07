# Speaker Notes — DS2500 Presentation

Total time: 4:00 (with 15-second Q&A buffer within the 5-minute limit)

---

## Slide 1: Title — Min Yu Huang (30 seconds)

"Heart disease kills more Americans than anything else, but the rate varies dramatically from state to state. Mississippi's heart disease mortality rate is nearly double Colorado's."

[PAUSE — let that sink in]

"We wanted to know why. Our team used CDC data covering all 50 states and DC to figure out which health and lifestyle factors actually predict where chronic disease hits hardest. Each of us focused on a different disease area. Jonathan will walk you through our data."

---

## Slide 2: Problem & Dataset — Jonathan Chamberlin (45 seconds)

"We pulled our data from the CDC's U.S. Chronic Disease Indicators database, hosted on data.gov. It's the federal government's official chronic disease tracking system, so the data is well-documented and covers every state. Each row is one state. Each column is a health metric — either a disease outcome like heart disease mortality, or a risk factor like smoking or poverty rates."

[POINT TO MAP]

"This map shows heart disease mortality by state. The Southeast has the highest rates. The question is: what's driving that pattern? Is it smoking? Obesity? Or something else? Anuhya will explain our approach."

---

## Slide 3: Approach — Anuhya Mandava (45 seconds)

"We divided the work by disease. Jonathan took cardiovascular disease. Min Yu handled diabetes and obesity. I covered mental health and alcoholism. Tsion analyzed cancer and COPD."

"For each disease, we started with correlation analysis."

[POINT TO HEATMAP]

"This heatmap shows how all our variables relate. Dark red means a strong positive correlation. You can see poverty, obesity, and physical inactivity all cluster together with heart disease mortality."

"Then we built two types of prediction models: one that assumes simple direct relationships, and one that captures more complex patterns. Both gave similar results, which made us more confident in our findings. We validated by predicting each state using only data from the other 50. Tsion will share what we found."

---

## Slide 4: Results — Tsion Teklaeb (60 seconds)

"Here's our most important finding. When we look at what predicts heart disease mortality across states, poverty is the strongest factor."

[PAUSE]

"It's not close."

[POINT TO CHART — red bars]

"The red bars show the relative strength of each predictor for heart disease. Poverty's effect is more than four times larger than smoking's. That matters because public health campaigns focus heavily on individual behavior — quit smoking, eat better, exercise more. But our data suggests the economic environment matters more at the state level."

"Diabetes has a different pattern. Obesity and poverty contribute almost equally as drivers, unlike heart disease where poverty dominates. Different diseases, different balance of drivers. Min Yu will wrap us up with what this means."

---

## Slide 5: Conclusions — Min Yu Huang (45 seconds)

"So what does this mean? The biggest takeaway is that where you live matters. States with high poverty consistently have high heart disease mortality."

[GESTURE TO MAP]

"Compare this poverty map to the heart disease map from earlier — the overlap is striking. The Southeast has the highest rates of both. That pattern held up in our prediction models too."

"For public health policy, this suggests that economic interventions — addressing poverty, food access, insurance coverage — could reduce chronic disease as much as traditional health campaigns."

"One important caveat: our data is at the state level, so we can't say poverty causes heart disease in individuals. We can say that states with more poverty have more heart disease, and that relationship is strong and consistent."

---

## Q&A Protocol
- **Jonathan:** fields data/dataset questions
- **Tsion:** fields results/model questions
- **Anuhya & Min Yu:** field methodology/interpretation questions

## If Running Long
- **Over 4:30:** Cut the "ecological fallacy" caveat from Slide 5 (mention only if time allows)
- **Over 5:00:** Cut the diabetes comparison from Slide 4 (keep poverty as sole focus)
