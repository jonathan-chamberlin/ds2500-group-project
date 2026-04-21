"""
Anuhya Mandava
DS2500
Final Project
FinalProject.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.metrics import f1_score, mean_squared_error, r2_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from matplotlib.patches import Patch
from scipy import stats

import os

BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
df = pd.read_csv(BASE_PATH + "U.S._Chronic_Disease_Indicators (1).csv")

PREVALENCE_TYPES = ["crude prevalence", "age-adjusted prevalence"]
SIGNIFICANCE = 0.05

SIGNIFICANT_MENTAL = [
    "Depression among adults",
    "Frequent mental distress among adults",
    "Postpartum depressive symptoms among women with a recent live birth"
]

SIGNIFICANT_ALCOHOL = [
    "Binge drinking prevalence among adults",
    "Per capita alcohol consumption among people aged 14 years and older"
]


def save_results(disease, filename):
    """
    Save cleaned data for a disease topic to a new CSV file.

    Parameters: str, disease
                str, filename

    Returns: None
    """
    cleaned_data = df.dropna(axis=1, how='all')
    disease_rows = cleaned_data[cleaned_data["Topic"] == disease]
    disease_rows.to_csv(BASE_PATH + filename, index=False)
    print(f"Results saved to {filename} for {disease}")


def filter_data(dataframe, year):
    """
    Filter data to a specific year, US level, and Overall stratification.

    Parameters: dataframe, dataframe
                int, year

    Returns: dataframe, filtered dataframe
    """
    filtered = dataframe[
        (dataframe["YearStart"] == year) &
        (dataframe["LocationDesc"] == "United States") &
        (dataframe["Stratification1"] == "Overall")
    ].copy()
    return filtered


def normalize_rate(value, value_type):
    """
    Normalize a single rate value to 0-1 based on its DataValueType.
    - Percentage / Prevalence -> divide by 100
    - Per 100,000 -> divide by 100,000
    - Per 1,000 -> divide by 1,000
    - Mean / Days -> divide by 30
    - Rate / Median -> divide by 100
    - Per capita gallons -> divide by 5
    - Number / Percentile -> excluded, return None

    Parameters: float, value
                str, value_type

    Returns: float or None, normalized value
    """
    dtype = str(value_type).lower()

    if "percentile" in dtype or "75th" in dtype or "number" in dtype:
        return None
    elif "%" in dtype or "percent" in dtype or "prevalence" in dtype:
        return value / 100
    elif "100,000" in dtype:
        return value / 100000
    elif "1,000" in dtype:
        return value / 1000
    elif "mean" in dtype or "days" in dtype:
        return value / 30
    elif "rate" in dtype:
        return value / 100
    elif "median" in dtype:
        return value / 100
    elif "gallon" in dtype:
        return value / 5
    else:
        print(f"Unrecognized DataValueType: {value_type}")
        return None


def get_indicator_rates(dataframe, year):
    """
    For each indicator at US Overall level for a given year,
    compute the normalized rate.

    Parameters: dataframe, dataframe
                int, year

    Returns: dataframe, with columns Question, DataValueType,
             RawRate, and NormalizedRate
    """
    filtered = filter_data(dataframe, year)
    rows = []
    for _, row in filtered.iterrows():
        normalized = normalize_rate(row["DataValue"], row["DataValueType"])
        if normalized is not None:
            rows.append({
                "Question": row["Question"],
                "DataValueType": row["DataValueType"],
                "RawRate": row["DataValue"],
                "NormalizedRate": normalized
            })

    result = pd.DataFrame(rows).dropna(subset=["NormalizedRate"])
    return result


def get_indicator_rates_all_years(dataframe):
    """
    Get normalized rates for each indicator across all years at US Overall level.

    Parameters: dataframe, dataframe

    Returns: dataframe, with columns Year, Question, and NormalizedRate
    """
    filtered = dataframe[
        (dataframe["LocationDesc"] == "United States") &
        (dataframe["Stratification1"] == "Overall")
    ].copy()

    rows = []
    for _, row in filtered.iterrows():
        normalized = normalize_rate(row["DataValue"], row["DataValueType"])
        if normalized is not None:
            rows.append({
                "Year": row["YearStart"],
                "Question": row["Question"],
                "DataValueType": row["DataValueType"],
                "NormalizedRate": normalized
            })

    result = pd.DataFrame(rows).dropna(subset=["NormalizedRate"])
    return result


def get_state_level_data(dataframe, year, question):
    """
    Get state level data for a specific year and question at Overall stratification.

    Parameters: dataframe, dataframe
                int, year
                str, question

    Returns: dataframe, one row per state with DataValue
    """
    filtered = dataframe[
        (dataframe["YearStart"] == year) &
        (dataframe["Question"] == question) &
        (dataframe["Stratification1"] == "Overall")
    ].copy()

    state_df = filtered.groupby("LocationAbbr")["DataValue"].mean().reset_index()
    state_df.columns = ["StateAbbr", "DataValue"]
    state_df = state_df.dropna()
    return state_df


def get_average_prevalence_by_state(dataframe, year):
    """
    Compute the average prevalence rate across all prevalence-type indicators
    per state, used as the disease anchor.

    Parameters: dataframe, dataframe
                int, year

    Returns: dataframe, one row per state with AveragePrevalence
    """
    filtered = dataframe[
        (dataframe["YearStart"] == year) &
        (dataframe["Stratification1"] == "Overall") &
        (dataframe["DataValueType"].str.lower().isin(PREVALENCE_TYPES))
    ].copy()

    state_df = filtered.groupby("LocationAbbr")["DataValue"].mean().reset_index()
    state_df.columns = ["StateAbbr", "AveragePrevalence"]
    state_df = state_df.dropna()
    return state_df


def merge_state_indicator(dataframe, year, question, anchor_df, on="StateAbbr"):
    """
    Get state level data for a question and merge with an anchor dataframe.

    Parameters: dataframe, dataframe
                int, year
                str, question
                dataframe, anchor_df
                str, on, join key

    Returns: dataframe, merged result or None if too few rows
    """
    indicator_df = get_state_level_data(dataframe, year, question)
    merged = pd.merge(indicator_df, anchor_df, on=on)
    if len(merged) < 5:
        return None
    return merged


def get_indicator_pvalues(dataframe, year):
    """
    For each indicator, average across DataValueTypes first, then compute
    Pearson r and p-value against the average disease prevalence across states.

    Parameters: dataframe, dataframe
                int, year

    Returns: dataframe, with columns Question, r, and pvalue
    """
    anchor_df = get_average_prevalence_by_state(dataframe, year)
    questions = dataframe[
        (dataframe["Stratification1"] == "Overall") &
        (dataframe["YearStart"] == year)
    ]["Question"].unique()

    rows = []
    for question in questions:
        merged = merge_state_indicator(dataframe, year, question, anchor_df)
        if merged is None:
            continue
        r, p = stats.pearsonr(merged["DataValue"], merged["AveragePrevalence"])
        rows.append({"Question": question, "r": round(r, 3), "pvalue": round(p, 4)})

    result = pd.DataFrame(rows).sort_values("pvalue")
    return result



    """
    For each indicator, average across DataValueTypes first, then compute
    Pearson r and p-value against the average disease prevalence across states.

    Parameters: dataframe, dataframe
                int, year

    Returns: dataframe, with columns Question, r, and pvalue
    """
    anchor_df = get_average_prevalence_by_state(dataframe, year)
    questions = dataframe[
        (dataframe["Stratification1"] == "Overall") &
        (dataframe["YearStart"] == year)
    ]["Question"].unique()

    rows = []
    for question in questions:
        indicator_df = get_state_level_data(dataframe, year, question)
        indicator_df = indicator_df.groupby("StateAbbr")["DataValue"].mean().reset_index()
        merged = pd.merge(indicator_df, anchor_df, on="StateAbbr")

        if len(merged) < 5:
            continue

        r, p = stats.pearsonr(merged["DataValue"], merged["AveragePrevalence"])
        rows.append({"Question": question, "r": round(r, 3), "pvalue": round(p, 4)})

    result = pd.DataFrame(rows).sort_values("pvalue")
    return result


def get_demographic_rates(dataframe, year, strat_category):
    """
    Get average disease prevalence per demographic group within a
    stratification category across all states.

    Parameters: dataframe, dataframe
                int, year
                str, strat_category, stratification category to filter by

    Returns: dataframe, with columns Demographic and AverageRate
    """
    filtered = dataframe[
        (dataframe["YearStart"] == year) &
        (dataframe["StratificationCategory1"] == strat_category) &
        (dataframe["DataValueType"].str.lower().isin(PREVALENCE_TYPES))
    ].copy()

    result = filtered.groupby("Stratification1")["DataValue"].mean().reset_index()
    result.columns = ["Demographic", "AverageRate"]
    result = result.dropna().sort_values("AverageRate", ascending=False)
    return result


def get_stratification_pvalue(dataframe, year, strat_category):
    """
    Compute p-value for a stratification category using one-way ANOVA
    across demographic groups' disease rates.

    Parameters: dataframe, dataframe
                int, year
                str, strat_category

    Returns: float, p-value from one-way ANOVA
    """
    filtered = dataframe[
        (dataframe["YearStart"] == year) &
        (dataframe["StratificationCategory1"] == strat_category) &
        (dataframe["DataValueType"].str.lower().isin(PREVALENCE_TYPES))
    ].copy().dropna(subset=["DataValue"])

    groups = [g["DataValue"].values for _, g in filtered.groupby("Stratification1")
              if len(g) >= 3]

    if len(groups) < 2:
        return None

    _, p = stats.f_oneway(*groups)
    return round(p, 4)


def plot_indicator_rates(indicator_df, pvalue_df, topic, year):
    """
    Plot a bar chart of min-max scaled indicator rates sorted by p-value,
    colored by significance at p < 0.05, with bold labels for significant bars.

    Parameters: dataframe, indicator_df
                dataframe, pvalue_df
                str, topic
                int, year

    Returns: None
    """
    merged = pd.merge(indicator_df, pvalue_df, on="Question", how="left")
    merged = merged.groupby(["Question", "r", "pvalue"])["NormalizedRate"].mean().reset_index()

    col_min = merged["NormalizedRate"].min()
    col_max = merged["NormalizedRate"].max()
    col_range = col_max - col_min if col_max != col_min else 1
    merged["ScaledRate"] = (merged["NormalizedRate"] - col_min) / col_range
    merged = merged.sort_values("pvalue", ascending=True)

    colors = ["steelblue" if p < SIGNIFICANCE else "lightgray" for p in merged["pvalue"]]

    plt.figure(figsize=(12, 6))
    ax = plt.gca()
    ax.barh(merged["Question"], merged["ScaledRate"], color=colors)

    for i, row in enumerate(merged.itertuples()):
        if not pd.isna(row.r) and not pd.isna(row.pvalue):
            ax.text(row.ScaledRate + 0.01, i,
                    f"r={row.r:.2f}, p={row.pvalue:.4f}",
                    va="center", fontsize=8,
                    fontweight="bold" if row.pvalue < SIGNIFICANCE else "normal")

    for label, p in zip(ax.get_yticklabels(), merged["pvalue"]):
        if p < SIGNIFICANCE:
            label.set_fontweight("bold")

    legend_elements = [Patch(facecolor="steelblue", label="p < 0.05 (significant)"),
                       Patch(facecolor="lightgray", label="p ≥ 0.05 (not significant)")]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=8)

    plt.xlabel("Scaled Rate (min-max normalized)")
    plt.ylabel("Indicator")
    plt.title(f"{topic} Indicator Rates - {year} (US Overall)\nSorted by P-Value")
    plt.tight_layout()
    plt.savefig(BASE_PATH + f"{topic.replace(' ', '_')}_{year}_indicators.png")
    plt.show()
    print(f"Plot saved for {topic} {year}")


def plot_regression_trends(indicator_df, topic, year):
    """
    Plot rate trends over time for each indicator with regression lines.
    Indicators with the steepest slopes are highlighted with thicker lines.

    Parameters: dataframe, indicator_df
                str, topic
                int, year

    Returns: None
    """
    plt.figure(figsize=(12, 6))
    questions = indicator_df["Question"].unique()

    slopes = {}
    for question in questions:
        subset = indicator_df[indicator_df["Question"] == question].dropna()
        if len(subset) < 2:
            continue
        x = subset["Year"].values.reshape(-1, 1)
        y = subset["NormalizedRate"].values
        model = LinearRegression()
        model.fit(x, y)
        slopes[question] = abs(model.coef_[0])

    if not slopes:
        return

    max_slope = max(slopes.values())
    threshold = max_slope * 0.5

    for question in questions:
        subset = indicator_df[indicator_df["Question"] == question].dropna()
        if len(subset) < 2:
            continue

        x = subset["Year"].values.reshape(-1, 1)
        y = subset["NormalizedRate"].values
        model = LinearRegression()
        model.fit(x, y)
        y_pred = model.predict(x)

        slope = slopes.get(question, 0)
        lw = 3 if slope >= threshold else 1
        alpha = 1.0 if slope >= threshold else 0.4
        label = f"★ {question}" if slope >= threshold else question

        plt.scatter(subset["Year"], subset["NormalizedRate"], alpha=alpha * 0.6, s=20)
        plt.plot(subset["Year"], y_pred, label=label, linewidth=lw, alpha=alpha)

    plt.xlabel("Year")
    plt.ylabel("Normalized Rate (0-1)")
    plt.title(f"{topic} Indicator Trends Over Time (US Overall)\n★ = Strongest Trend")
    plt.legend(fontsize=7, loc="best")
    plt.tight_layout()
    plt.savefig(BASE_PATH + f"{topic.replace(' ', '_')}_trends.png")
    plt.show()
    print(f"Regression trend plot saved for {topic}")


def plot_predictor_strength(dataframe, year, topic):
    """
    Plot all indicators against average disease prevalence by state
    on one chart with regression lines and Pearson r in the legend.

    Parameters: dataframe, dataframe
                int, year
                str, topic

    Returns: None
    """
    anchor_df = get_average_prevalence_by_state(dataframe, year)
    questions = dataframe[
        (dataframe["Stratification1"] == "Overall") &
        (dataframe["YearStart"] == year)
    ]["Question"].unique()

    plt.figure(figsize=(12, 7))

    for question in questions:
        merged = merge_state_indicator(dataframe, year, question, anchor_df)
        if merged is None:
            continue

        x = merged["DataValue"].values
        y = merged["AveragePrevalence"].values
        r, p = stats.pearsonr(x, y)

        model = LinearRegression()
        model.fit(x.reshape(-1, 1), y)
        x_range = np.linspace(x.min(), x.max(), 100)
        y_pred = model.predict(x_range.reshape(-1, 1))

        plt.scatter(x, y, alpha=0.4, s=20)
        plt.plot(x_range, y_pred, label=f"{question} (r={r:.2f}, p={p:.3f})")

    plt.xlabel("Indicator Rate")
    plt.ylabel("Average Disease Prevalence")
    plt.title(f"{topic} Predictor Strength vs Average Prevalence by State ({year})")
    plt.legend(fontsize=7, loc="best")
    plt.tight_layout()
    plt.savefig(BASE_PATH + f"{topic.replace(' ', '_')}_{year}_predictor_strength.png")
    plt.show()
    print(f"Predictor strength plot saved for {topic} {year}")


def plot_state_scatter_per_indicator(dataframe, year, topic):
    """
    For each indicator, plot a state-labeled scatter against average disease
    prevalence with a regression line and Pearson r. One plot per indicator.
    States more than 1 std dev above average are highlighted in red.

    Parameters: dataframe, dataframe
                int, year
                str, topic

    Returns: None
    """
    anchor_df = get_average_prevalence_by_state(dataframe, year)
    questions = dataframe[
        (dataframe["Stratification1"] == "Overall") &
        (dataframe["YearStart"] == year)
    ]["Question"].unique()

    for question in questions:
        merged = merge_state_indicator(dataframe, year, question, anchor_df)
        if merged is None:
            continue

        x = merged["DataValue"].values
        y = merged["AveragePrevalence"].values
        r, p = stats.pearsonr(x, y)

        model = LinearRegression()
        model.fit(x.reshape(-1, 1), y)
        x_range = np.linspace(x.min(), x.max(), 100)
        y_pred = model.predict(x_range.reshape(-1, 1))

        mean_y = np.mean(y)
        std_y = np.std(y)
        colors = ["tomato" if val > mean_y + std_y else "steelblue" for val in y]

        plt.figure(figsize=(12, 6))
        plt.scatter(x, y, c=colors, alpha=0.7)

        for _, row in merged.iterrows():
            val = row["AveragePrevalence"]
            fw = "bold" if val > mean_y + std_y else "normal"
            plt.text(row["DataValue"], val, row["StateAbbr"],
                     fontsize=6, alpha=0.8, fontweight=fw)

        plt.plot(x_range, y_pred, color="red", linewidth=2)
        plt.axhline(y=mean_y + std_y, color="orange", linestyle="--",
                    linewidth=1, label="+1 std dev (highlighted)")
        plt.xlabel(f"{question} Rate")
        plt.ylabel("Average Disease Prevalence")
        plt.title(f"{topic}: {question} vs Disease Prevalence by State ({year})\n"
                  f"Pearson r = {r:.3f}, p = {p:.4f}")
        plt.legend(fontsize=7)
        plt.tight_layout()

        fname = question.replace(" ", "_").replace("/", "_")[:50]
        plt.savefig(BASE_PATH + f"{topic.replace(' ', '_')}_{fname}_{year}.png")
        plt.show()

    print(f"State scatter plots saved for {topic} {year}")


def plot_choropleth(dataframe, year, topic):
    """
    Plot an interactive choropleth map of average disease prevalence by state.

    Parameters: dataframe, dataframe
                int, year
                str, topic

    Returns: None
    """
    state_df = get_average_prevalence_by_state(dataframe, year)

    fig = px.choropleth(
        state_df,
        locations="StateAbbr",
        locationmode="USA-states",
        color="AveragePrevalence",
        scope="usa",
        color_continuous_scale="Blues",
        title=f"{topic} Average Disease Prevalence by State ({year})",
        labels={"AveragePrevalence": "Avg Prevalence (%)"}
    )
    fig.write_html(BASE_PATH + f"{topic.replace(' ', '_')}_{year}_choropleth.html")
    fig.show()
    print(f"Choropleth saved for {topic} {year}")


def plot_demographic_rates(dataframe, year, strat_category, topic):
    """
    Plot average disease rates per demographic group within a
    stratification category, with the highest rate highlighted.

    Parameters: dataframe, dataframe
                int, year
                str, strat_category
                str, topic

    Returns: None
    """
    demo_df = get_demographic_rates(dataframe, year, strat_category)

    if demo_df.empty:
        print(f"No data for {strat_category} in {topic} {year}")
        return

    plt.figure(figsize=(10, 5))
    colors = ["steelblue"] * len(demo_df)
    colors[0] = "tomato"

    plt.barh(demo_df["Demographic"], demo_df["AverageRate"], color=colors)
    plt.xlabel("Average Disease Rate (%)")
    plt.ylabel("Demographic Group")
    plt.title(f"{topic}: Disease Rate by {strat_category} ({year})")
    plt.tight_layout()
    plt.savefig(BASE_PATH + f"{topic.replace(' ', '_')}_{strat_category.replace(' ', '_').replace('/', '-')}_{year}_demo.png")
    plt.show()
    print(f"Demographic plot saved for {topic} {strat_category} {year}")


def plot_stratification_comparison(dataframe, year, topic):
    """
    Compare stratification categories by ANOVA p-value to show
    which category explains the most variance in disease rates.

    Parameters: dataframe, dataframe
                int, year
                str, topic

    Returns: None
    """
    strat_categories = dataframe["StratificationCategory1"].dropna().unique()
    strat_categories = [s for s in strat_categories if s != "Overall"]

    rows = []
    for cat in strat_categories:
        p = get_stratification_pvalue(dataframe, year, cat)
        if p is not None:
            rows.append({"StratificationCategory": cat, "pvalue": p})

    if not rows:
        print(f"No stratification data for {topic} {year}")
        return

    result = pd.DataFrame(rows).sort_values("pvalue")
    colors = ["steelblue" if p < SIGNIFICANCE else "lightgray" for p in result["pvalue"]]

    plt.figure(figsize=(10, 5))
    ax = plt.gca()
    ax.barh(result["StratificationCategory"], result["pvalue"], color=colors)

    for i, row in enumerate(result.itertuples()):
        ax.text(row.pvalue + 0.001, i, f"p={row.pvalue:.4f}", va="center", fontsize=8)

    ax.axvline(x=SIGNIFICANCE, color="red", linestyle="--", label="p=0.05 threshold")

    legend_elements = [Patch(facecolor="steelblue", label="p < 0.05 (significant)"),
                       Patch(facecolor="lightgray", label="p ≥ 0.05 (not significant)")]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=8)

    plt.xlabel("ANOVA P-Value")
    plt.ylabel("Stratification Category")
    plt.title(f"{topic}: Which Stratification Category Matters Most? ({year})")
    plt.tight_layout()
    plt.savefig(BASE_PATH + f"{topic.replace(' ', '_')}_{year}_strat_comparison.png")
    plt.show()
    print(f"Stratification comparison plot saved for {topic} {year}")


def plot_cross_topic_choropleth(alcohol_df, mental_df, year):
    """
    Plot separate choropleth maps for alcohol and mental health
    prevalence across states for visual comparison.

    Parameters: dataframe, alcohol_df
                dataframe, mental_df
                int, year

    Returns: None
    """
    alc_state = get_average_prevalence_by_state(alcohol_df, year)
    men_state = get_average_prevalence_by_state(mental_df, year)
    merged = pd.merge(alc_state, men_state, on="StateAbbr",
                      suffixes=("_alcohol", "_mental"))

    fig = px.choropleth(
        merged,
        locations="StateAbbr",
        locationmode="USA-states",
        color="AveragePrevalence_alcohol",
        scope="usa",
        color_continuous_scale="Reds",
        title=f"Alcohol Prevalence by State ({year})",
        labels={"AveragePrevalence_alcohol": "Alcohol Prevalence (%)"}
    )
    fig.write_html(BASE_PATH + f"alcohol_{year}_choropleth.html")
    fig.show()

    fig2 = px.choropleth(
        merged,
        locations="StateAbbr",
        locationmode="USA-states",
        color="AveragePrevalence_mental",
        scope="usa",
        color_continuous_scale="Purples",
        title=f"Mental Health Prevalence by State ({year})",
        labels={"AveragePrevalence_mental": "Mental Health Prevalence (%)"}
    )
    fig2.write_html(BASE_PATH + f"mental_{year}_choropleth.html")
    fig2.show()
    print(f"Cross topic choropleths saved for {year}")


def plot_cross_correlation(alcohol_df, mental_df, year):
    """
    Heatmap of Pearson r for every alcohol vs mental health
    indicator combination across states. Strong correlations
    (|r| > 0.5) are marked with a star.

    Parameters: dataframe, alcohol_df
                dataframe, mental_df
                int, year

    Returns: None
    """
    alcohol_questions = alcohol_df[
        (alcohol_df["Stratification1"] == "Overall") &
        (alcohol_df["YearStart"] == year)
    ]["Question"].unique()

    mental_questions = mental_df[
        (mental_df["Stratification1"] == "Overall") &
        (mental_df["YearStart"] == year)
    ]["Question"].unique()

    corr_matrix = pd.DataFrame(index=alcohol_questions, columns=mental_questions, dtype=float)

    for aq in alcohol_questions:
        alc_state = get_state_level_data(alcohol_df, year, aq)
        for mq in mental_questions:
            men_state = get_state_level_data(mental_df, year, mq)
            merged = pd.merge(alc_state, men_state, on="StateAbbr",
                              suffixes=("_alc", "_men"))
            if len(merged) < 5:
                corr_matrix.loc[aq, mq] = np.nan
                continue
            r, _ = stats.pearsonr(merged["DataValue_alc"], merged["DataValue_men"])
            corr_matrix.loc[aq, mq] = r

    corr_vals = corr_matrix.astype(float)

    annot_matrix = corr_vals.copy().astype(object)
    for row in corr_vals.index:
        for col in corr_vals.columns:
            val = corr_vals.loc[row, col]
            if pd.isna(val):
                annot_matrix.loc[row, col] = ""
            elif abs(val) > 0.5:
                annot_matrix.loc[row, col] = f"{val:.2f} ★"
            else:
                annot_matrix.loc[row, col] = f"{val:.2f}"

    plt.figure(figsize=(12, 7))
    sns.heatmap(corr_vals, annot=annot_matrix, fmt="",
                cmap="coolwarm", center=0, linewidths=0.5)
    plt.title(f"Cross Correlation: Alcohol vs Mental Health Indicators ({year})\n★ = |r| > 0.5")
    plt.xticks(rotation=30, ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    plt.savefig(BASE_PATH + f"cross_correlation_{year}.png")
    plt.show()
    print(f"Cross correlation heatmap saved for {year}")


def plot_cross_topic_scatter(alcohol_df, mental_df, year):
    """
    Scatter of alcohol vs mental health average prevalence by state
    with state labels, regression line, and Pearson r.

    Parameters: dataframe, alcohol_df
                dataframe, mental_df
                int, year

    Returns: None
    """
    alc_state = get_average_prevalence_by_state(alcohol_df, year)
    men_state = get_average_prevalence_by_state(mental_df, year)
    merged = pd.merge(alc_state, men_state, on="StateAbbr",
                      suffixes=("_alcohol", "_mental"))

    x = merged["AveragePrevalence_alcohol"].values
    y = merged["AveragePrevalence_mental"].values
    r, p = stats.pearsonr(x, y)

    model = LinearRegression()
    model.fit(x.reshape(-1, 1), y)
    x_range = np.linspace(x.min(), x.max(), 100)
    y_pred = model.predict(x_range.reshape(-1, 1))

    plt.figure(figsize=(12, 6))
    plt.scatter(x, y, alpha=0.6)

    for _, row in merged.iterrows():
        plt.text(row["AveragePrevalence_alcohol"], row["AveragePrevalence_mental"],
                 row["StateAbbr"], fontsize=6, alpha=0.7)

    plt.plot(x_range, y_pred, color="red", linewidth=2)
    plt.xlabel("Alcohol Prevalence (%)")
    plt.ylabel("Mental Health Prevalence (%)")
    plt.title(f"Alcohol vs Mental Health Prevalence by State ({year})\n"
              f"Pearson r = {r:.3f}, p = {p:.4f}")
    plt.tight_layout()
    plt.savefig(BASE_PATH + f"cross_topic_scatter_{year}.png")
    plt.show()
    print(f"Cross topic scatter saved for {year}")


def prepare_model_data(dataframe, all_questions):
    """
    Build a feature matrix using all years and stratifications,
    keeping only specified indicators as features.

    Parameters: dataframe, dataframe
                list, all_questions

    Returns: dataframe, with features and target column
    """
    filtered = dataframe[
        dataframe["Question"].isin(all_questions) &
        dataframe["DataValueType"].str.lower().isin(PREVALENCE_TYPES)
    ].copy().dropna(subset=["DataValue"])

    le = LabelEncoder()
    filtered["StratCode"] = le.fit_transform(filtered["Stratification1"].astype(str))

    pivot = filtered.groupby(
        ["YearStart", "LocationAbbr", "StratCode", "Question"]
    )["DataValue"].mean().unstack("Question").reset_index()

    pivot.columns.name = None
    pivot = pivot.dropna(thresh=len(pivot.columns) - 3)
    return pivot


def bin_disease_rates(series):
    """
    Bin continuous disease rates into low/medium/high categories
    based on mean ± 0.5 std dev.

    Parameters: series, continuous prevalence rates

    Returns: series, binned labels as strings
    """
    mean = series.mean()
    std = series.std()
    bins = []
    for val in series:
        if val < mean - 0.5 * std:
            bins.append("low")
        elif val > mean + 0.5 * std:
            bins.append("high")
        else:
            bins.append("medium")
    return pd.Series(bins, index=series.index)


def find_best_k_regressor(X_train, y_train, X_val, y_val, max_k=20):
    """
    Find best K for KNN regressor using MSE on validation set.

    Parameters: X_train, y_train, X_val, y_val
                int, max_k

    Returns: int, best_k
    """
    best_k = 1
    best_mse = float("inf")

    for k in range(1, max_k + 1):
        model = KNeighborsRegressor(n_neighbors=k)
        model.fit(X_train, y_train)
        preds = model.predict(X_val)
        mse = mean_squared_error(y_val, preds)
        if mse < best_mse:
            best_mse = mse
            best_k = k

    print(f"Best K (Regressor): {best_k} with MSE={best_mse:.4f}")
    return best_k


def find_best_k_classifier(X_train, y_train, X_val, y_val, max_k=20):
    """
    Find best K for KNN classifier using weighted F1 on validation set.

    Parameters: X_train, y_train, X_val, y_val
                int, max_k

    Returns: int, best_k
    """
    best_k = 1
    best_f1 = 0

    for k in range(1, max_k + 1):
        model = KNeighborsClassifier(n_neighbors=k)
        model.fit(X_train, y_train)
        preds = model.predict(X_val)
        f1 = f1_score(y_val, preds, average="weighted")
        if f1 > best_f1:
            best_f1 = f1
            best_k = k

    print(f"Best K (Classifier): {best_k} with F1={best_f1:.4f}")
    return best_k


def run_knn_models(dataframe, all_questions, target_question, topic):
    """
    Prepare data, train KNN regressor and classifier predicting disease
    prevalence from all other indicators. Train/test split is random across
    all years and demographics.

    Parameters: dataframe, dataframe
                list, all_questions, all indicators to use as features
                str, target_question, indicator to predict
                str, topic

    Returns: None
    """
    model_df = prepare_model_data(dataframe, all_questions)

    if model_df.empty:
        print(f"Not enough data for KNN models for {topic}")
        return

    target_col = target_question
    if target_col not in model_df.columns:
        print(f"Target column not found for {topic}")
        return

    model_df = model_df.dropna(subset=[target_col])

    feature_cols = sorted([c for c in model_df.columns
                           if c not in ["YearStart", "LocationAbbr", "StratCode", target_col]])

    model_df = model_df.dropna(subset=feature_cols)

    if len(model_df) < 10:
        print(f"Not enough data points for {topic}")
        return

    X = model_df[feature_cols]
    y_reg = model_df[target_col]
    y_clf = bin_disease_rates(y_reg)

    col_min = X.min()
    col_max = X.max()
    col_range = (col_max - col_min).replace(0, 1)
    X_scaled = (X - col_min) / col_range

    X_train, X_test, y_train_reg, y_test_reg = train_test_split(
        X_scaled, y_reg, test_size=0.2, random_state=2500)
    y_train_clf = y_clf.loc[y_train_reg.index]
    y_test_clf = y_clf.loc[y_test_reg.index]

    X_tr, X_val, y_tr_reg, y_val_reg = train_test_split(
        X_train, y_train_reg, test_size=0.2, random_state=2500)
    y_tr_clf = y_train_clf.loc[y_tr_reg.index]
    y_val_clf = y_train_clf.loc[y_val_reg.index]

    best_k_reg = find_best_k_regressor(X_tr, y_tr_reg, X_val, y_val_reg)
    reg_model = KNeighborsRegressor(n_neighbors=best_k_reg)
    reg_model.fit(X_train, y_train_reg)
    reg_preds = reg_model.predict(X_test)
    mse = mean_squared_error(y_test_reg, reg_preds)
    r2 = r2_score(y_test_reg, reg_preds)
    print(f"\n{topic} KNN Regressor:")
    print(f"  MSE: {mse:.4f}")
    print(f"  R²:  {r2:.4f}")

    best_k_clf = find_best_k_classifier(X_tr, y_tr_clf, X_val, y_val_clf)
    clf_model = KNeighborsClassifier(n_neighbors=best_k_clf)
    clf_model.fit(X_train, y_train_clf)
    clf_preds = clf_model.predict(X_test)
    f1 = f1_score(y_test_clf, clf_preds, average="weighted")
    print(f"\n{topic} KNN Classifier:")
    print(f"  F1 (weighted): {f1:.4f}")

    plot_knn_regression_results(y_test_reg.values, reg_preds, topic)
    plot_knn_classification_results(y_test_clf.values, clf_preds, topic)


def plot_knn_regression_results(y_true, y_pred, topic):
    """
    Plot predicted vs actual disease rates for KNN regressor.

    Parameters: array, y_true
                array, y_pred
                str, topic

    Returns: None
    """
    plt.figure(figsize=(8, 6))
    plt.scatter(y_true, y_pred, alpha=0.6, color="steelblue")
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val],
             color="red", linestyle="--", label="Perfect prediction")
    plt.xlabel("Actual Disease Rate")
    plt.ylabel("Predicted Disease Rate")
    plt.title(f"{topic} KNN Regressor: Predicted vs Actual")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(BASE_PATH + f"{topic.replace(' ', '_')}_knn_regression.png")
    plt.show()
    print(f"KNN regression plot saved for {topic}")


def plot_knn_classification_results(y_true, y_pred, topic):
    """
    Plot confusion matrix heatmap for KNN classifier predictions.

    Parameters: array, y_true
                array, y_pred
                str, topic

    Returns: None
    """
    labels = ["low", "medium", "high"]
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    plt.figure(figsize=(7, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(f"{topic} KNN Classifier: Confusion Matrix")
    plt.tight_layout()
    plt.savefig(BASE_PATH + f"{topic.replace(' ', '_')}_knn_classifier.png")
    plt.show()
    print(f"KNN classifier plot saved for {topic}")


def main():
    save_results("Mental Health", "mental_health_data.csv")
    save_results("Alcohol", "alcohol_data.csv")

    mental_health_df = pd.read_csv(BASE_PATH + "mental_health_data.csv")
    alcohol_df = pd.read_csv(BASE_PATH + "alcohol_data.csv")

    print("Mental Health years:", sorted(mental_health_df["YearStart"].unique()))
    print("Alcohol years:", sorted(alcohol_df["YearStart"].unique()))

    year = int(input("Enter a year to analyze: "))

    mental_rates = get_indicator_rates(mental_health_df, year)
    alcohol_rates = get_indicator_rates(alcohol_df, year)

    print("\nMental Health Indicators:")
    print(mental_rates)
    print("\nAlcohol Indicators:")
    print(alcohol_rates)

    mental_pvalues = get_indicator_pvalues(mental_health_df, year)
    alcohol_pvalues = get_indicator_pvalues(alcohol_df, year)

    print("\nMental Health P-Values:")
    print(mental_pvalues)
    print("\nAlcohol P-Values:")
    print(alcohol_pvalues)

    plot_indicator_rates(mental_rates, mental_pvalues, "Mental Health", year)
    plot_indicator_rates(alcohol_rates, alcohol_pvalues, "Alcohol", year)

    mental_all_years = get_indicator_rates_all_years(mental_health_df)
    alcohol_all_years = get_indicator_rates_all_years(alcohol_df)
    plot_regression_trends(mental_all_years, "Mental Health", year)
    plot_regression_trends(alcohol_all_years, "Alcohol", year)

    plot_predictor_strength(mental_health_df, year, "Mental Health")
    plot_predictor_strength(alcohol_df, year, "Alcohol")

    plot_state_scatter_per_indicator(mental_health_df, year, "Mental Health")
    plot_state_scatter_per_indicator(alcohol_df, year, "Alcohol")

    plot_choropleth(mental_health_df, year, "Mental Health")
    plot_choropleth(alcohol_df, year, "Alcohol")

    strat_categories = mental_health_df["StratificationCategory1"].dropna().unique()
    strat_categories = [s for s in strat_categories if s != "Overall"]

    for category in strat_categories:
        plot_demographic_rates(mental_health_df, year, category, "Mental Health")
        plot_demographic_rates(alcohol_df, year, category, "Alcohol")

    plot_stratification_comparison(mental_health_df, year, "Mental Health")
    plot_stratification_comparison(alcohol_df, year, "Alcohol")

    plot_cross_topic_choropleth(alcohol_df, mental_health_df, year)
    plot_cross_topic_scatter(alcohol_df, mental_health_df, year)
    plot_cross_correlation(alcohol_df, mental_health_df, year)

    run_knn_models(mental_health_df, list(mental_health_df["Question"].unique()), SIGNIFICANT_MENTAL[0], "Mental Health")
    run_knn_models(alcohol_df, list(alcohol_df["Question"].unique()), SIGNIFICANT_ALCOHOL[0], "Alcohol")


if __name__ == "__main__":
    main()