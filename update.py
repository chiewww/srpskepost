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


def extract_country_text(country_cell):
    """
    Keep the complete visible country-column text.

    Example:
        Avganistan (AF) AFGANISTAN

    The website may contain an asterisk used as a change marker.
    That marker is removed so the output contains the actual
    country/code/English-name information.
    """

    text = normalize_space(country_cell)

    # Remove the change marker used by Pošta Srpske.
    text = text.replace("*", "")

    return normalize_space(text)


def find_target_table(soup):
    """
    Find the table containing the two columns we need.
    """

    for table in soup.find_all("table"):
        headers = []

        # Check <th> elements first.
        for th in table.find_all("th"):
            headers.append(
                normalize_for_comparison(
                    th.get_text(" ", strip=True)
                )
            )

        # Some HTML tables may use the first row as headers.
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

      1. All country/territory names exactly as displayed in the
         country column, including the two-letter code and English name.
      2. Suspended country/territory names.

    A country is suspended when:
      - the allowed-services column is STOP, OR
      - "Pismonosne" is missing from the allowed-services column.

    Both numbered countries and continuation/territory rows are included.
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

        # Skip the header row.
        combined = normalize_for_comparison(
            " ".join(cell_texts)
        )

        if (
            "odredišna zemlja" in combined
            or "dozvoljene vrste pošiljaka" in combined
        ):
            continue

        # Normal rows:
        #   [R. b., country, services]
        #
        # Continuation/territory rows:
        #   [country, services]

        if len(cell_texts) >= 3:
            country_cell = cell_texts[-2]
            services_cell = cell_texts[-1]

        elif len(cell_texts) == 2:
            country_cell = cell_texts[0]
            services_cell = cell_texts[1]

        else:
            continue

        # The complete text from the country column.
        country_text = extract_country_text(country_cell)

        if not country_text:
            continue

        # A valid country/territory entry should contain a
        # two-letter country/territory code in parentheses.
        if not re.search(r"\([A-Z]{2}\)", country_text):
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


def build_output(all_countries, suspended_countries):
    """
    Build a deterministic output file.

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
            "ERROR: Could not find the expected Pošta Srpske table.",
            file=sys.stderr,
        )
        sys.exit(1)

    all_countries, suspended_countries = parse_table(table)

    print(
        f"Countries found: {len(all_countries)}"
    )

    print(
        f"Suspended countries found: "
        f"{len(suspended_countries)}"
    )

    # Safety check.
    #
    # If the website changes its HTML and the parser suddenly
    # finds too few countries, NEVER overwrite the existing
    # output.txt with bad data.
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

    OUTPUT_FILE.write_text(
        output,
        encoding="utf-8",
    )

    print(f"Wrote {OUTPUT_FILE}")
    print("Update completed successfully.")


if __name__ == "__main__":
    main()
