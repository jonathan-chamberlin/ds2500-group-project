# Milestone 3 Progress Report — Draft

**Team:** Jonathan Chamberlin, Anuhya Mandava, Min Yu Huang, Tsion Teklaeb

## 1. Progress Summary
**Q: What has your team accomplished since the proposal? Include any preliminary findings.**

I downloaded the full CDC Chronic Disease Indicators dataset from data.gov and cleaned it into a state-level table with 51 rows and 27 health indicators. Heart disease mortality ranges from about 120 to 280 per 100k across states, and most indicators have full coverage except insurance (16 states missing) and social support (16 states missing). That table covers all four of our disease topics so everyone can pull from the same processed file.

Poverty turned out to be a stronger predictor of heart disease mortality than smoking or obesity. States above the median poverty rate have significantly higher heart disease death rates (p < 0.0001). I didn't expect a socioeconomic variable to outperform the traditional clinical risk factors, but it does.

[ANUHYA — add your progress on mental health / alcoholism here]

[MIN YU — add your progress on diabetes / obesity here]

[TSION — add your progress on cancer / COPD here]

### 1b. What algorithms/tools did you use? Include basic dataset statistics and any preliminary results.

I used pandas for data processing, seaborn and plotly for visualization, and scikit-learn for modeling. The dataset is 51 observations (50 states plus DC) across 27 numeric indicators, so it's small. Because a traditional train/test split would leave only about 15 states for testing, I used leave-one-out cross-validation (LOOCV) instead.

[TEAMMATES — what tools/methods did you use? any preliminary results?]

### 1c. If you used a machine learning method, state which method and how it was implemented.

I built both KNN regression and linear regression models to predict heart disease mortality using 7 features: smoking, obesity, physical inactivity, flu vaccination, poverty, food insecurity, and high school completion rates. KNN with k=7 performed best (LOOCV R-squared = 0.65, RMSE = 19.4). Linear regression came in lower at R-squared = 0.53.

[TEAMMATES — if you've started modeling, add your method/features/metrics here]

## 2. Current Challenges
**Q: What obstacles have you encountered and how are you addressing them? Any changes to your original approach?**

The biggest issue is missing data. 16 of the 51 states don't have values for the insurance coverage variable, which was supposed to be central to my social determinants analysis. I can't just drop a third of the data or impute it without introducing noise, so I'm running two parallel analyses: one on all 51 states without the insurance variable, and one on the 35-state subset that has it. That way I can still compare whether insurance actually adds anything, even with fewer states.

I also found that stroke mortality is poorly predicted by these features (R-squared = 0.11). That was unexpected. Heart disease was driven mostly by socioeconomic factors, so in the final report I want to test whether stroke responds more to behavioral ones like smoking and physical inactivity instead.

[TEAMMATES — any challenges on your end? missing data, unexpected results, etc?]

## 3. Team Check-in
**Q: What did each member do so far for the project? Is your division of labor working? Any role adjustments needed?**

- **Jonathan:** Built the data pipeline (downloading, cleaning, merging the CDC dataset into the shared state-level table). Finished EDA, correlation testing, choropleth maps, and initial KNN/linear regression models for cardiovascular disease.
- **Anuhya:** [waiting for update]
- **Min Yu:** [waiting for update]
- **Tsion:** [waiting for update]

The division of labor is working because everyone has their own disease pair and we're all pulling from the same cleaned dataset. Nothing needs to change so far.

## 4. Next Steps
**Q: What major tasks remain and your timeline for completion? How would you evaluate the performance of your machine learning model?**

I still need to finish the cross-disease comparison (testing whether the same features that predict heart disease also predict diabetes), the comorbidity analysis between cardiovascular outcomes and poverty, and the ethical considerations section. Slides need to get done too.

[TEAMMATES — what do you still need to finish?]

Timeline: models done by 4/10, visualizations polished by 4/12, slides mostly done by 4/12, and we're meeting 4/13 at 1:30 to practice the presentation. I think we're on track. The modeling is the hardest part and it's mostly done.

## 5. Questions
**Q: Specific areas where you need instructor/TA guidance.**

With only 51 state-level observations, is LOOCV the right evaluation strategy? Should we also report 5-fold or 10-fold CV results for comparison?

[TEAMMATES — any questions for the TA from your end?]
