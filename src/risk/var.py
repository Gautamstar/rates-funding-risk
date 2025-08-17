import numpy as np
import pandas as pd

def portfolio_returns(returns_df: pd.DataFrame, weights: pd.Series) -> pd.Series:
    w = weights.reindex(returns_df.columns).fillna(0.0).values
    return returns_df.dot(w)

def hs_var_es(port_rets: pd.Series, alpha=0.99):
    x = np.sort(port_rets.dropna().values)
    idx = int((1 - alpha) * len(x))
    var = -x[idx]
    es  = -x[:idx].mean() if idx > 0 else float("nan")
    return {"VaR": var, "ES": es}

def vcov_var(weights: np.ndarray, cov: np.ndarray, alpha=0.99):
    z = {0.95: 1.645, 0.99: 2.326}.get(alpha, 2.326)
    sigma = float(np.sqrt(weights.T @ cov @ weights))
    return z * sigma
