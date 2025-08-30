# Python Portfolio Tracker

A minimal **FIFO/LIFO portfolio tracker** in pure Python.  
Supports per-trade fees, short selling, realized & unrealized PnL, and simple CSV I/O.

## Features
- FIFO / LIFO trade matching  
- Realized and unrealized PnL  
- Optional short selling  
- Fees included in cost basis  
- CSV input (trades, prices)  
- CLI entrypoint `python_portfolio_tracker`  

## Install
Clone the repo and install in editable mode:

```bash
git clone https://github.com/eddipa/python_portfolio_tracker.git
cd python_portfolio_tracker
pip install -e .
```

## Usage
Prepare your `trades.csv`:

```csv
date,ticker,side,qty,price,fee
2024-01-10,AAPL,BUY,10,180,0.50
2024-02-05,AAPL,SELL,5,200,0.50
2024-03-12,MSFT,BUY,4,400,0.00
```

(Optional) `prices.csv`:

```csv
ticker,price
AAPL,195.34
MSFT,420.10
```

Run the CLI:

```bash
python_portfolio_tracker trades.csv FIFO --prices prices.csv
```

Example output:

```
=== Portfolio Report (FIFO) ===
-- Realized PnL by ticker --
  AAPL          97.50

-- Open Positions --
Ticker          Qty      AvgCost       Price     MktValue    CostBasis      UnrlPnL
------------------------------------------------------------------------------------
MSFT             4     400.00        420.10     1680.40      1600.00        80.40

-- Totals --
  Realized:   97.50
  Unrealized: 80.40
  Equity:     1760.80
```

## Development
Run tests with [pytest](https://docs.pytest.org/):

```bash
pytest -q
```

## License
MIT
