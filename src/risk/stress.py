import numpy as np
import pandas as pd
from ..config.config import cfg
from .pnl import TENORS, fit_betas, portfolio_weights_series

def classic_scenarios():
    # shocks in basis points
    return {
        "Parallel +50bp": {"3M":50, "2Y":50, "5Y":50, "10Y":50, "30Y":50},
        "Bear steepener": {"3M":25, "2Y":35, "5Y":55, "10Y":70, "30Y":85},
        "Bull flattener": {"3M":-40, "2Y":-35, "5Y":-20, "10Y":-10, "30Y":-5},
    }

def load_data():
    rets = pd.read_csv(cfg.curated_dir / "asset_returns.csv", parse_dates=["date"]).set_index("date")
    yc = pd.read_csv(cfg.curated_dir / "yield_curves.csv", parse_dates=["date"]).set_index("date")
    dy = yc[TENORS].diff().dropna() * 10000.0
    idx = rets.index.intersection(dy.index)
    return rets.loc[idx], dy.loc[idx]

def estimate_betas(rets: pd.DataFrame, dy_bp: pd.DataFrame, lookback=60):
    if len(rets) < 5:
        raise ValueError("Need at least a few rows to estimate betas.")
    w = min(lookback, len(rets))
    R = rets.iloc[-w:]
    X = dy_bp.reindex(R.index)
    betas = {a: fit_betas(X, R[a]) for a in R.columns}
    return pd.DataFrame(betas).T  # assets x tenors

def scenario_pnl(betas_df: pd.DataFrame, scenario_bp: dict):
    dy_vec = pd.Series(scenario_bp).reindex(TENORS).fillna(0.0)
    asset_ret = betas_df @ dy_vec
    w = portfolio_weights_series(betas_df.index)
    port_ret = float((asset_ret * w).sum())
    tenor_contrib = (betas_df.mul(w, axis=0).T * dy_vec).sum(axis=1)
    return port_ret, tenor_contrib

def main():
    rets, dy_bp = load_data()
    betas_df = estimate_betas(rets, dy_bp, lookback=60)

    rows = []
    for name, sc in classic_scenarios().items():
        pr, tc = scenario_pnl(betas_df, sc)
        row = {"scenario": name, "pred_port_return": pr}
        for t in TENORS:
            row[f"C_{t}"] = tc.get(t, 0.0)
        rows.append(row)

    out = pd.DataFrame(rows)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    path = cfg.out_dir / "stress_results.csv"
    out.to_csv(path, index=False)
    print("Wrote", path.resolve())

if __name__ == "__main__":
    main()
