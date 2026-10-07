from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from . import config


def load_data(data_file: Path, scenario: str, start_year: int, end_year: int) -> pd.DataFrame:
    df = pd.read_parquet(data_file)

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df = df.dropna(subset=["time"])
        # Use the stored year when present, but derive it from time if needed.
        if "year" not in df.columns:
            df["year"] = df["time"].dt.year
    elif "year" not in df.columns:
        raise ValueError("Dataset must contain either a 'time' or 'year' column.")

    required = {"scenario", "model", "variable", "value", "year"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    df = df[
        (df["scenario"] == scenario)
        & (df["year"] >= start_year)
        & (df["year"] <= end_year)
    ].copy()

    if df.empty:
        raise ValueError(
            f"No rows found for scenario={scenario!r}, years={start_year}-{end_year}."
        )

    return df


def plot_future_trends(df: pd.DataFrame, output_dir: Path, variables: list[str]) -> None:
    for i, var in enumerate(variables, start=1):
        if var not in config.VAR_META:
            print(f"Skipping {var}: no metadata.")
            continue

        label, units, converter = config.VAR_META[var]
        d = df[df["variable"] == var].copy()
        if d.empty:
            print(f"Skipping {var}: no data.")
            continue

        d["value"] = converter(d["value"])

        yearly = (
            d.groupby(["model", "year"], as_index=False)["value"]
            .mean()
        )
        ensemble = yearly.groupby("year")["value"].mean()
        p05 = yearly.groupby("year")["value"].quantile(0.05)
        p95 = yearly.groupby("year")["value"].quantile(0.95)

        plt.figure(figsize=(10, 5))
        for model in yearly["model"].unique():
            m = yearly[yearly["model"] == model]
            plt.plot(m["year"], m["value"], alpha=0.3)

        plt.plot(ensemble.index, ensemble.values, linewidth=2, label="Ensemble mean")
        plt.fill_between(ensemble.index, p05.values, p95.values, alpha=0.2, label="5–95% range")
        plt.title(f"Figure 1.{i}: {label} ({units})")
        plt.xlabel("Year")
        plt.ylabel(units)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"future_climate_{var}.png", dpi=180)
        plt.close()


def january_analysis(df: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    dfx = df.copy()
    dfx["month"] = dfx["time"].dt.month
    jan = dfx[dfx["month"] == 1].copy()

    variables = {
        "tas": ("January Mean Air Temperature", "°C", lambda x: x - 273.15),
        "pr": ("January Total Precipitation", "mm", lambda x: x * 86400.0 * 30.0),
    }

    rows = []

    for i, (var, (label, units, converter)) in enumerate(variables.items(), start=1):
        d = jan[jan["variable"] == var].copy()
        if d.empty:
            print(f"Skipping January {var}: no data.")
            continue

        d["value"] = converter(d["value"])

        plt.figure(figsize=(10, 5))
        for model in d["model"].unique():
            m = d[d["model"] == model]
            yearly = m.groupby("year")["value"].mean()
            plt.plot(yearly.index, yearly.values, alpha=0.3)

        ensemble = d.groupby("year")["value"].mean()
        p05 = d.groupby("year")["value"].quantile(0.05)
        p95 = d.groupby("year")["value"].quantile(0.95)

        plt.plot(ensemble.index, ensemble.values, linewidth=2, label="Ensemble mean")
        plt.fill_between(ensemble.index, p05.values, p95.values, alpha=0.2, label="5–95% range")
        plt.title(f"Figure 2.{i}: {label}")
        plt.xlabel("Year")
        plt.ylabel(units)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"january_{var}.png", dpi=180)
        plt.close()

        early = d[d["year"] < config.START_YEAR + 10]["value"]
        late = d[d["year"] > config.END_YEAR - 10]["value"]

        rows.append({
            "Variable": label,
            "First Decade Mean": early.mean(),
            "Last Decade Mean": late.mean(),
            "Absolute Change": late.mean() - early.mean(),
            "95% CI (Last Decade)": f"{late.quantile(0.05):.2f} to {late.quantile(0.95):.2f}",
        })

    result = pd.DataFrame(rows)
    result.to_csv(output_dir / "january_summary.csv", index=False)
    return result


def _apply_day_definition(df: pd.DataFrame, criteria: dict) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for var, rules in criteria.items():
        if var not in df.columns or rules is None:
            continue
        if "min" in rules:
            mask &= df[var] >= rules["min"]
        if "max" in rules:
            mask &= df[var] <= rules["max"]
    return mask


def good_bad_days(df: pd.DataFrame, output_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    daily = (
        df.pivot_table(
            index=["model", "time", "year"],
            columns="variable",
            values="value",
        )
        .reset_index()
    )

    daily["good_day"] = _apply_day_definition(daily, config.GOOD_DAY)
    daily["bad_day"] = _apply_day_definition(daily, config.BAD_DAY)

    df_days = (
        daily.groupby(["model", "year"])
        .agg(good_days=("good_day", "sum"), bad_days=("bad_day", "sum"))
        .reset_index()
    )
    df_days.to_csv(output_dir / "good_bad_by_model_year.csv", index=False)

    summary = (
        df_days.groupby("year")
        .agg(
            good_mean=("good_days", "mean"),
            good_p05=("good_days", lambda x: x.quantile(0.05)),
            good_p95=("good_days", lambda x: x.quantile(0.95)),
            bad_mean=("bad_days", "mean"),
            bad_p05=("bad_days", lambda x: x.quantile(0.05)),
            bad_p95=("bad_days", lambda x: x.quantile(0.95)),
        )
        .reset_index()
    )

    _plot_days(
        df_days, summary, "good_days", "good_mean", "good_p05", "good_p95",
        "Figure 2.1: Projected Number of Good (Snowmaking-Favorable) Days",
        output_dir / "good_days.png",
    )
    _plot_days(
        df_days, summary, "bad_days", "bad_mean", "bad_p05", "bad_p95",
        "Figure 2.2: Projected Number of Bad (Operationally Unfavorable) Days",
        output_dir / "bad_days.png",
    )

    early_years = range(config.START_YEAR, config.START_YEAR + 10)
    late_years = range(config.END_YEAR - 9, config.END_YEAR + 1)

    summary_table = pd.DataFrame({
        "Metric": ["Good days", "Bad days"],
        "Early period (avg)": [
            summary.loc[summary["year"].isin(early_years), "good_mean"].mean(),
            summary.loc[summary["year"].isin(early_years), "bad_mean"].mean(),
        ],
        "Late period (avg)": [
            summary.loc[summary["year"].isin(late_years), "good_mean"].mean(),
            summary.loc[summary["year"].isin(late_years), "bad_mean"].mean(),
        ],
    })
    summary_table.to_csv(output_dir / "good_bad_summary.csv", index=False)

    return df_days, summary_table


def _plot_days(
    df_days: pd.DataFrame,
    summary: pd.DataFrame,
    raw_col: str,
    mean_col: str,
    p05_col: str,
    p95_col: str,
    title: str,
    filename: Path,
) -> None:
    plt.figure(figsize=(10, 5))
    for model in df_days["model"].unique():
        m = df_days[df_days["model"] == model]
        plt.plot(m["year"], m[raw_col], alpha=0.3)

    plt.plot(summary["year"], summary[mean_col], linewidth=2, label="Ensemble mean")
    plt.fill_between(
        summary["year"],
        summary[p05_col],
        summary[p95_col],
        alpha=0.2,
        label="5–95% range",
    )
    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel("Days per year")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=180)
    plt.close()


def run(
    data_file: Path = config.DATA_FILE,
    output_dir: Path = config.OUTPUT_DIR,
    scenario: str = config.SCENARIO,
    start_year: int = config.START_YEAR,
    end_year: int = config.END_YEAR,
) -> None:
    # Keep config values synchronized for the summary-period calculation.
    config.START_YEAR = start_year
    config.END_YEAR = end_year

    output_dir.mkdir(parents=True, exist_ok=True)
    df = load_data(data_file, scenario, start_year, end_year)

    print(f"Loaded {len(df):,} rows.")
    print(f"Scenario: {scenario}")
    print(f"Years: {start_year}-{end_year}")
    print(f"Models: {df['model'].nunique()}")
    print(f"Variables: {', '.join(sorted(df['variable'].unique()))}")

    plot_future_trends(df, output_dir, config.TREND_VARIABLES)
    january_analysis(df, output_dir)
    good_bad_days(df, output_dir)

    print(f"Done. Outputs are in: {output_dir.resolve()}")
