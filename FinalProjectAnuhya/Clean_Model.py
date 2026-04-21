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
from sklearn.metrics import mean_squared_error
from scipy import stats

BASE_PATH = "C:\\Users\\anuhy\\DS2500\\FinalProject\\"
df = pd.read_csv(BASE_PATH + "U.S._Chronic_Disease_Indicators (1).csv")

PREVALENCE_TYPES = ["crude prevalence", "age-adjusted prevalence"]
SIGNIFICANCE = 0.05


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

    # bold y-axis labels for significant indicators
    for label, p in zip(ax.get_yticklabels(), merged["pvalue"]):
        if p < SIGNIFICANCE:
            label.set_fontweight("bold")

    from matplotlib.patches import Patch
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
    threshold = max_slope * 0.5  # top half of slopes highlighted

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
        indicator_df = get_state_level_data(dataframe, year, question)
        merged = pd.merge(indicator_df, anchor_df, on="StateAbbr")

        if len(merged) < 5:
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
        indicator_df = get_state_level_data(dataframe, year, question)
        merged = pd.merge(indicator_df, anchor_df, on="StateAbbr")

        if len(merged) < 5:
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
        colors = ["tomato" if val > mean_y + std_y else
                  "steelblue" if val < mean_y - std_y else
                  "steelblue" for val in y]

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

    from matplotlib.patches import Patch
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

    # build annotation matrix with stars for strong correlations
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


def main():
    # save disease-specific CSVs
    save_results("Mental Health", "mental_health_data.csv")
    save_results("Alcohol", "alcohol_data.csv")

    mental_health_df = pd.read_csv(BASE_PATH + "mental_health_data.csv")
    alcohol_df = pd.read_csv(BASE_PATH + "alcohol_data.csv")

    print("Mental Health years:", sorted(mental_health_df["YearStart"].unique()))
    print("Alcohol years:", sorted(alcohol_df["YearStart"].unique()))

    year = int(input("Enter a year to analyze: "))

    # --- INDICATOR ANALYSIS ---
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

    # --- STATE ANALYSIS ---
    plot_choropleth(mental_health_df, year, "Mental Health")
    plot_choropleth(alcohol_df, year, "Alcohol")

    # --- DEMOGRAPHIC ANALYSIS ---
    strat_categories = mental_health_df["StratificationCategory1"].dropna().unique()
    strat_categories = [s for s in strat_categories if s != "Overall"]

    for category in strat_categories:
        plot_demographic_rates(mental_health_df, year, category, "Mental Health")
        plot_demographic_rates(alcohol_df, year, category, "Alcohol")

    plot_stratification_comparison(mental_health_df, year, "Mental Health")
    plot_stratification_comparison(alcohol_df, year, "Alcohol")

    # --- CROSS TOPIC ANALYSIS ---
    plot_cross_topic_choropleth(alcohol_df, mental_health_df, year)
    plot_cross_topic_scatter(alcohol_df, mental_health_df, year)
    plot_cross_correlation(alcohol_df, mental_health_df, year)


if __name__ == "__main__":
    main()