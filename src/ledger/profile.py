"""A plain profiler: for every column, the type, null share, distinct count, range and top values."""

from __future__ import annotations

import pandas as pd


def profile(df: pd.DataFrame, top: int = 5) -> pd.DataFrame:
    rows = []
    n = len(df)
    for col in df.columns:
        s = df[col]
        numeric = pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s)
        vc = s.value_counts(dropna=True).head(top)
        rows.append(
            {
                "column": col,
                "dtype": str(s.dtype),
                "null_pct": round(100 * s.isna().mean(), 2) if n else 0.0,
                "distinct": s.nunique(dropna=True),
                "min": s.min() if numeric else None,
                "median": s.median() if numeric else None,
                "max": s.max() if numeric else None,
                "zeros_pct": round(100 * (s == 0).mean(), 2) if numeric and n else None,
                "top_values": ", ".join(f"{k} ({v})" for k, v in vc.items()),
            }
        )
    return pd.DataFrame(rows)


def duplicate_keys(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Rows whose key combination appears more than once. Empty means `keys` is the grain."""
    dup = df.duplicated(keys, keep=False)
    return df.loc[dup].sort_values(keys)


def report(name: str, df: pd.DataFrame) -> str:
    """Markdown for docs/profiles/<name>.md."""
    mem = df.memory_usage(deep=True).sum() / 1e6
    head = f"# Profile: {name}\n\n{len(df):,} rows x {df.shape[1]} columns, {mem:,.1f} MB in memory\n\n"
    return head + profile(df).to_markdown(index=False) + "\n"
