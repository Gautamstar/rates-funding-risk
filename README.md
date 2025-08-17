# Rates Funding Risk

This project is a lightweight framework for analyzing **interest rate risk in fixed income portfolios**. It focuses on calculating DV01 (Dollar Value of 1 Basis Point), applying rate shock scenarios, and breaking down PnL contributions by maturity buckets. The goal is to give a clear view of how different parts of the yield curve affect portfolio risk.

---

## Features

- **DV01 Calculation** – measures sensitivity of portfolio value to a 1 bp shift in rates across maturities (3M, 2Y, 5Y, 10Y, 30Y).  
- **Stress Testing** – applies common market scenarios such as parallel shifts, bear steepeners, and bull flatteners, then outputs predicted portfolio returns.  
- **PnL Attribution** – explains portfolio moves by showing tenor-level contributions to overall PnL.  
- **CSV Outputs** – results are automatically saved in the `out/` folder:
  - `stress_results_dv01.csv` → scenario results  
  - `pnl_explain_dv01.csv` → attribution by maturity  

## Project Structure
```
rates-funding-risk/
├── src/
│ └── risk/
│ ├── stress_dv01.py # Stress testing engine
│ ├── pnl_dv01.py # DV01 attribution
│ └── stress.py # placeholder for beta estimation
├── out/ # Results written here
│ ├── stress_results_dv01.csv
│ └── pnl_explain_dv01.csv
└── README.md
```
## Example Outputs
Stress Results
```
scenario        pred_port_return     C_3M   C_2Y   C_5Y   C_10Y   C_30Y
Parallel +50bp  -158.0               -3.0   -12.0  -27.0  -50.0   -66.0
Bear steepener  -221.8               -1.5   -8.4   -29.7  -70.0   -112.2
Bull flattener   38.2                 2.4    8.4   10.8   10.0     6.6
```
PnL Attrivution
```
tenor   bp_move   tenor_contribution_pct
3M      -10.0     0.0014
2Y      -10.0     0.0040
5Y      -10.0     0.0076
10Y     -10.0     0.0124
30Y     -10.0     0.0160
TOTAL              0.0414



