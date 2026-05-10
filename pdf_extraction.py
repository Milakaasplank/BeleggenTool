"""KIID/EID PDF extractor voor ETF-fundamentele gegevens.

Werkt op gestandaardiseerde PRIIP-documenten in NL en ENG. Extraheert structuur-
en kostenvelden (ISIN, naam, domicilie, replicatie, distributie, TER, UCITS, type, regio).
Performance, AUM en holdings staan niet in een KIID — die blijven handmatig.
"""
import re
from io import BytesIO


def _read_pdf_text(file):
    """Lees alle tekst uit een PDF (Streamlit UploadedFile of pad)."""
    try:
        import pdfplumber
    except ImportError as e:
        raise ImportError(
            "pdfplumber niet geïnstalleerd. Run: pip install pdfplumber"
        ) from e

    if hasattr(file, "read"):
        data = file.read()
        if hasattr(file, "seek"):
            file.seek(0)
        bio = BytesIO(data)
    else:
        bio = file

    text_parts = []
    with pdfplumber.open(bio) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            text_parts.append(t)
    return "\n".join(text_parts)


ISIN_DOMICILIE = {
    "IE": "Ierland (IE)",
    "LU": "Luxemburg (LU)",
    "NL": "Nederland (NL)",
    "DE": "Duitsland (DE)",
    "US": "Verenigde Staten (US)",
}


def _extract_isin(text):
    m = re.search(r"\bISIN[:\s]+([A-Z]{2}[0-9A-Z]{10})\b", text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    m = re.search(r"\b([A-Z]{2}[0-9A-Z]{10})\b", text)
    return m.group(1) if m else None


def _extract_naam(text):
    patterns = [
        # VanEck-stijl: expliciet label
        r"Naam van het Product[:\s]+(.+?)(?=\(het|\n|ISIN)",
        r"Naam van het beleggingsproduct[:\s]+(.+?)(?=\(het|\n|ISIN)",
        r"Product Name[:\s]+(.+?)(?=\(the|\n|ISIN)",
        r"Name of the (?:UCITS|product|fund)[:\s]+(.+?)(?=\(the|\n|ISIN)",
        # iShares-stijl: naam vlak voor "(het 'Fonds')" of "(the 'Fund')"
        r"^([^\n]+?)\s*\(het ['‘’]Fonds['‘’]\)",
        r"^([^\n]+?)\s*\(the ['‘’]Fund['‘’]\)",
        # Fallback: eerste regel met "UCITS ETF" in de naam
        r"^([A-Z][\w\s&\.\-\d]{5,}UCITS\s+ETF[^\n]*?)(?=\s*\(|,|\n|$)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if m:
            naam = m.group(1).strip().replace("\n", " ")
            naam = re.sub(r"\s+", " ", naam)
            # Filter out zwakke matches
            if naam.lower().startswith("product") and len(naam) < 15:
                continue
            if len(naam) < 6:
                continue
            return naam
    return None


def _extract_domicilie(text, isin=None):
    nl_patterns = [
        r"geregistreerd in (\w+)",
        r"goedgekeurd in (\w+)",
        r"opgericht in (\w+)",
        r"gevestigd in (\w+)",
    ]
    for p in nl_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            land = m.group(1).lower()
            if "ierland" in land:
                return "Ierland (IE)"
            if "luxemburg" in land:
                return "Luxemburg (LU)"
            if "nederland" in land:
                return "Nederland (NL)"
            if "duitsland" in land:
                return "Duitsland (DE)"
    en_patterns = [
        r"domicil(?:ed|e) in (\w+)",
        r"registered in (\w+)",
        r"incorporated in (\w+)",
        r"approved in (\w+)",
    ]
    for p in en_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            land = m.group(1).lower()
            if "ireland" in land:
                return "Ierland (IE)"
            if "luxembourg" in land:
                return "Luxemburg (LU)"
            if "netherlands" in land:
                return "Nederland (NL)"
    if isin:
        return ISIN_DOMICILIE.get(isin[:2].upper(), "Anders")
    return None


def _extract_uitkering(text):
    # 1. Expliciet label
    label_patterns = [
        r"Uitkeringsbeleid[:\s]+([^\n]+)",
        r"Distribution Policy[:\s]+([^\n]+)",
        r"Income Treatment[:\s]+([^\n]+)",
    ]
    val = ""
    for p in label_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            break
    val_lower = val.lower()
    if any(k in val_lower for k in ["herbelegd", "accumul", "kapitalis", "reinvest"]):
        return "Accumulerend"
    if any(k in val_lower for k in ["uitgekeerd", "distribu", "uitkering"]):
        return "Distribuerend"

    # 2. Suffix in productnaam: (Dist), (Distr), (Acc)
    if re.search(r"\((?:Dist|Distr|Distributing|D)\)", text):
        return "Distribuerend"
    if re.search(r"\((?:Acc|Accumulating|A)\)", text):
        return "Accumulerend"

    # 3. Generieke tekstpatronen
    text_lower = text.lower()
    if any(k in text_lower for k in [
        "dividendaandelen", "per kwartaal uitgekeerd", "per jaar uitgekeerd",
        "income is paid", "dividends are distributed",
    ]):
        return "Distribuerend"
    if any(k in text_lower for k in [
        "opbrengsten herbelegd", "income reinvested", "income is reinvested",
    ]):
        return "Accumulerend"

    return None


def _extract_replicatie(text):
    text_lower = text.lower()
    if any(k in text_lower for k in ["synthet", "total return swap", "swap-based"]):
        return "Synthetisch (swap)"
    if any(k in text_lower for k in [
        "geoptimaliseerde replicatie", "sampling", "optimised replication",
        "optimized replication", "representative sampling",
    ]):
        return "Fysiek sampling"
    if any(k in text_lower for k in [
        # VanEck-stijl
        "direct in de onderliggende", "directly in the underlying",
        "fysieke replicatie", "physical replication", "full replication",
        "volledige replicatie",
        # iShares-stijl
        "in vergelijkbare verhoudingen aan te houden",
        "fonds wil de index repliceren", "fund seeks to replicate",
        "te beleggen in de effecten met een aandelenkarakter",
        # Vanguard-stijl
        "fund holds the securities", "fund invests in the securities",
        "physically replicates",
    ]):
        return "Fysiek volledig"
    return None


def _extract_ter(text):
    # Volgorde: eerst totale kosten (PRIIP-verplicht label), daarna fallbacks
    patterns = [
        # Totale jaarlijkse kosten — meest accurate
        r"Effect van de kosten per jaar[^\d%]*([\d,\.]+)\s*%",
        r"Impact van de jaarlijkse kosten[^\d%]*([\d,\.]+)\s*%",
        r"Impact of (?:the )?annual cost[^\d%]*([\d,\.]+)\s*%",
        # Lopende kosten / TER
        r"Lopende kosten[^\d%]*([\d,\.]+)\s*%",
        r"Total Expense Ratio[^\d%]*([\d,\.]+)\s*%",
        r"Ongoing charges?[^\d%]*([\d,\.]+)\s*%",
        r"Ongoing costs?[^\d%]*([\d,\.]+)\s*%",
        # Fallback: alleen beheerkosten (kan onderschatting zijn)
        r"Beheerskoste?n(?:\s+en\s+andere)?[^\d%]*([\d,\.]+)\s*%",
        r"Beheerkoste?n(?:\s+en\s+andere)?[^\d%]*([\d,\.]+)\s*%",
        r"Management fee[^\d%]*([\d,\.]+)\s*%",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE | re.DOTALL)
        if m:
            v = m.group(1).replace(",", ".")
            try:
                return float(v)
            except ValueError:
                continue
    return None


def _extract_ucits(text):
    return bool(re.search(r"\bUCITS\b", text))


def _extract_type(text):
    text_lower = text.lower()
    if any(k in text_lower for k in ["obligatie", "bond", "fixed income"]):
        return "Obligaties"
    if any(k in text_lower for k in ["vastgoed", "real estate", "reit"]):
        return "Vastgoed"
    if any(k in text_lower for k in ["grondstof", "commodity", "commodities", "metals"]):
        return "Grondstoffen"
    if any(k in text_lower for k in ["aandelen", "equity", "equities", "stocks"]):
        return "Aandelen"
    return None


def _extract_regio(text):
    text_lower = text.lower()
    if any(k in text_lower for k in [
        "opkomende markt", "emerging market", "msci em", "emerging markets",
    ]):
        return "Opkomende Markten"
    if any(k in text_lower for k in [
        "wereldwijd", "msci world", "ftse all-world", "global",
    ]):
        return "Wereldwijd"
    if any(k in text_lower for k in [
        "verenigde staten", "s&p 500", "russell 3000", "u.s. market", "nasdaq",
    ]):
        return "Verenigde Staten"
    if any(k in text_lower for k in ["stoxx europe", "msci europe", "europa"]):
        return "Europa"
    if any(k in text_lower for k in ["azië", "asia pacific", "msci asia"]):
        return "Azië"
    if "nederland" in text_lower and "geregistreerd" not in text_lower[:200]:
        return "Nederland"
    return None


def parse_kiid(file):
    """Extract velden uit een KIID/EID PDF.

    Returns:
        (extracted: dict, full_text: str) — extracted bevat alleen velden waarvan
        de extractie is gelukt, met session_state-keys als sleutel.
    """
    text = _read_pdf_text(file)

    isin = _extract_isin(text)
    naam = _extract_naam(text)
    domicilie = _extract_domicilie(text, isin)
    distributie = _extract_uitkering(text)
    replicatie = _extract_replicatie(text)
    ter = _extract_ter(text)
    type_fonds = _extract_type(text)
    regio = _extract_regio(text)
    ucits = _extract_ucits(text)

    out = {}
    if naam:
        out["etf_naam"] = naam
    if isin:
        out["etf_isin"] = isin
    if domicilie:
        out["etf_domicilie"] = domicilie
    if distributie:
        out["etf_distributie"] = distributie
    if replicatie:
        out["etf_replicatie"] = replicatie
    if ter is not None:
        out["etf_ter"] = ter
    if ucits:
        out["etf_ucits"] = True
    if type_fonds:
        out["etf_type"] = type_fonds
    if regio:
        out["etf_regio"] = regio

    return out, text
