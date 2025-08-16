import numpy as np

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

def rentabiliteit(uitstaande_aandelen, totaal_vermogen):
    """
    Calculate rentabiliteit (return on equity).

    :param uitstaande_aandelen: Outstanding shares
    :param totaal_vermogen: Total equity
    :return: Rentabiliteit (return on equity)
    """
    if uitstaande_aandelen > 0 and totaal_vermogen > 0:
        return uitstaande_aandelen / totaal_vermogen * 100
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

def peg(kw, verwachte_winst):
    """
    Calculate PEG ratio (price/earnings to growth ratio).

    :param actuele_beurskoers: Current stock price
    :param wpa: Winst per aandeel (earnings per share)
    :param verwachte_winstgroei: Expected earnings growth rate
    :return: PEG ratio
    """
    if verwachte_winst > 0:
        return kw / verwachte_winst
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
