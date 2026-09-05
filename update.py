#!/usr/bin/env python3

import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup


SOURCE_URL = "https://www.postesrpske.com/spisak-zemalja-medjunarodne-posiljke/"
OUTPUT_FILE = Path("output.txt")

EXPECTED_HEADER_PARTS = (
    "odredišna zemlja",
    "dozvoljene vrste pošiljaka",
)


def normalize_space(text):
    """Collapse all whitespace into single spaces."""
    return re.sub(r"\s+", " ", text).strip()


def normalize_for_comparison(text):
    """Normalize text for case-insensitive comparisons."""
    return normalize_space(text).casefold()


def extract_serbian_name(country_cell):
    """
    Extract the Serbian country/territory name from a cell such as:

        Avganistan (AF) AFGANISTAN
        Crna Gora (ME) MONTENEGRO
        Gernzi – (GB) GUERNSEY

    The Serbian name is everything before the two-letter code.
    """
    text = normalize_space(country_cell)

    # Remove the change marker used by Pošta Srpske.
    text = text.replace("*", "")

    # Country code is normally a two-letter code in parentheses.
    match = re.search(r"\s*\(([A-Z]{2})\)", text)

    if match:
        name = text[:match.start()]
    else:
        # Fallback if the website changes its formatting.
        name = text

    return normalize_space(name)


def find_target_table(soup):
    """
    Find the table containing the two columns we need.
    """

    for table in soup.find_all("table"):
        headers = []

        # Check <th> elements first.
        for th in table.find_all("th"):
            headers.append(normalize_for_comparison(th.get_text(" ", strip=True)))

        # Some HTML tables may use the first row as headers instead.
        if not headers:
            first_row = table.find("tr")
            if first_row:
                headers = [
                    normalize_for_comparison(
                        cell.get_text(" ", strip=True)
                    )
                    for cell in first_row.find_all(["td", "th"])
                ]

        header_text = " ".join(headers)

        if all(part in header_text for part in EXPECTED_HEADER_PARTS):
            return table

    return None


def parse_table(table):
    """
    Extract:

      1. All country/territory names.
      2. Suspended country/territory names.

    A country is suspended when:
      - the allowed-services column contains STOP, OR
      - "Pismonosne" is missing from the allowed-services column.

    Rows without a country name are ignored.
    """

    all_countries = []
    suspended_countries = []

    rows = table.find_all("tr")

    for row in rows:
        cells = row.find_all(["td", "th"])

        if not cells:
            continue

        cell_texts = [
            normalize_space(cell.get_text(" ", strip=True))
            for cell in cells
        ]

        # Skip the header row.
        combined = normalize_for_comparison(" ".join(cell_texts))
        if (
            "odredišna zemlja" in combined
            or "dozvoljene vrste pošiljaka" in combined
        ):
            continue

        # We need at least the country column and services column.
        #
        # Normal rows have:
        #   [R. b., country, services]
        #
        # Some continuation rows have:
        #   [country, services]
        #
        # Therefore handle both forms.

        if len(cell_texts) >= 3:
            country_cell = cell_texts[-2]
            services_cell = cell_texts[-1]
        elif len(cell_texts) == 2:
            country_cell = cell_texts[0]
            services_cell = cell_texts[1]
        else:
            continue

        country_name = extract_serbian_name(country_cell)

        # Ignore obvious non-data rows.
        if not country_name:
            continue

        if normalize_for_comparison(country_name) in {
            "odredišna zemlja",
            "odredišna zemlja srpski naziv",
        }:
            continue

        # A valid country cell should normally contain a country code.
        # This prevents unrelated page/table rows from being collected.
        if not re.search(r"\([A-Z]{2}\)", country_cell):
            continue

        all_countries.append(country_name)

        services_normalized = normalize_for_comparison(services_cell)

        is_stop = services_normalized == "stop"

        has_pismonosne = "pismonosne" in services_normalized

        if is_stop or not has_pismonosne:
            suspended_countries.append(country_name)

    return all_countries, suspended_countries


def build_output(all_countries, suspended_countries):
    """
    Build a deterministic output file.

    IMPORTANT:
    No retrieval timestamp is included because changedetection.io
    should only detect actual changes to the country lists.
    """

    lines = []

    lines.append("POŠTA SRPSKE - MEĐUNARODNE POŠILJKE")
    lines.append("")
    lines.append("SVE ZEMLJE")
    lines.append(f"Ukupno: {len(all_countries)}")
    lines.append("")

    for country in all_countries:
        lines.append(country)

    lines.append("")
    lines.append("SUSPENDOVANE ZEMLJE")
    lines.append(f"Ukupno: {len(suspended_countries)}")
    lines.append("")

    for country in suspended_countries:
        lines.append(country)

    lines.append("")

    return "\n".join(lines)


def main():
    print(f"Downloading: {SOURCE_URL}")

    try:
        response = requests.get(
            SOURCE_URL,
            timeout=60,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; srpskepost-monitor/1.0; "
                    "+https://github.com/)"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;"
                    "q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "sr,en;q=0.8",
            },
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        print(f"ERROR: Could not download the website: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Downloaded {len(response.content):,} bytes")

    soup = BeautifulSoup(response.content, "html.parser")

    table = find_target_table(soup)

    if table is None:
        print(
            "ERROR: Could not find the expected Pošta Srpske table.",
            file=sys.stderr,
        )
        sys.exit(1)

    all_countries, suspended_countries = parse_table(table)

    print(f"Countries found: {len(all_countries)}")
    print(f"Suspended countries found: {len(suspended_countries)}")

    # Safety check.
    #
    # If the website changes its HTML and our parser suddenly finds
    # nothing, NEVER overwrite the existing output.txt with bad data.
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
            "This is probably a parsing problem, so output.txt "
            "will NOT be overwritten.",
            file=sys.stderr,
        )
        sys.exit(1)

    output = build_output(
        all_countries,
        suspended_countries,
    )

    OUTPUT_FILE.write_text(output, encoding="utf-8")

    print(f"Wrote {OUTPUT_FILE}")
    print("Update completed successfully.")


if __name__ == "__main__":
    main()
