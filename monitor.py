import re
import unicodedata
import requests
from bs4 import BeautifulSoup


URL = "https://www.postesrpske.com/spisak-zemalja-medjunarodne-posiljke/"


# Postcrossing number by country/territory code.
# The code from the Pošta Srpske table is used as the primary match.
CODE_TO_NUMBER = {
    "AF": 1,
    "AX": 2,
    "AL": 3,
    "DZ": 4,
    "AS": 5,
    "AD": 6,
    "AO": 7,
    "AI": 8,
    "AQ": 9,
    "AG": 10,
    "AR": 11,
    "AM": 12,
    "AW": 13,
    "AU": 14,
    "AT": 15,
    "AZ": 16,
    "BS": 17,
    "BH": 18,
    "BD": 19,
    "BB": 20,
    "BY": 21,
    "BE": 22,
    "BZ": 23,
    "BJ": 24,
    "BM": 25,
    "BT": 26,
    "BO": 27,
    "BQ": 28,
    "BA": 29,
    "BW": 30,
    "BR": 31,
    "IO": 32,
    "BN": 33,
    "BG": 34,
    "BF": 35,
    "BI": 36,
    "CV": 37,
    "KH": 38,
    "CM": 39,
    "CA": 40,
    "KY": 41,
    "CF": 42,
    "TD": 43,
    "CL": 44,
    "CN": 45,
    "CX": 46,
    "CC": 47,
    "CO": 48,
    "KM": 49,
    "CG": 50,
    "CD": 51,
    "CK": 52,
    "CR": 53,
    "CI": 54,
    "HR": 55,
    "CU": 56,
    "CW": 57,
    "CY": 58,
    "CZ": 59,
    "DK": 60,
    "DJ": 61,
    "DM": 62,
    "DO": 63,
    "EC": 64,
    "EG": 65,
    "SV": 66,
    "GQ": 67,
    "ER": 68,
    "EE": 69,
    "SZ": 70,
    "ET": 71,
    "FK": 72,
    "FO": 73,
    "FJ": 74,
    "FI": 75,
    "FR": 76,
    "GF": 77,
    "PF": 78,
    "TF": 79,
    "GA": 80,
    "GM": 81,
    "GE": 82,
    "DE": 83,
    "GH": 84,
    "GI": 85,
    "GR": 86,
    "GL": 87,
    "GD": 88,
    "GP": 89,
    "GU": 90,
    "GT": 91,
    "GG": 92,
    "GN": 93,
    "GW": 94,
    "GY": 95,
    "HT": 96,
    "HN": 97,
    "HK": 98,
    "HU": 99,
    "IS": 100,
    "IN": 101,
    "ID": 102,
    "IR": 103,
    "IQ": 104,
    "IE": 105,
    "IM": 106,
    "IL": 107,
    "IT": 108,
    "JM": 109,
    "JP": 110,
    "JE": 111,
    "JO": 112,
    "KZ": 113,
    "KE": 114,
    "KI": 115,
    "KP": 116,
    "KR": 117,
    "XK": 118,
    "PS": 119,
    "KW": 120,
    "KG": 120,
    "LA": 121,
    "LV": 122,
    "LB": 123,
    "LS": 124,
    "LR": 125,
    "LY": 126,
    "LI": 127,
    "LT": 128,
    "LU": 129,
    "MO": 130,
    "MG": 131,
    "MW": 132,
    "MY": 133,
    "MV": 134,
    "ML": 135,
    "MT": 136,
    "MH": 137,
    "MQ": 138,
    "MR": 139,
    "MU": 140,
    "YT": 141,
    "MX": 142,
    "FM": 143,
    "MD": 144,
    "MC": 145,
    "MN": 146,
    "ME": 147,
    "MS": 148,
    "MA": 149,
    "MZ": 150,
    "MM": 151,
    "NA": 152,
    "NR": 153,
    "NP": 154,
    "NL": 155,
    "NC": 156,
    "NZ": 157,
    "NI": 158,
    "NE": 159,
    "NG": 160,
    "NU": 161,
    "NF": 162,
    "MP": 163,
    "MK": 164,
    "NO": 165,
    "OM": 166,
    "PK": 167,
    "PW": 168,
    "PA": 170,
    "PG": 171,
    "PY": 172,
    "PE": 173,
    "PH": 174,
    "PN": 175,
    "PL": 176,
    "PT": 177,
    "PR": 178,
    "QA": 179,
    "RE": 180,
    "RO": 181,
    "RU": 182,
    "RW": 183,
    "BL": 184,
    "SH": 185,
    "KN": 186,
    "LC": 187,
    "MF": 188,
    "PM": 189,
    "VC": 190,
    "WS": 191,
    "SM": 192,
    "ST": 193,
    "SA": 194,
    "SN": 195,
    "RS": 196,
    "SC": 197,
    "SL": 198,
    "SG": 199,
    "SX": 200,
    "SK": 201,
    "SI": 202,
    "SB": 203,
    "SO": 204,
    "ZA": 205,
    "GS": 206,
    "SS": 207,
    "ES": 208,
    "LK": 209,
    "SD": 210,
    "SR": 211,
    "SJ": 212,
    "SE": 213,
    "CH": 214,
    "SY": 215,
    "TW": 216,
    "TJ": 217,
    "TZ": 218,
    "TH": 219,
    "TL": 220,
    "TG": 221,
    "TK": 222,
    "TO": 223,
    "TT": 224,
    "TN": 225,
    "TR": 226,
    "TM": 227,
    "TC": 228,
    "TV": 229,
    "UG": 230,
    "UA": 231,
    "AE": 232,
    "GB": 233,
    "UY": 234,
    "US": 235,
    "UM": 236,
    "UZ": 237,
    "VU": 238,
    "VA": 239,
    "VE": 240,
    "VN": 241,
    "VG": 242,
    "VI": 243,
    "WF": 244,
    "EH": 245,
    "YE": 246,
    "ZM": 247,
    "ZW": 248,
}


def normalize_text(text):
    text = unicodedata.normalize("NFD", text)
    text = "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )
    text = text.lower()
    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_postcrossing_number(country_text):
    normalized = normalize_text(country_text)
    words = set(normalized.split())

    # Special rules requested by the user.
    if "salvador" in words:
        return 66

    if "man" in words:
        return 106

    if (
        "helena" in words
        and "ascension" in words
        and "tristan" in words
    ):
        return 185

    if "vincent" in words:
        return 190

    if "nevis" in words:
        return 186

    if "swaziland" in words:
        return 70

    # Primary matching: two-letter code in the country name.
    match = re.search(r"\(([A-Za-z]{2})\)", country_text)

    if match:
        code = match.group(1).upper()

        if code in CODE_TO_NUMBER:
            return CODE_TO_NUMBER[code]

    return None


def add_postcrossing_number(country_text):
    number = find_postcrossing_number(country_text)

    if number is None:
        return country_text

    return f"{number} - {country_text}"


def extract_country_text(cell):
    text = cell.get_text(" ", strip=True)

    text = text.replace("*", "")

    text = re.sub(r"\s+", " ", text).strip()

    return text


def parse_table(html):
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")

    if table is None:
        raise RuntimeError("Country table was not found.")

    all_countries = []
    suspended_countries = []

    rows = table.find_all("tr")

    for row in rows:
        cells = row.find_all(["td", "th"])

        if len(cells) < 2:
            continue

        country_cell = cells[1]

        # A real country/territory row contains a two-letter
        # country code in parentheses, e.g. (AF), (RS), (PG).
        country_text = extract_country_text(country_cell)

        code_match = re.search(
            r"\(([A-Za-z]{2})\)",
            country_text
        )

        if not code_match:
            # This filters out lines such as:
            # "Pismonosne, paketske"
            # "STOP"
            # table headers
            continue

        services_cell = cells[2] if len(cells) >= 3 else None

        if services_cell is not None:
            services_text = services_cell.get_text(
                " ",
                strip=True
            )
        else:
            services_text = ""

        normalized_services = normalize_text(
            services_text
        )

        all_countries.append(country_text)

        # Suspended when:
        # 1. Services are exactly STOP
        # OR
        # 2. Pismonosne is missing.
        is_stop = normalized_services == "stop"

        has_pismonosne = (
            "pismonosne" in normalized_services
        )

        if is_stop or not has_pismonosne:
            suspended_countries.append(country_text)

    return all_countries, suspended_countries


def build_output(
    all_countries,
    suspended_countries
):
    lines = []

    lines.append("SVE ZEMLJE")
    lines.append(
        f"UKUPNO: {len(all_countries)}"
    )
    lines.append("")

    for country in all_countries:
        lines.append(
            add_postcrossing_number(country)
        )

    lines.append("")
    lines.append("SUSPENDOVANE ZEMLJE")
    lines.append(
        f"UKUPNO: {len(suspended_countries)}"
    )
    lines.append("")

    for country in suspended_countries:
        lines.append(
            add_postcrossing_number(country)
        )

    lines.append("")

    return "\n".join(lines)


def main():
    response = requests.get(
        URL,
        timeout=30,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; srpskepost-monitor/1.0)"
            )
        },
    )

    response.raise_for_status()

    all_countries, suspended_countries = parse_table(
        response.text
    )

    # Safety check: never overwrite output.txt if
    # the website structure has unexpectedly changed.
    if len(all_countries) < 100:
        raise RuntimeError(
            f"Only {len(all_countries)} countries were found. "
            "Refusing to overwrite output.txt."
        )

    if len(suspended_countries) == 0:
        raise RuntimeError(
            "No suspended countries were found. "
            "Refusing to overwrite output.txt."
        )

    output = build_output(
        all_countries,
        suspended_countries
    )

    with open(
        "output.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(output)

    print(
        f"Successfully wrote "
        f"{len(all_countries)} countries and "
        f"{len(suspended_countries)} suspended countries "
        f"to output.txt"
    )


if __name__ == "__main__":
    main()
