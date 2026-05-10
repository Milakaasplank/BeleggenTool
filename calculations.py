import numpy as np


def parse_degiro_number(text):
    """
    Parse a value copied from DeGiro into an exact float.

    Handles suffix K (10^3), M (10^6), B/T (biljoen, 10^12).
    Both '.' and ',' are accepted as decimal separator.
    Returns 0.0 for empty input. Raises ValueError on unparseable input.
    """
    if text is None:
        return 0.0
    s = str(text).strip().upper().replace(" ", "").replace(" ", "").replace("€", "").replace("$", "")
    if not s:
        return 0.0

    multiplier = 1.0
    if s[-1] in ("B", "T"):
        multiplier = 1_000_000_000_000
        s = s[:-1]
    elif s[-1] == "M":
        multiplier = 1_000_000
        s = s[:-1]
    elif s[-1] == "K":
        multiplier = 1_000
        s = s[:-1]

    s = s.replace(",", ".")
    return float(s) * multiplier


def _fmt_nl(value, decimals=0):
    """Format number with Dutch separators: 1.234.567,89"""
    s = f"{value:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def preview_geld_M(value_in_miljoenen):
    """Live preview onder een 'in M €'-veld. Toont het absolute bedrag + magnitude."""
    if not value_in_miljoenen:
        return ""
    v = value_in_miljoenen * 1_000_000
    if abs(v) >= 1_000_000_000_000:
        return f"= € {_fmt_nl(v)} ({_fmt_nl(v/1e12, 2)} B / biljoen)"
    if abs(v) >= 1_000_000_000:
        return f"= € {_fmt_nl(v)} ({_fmt_nl(v/1e9, 2)} mrd)"
    if abs(v) >= 1_000_000:
        return f"= € {_fmt_nl(v)} ({_fmt_nl(v/1e6, 2)} mln)"
    return f"= € {_fmt_nl(v)}"


def preview_aantal_M(value_in_miljoenen):
    """Live preview onder een 'in M aandelen'-veld."""
    if not value_in_miljoenen:
        return ""
    v = value_in_miljoenen * 1_000_000
    if abs(v) >= 1_000_000_000_000:
        return f"= {_fmt_nl(v)} aandelen ({_fmt_nl(v/1e12, 2)} B / biljoen)"
    if abs(v) >= 1_000_000_000:
        return f"= {_fmt_nl(v)} aandelen ({_fmt_nl(v/1e9, 2)} mrd)"
    if abs(v) >= 1_000_000:
        return f"= {_fmt_nl(v)} aandelen ({_fmt_nl(v/1e6, 2)} mln)"
    return f"= {_fmt_nl(v)} aandelen"


def format_degiro_number(value):
    """Short display form: 3.809B / 18.90M / 12,34 — uses Dutch decimal comma."""
    if value is None:
        return "0"
    v = float(value)
    if abs(v) >= 1e12:
        return f"{v/1e12:.3f}B".replace(".", ",")
    if abs(v) >= 1e6:
        return f"{v/1e6:.2f}M".replace(".", ",")
    if abs(v) >= 1e3:
        return f"{v/1e3:.2f}K".replace(".", ",")
    return f"{v:.2f}".replace(".", ",")


def eigen_vermogen(activa, passiva):
    """
    Calculate eigen vermogen (equity) from assets and liabilities.

    :param activa: Total assets
    :param passiva: Total liabilities
    :return: Eigen vermogen (equity)
    """
    if activa >= passiva:
        return activa - passiva
    else:
        return None

def solvabiliteit(eigen_vermogen, activa):
    if eigen_vermogen > 0 and activa > 0:
        solvabiliteit = eigen_vermogen / activa * 100
        return solvabiliteit
    else:
        return 0

def rentabiliteit(nettowinst, eigen_vermogen):
    """
    Calculate rentabiliteit (return on equity).

    :param nettowinst: Net profit (same unit as eigen_vermogen)
    :param eigen_vermogen: Equity (same unit as nettowinst)
    :return: Rentabiliteit (return on equity) in %
    """
    if nettowinst > 0 and eigen_vermogen > 0:
        return nettowinst / eigen_vermogen * 100
    else:
        return 0

def wpa(nettowinst, uitstaande_aandelen):
    """
    Calculate winst per aandeel (earnings per share).

    :param nettowinst: Net profit
    :param uitstaande_aandelen: Outstanding shares
    :return: Winst per aandeel (earnings per share)
    """
    if uitstaande_aandelen > 0:
        return nettowinst / uitstaande_aandelen
    else:
        return 0

def kw(actuele_beurskoers, wpa):
    """
    Calculate koers-winstverhouding (price-earnings ratio).

    :param actuele_beurskoers: Current stock price
    :param wpa: Winst per aandeel (earnings per share)
    :return: Koers-winstverhouding (price-earnings ratio)
    """
    if wpa > 0:
        return actuele_beurskoers / wpa
    else:
        return 0

def peg(kw, verwachte_winstgroei):
    """
    Calculate PEG ratio (price/earnings to growth ratio).

    :param kw: Koers-winstverhouding (P/E ratio)
    :param verwachte_winstgroei: Expected earnings growth rate in % (e.g. 12 for 12%)
    :return: PEG ratio
    """
    if verwachte_winstgroei > 0:
        return kw / verwachte_winstgroei
    else:
        return 0

def graham_number(wpa, boekwaarde_per_aandeel):
    """
    Calculate Graham number.

    :param eigen_vermogen: Eigen vermogen (equity)
    :param nettowinst: Nettowinst (net profit)
    :param uitstaande_aandelen: Uitstaande aandelen (outstanding shares)
    :return: Graham number
    """
    if boekwaarde_per_aandeel > 0 and wpa > 0:
        return np.sqrt(22.5 * wpa * boekwaarde_per_aandeel)
    else:
        return 0

# import yfinance as yf
# import pandas as pd

# def analyze_etf(ticker):
#     etf = yf.Ticker(ticker)
#     hist = etf.history(period="5y")

#     # Basic Performance
#     return_1y = (hist['Close'][-1] / hist['Close'][-252] - 1) * 100  # 252 trading days in a year
#     return_3y = (hist['Close'][-1] / hist['Close'][-252*3]) ** (1/3) - 1
#     return_5y = (hist['Close'][-1] / hist['Close'][0]) ** (1/5) - 1

#     # Volatility
#     std_dev = hist['Close'].pct_change().std() * (252 ** 0.5) * 100
#     max_drawdown = ((hist['Close'] / hist['Close'].cummax()) - 1).min() * 100

#     # Dividend
#     info = etf.info
#     dividend_yield = info.get('dividendYield', None)
#     expense_ratio = info.get('expenseRatio', None)
#     aum = info.get('totalAssets', None)

#     return {
#         "Ticker": ticker,
#         "1Y Return (%)": round(return_1y, 2),
#         "3Y Annualized Return (%)": round(return_3y * 100, 2),
#         "5Y Annualized Return (%)": round(return_5y * 100, 2),
#         "Std Dev (Volatility %)": round(std_dev, 2),
#         "Max Drawdown (%)": round(max_drawdown, 2),
#         "Dividend Yield (%)": round(dividend_yield * 100, 2) if dividend_yield else None,
#         "Expense Ratio (%)": round(expense_ratio * 100, 2) if expense_ratio else None,
#         "Assets Under Management ($)": round(aum / 1e9, 2) if aum else None,
#     }
