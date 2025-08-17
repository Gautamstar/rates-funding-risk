import numpy as np
import pandas as pd
from ..config.config import cfg

TENORS = ["3M", "2Y", "5Y", "10Y", "30Y"]

def prepare_data():
    rets = pd.read_csv(cfg.curated_dir / "asset_returns.csv", parse_dates=["date"]).set_index("date")
    yc = pd.read_csv(cfg.curated_dir / "yield_curves.csv", parse_dates=["date"]).set_index("date")
    dy = yc[TENORS].diff().dropna() * 10000.0  # daily changes in basis points
    idx = rets.index.intersection(dy.index)
    return rets.loc[idx], dy.loc[idx]

def fit_betas(X_bp: pd.DataFrame, y_ret: pd.Series):
    X = X_bp.values
    y = y_ret.values
    XtX = X.T @ X
    ridge = 1e-6 * np.eye(XtX.shape[0])  # tiny ridge for stability
    b = np.linalg.solve(XtX + ridge, X.T @ y)
    return pd.Series(b, index=X_bp.columns)

def portfolio_weights_series(asset_cols):
    w = pd.Series(cfg.weights)
    return w.reindex(asset_cols).fillna(0.0)

def attribute_last_day(rets: pd.DataFrame, dy_bp: pd.DataFrame, lookback=60):
    if len(rets) < 2 or len(dy_bp) < 2:
        raise ValueError("Not enough data for attribution.")
    w = min(lookback, len(rets) - 1)
    window_idx = rets.index[-w-1:]
    R = rets.loc[window_idx].iloc[:-1]
    X = dy_bp.loc[window_idx].iloc[:-1]

    betas = {a: fit_betas(X, R[a]) for a in R.columns}
    betas_df = pd.DataFrame(betas).T  # assets x tenors

    last_dy = dy_bp.loc[window_idx].iloc[-1]
    wts = portfolio_weights_series(rets.columns)

    tenor_contrib = (betas_df.mul(wts, axis=0).T * last_dy).sum(axis=1)
    last_port_ret = float((rets.loc[window_idx].iloc[-1] * wts).sum())

    out = pd.DataFrame({"bp_move": last_dy, "tenor_contribution": tenor_contrib})
    out.loc["TOTAL", "bp_move"] = np.nan
    out.loc["TOTAL", "tenor_contribution"] = out["tenor_contribution"].sum()
    return out, last_port_ret

def main():
    rets, dy_bp = prepare_data()
    explain, last_port = attribute_last_day(rets, dy_bp, lookback=60)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = cfg.out_dir / "pnl_explain.csv"
    explain.reset_index(names="tenor").to_csv(out_csv, index=False)
    print("Wrote", out_csv.resolve())
    print("Last-day actual portfolio return:", f"{last_port:.6f}")

if __name__ == "__main__":
    main()

