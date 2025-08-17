from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import date
import pandas as pd
from ..config.config import cfg
from ..risk.var import portfolio_returns, hs_var_es

def main():
    rets = pd.read_csv(cfg.curated_dir / "asset_returns.csv", parse_dates=["date"]).set_index("date")
    port = portfolio_returns(rets, pd.Series(cfg.weights))
    m = hs_var_es(port, 0.99)

    ctx = {
        "date": date.today().isoformat(),
        "metrics": {
            "var_99": f"{m['VaR']:.6f}",
            "es_99": "n/a" if m["ES"] != m["ES"] else f"{m['ES']:.6f}"
        },
        "commentary": "Losses driven by duration; monitor 10Y moves."
    }

    env = Environment(loader=FileSystemLoader(str(cfg.templates_dir)))
    html_str = env.get_template("daily.html").render(**ctx)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    try:
        HTML(string=html_str).write_pdf(str(cfg.out_dir / "daily.pdf"))
        print("Wrote out/daily.pdf")
    except Exception:
        (cfg.out_dir / "daily.html").write_text(html_str, encoding="utf-8")
        print("PDF deps missing; wrote out/daily.html")

if __name__ == "__main__":
    main()
