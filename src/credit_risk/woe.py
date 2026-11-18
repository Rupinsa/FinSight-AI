
import pandas as pd
import numpy as np

def calculate_woe_iv(X, y, features, bins=5):
    """Calculate numeric-feature Weight of Evidence and Information Value tables."""
    y = pd.Series(y).reset_index(drop=True).astype(int)
    results = []
    for feature in features:
        x = pd.Series(X[feature]).reset_index(drop=True)
        try:
            grouped = pd.qcut(x, q=bins, duplicates="drop")
        except ValueError:
            grouped = x.astype(str)
        temp = pd.DataFrame({"bin": grouped.astype(str), "target": y})
        summary = temp.groupby("bin", observed=False)["target"].agg(
            total="count", bad="sum"
        ).reset_index()
        summary["good"] = summary["total"] - summary["bad"]
        # 0.5 smoothing avoids division by zero in small bins.
        bad_dist = (summary["bad"] + 0.5) / (summary["bad"].sum() + 0.5*len(summary))
        good_dist = (summary["good"] + 0.5) / (summary["good"].sum() + 0.5*len(summary))
        summary["woe"] = np.log(good_dist / bad_dist)
        summary["iv_component"] = (good_dist - bad_dist) * summary["woe"]
        summary.insert(0, "feature", feature)
        results.append(summary)
    if not results:
        return pd.DataFrame()
    return pd.concat(results, ignore_index=True)
