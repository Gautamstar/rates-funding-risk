# src/risk/pnl_dv01.py
import pandas as pd
from ..config.config import cfg

TENORS = ["3M", "2Y", "5Y", "10Y", "30Y"]

# Approximate key-rate DV01s per $100 notional, per 1 bp
# (Tune to your holdings; these are illustrative and smaller than before)
ASSET_KRD = {
    "ZFL_TO": {"3M":0.00, "2Y":0.02, "5Y":0.08, "10Y":0.16, "30Y":0.22},
    "GOVT":   {"3M":0.01, "2Y":0.04, "5Y":0.10, "10Y":0.15, "30Y":0.18},
    "SHY":    {"3M":0.05, "2Y":0.08, "5Y":0.02, "10Y":0.00, "30Y":0.00},
}

def portfolio_krd(weights: dict) -> pd.Series:
    w = pd.Series(weights)
    # weighted sum of asset KRDs → portfolio KRD (per $100 notional)
    return sum(w[a] * pd.Series(ASSET_KRD[a]) for a in w.index).reindex(TENORS).fillna(0.0)

def main():
    # Shock results already written by stress_dv01; here we compute DV01 explain vs last-day bp moves
    yc = pd.read_csv(cfg.curated_dir / "yield_curves.csv", parse_dates=["date"]).set_index("date")
    dy_bp = yc[TENORS].diff().dropna().iloc[-1] * 10000.0  # last-day bp moves
    krd = portfolio_krd(cfg.weights)                       # per $100 per bp
    # Dollar contribution per $100 notional = -DV01 * bp_move
    dollar_contrib_per_100 = -krd * dy_bp
    # Convert to percent portfolio return (per $100 basis)
    pct_return_contrib = dollar_contrib_per_100 / 100.0
    out = pd.DataFrame({
        "tenor": TENORS,
        "bp_move": dy_bp.reindex(TENORS).values,
        "tenor_contribution_pct": pct_return_contrib.reindex(TENORS).values
    })
    out.loc[len(out)] = ["TOTAL", float("nan"), out["tenor_contribution_pct"].sum()]
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    path = cfg.out_dir / "pnl_explain_dv01.csv"
    out.to_csv(path, index=False)
    print("Wrote", path.resolve())

if __name__ == "__main__":
    main()

