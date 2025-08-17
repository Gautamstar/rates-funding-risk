import pandas as pd
from ..config.config import cfg

def main():
    cfg.curated_dir.mkdir(parents=True, exist_ok=True)

    # Yield curves → keep as normal CSV
    yc = pd.read_csv(cfg.raw_dir / "yield_curves.csv", parse_dates=["date"])
    yc.to_csv(cfg.curated_dir / "yield_curves.csv", index=False)

    # Asset returns → use date index for downstream math
    rets = (
        pd.read_csv(cfg.raw_dir / "asset_returns.csv", parse_dates=["date"])
          .set_index("date")
          .sort_index()
    )
    rets.to_csv(cfg.curated_dir / "asset_returns.csv")

    print("✅ Curated files written to:", cfg.curated_dir.resolve())

if __name__ == "__main__":
    main()
