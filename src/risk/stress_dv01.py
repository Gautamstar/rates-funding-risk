import pandas as pd
from ..config.config import cfg
from .pnl_dv01 import TENORS, portfolio_krd

def scenarios_bp():
    return {
        "Parallel +50bp": {"3M":50,"2Y":50,"5Y":50,"10Y":50,"30Y":50},
        "Bear steepener": {"3M":25,"2Y":35,"5Y":55,"10Y":70,"30Y":85},
        "Bull flattener": {"3M":-40,"2Y":-35,"5Y":-20,"10Y":-10,"30Y":-5},
    }

def main():
    krd = portfolio_krd(cfg.weights)  # key-rate DV01 of the portfolio
    rows = []
    for name, shock in scenarios_bp().items():
        shock_s = pd.Series(shock).reindex(TENORS).fillna(0.0)
        contrib = -krd * shock_s  # price down when yields up
        port_ret = contrib.sum()
        row = {"scenario": name, "pred_port_return": port_ret}
        for t in TENORS:
            row[f"C_{t}"] = contrib[t]
        rows.append(row)
    out = pd.DataFrame(rows)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    path = cfg.out_dir / "stress_results_dv01.csv"
    out.to_csv(path, index=False)
    print("Wrote", path.resolve())

if __name__ == "__main__":
    main()
