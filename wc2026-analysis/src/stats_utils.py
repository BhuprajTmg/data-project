"""Reusable descriptive- and inferential-statistics helpers for the
FIFA World Cup 2026 analytics project.

Kept deliberately simple and transparent (no black-box wrappers) so every
number that appears in the notebooks can be traced back to a formula.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def describe(series: pd.Series) -> pd.Series:
    """Return a compact set of descriptive statistics for a numeric sample."""
    s = pd.Series(series).dropna().astype(float)
    return pd.Series(
        {
            "n": s.shape[0],
            "mean": s.mean(),
            "median": s.median(),
            "std": s.std(ddof=1),
            "min": s.min(),
            "max": s.max(),
            "range": s.max() - s.min(),
            "skew": s.skew(),
            "q1": s.quantile(0.25),
            "q3": s.quantile(0.75),
        }
    )


def ci_mean(series: pd.Series, confidence: float = 0.95) -> dict:
    """Confidence interval for a population mean using the t-distribution
    (appropriate whenever the population standard deviation is unknown,
    which is always the case here since we only ever observe a sample).
    """
    s = pd.Series(series).dropna().astype(float)
    n = s.shape[0]
    mean = s.mean()
    se = s.std(ddof=1) / np.sqrt(n)
    alpha = 1 - confidence
    t_crit = stats.t.ppf(1 - alpha / 2, df=n - 1)
    margin = t_crit * se
    return {
        "n": n,
        "mean": mean,
        "se": se,
        "t_crit": t_crit,
        "margin_of_error": margin,
        "ci_low": mean - margin,
        "ci_high": mean + margin,
        "confidence": confidence,
    }


def one_sample_ttest(series: pd.Series, popmean: float, alternative: str = "two-sided") -> dict:
    s = pd.Series(series).dropna().astype(float)
    t_stat, p_val = stats.ttest_1samp(s, popmean=popmean, alternative=alternative)
    n = s.shape[0]
    d = (s.mean() - popmean) / s.std(ddof=1)  # Cohen's d
    return {
        "n": n,
        "sample_mean": s.mean(),
        "popmean_h0": popmean,
        "t_stat": t_stat,
        "df": n - 1,
        "p_value": p_val,
        "alternative": alternative,
        "cohens_d": d,
    }


def two_sample_ttest(
    group_a: pd.Series,
    group_b: pd.Series,
    equal_var: bool = False,
    alternative: str = "two-sided",
) -> dict:
    """Welch's t-test by default (equal_var=False), which does not assume
    equal population variances between the two groups -- the safer default
    for real-world sports data.
    """
    a = pd.Series(group_a).dropna().astype(float)
    b = pd.Series(group_b).dropna().astype(float)
    t_stat, p_val = stats.ttest_ind(a, b, equal_var=equal_var, alternative=alternative)

    n1, n2 = a.shape[0], b.shape[0]
    v1, v2 = a.var(ddof=1), b.var(ddof=1)
    if equal_var:
        df = n1 + n2 - 2
    else:
        df = (v1 / n1 + v2 / n2) ** 2 / (
            (v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1)
        )
    pooled_sd = np.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    cohens_d = (a.mean() - b.mean()) / pooled_sd

    return {
        "n1": n1,
        "n2": n2,
        "mean1": a.mean(),
        "mean2": b.mean(),
        "sd1": np.sqrt(v1),
        "sd2": np.sqrt(v2),
        "t_stat": t_stat,
        "df": df,
        "p_value": p_val,
        "alternative": alternative,
        "equal_var": equal_var,
        "cohens_d": cohens_d,
    }


def levene_test(group_a: pd.Series, group_b: pd.Series) -> dict:
    """Test the equal-variance assumption; informs whether Welch's or the
    pooled-variance t-test is more appropriate."""
    a = pd.Series(group_a).dropna().astype(float)
    b = pd.Series(group_b).dropna().astype(float)
    stat, p_val = stats.levene(a, b)
    return {"levene_stat": stat, "p_value": p_val}
