#!/usr/bin/env python3

import re
import sys
import unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup


SOURCE_URL = "https://www.postesrpske.com/spisak-zemalja-medjunarodne-posiljke/"
OUTPUT_FILE = Path("output.txt")

EXPECTED_HEADER_PARTS = (
    "odredišna zemlja",
    "dozvoljene vrste pošiljaka",
)


# ---------------------------------------------------------------------------
# POSTCROSSING NUMBERS
# ---------------------------------------------------------------------------

POSTCROSSING = {
    1: "Afghanistan",
    2: "Åland Islands",
    3: "Albania",
    4: "Algeria",
    5: "American Samoa",
    6: "Andorra",
    7: "Angola",
    8: "Anguilla",
    9: "Antarctica",
    10: "Antigua & Barbuda",
    11: "Argentina",
    12: "Armenia",
    13: "Aruba",
    14: "Australia",
    15: "Austria",
    16: "Azerbaijan",
    17: "Bahamas",
    18: "Bahrain",
    19: "Bangladesh",
    20: "Barbados",
    21: "Belarus",
    22: "Belgium",
    23: "Belize",
    24: "Benin",
    25: "Bermuda",
    26: "Bhutan",
    27: "Bolivia",
    28: "Bonaire, Sint Eustatius and Saba",
    29: "Bosnia-Herzegovina",
    30: "Botswana",
    31: "Brazil",
    32: "British Indian Ocean Territory",
    33: "Brunei",
    34: "Bulgaria",
    35: "Burkina Faso",
    36: "Burundi",
    37: "Cabo Verde",
    38: "Cambodia",
    39: "Cameroon",
    40: "Canada",
    41: "Cayman Islands",
    42: "Central African Republic",
    43: "Chad",
    44: "Chile",
    45: "China",
    46: "Christmas Island",
    47: "Cocos Islands",
    48: "Colombia",
    49: "Comoros",
    50: "Congo",
    51: "Dem. Rep. Of Congo",
    52: "Cook Islands",
    53: "Costa Rica",
    54: "Côte d'Ivoire",
    55: "Croatia",
    56: "Cuba",
    57: "Curaçao",
    58: "Cyprus",
    59: "Czechia",
    60: "Denmark",
    61: "Djibouti",
    62: "Dominica",
    63: "Dominican Republic",
    64: "Ecuador",
    65: "Egypt",
    66: "El Salvador",
    67: "Equatorial Guinea",
    68: "Eritrea",
    69: "Estonia",
    70: "Eswatini /Swaziland",
    71: "Ethiopia",
    72: "Falkland Islands /Malvinas",
    73: "Faroe Islands",
    74: "Fiji",
    75: "Finland",
    76: "France",
    77: "French Guiana",
    78: "French Polynesia",
    79: "French Southern Territories",
    80: "Gabon",
    81: "Gambia",
    82: "Georgia",
    83: "Germany",
    84: "Ghana",
    85: "Gibraltar",
    86: "Greece",
    87: "Greenland",
    88: "Grenada",
    89: "Guadeloupe",
    90: "Guam",
    91: "Guatemala",
    92: "Guernsey",
    93: "Guinea",
    94: "Guinea-Bissau",
    95: "Guyana",
    96: "Haiti",
    97: "Honduras",
    98: "Hong Kong",
    99: "Hungary",
    100: "Iceland",
    101: "India",
    102: "Indonesia",
    103: "Iran",
    104: "Iraq",
    105: "Ireland",
    106: "Isle of Man",
    107: "Israel",
    108: "Italy",
    109: "Jamaica",
    110: "Japan",
    111: "Jersey",
    112: "Jordan",
    113: "Kazakhstan",
    114: "Kenya",
    115: "Kiribati",
    116: "Korea(North)",
    117: "Korea(South)",
    118: "Kosovo",
    119: "Kuwait",
    120: "Kyrgyzstan",
    121: "Laos",
    122: "Latvia",
    123: "Lebanon",
    124: "Lesotho",
    125: "Liberia",
    126: "Libya",
    127: "Liechtenstein",
    128: "Lithuania",
    129: "Luxembourg",
    130: "Macao",
    131: "Madagascar",
    132: "Malawi",
    133: "Malaysia",
    134: "Maldives",
    135: "Mali",
    136: "Malta",
    137: "Marshall Islands",
    138: "Martinique",
    139: "Mauritania",
    140: "Mauritius",
    141: "Mayotte",
    142: "Mexico",
    143: "Micronesia",
    144: "Moldova",
    145: "Monaco",
    146: "Mongolia",
    147: "Montenegro",
    148: "Montserrat",
    149: "Morocco",
    150: "Mozambique",
    151: "Myanmar",
    152: "Namibia",
    153: "Nauru / Naoero",
    154: "Nepal",
    155: "Netherlands",
    156: "New Caledonia",
    157: "New Zealand",
    158: "Nicaragua",
    159: "Niger",
    160: "Nigeria",
    161: "Niue",
    162: "Norfolk Island",
    163: "Northern Mariana Islands",
    164: "North Macedonia",
    165: "Norway",
    166: "Oman",
    167: "Pakistan",
    168: "Palau",
    169: "Palestine",
    170: "Panama",
    171: "Papua New Guinea",
    172: "Paraguay",
    173: "Peru",
    174: "Philippines",
    175: "Pitcairn",
    176: "Poland",
    177: "Portugal",
    178: "Puerto Rico",
    179: "Qatar",
    180: "Réunion",
    181: "Romania",
    182: "Russia",
    183: "Rwanda",
    184: "Saint Barthélemy",
    185: "Saint Helena, Ascension and Tristan da Cunha",
    186: "Saint Kitts and Nevis",
    187: "Saint Lucia",
    188: "Saint Martin",
    189: "Saint Pierre & Miquelon",
    190: "Saint Vincent and the Grenadines",
    191: "Samoa",
    192: "San Marino",
    193: "Sao Tome and Principe",
    194: "Saudi Arabia",
    195: "Senegal",
    196: "Serbia",
    197: "Seychelles",
    198: "Sierra Leone",
    199: "Singapore",
    200: "Sint Maarten",
    201: "Slovakia",
    202: "Slovenia",
    203: "Solomon Islands",
    204: "Somalia",
    205: "South Africa",
    206: "South Georgia and S. Sandwich Islands",
    207: "South Sudan",
    208: "Spain",
    209: "Sri Lanka",
    210: "Sudan",
    211: "Suriname",
    212: "Svalbard and Jan Mayen",
    213: "Sweden",
    214: "Switzerland",
    215: "Syria",
    216: "Taiwan",
    217: "Tajikistan",
    218: "Tanzania",
    219: "Thailand",
    220: "Timor-Leste",
    221: "Togo",
    222: "Tokelau",
    223: "Tonga",
    224: "Trinidad and Tobago",
    225: "Tunisia",
    226: "Turkey",
    227: "Turkmenistan",
    228: "Turks and Caicos Islands",
    229: "Tuvalu",
    230: "Uganda",
    231: "Ukraine",
    232: "United Arab Emirates",
    233: "United Kingdom",
    234: "Uruguay",
    235: "U.S.A.",
    236: "U.S. Minor Outlying Islands",
    237: "Uzbekistan",
    238: "Vanuatu",
    239: "Vatican",
    240: "Venezuela",
    241: "Vietnam",
    242: "Virgin Islands (UK)",
    243: "Virgin Islands of the USA",
    244: "Wallis & Futuna",
    245: "Western Sahara",
    246: "Yemen",
    247: "Zambia",
    248: "Zimbabwe",
}


# ---------------------------------------------------------------------------
# MATCHING
# ---------------------------------------------------------------------------

# Direct aliases for Serbian/Pošta Srpske names that differ from the
# Postcrossing English names.
ALIASES = {
    "avganistan": 1,
    "americka samoa": 5,
    "andora": 6,
    "angola": 7,
    "angvila": 8,
    "antarktik": 9,
    "antigva i barbuda": 10,
    "argentina": 11,
    "jermenija": 12,
    "aruba": 13,
    "australija": 14,
    "austrija": 15,
    "azerbejdzan": 16,
    "bahami": 17,
    "bahrein": 18,
    "banglades": 19,
    "barbados": 20,
    "belorusija": 21,
    "bjelorusija": 21,
    "belgija": 22,
    "belize": 23,
    "benin": 24,
    "bermudi": 25,
    "butan": 26,
    "bolivija": 27,
    "bonaire": 28,
    "sint eustatius": 28,
    "saba": 28,
    "bosna i hercegovina": 29,
    "bosna hercegovina": 29,
    "bocvana": 30,
    "brazil": 31,
    "britanska teritorija u indijskom okeanu": 32,
    "brunej": 33,
    "bugarska": 34,
    "burkina faso": 35,
    "burundi": 36,
    "zelenortska ostrva": 37,
    "zelenortska": 37,
    "kambodza": 38,
    "kamerun": 39,
    "kanada": 40,
    "kajmanska ostrva": 41,
    "centralnoafricka republika": 42,
    "cad": 43,
    "cile": 44,
    "kina": 45,
    "bozicno ostrvo": 46,
    "kokosova ostrva": 47,
    "kolumbija": 48,
    "komori": 49,
    "kongo": 50,
    "demokratska republika kongo": 51,
    "demokratska republika konga": 51,
    "kukova ostrva": 52,
    "kostarika": 53,
    "kostarika": 53,
    "obala slonovace": 54,
    "hrvatska": 55,
    "kuba": 56,
    "kurasao": 57,
    "kipar": 58,
    "ceska": 59,
    "ceska republika": 59,
    "danska": 60,
    "danska kraljevina": 60,
    "dzibuti": 61,
    "dominika": 62,
    "dominikanska republika": 63,
    "ekvador": 64,
    "egipat": 65,
    "el salvador": 66,
    "ekvatorijalna gvineja": 67,
    "eritreja": 68,
    "estonija": 69,
    "esvatini": 70,
    "svazilend": 70,
    "etiopija": 71,
    "foklandska ostrva": 72,
    "farska ostrva": 73,
    "fidzi": 74,
    "finska": 75,
    "finska": 75,
    "francuska": 76,
    "francuska gvajana": 77,
    "francuska polinezija": 78,
    "francuske juzne i antarkticke zemlje": 79,
    "gabon": 80,
    "gambija": 81,
    "gruzija": 82,
    "njemacka": 83,
    "nemacka": 83,
    "njemačka": 83,
    "ghana": 84,
    "gana": 84,
    "gibraltar": 85,
    "grcka": 86,
    "grenland": 87,
    "grenada": 88,
    "gvadelup": 89,
    "gvadelupa": 89,
    "guam": 90,
    "gvatemala": 91,
    "gernzi": 92,
    "gijana": 95,
    "gvajana": 95,
    "gvineja": 93,
    "gvineja bisao": 94,
    "gvineja-bisao": 94,
    "gvineja bisau": 94,
    "haiti": 96,
    "honduras": 97,
    "hong kong": 98,
    "madjarska": 99,
    "mađarska": 99,
    "island": 100,
    "indija": 101,
    "indonezija": 102,
    "iran": 103,
    "irak": 104,
    "irska": 105,
    "irska": 105,
    "ostrvo man": 106,
    "ostrvo men": 106,
    "isle of man": 106,
    "izrael": 107,
    "italija": 108,
    "jamajka": 109,
    "japan": 110,
    "dzerzi": 111,
    "jerzi": 111,
    "jord an": 112,
    "jordan": 112,
    "kazahstan": 113,
    "kenija": 114,
    "kiribati": 115,
    "sjeverna koreja": 116,
    "sjeverna koreja": 116,
    "koreja sjeverna": 116,
    "koreja republika": 117,
    "juzna koreja": 117,
    "kosovo": 118,
    "kuvajt": 119,
    "kirgistan": 120,
    "kirgizija": 120,
    "laos": 121,
    "letonija": 122,
    "letonija": 122,
    "liban": 123,
    "lesoto": 124,
    "liberija": 125,
    "libija": 126,
    "lihtenstajn": 127,
    "lihtenštajn": 127,
    "litvanija": 128,
    "luksemburg": 129,
    "makao": 130,
    "madagaskar": 131,
    "malavi": 132,
    "malezija": 133,
    "maldivi": 134,
    "mali": 135,
    "malta": 136,
    "maršalska ostrva": 137,
    "marsalska ostrva": 137,
    "martinik": 138,
    "mauritanija": 139,
    "mauricijus": 140,
    "mauricij": 140,
    "majot": 141,
    "meksiko": 142,
    "mikronezija": 143,
    "moldavija": 144,
    "monako": 145,
    "mongolija": 146,
    "crna gora": 147,
    "montserat": 148,
    "maroko": 149,
    "mozambik": 150,
    "mjanmar": 151,
    "mjanmar": 151,
    "namibija": 152,
    "nauru": 153,
    "nepal": 154,
    "holandija": 155,
    "nizozemska": 155,
    "nova kaledonija": 156,
    "novi zeland": 157,
    "nikaragva": 158,
    "niger": 159,
    "nigerija": 160,
    "niu": 161,
    "norfolk ostrvo": 162,
    "norfolk ostrva": 162,
    "sjeverna marijanska ostrva": 163,
    "sjeverna makedonija": 164,
    "norveska": 165,
    "norveška": 165,
    "oman": 166,
    "pakistan": 167,
    "palau": 168,
    "palestina": 169,
    "panama": 170,
    "papua nova gvineja": 171,
    "paragvaj": 172,
    "peru": 173,
    "filipini": 174,
    "pitkern": 175,
    "poljska": 176,
    "portugal": 177,
    "portoriko": 178,
    "katar": 179,
    "reunion": 180,
    "reunion": 180,
    "rumunija": 181,
    "rusija": 182,
    "ruanda": 183,
    "sveti bartolomej": 184,
    "sveta jelena": 185,
    "sveta jelena askension i tristan da kunja": 185,
    "sveti kristofer i nevis": 186,
    "sveti kits i nevis": 186,
    "sveta lucija": 187,
    "sveti martin": 188,
    "sveti petar i mikelon": 189,
    "sveti vincent i grenadini": 190,
    "samoa": 191,
    "san marino": 192,
    "sao tome i principe": 193,
    "saudijska arabija": 194,
    "senegal": 195,
    "srbija": 196,
    "sejseli": 197,
    "sijera leone": 198,
    "singapur": 199,
    "sint marten": 200,
    "slovacka": 201,
    "slovačka": 201,
    "slovenija": 202,
    "solomonska ostrva": 203,
    "solomonova ostrva": 203,
    "somalija": 204,
    "juzna afrika": 205,
    "južna afrika": 205,
    "juzna dzordzija i juzna sendvicka ostrva": 206,
    "juzna dzordzija i juzna sendvicka ostrva": 206,
    "juzni sudan": 207,
    "spanija": 208,
    "španija": 208,
    "sri lanka": 209,
    "sudan": 210,
    "surinam": 211,
    "svalbard i jan majen": 212,
    "svalbard i jan mayen": 212,
    "svedska": 213,
    "švedska": 213,
    "svajcarska": 214,
    "švajcarska": 214,
    "sirija": 215,
    "tajvan": 216,
    "tadzikistan": 217,
    "tanzanija": 218,
    "tajland": 219,
    "istocni timor": 220,
    "istočni timor": 220,
    "timor leste": 220,
    "togo": 221,
    "tokelau": 222,
    "tonga": 223,
    "trinidad i tobago": 224,
    "tunis": 225,
    "tunisija": 225,
    "turska": 226,
    "turkmenistan": 227,
    "ostrva turks i caicos": 228,
    "turks i kaikos": 228,
    "tuvalu": 229,
    "uganda": 230,
    "ukrajina": 231,
    "ujedinjeni arapski emirati": 232,
    "ujedinjeno kraljevstvo": 233,
    "velika britanija": 233,
    "urugvaj": 234,
    "sad": 235,
    "usa": 235,
    "sjedinjene americke drzave": 235,
    "sjedinjene američke države": 235,
    "mala udaljena ostrva sad": 236,
    "mala udaljena ostrva sjedinjenih americkih drzava": 236,
    "uzbekistan": 237,
    "vanuatu": 238,
    "vatikan": 239,
    "venecuela": 240,
    "vijetnam": 241,
    "britanska djevičanska ostrva": 242,
    "britanska djevicanska ostrva": 242,
    "djevičanska ostrva sad": 243,
    "djevicanska ostrva sad": 243,
    "americka djevičanska ostrva": 243,
    "americka djevicanska ostrva": 243,
    "valis i futuna": 244,
    "valis i futuna": 244,
    "zapadna sahara": 245,
    "jemen": 246,
    "zambija": 247,
    "zimbabve": 248,
}


def normalize_text(text):
    """
    Normalize text for matching.

    Removes accents/diacritics, converts to lowercase,
    standardizes punctuation, and collapses whitespace.
    """

    text = text.replace("Đ", "D").replace("đ", "d")

    text = unicodedata.normalize("NFKD", text)

    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    text = text.casefold()

    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = text.replace("(", " ")
    text = text.replace(")", " ")
    text = text.replace(".", " ")
    text = text.replace(",", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def build_postcrossing_lookup():
    """
    Build a normalized English-name lookup.
    """

    lookup = {}

    for number, name in POSTCROSSING.items():
        lookup[normalize_text(name)] = number

    return lookup


POSTCROSSING_LOOKUP = build_postcrossing_lookup()


def find_postcrossing_number(country_text):
    """
    Find the Postcrossing number for a Pošta Srpske country entry.

    Matching is performed using:
      1. Explicit Serbian aliases.
      2. English name if the website uses an English-style name.
      3. The country code as a final safety mechanism for entries
         whose names are difficult to match.
    """

    text = normalize_text(country_text)

    # Remove the two-letter postal code from the middle of the name.
    text_without_code = re.sub(
        r"\b[a-z]{2}\b",
        " ",
        text,
    )

    text_without_code = re.sub(
        r"\s+",
        " ",
        text_without_code,
    ).strip()

    # Try the full normalized country text.
    if text in POSTCROSSING_LOOKUP:
        return POSTCROSSING_LOOKUP[text]

    # Try the name without the country code.
    if text_without_code in POSTCROSSING_LOOKUP:
        return POSTCROSSING_LOOKUP[text_without_code]

    # Try Serbian aliases.
    if text_without_code in ALIASES:
        return ALIASES[text_without_code]

    # Sometimes the country cell contains the Serbian name followed
    # by the English name. Check each useful portion separately.
    words = text_without_code.split()

    # Look for known aliases inside the text.
    for alias, number in sorted(
        ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if alias in text_without_code:
            return number

    # Last attempt: compare against English Postcrossing names
    # using containment.
    for normalized_name, number in POSTCROSSING_LOOKUP.items():
        if normalized_name in text_without_code:
            return number

    return None


def add_postcrossing_number(country_text):
    """
    Prefix the country text with its Postcrossing number.

    If no confident match exists, return the country text unchanged.
    """

    number = find_postcrossing_number(country_text)

    if number is None:
        return country_text

    return f"{number} - {country_text}"


# ---------------------------------------------------------------------------
# WEBSITE PARSING
# ---------------------------------------------------------------------------

def normalize_space(text):
    """Collapse all whitespace into single spaces."""
    return re.sub(r"\s+", " ", text).strip()


def normalize_for_comparison(text):
    """Normalize text for case-insensitive comparisons."""
    return normalize_space(text).casefold()


def extract_country_text(country_cell):
    """
    Keep the complete visible country-column text.

    Example:

        Avganistan (AF) AFGANISTAN

    The change marker '*' is removed.
    """

    text = normalize_space(country_cell)

    text = text.replace("*", "")

    return normalize_space(text)


def find_target_table(soup):
    """
    Find the table containing the two columns we need.
    """

    for table in soup.find_all("table"):
        headers = []

        for th in table.find_all("th"):
            headers.append(
                normalize_for_comparison(
                    th.get_text(" ", strip=True)
                )
            )

        if not headers:
            first_row = table.find("tr")

            if first_row:
                headers = [
                    normalize_for_comparison(
                        cell.get_text(" ", strip=True)
                    )
                    for cell in first_row.find_all(
                        ["td", "th"]
                    )
                ]

        header_text = " ".join(headers)

        if all(
            part in header_text
            for part in EXPECTED_HEADER_PARTS
        ):
            return table

    return None


def parse_table(table):
    """
    Extract:

      1. All country/territory names exactly as displayed.
      2. Suspended country/territory names.

    A country is suspended when:
      - the allowed-services column is STOP, OR
      - "Pismonosne" is missing from the allowed-services column.
    """

    all_countries = []
    suspended_countries = []

    rows = table.find_all("tr")

    for row in rows:
        cells = row.find_all(["td", "th"])

        if not cells:
            continue

        cell_texts = [
            normalize_space(
                cell.get_text(" ", strip=True)
            )
            for cell in cells
        ]

        combined = normalize_for_comparison(
            " ".join(cell_texts)
        )

        if (
            "odredišna zemlja" in combined
            or "dozvoljene vrste pošiljaka" in combined
        ):
            continue

        if len(cell_texts) >= 3:
            country_cell = cell_texts[-2]
            services_cell = cell_texts[-1]

        elif len(cell_texts) == 2:
            country_cell = cell_texts[0]
            services_cell = cell_texts[1]

        else:
            continue

        country_text = extract_country_text(
            country_cell
        )

        if not country_text:
            continue

        if not re.search(
            r"\([A-Z]{2}\)",
            country_text,
        ):
            continue

        all_countries.append(country_text)

        services_normalized = normalize_for_comparison(
            services_cell
        )

        is_stop = services_normalized == "stop"

        has_pismonosne = (
            "pismonosne" in services_normalized
        )

        if is_stop or not has_pismonosne:
            suspended_countries.append(country_text)

    return all_countries, suspended_countries


# ---------------------------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------------------------

def build_output(
    all_countries,
    suspended_countries,
):
    """
    Build the output file.

    Postcrossing numbers are added to every country/territory
    where a match exists.
    """

    lines = []

    lines.append(
        "POŠTA SRPSKE - MEĐUNARODNE POŠILJKE"
    )
    lines.append("")

    lines.append("SVE ZEMLJE")
    lines.append(
        f"Ukupno: {len(all_countries)}"
    )
    lines.append("")

    for country in all_countries:
        lines.append(
            add_postcrossing_number(country)
        )

    lines.append("")

    lines.append("SUSPENDOVANE ZEMLJE")
    lines.append(
        f"Ukupno: {len(suspended_countries)}"
    )
    lines.append("")

    for country in suspended_countries:
        lines.append(
            add_postcrossing_number(country)
        )

    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print(
        f"Downloading: {SOURCE_URL}"
    )

    try:
        response = requests.get(
            SOURCE_URL,
            timeout=60,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(compatible; srpskepost-monitor/1.0; "
                    "+https://github.com/)"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "*/*;q=0.8"
                ),
                "Accept-Language": (
                    "sr,en;q=0.8"
                ),
            },
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        print(
            f"ERROR: Could not download the website: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        f"Downloaded {len(response.content):,} bytes"
    )

    soup = BeautifulSoup(
        response.content,
        "html.parser",
    )

    table = find_target_table(soup)

    if table is None:
        print(
            "ERROR: Could not find the expected "
            "Pošta Srpske table.",
            file=sys.stderr,
        )
        sys.exit(1)

    all_countries, suspended_countries = (
        parse_table(table)
    )

    print(
        f"Countries found: "
        f"{len(all_countries)}"
    )

    print(
        f"Suspended countries found: "
        f"{len(suspended_countries)}"
    )

    # Report unmatched countries without failing the run.
    unmatched = []

    for country in all_countries:
        if find_postcrossing_number(country) is None:
            unmatched.append(country)

    if unmatched:
        print(
            "Countries without a Postcrossing match:"
        )

        for country in unmatched:
            print(f"  - {country}")

    else:
        print(
            "All countries matched to a "
            "Postcrossing number."
        )

    # Safety check.
    if len(all_countries) < 100:
        print(
            "ERROR: Fewer than 100 countries were found. "
            "The website structure may have changed. "
            "Existing output.txt will NOT be overwritten.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not suspended_countries:
        print(
            "ERROR: No suspended countries were found. "
            "This is probably a parsing problem, so "
            "output.txt will NOT be overwritten.",
            file=sys.stderr,
        )
        sys.exit(1)

    output = build_output(
        all_countries,
        suspended_countries,
    )

    OUTPUT_FILE.write_text(
        output,
        encoding="utf-8",
    )

    print(
        f"Wrote {OUTPUT_FILE}"
    )

    print(
        "Update completed successfully."
    )


if __name__ == "__main__":
    main()
