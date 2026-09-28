"""Generate one birthday page per entry in birthdays.md.

Run with: python generate_birthdays.py
Laviksha.html is used as the reusable HTML template.
"""

from datetime import date
from html import escape
from pathlib import Path
import re


MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}
ENTRY_PATTERN = re.compile(r"^\s*(.+?)\s*-\s*(\d{1,2})-([A-Za-z]{3})-(\d{4})\s*$")
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def parse_entries(markdown: str) -> list[tuple[str, date]]:
    entries = []
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        if not line.strip():
            continue

        match = ENTRY_PATTERN.fullmatch(line)
        if match is None:
            raise ValueError(f"Line {line_number}: expected 'Name - DD-MMM-YYYY'")

        name, day_text, month_text, year_text = match.groups()
        month = MONTHS.get(month_text.casefold())
        if month is None:
            raise ValueError(f"Line {line_number}: unknown month '{month_text}'")

        try:
            birthday = date(int(year_text), month, int(day_text))
        except ValueError as error:
            raise ValueError(f"Line {line_number}: invalid birthday: {error}") from error

        entries.append((name.strip(), birthday))

    if not entries:
        raise ValueError("birthdays.md does not contain any birthday entries")
    return entries


def safe_filename(name: str) -> str:
    filename = INVALID_FILENAME_CHARS.sub("_", name).strip().rstrip(".")
    if not filename:
        raise ValueError(f"Name cannot be used as a filename: {name!r}")
    return filename


def render_page(template: str, name: str, birthday: date) -> str:
    replacements = {
        "data-name": escape(name, quote=True),
        "data-dob": birthday.isoformat(),
    }
    page = template
    for attribute, value in replacements.items():
        page, count = re.subn(
            rf'\b{attribute}="[^"]*"',
            f'{attribute}="{value}"',
            page,
            count=1,
        )
        if count != 1:
            raise ValueError(f"Template must contain exactly one {attribute} attribute")
    return page


def main() -> None:
    folder = Path(__file__).resolve().parent
    birthdays_path = folder / "birthdays.md"
    template_path = folder / "Laviksha.html"
    template = template_path.read_text(encoding="utf-8")
    entries = parse_entries(birthdays_path.read_text(encoding="utf-8"))

    filenames = [safe_filename(name) for name, _ in entries]
    if len({filename.casefold() for filename in filenames}) != len(filenames):
        raise ValueError("Birthday entries produce duplicate filenames")

    for (name, birthday), filename in zip(entries, filenames):
        output_path = folder / f"{filename}.html"
        output_path.write_text(render_page(template, name, birthday), encoding="utf-8")
        print(f"Generated {output_path.name}")


if __name__ == "__main__":
    main()
