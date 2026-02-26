# DS 2500 Project Proposal

Jonathan Chamberlin (chamberlin.j@northeastern.edu)
Min Yu Huang (huang.minyu@northeastern.edu)
Anuhya Mandava (mandava.an@northeastern.edu)
Tsion Teklaeb (teklaeb.t@northeastern.edu)

Section 1

## Problem Statement

We want to figure out which state-level health and lifestyle factors are the best predictors of chronic disease rates across the US. Specifically, we're looking at state-level prevalence rates (percentage of population affected) for diabetes, heart disease, and COPD as our target outcomes, and testing whether indicators like smoking rates, obesity, alcohol use, household income, and insurance coverage can predict how those rates vary from state to state. Some states have way higher chronic disease rates than others, and we want to understand what's actually driving those gaps.

This is scoped to state-level analysis using existing public datasets, which keeps it manageable for one semester and still gives us enough variation across 50+ states to build meaningful models.

## Data Sources

Our primary dataset is the U.S. Chronic Disease Indicators dataset published by the CDC (https://catalog.data.gov/dataset/u-s-chronic-disease-indicators). It covers 115 health indicators tracked across all US states and territories, including diabetes, COPD, tobacco use, cardiovascular disease, and more. The data is available in CSV format and is organized at the state level.

We also plan to pull in supplementary data from the National Alcohol Surveys (https://arg.org/center/national-alcohol-surveys/) for more detailed alcohol-related risk factors, and potentially US Census data for socioeconomic variables like household income and insurance coverage rates.

Ethical Considerations: Since all of our data is aggregated at the state level, there's no risk of identifying individual people. But there are still things to be careful about. State-level averages can hide disparities within a state, so our conclusions might not apply equally to all communities. Some populations are underrepresented in health surveys due to barriers like language or healthcare access, which means the data could undercount certain groups. We also need to be thoughtful about how we frame our results, since labeling states as "high risk" could affect how resources get allocated or reinforce existing stereotypes about certain regions. We'll frame our findings around systemic factors instead of blaming individual states, and note limitations of the data where relevant.

## Analysis Goals and Methods

We would like to use correlation analysis (Pearson and Spearman) and hypothesis testing to identify which health and demographic indicators have the strongest association with chronic disease prevalence across states. For example, we want to see if smoking rates or obesity levels are more predictive of diabetes rates than income or insurance coverage.

We would like to build machine learning models (KNN and linear regression) to predict chronic disease rates in a given state based on its risk factor profile. We'll build separate models for each disease and evaluate them using metrics like R-squared and RMSE with cross-validation. We plan to compare how well these models perform across different diseases to see whether the same factors drive diabetes, heart disease, and COPD or if each has its own key predictors.

We also want to create geographic visualizations like choropleth maps and scatter plots to show spatial patterns in chronic disease burden and highlight which regions are most affected. By the end of the project, we want to be able to say which handful of factors matter the most for each disease and see if it actually works well enough to be useful for predicting state-level outcomes.

## Division of Labor

Jonathan Chamberlin will handle data acquisition and pipeline development, including downloading, cleaning, and merging the CDC dataset with any supplementary sources. He has a programming background and will make sure the data infrastructure is set up for the rest of the team to build on. He'll also contribute analysis focused on geographic trends in chronic disease.

Min Yu Huang will lead the statistical analysis, running correlation tests and hypothesis testing to determine which risk factors have the strongest relationships with disease outcomes. She has experience with statistical methods and will focus specifically on diabetes prevalence as her primary analysis question.

Anuhya Mandava will lead the machine learning modeling effort, building and evaluating KNN and regression models to predict chronic disease rates. She has coursework in data science and will compare model accuracy across different diseases and work on tuning parameters.

Tsion Teklaeb will lead the visualization work, creating choropleth maps, trend plots, and other visual summaries of the data. She has a background in public health topics and will also take the lead on the ethical considerations section of the final report, examining biases in the data and what our findings mean for policy.

All team members will contribute to writing the final report and preparing the presentation.
