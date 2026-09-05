import re
import unicodedata
import requests
from bs4 import BeautifulSoup


URL = "https://www.postesrpske.com/spisak-zemalja-medjunarodne-posiljke/"


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


ALIASES = {
    "avganistan": 1,
    "aland": 2,
    "alandska ostrva": 2,
    "bosna i hercegovina": 29,
    "bonaire": 28,
    "sint eustatius": 28,
    "saba": 28,
    "cape verde": 37,
    "kabo verde": 37,
    "demokratska republika kongo": 51,
    "dem rep kongo": 51,
    "dem rep of congo": 51,
    "kostarika": 53,
    "obala slonovace": 54,
    "bjelorusija": 21,
    "ceska": 59,
    "ceska republika": 59,
    "esvatini": 70,
    "svazilend": 70,
    "swaziland": 70,
    "falklandska ostrva": 72,
    "malvini": 72,
    "francuska gvajana": 77,
    "francuska polinezija": 78,
    "francuske juzne teritorije": 79,
    "gambija": 81,
    "gruzija": 82,
    "njemacka": 83,
    "gibraltar": 85,
    "grenada": 88,
    "gvadelup": 89,
    "gurnzi": 92,
    "gvineja bisao": 94,
    "gvineja": 93,
    "gvajana": 95,
    "hong kong": 98,
    "island": 100,
    "indija": 101,
    "indonezija": 102,
    "irak": 104,
    "iran": 103,
    "irska": 105,
    "ostrvo man": 106,
    "ostrvo covjeka": 106,
    "ostrvo coveka": 106,
    "izrael": 107,
    "italija": 108,
    "jamajka": 109,
    "japan": 110,
    "dzersi": 111,
    "kazahstan": 113,
    "kenija": 114,
    "koreja sjever": 116,
    "sjeverna koreja": 116,
    "koreja jug": 117,
    "juzna koreja": 117,
    "kosovo": 118,
    "kirgistan": 120,
    "kirgistan": 120,
    "letonija": 122,
    "latvija": 122,
    "liban": 123,
    "lesoto": 124,
    "liberija": 125,
    "libija": 126,
    "lihtenstajn": 127,
    "litvanija": 128,
    "luksemburg": 129,
    "makao": 130,
    "mjanmar": 151,
    "mjanma": 151,
    "namibija": 152,
    "nauru": 153,
    "naoero": 153,
    "novi zeland": 157,
    "nikaragva": 158,
    "niger": 159,
    "nigerija": 160,
    "sjeverna makedonija": 164,
    "oman": 166,
    "pakistan": 167,
    "palestina": 169,
    "papua nova gvineja": 171,
    "paragvaj": 172,
    "peru": 173,
    "filipini": 174,
    "poljska": 176,
    "portoriko": 178,
    "reunion": 180,
    "rumunija": 181,
    "rusija": 182,
    "ruanda": 183,
    "sveta helena": 185,
    "sveti kristofor i nevis": 186,
    "sveti kristofor": 186,
    "sveta lucija": 187,
    "sveti martin": 188,
    "sveti petar i mikelon": 189,
    "sveti vinko i grenadini": 190,
    "samoa": 191,
    "san marino": 192,
    "sao tome": 193,
    "saomi": 193,
    "saudijska arabija": 194,
    "senegal": 195,
    "srbija": 196,
    "sejseli": 197,
    "sijera leone": 198,
    "singapur": 199,
    "sint marten": 200,
    "slovacka": 201,
    "slovenija": 202,
    "solomonska ostrva": 203,
    "somalija": 204,
    "juzna afrika": 205,
    "juzna dzordzija": 206,
    "juzni sendvic": 206,
    "juzni sudan": 207,
    "spanija": 208,
    "sri lanka": 209,
    "sudan": 210,
    "surinam": 211,
    "spicbergen": 212,
    "svalbard": 212,
    "jan mayen": 212,
    "svedska": 213,
    "svajcarska": 214,
    "sirija": 215,
    "tajvan": 216,
    "tadzikistan": 217,
    "tanzanija": 218,
    "tajland": 219,
    "istocni timor": 220,
    "timor leste": 220,
    "togo": 221,
    "tokelau": 222,
    "tonga": 223,
    "trinidad i tobago": 224,
    "tunis": 225,
    "tunisija": 225,
    "turska": 226,
    "turkmenistan": 227,
    "turks i kaikos": 228,
    "tuvalu": 229,
    "uganda": 230,
    "ukrajina": 231,
    "ujedinjeni arapski emirati": 232,
    "velika britanija": 233,
    "urugvaj": 234,
    "sad": 235,
    "sjedinjene americke drzave": 235,
    "mala udaljena ostrva sad": 236,
    "uzbekistan": 237,
    "vanuatu": 238,
    "vatikan": 239,
    "venecuela": 240,
    "vijetnam": 241,
    "djevičanska ostrva britanska": 242,
    "djevičanska ostrva sad": 243,
    "valis i futuna": 244,
    "zapadna sahara": 245,
    "jemen": 246,
    "zambija": 247,
    "zimbabve": 248,
}


def normalize_text(text):
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_postcrossing_number(country_text):
    normalized = normalize_text(country_text)

    # Explicit special rules requested by the user.
    words = set(normalized.split())

    if "salvador" in words:
        return 66

    if "man" in words:
        return 106

    if "helena" in words and "ascension" in words and "tristan" in words:
        return 185

    if "vincent" in words:
        return 190

    if "nevis" in words:
        return 186

    # Swaziland is always treated as Eswatini.
    if "swaziland" in words:
        return 70

    # Exact/alias matching.
    if normalized in ALIASES:
        return ALIASES[normalized]

    for alias, number in ALIASES.items():
        if alias in normalized:
            return number

    # Match against the English Postcrossing names.
    for number, name in POSTCROSSING.items():
        if normalized == normalize_text(name):
            return number

    # Try matching without the two-letter country code.
    without_code = re.sub(r"\b[a-z]{2}\b", " ", normalized)
    without_code = re.sub(r"\s+", " ", without_code).strip()

    for number, name in POSTCROSSING.items():
        candidate = normalize_text(name)

        if without_code == candidate:
            return number

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
        services_cell = cells[2] if len(cells) >= 3 else None

        country_text = extract_country_text(country_cell)

        if not country_text:
            continue

        # Skip the table header.
        normalized_country = normalize_text(country_text)
        if "odredistna zemlja" in normalized_country:
            continue

        services_text = (
            services_cell.get_text(" ", strip=True)
            if services_cell is not None
            else ""
        )

        normalized_services = normalize_text(services_text)

        all_countries.append(country_text)

        # Suspended if:
        # 1. services column contains exactly STOP, or
        # 2. "Pismonosne" is missing from allowed services.
        is_stop = normalized_services == "stop"
        has_pismonosne = "pismonosne" in normalized_services

        if is_stop or not has_pismonosne:
            suspended_countries.append(country_text)

    return all_countries, suspended_countries


def build_output(all_countries, suspended_countries):
    lines = []

    lines.append("SVE ZEMLJE")
    lines.append(f"UKUPNO: {len(all_countries)}")
    lines.append("")

    for country in all_countries:
        lines.append(add_postcrossing_number(country))

    lines.append("")
    lines.append("SUSPENDOVANE ZEMLJE")
    lines.append(f"UKUPNO: {len(suspended_countries)}")
    lines.append("")

    for country in suspended_countries:
        lines.append(add_postcrossing_number(country))

    lines.append("")

    return "\n".join(lines)


def main():
    response = requests.get(
        URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; srpskepost-monitor/1.0)"
        },
    )

    response.raise_for_status()

    all_countries, suspended_countries = parse_table(response.text)

    # Safety checks.
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

    output = build_output(all_countries, suspended_countries)

    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(output)

    print(
        f"Successfully wrote {len(all_countries)} countries and "
        f"{len(suspended_countries)} suspended countries to output.txt"
    )


if __name__ == "__main__":
    main()
