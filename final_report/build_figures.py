"""Generate clean matplotlib figures for the final report.

Replaces the slide-deck screenshots (slide-06/07/08.png) with proper
academic-style figures rendered directly from the project's analyses.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.preprocessing import StandardScaler

REPO = Path(__file__).resolve().parents[1]
FIG_DIR = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams.update(
    {
        "figure.dpi": 150,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
    }
)


def figure_2_coefficients() -> None:
    """Standardized regression coefficients for heart disease mortality (7-feature LR)."""
    df = pd.read_csv(REPO / "data" / "processed" / "state_indicators.csv")

    predictors = [
        "smoking_prev",
        "obesity_prev",
        "physical_inactivity_prev",
        "flu_vaccination_prev",
        "poverty_prev",
        "food_insecurity_prev",
        "hs_completion_prev",
    ]
    display = {
        "smoking_prev": "Smoking",
        "obesity_prev": "Obesity",
        "physical_inactivity_prev": "Phys. Inactivity",
        "flu_vaccination_prev": "Flu Vaccination",
        "poverty_prev": "Poverty",
        "food_insecurity_prev": "Food Insecurity",
        "hs_completion_prev": "HS Completion",
    }
    target = "heart_disease_mortality_rate"

    sub = df[predictors + [target]].dropna()
    x_scaled = StandardScaler().fit_transform(sub[predictors].values)
    y = sub[target].values
    coefs = LinearRegression().fit(x_scaled, y).coef_

    order = np.argsort(np.abs(coefs))
    sorted_labels = [display[predictors[i]] for i in order]
    sorted_coefs = coefs[order]
    colors = ["#c0392b" if c >= 0 else "#2980b9" for c in sorted_coefs]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(sorted_labels, sorted_coefs, color=colors, alpha=0.85, edgecolor="white")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Standardized Coefficient (\u03b2)")
    ax.set_title(
        "Heart Disease Mortality: Standardized Regression Coefficients\n"
        "Seven-feature linear regression, n = 51 states"
    )
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    for i, (label, c) in enumerate(zip(sorted_labels, sorted_coefs)):
        offset = 0.4 if c >= 0 else -0.4
        ha = "left" if c >= 0 else "right"
        ax.text(c + offset, i, f"{c:+.2f}", va="center", ha=ha, fontsize=9)

    out = FIG_DIR / "fig_coefficients_heart_disease.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out}")
    poverty = coefs[predictors.index("poverty_prev")]
    smoking = coefs[predictors.index("smoking_prev")]
    print(f"  poverty/smoking ratio = {poverty/smoking:.2f}x")


def figure_4_tobacco_cancer_copd() -> None:
    """Side-by-side scatter: tobacco vs cancer prevalence and tobacco vs COPD prevalence."""
    df = pd.read_csv(
        REPO / "FinalProjectAnuhya" / "U.S._Chronic_Disease_Indicators (1).csv",
        low_memory=False,
    )
    df = df.dropna(subset=["DataValue", "YearStart", "LocationDesc"])
    df["DataValue"] = pd.to_numeric(df["DataValue"], errors="coerce")

    research = df[
        (df["Topic"].isin(["Cancer", "Tobacco", "Chronic Obstructive Pulmonary Disease"]))
        & (df["DataValueType"].astype(str).str.contains("Prevalence", na=False))
        & (df["DataValue"] < 100)
    ].copy()

    table = (
        research.pivot_table(
            index=["LocationDesc", "YearStart"],
            columns="Topic",
            values="DataValue",
        ).dropna()
    )

    tob = table["Tobacco"].values
    cancer = table["Cancer"].values
    copd = table["Chronic Obstructive Pulmonary Disease"].values

    r_cancer, p_cancer = pearsonr(tob, cancer)
    r_copd, p_copd = pearsonr(tob, copd)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    def fit_line(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        coef = np.polyfit(x, y, 1)
        xs = np.linspace(x.min(), x.max(), 100)
        return xs, coef[0] * xs + coef[1]

    xs1, ys1 = fit_line(tob, cancer)
    ax1.scatter(tob, cancer, alpha=0.55, color="steelblue", s=35, edgecolor="white", linewidth=0.4)
    ax1.plot(xs1, ys1, color="crimson", linewidth=2, label="Linear trend")
    ax1.set_xlabel("Tobacco Use (%)")
    ax1.set_ylabel("Cancer Prevalence (%)")
    ax1.set_title(f"Tobacco vs Cancer\nPearson r = {r_cancer:.2f}, R\u00b2 = {r_cancer**2:.2f}")
    ax1.grid(linestyle="--", alpha=0.4)
    ax1.legend()

    xs2, ys2 = fit_line(tob, copd)
    ax2.scatter(tob, copd, alpha=0.55, color="darkorange", s=35, edgecolor="white", linewidth=0.4)
    ax2.plot(xs2, ys2, color="crimson", linewidth=2, label="Linear trend")
    ax2.set_xlabel("Tobacco Use (%)")
    ax2.set_ylabel("COPD Prevalence (%)")
    ax2.set_title(f"Tobacco vs COPD\nPearson r = {r_copd:.2f}, R\u00b2 = {r_copd**2:.2f}")
    ax2.grid(linestyle="--", alpha=0.4)
    ax2.legend()

    out = FIG_DIR / "fig_tobacco_cancer_copd.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out}")
    print(f"  tobacco-cancer r={r_cancer:.3f} R^2={r_cancer**2:.3f} p={p_cancer:.4g}")
    print(f"  tobacco-COPD   r={r_copd:.3f} R^2={r_copd**2:.3f} p={p_copd:.4g}")


def figure_5_alcohol_mental() -> None:
    """Normalized rates of alcohol and mental health indicators (US overall, 2020)."""
    base = REPO / "FinalProjectAnuhya"

    PER_CAPITA_GALLONS_SCALE = 5.0  # US per-capita alcohol consumption rarely exceeds 5 gal/yr

    def normalize(value: float, unit: str) -> float | None:
        u = str(unit).lower()
        if "%" in u or "percent" in u:
            return value / 100.0
        if "100,000" in u:
            return value / 100_000.0
        if "1,000" in u:
            return value / 1_000.0
        if "gallons" in u:
            return value / PER_CAPITA_GALLONS_SCALE
        return None

    SHORT_LABEL = {
        "Binge drinking frequency among adults who binge drink": "Binge drinking frequency",
        "Binge drinking intensity among adults who binge drink": "Binge drinking intensity",
        "Binge drinking prevalence among adults": "Binge drinking prevalence",
        "Per capita alcohol consumption among people aged 14 years and older": "Per-capita alcohol consumption (\u226514 yrs)",
        "Chronic liver disease mortality among all people, underlying cause": "Chronic liver disease mortality",
        "Depression among adults": "Depression among adults",
        "Frequent mental distress among adults": "Frequent mental distress",
        "Average mentally unhealthy days among adults": "Avg. mentally unhealthy days",
        "Postpartum depressive symptoms among women with a recent live birth": "Postpartum depressive symptoms",
    }

    def load_rates(filename: str, year: int) -> pd.DataFrame:
        df = pd.read_csv(base / filename, low_memory=False)
        df = df[
            (df["YearStart"] == year)
            & (df["LocationDesc"] == "United States")
            & (df["Stratification1"] == "Overall")
        ].copy()
        rows = []
        for _, row in df.iterrows():
            normed = normalize(row["DataValue"], row["DataValueUnit"])
            if normed is None:
                continue
            label = SHORT_LABEL.get(row["Question"], row["Question"])
            rows.append({"Question": label, "NormalizedRate": normed})
        out = pd.DataFrame(rows).dropna()
        if not out.empty:
            out = (
                out.groupby("Question", as_index=False)["NormalizedRate"]
                .mean()  # collapse Crude / Age-adjusted variants
            )
        return out

    year = 2020
    alcohol = load_rates("alcohol_data.csv", year)
    mental = load_rates("mental_health_data.csv", year)

    if alcohol.empty or mental.empty:
        raise RuntimeError("alcohol or mental-health frame empty — check input CSVs")

    alcohol = alcohol.sort_values("NormalizedRate")
    mental = mental.sort_values("NormalizedRate")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6.5), gridspec_kw={"hspace": 0.55})

    ax1.barh(alcohol["Question"], alcohol["NormalizedRate"], color="steelblue", alpha=0.85)
    ax1.set_xlabel("Normalized Rate (0\u20131)")
    ax1.set_title(f"Alcohol Indicator Rates \u2014 {year} (US Overall)")
    ax1.grid(axis="x", linestyle="--", alpha=0.4)
    ax1.set_xlim(0, max(alcohol["NormalizedRate"].max(), 0.6) * 1.1)
    for i, v in enumerate(alcohol["NormalizedRate"]):
        ax1.text(v + 0.005, i, f"{v:.3f}", va="center", fontsize=8)

    ax2.barh(mental["Question"], mental["NormalizedRate"], color="mediumseagreen", alpha=0.85)
    ax2.set_xlabel("Normalized Rate (0\u20131)")
    ax2.set_title(f"Mental Health Indicator Rates \u2014 {year} (US Overall)")
    ax2.grid(axis="x", linestyle="--", alpha=0.4)
    ax2.set_xlim(0, max(mental["NormalizedRate"].max(), 0.25) * 1.1)
    for i, v in enumerate(mental["NormalizedRate"]):
        ax2.text(v + 0.003, i, f"{v:.3f}", va="center", fontsize=8)
    out = FIG_DIR / "fig_alcohol_mental_indicators.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    figure_2_coefficients()
    figure_4_tobacco_cancer_copd()
    figure_5_alcohol_mental()
