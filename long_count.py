import argparse
import datetime
import os
import re
import sys
from typing import Tuple, Optional

# =========================
# Configuration / Defaults
# =========================

MAYA_EPOCH_JDN = 584283  # default: GMT correlation
HAAB_DAY_BASE = 0        # 0 => 0..19 (Wayebʼ 0..4) [DEFAULT], 1 => 1..20 (Wayebʼ 1..5)
HAAB_MODE = "great"      # "great" = Community Gran Wayebʼ [DEFAULT], "standard" = continuous 365-day Haabʼ

# Haabʼ and Cholqʼij names
HAAB_MONTHS = [
    "Pop", "Wo", "Sip", "Sotzʼ", "Sek", "Xul", "Yaxkʼin", "Mol", "Chʼen", "Yax",
    "Sak", "Keh", "Mak", "Kʼankʼin", "Muwan", "Pax", "Kʼayab", "Kumkʼu", "Wayebʼ"
]
CHOLQIJ_NAMES = [
    "Imox", "Iqʼ", "Aqʼabʼal", "Kʼat", "Kan", "Keme", "Kej", "Qʼanil", "Toj", "Tzʼiʼ",
    "Bʼatzʼ", "E", "Aj", "Iʼx", "Tzʼikin", "Ajmaq", "Noʼj", "Tijax", "Kawoq", "Ajpuʼ"
]

# Epoch alignments for 0.0.0.0.0: 4 Ajpuʼ, 8 Kumkʼu, G9
_CHOLQIJ_START_NUMBER = 4
_CHOLQIJ_START_NAME_INDEX = CHOLQIJ_NAMES.index("Ajpuʼ")  # 19
# This is the Haabʼ position at 0.0.0.0.0, not at 13.0.0.0.0. Advancing
# 13 Bʼakʼtuns makes 13.0.0.0.0 equal 3 Kʼankʼin in standard mode.
_HAAB_START_ABS_INDEX = 17 * 20 + 8  # 8 Kumkʼu at 0.0.0.0.0 (0-based day)
_LORD_START_NUMBER = 9

# Community Gran Wayebʼ configuration, anchored to the Ajqʼijʼs supplied count:
# 2013-01-02 = 0 Gran Wayebʼ; 2013-01-14 = 12 Gran Wayebʼ; 2013-01-15 = 0 Pop.
GREAT_WAYEB_ANCHOR_YEAR = 2013
GREAT_WAYEB_ANCHOR_MONTH = 1
GREAT_WAYEB_ANCHOR_DAY_OF_MONTH = 2
GREAT_WAYEB_DAYS = 13
HAAB_YEARS_PER_GREAT_CYCLE = 52
REGULAR_HAAB_DAYS = 365
REGULAR_WAYEB_DAYS = 5

# Gran Wayebʼ replaces the final regular five-day Wayebʼ of the 52-Haab block.
ORDINARY_DAYS_PER_GREAT_CYCLE = (
    HAAB_YEARS_PER_GREAT_CYCLE * REGULAR_HAAB_DAYS - REGULAR_WAYEB_DAYS
)
GREAT_WAYEB_CYCLE_DAYS = ORDINARY_DAYS_PER_GREAT_CYCLE + GREAT_WAYEB_DAYS

# ===============
# Helper / Math
# ===============

def gregorian_to_jdn(year: int, month: int, day: int) -> int:
    """Proleptic Gregorian → JDN (astronomical year numbering internally)."""
    y = year + 1 if year < 0 else year
    a = (14 - month) // 12
    y_ = y + 4800 - a
    m_ = month + 12 * a - 3
    return day + (153 * m_ + 2) // 5 + 365 * y_ + y_ // 4 - y_ // 100 + y_ // 400 - 32045


def jdn_to_gregorian(jdn: int) -> Tuple[int, int, int]:
    """JDN → (year, month, day) in historical numbering (…,-2,-1,1,2,…)."""
    f = jdn + 1401 + (((4 * jdn + 274277) // 146097) * 3) // 4 - 38
    e = 4 * f + 3
    g = (e % 1461) // 4
    h = 5 * g + 2
    day = (h % 153) // 5 + 1
    month = ((h // 153 + 2) % 12) + 1
    year = e // 1461 - 4716 + (12 + 2 - month) // 12
    if year <= 0:
        year -= 1
    return year, month, day


def floor_divmod(a: int, b: int) -> Tuple[int, int]:
    """Divmod with non-negative remainder, works for negative a as Python does."""
    q = a // b
    r = a - q * b
    return q, r


def jdn_to_long_count(jdn: int) -> Tuple[int, int, int, int, int]:
    """JDN → normalized Long Count (baktun, katun, tun, uinal, kin)."""
    days = jdn - MAYA_EPOCH_JDN
    baktun, rem = floor_divmod(days, 144000)   # 20*20*18*20
    katun, rem  = floor_divmod(rem, 7200)      # 20*18*20
    tun, rem    = floor_divmod(rem, 360)       # 18*20
    uinal, kin  = floor_divmod(rem, 20)
    return (baktun, katun, tun, uinal, kin)


# ===========================
# Extended Long Count (beyond Bʼakʼtun)
# ===========================

# Higher-order units (each is 20× the previous, above Bʼakʼtun)
# Bʼakʼtun = 144,000 days
PIKTUN_DAYS     = 20 * 144000            # 2,880,000
KALABTUN_DAYS   = 20 * PIKTUN_DAYS       # 57,600,000
KINCHILTUN_DAYS = 20 * KALABTUN_DAYS     # 1,152,000,000
ALAUTUN_DAYS    = 20 * KINCHILTUN_DAYS   # 23,040,000,000


def jdn_to_extended_long_count(jdn: int) -> Tuple[int, int, int, int, int, int, int, int, int]:
    """JDN → normalized *extended* Long Count:
    (alautun, kinchiltun, kalabtun, piktun, baktun, katun, tun, uinal, kin).
    """
    days = jdn - MAYA_EPOCH_JDN

    alautun, rem     = floor_divmod(days, ALAUTUN_DAYS)
    kinchiltun, rem  = floor_divmod(rem, KINCHILTUN_DAYS)
    kalabtun, rem    = floor_divmod(rem, KALABTUN_DAYS)
    piktun, rem      = floor_divmod(rem, PIKTUN_DAYS)

    baktun, rem = floor_divmod(rem, 144000)
    katun, rem  = floor_divmod(rem, 7200)
    tun, rem    = floor_divmod(rem, 360)
    uinal, kin  = floor_divmod(rem, 20)

    return (alautun, kinchiltun, kalabtun, piktun, baktun, katun, tun, uinal, kin)


def format_extended_lc(ext_lc: Tuple[int, int, int, int, int, int, int, int, int]) -> str:
    """Format extended LC as dot-separated string: A.KC.KAL.PIK.B.K.T.U.K"""
    return ".".join(map(str, ext_lc))

def long_count_components_to_total_days(b: int, k: int, t: int, u: int, kin: int) -> int:
    """Allow out-of-range LC components; convert straight to total days (may be negative)."""
    return b * 144000 + k * 7200 + t * 360 + u * 20 + kin


def normalize_long_count(b: int, k: int, t: int, u: int, kin: int) -> Tuple[int, int, int, int, int]:
    """
    Normalize possibly out-of-range LC components into canonical ranges by:
      1) summing to total days,
      2) converting back via jdn_to_long_count.
    """
    total_days = long_count_components_to_total_days(b, k, t, u, kin)
    jdn = MAYA_EPOCH_JDN + total_days
    return jdn_to_long_count(jdn)


def long_count_to_jdn(baktun: int, katun: int, tun: int, uinal: int, kin: int, strict: bool = False) -> int:
    """
    LC → JDN.
    - If strict=True: enforce canonical ranges (katun,tun,kin 0..19; uinal 0..17).
    - If strict=False: auto-normalize arbitrary values.
    """
    if strict:
        if not (0 <= katun <= 19 and 0 <= tun <= 19 and 0 <= uinal <= 17 and 0 <= kin <= 19):
            raise ValueError("Invalid Long Count: katun,tun,kin must be 0..19 and uinal 0..17.")
        total = baktun * 144000 + katun * 7200 + tun * 360 + uinal * 20 + kin
        return MAYA_EPOCH_JDN + total
    else:
        nb, nk, nt, nu, nkin = normalize_long_count(baktun, katun, tun, uinal, kin)
        total = nb * 144000 + nk * 7200 + nt * 360 + nu * 20 + nkin
        return MAYA_EPOCH_JDN + total


# ===========================
# Cholqʼij / Haabʼ / Night 9
# ===========================

def cholqij_from_jdn(jdn: int) -> Tuple[str, int]:
    """Return the Kʼicheʼ Cholqʼij day name and number for a JDN."""
    days = jdn - MAYA_EPOCH_JDN
    name_idx = (_CHOLQIJ_START_NAME_INDEX + days) % 20
    number = ((_CHOLQIJ_START_NUMBER - 1 + days) % 13) + 1
    return CHOLQIJ_NAMES[name_idx], number


def standard_haab_from_jdn(jdn: int) -> Tuple[str, int]:
    """Return the uninterrupted 365-day Haabʼ for a JDN."""
    days = jdn - MAYA_EPOCH_JDN
    haab_index = (_HAAB_START_ABS_INDEX + days) % REGULAR_HAAB_DAYS
    month = haab_index // 20
    day_zero_based = haab_index % 20   # 0..19 (Wayebʼ 0..4)
    day_display = day_zero_based if HAAB_DAY_BASE == 0 else day_zero_based + 1
    return HAAB_MONTHS[month], day_display


def great_wayeb_haab_from_jdn(jdn: int) -> Tuple[str, int]:
    """
    Return the Community Gran Wayebʼ Haabʼ label for a JDN.

    Gran Wayebʼ contains 13 days numbered 0..12 and replaces the regular
    five-day Wayebʼ at the end of each 52-Haab block. The modulo operation
    extends the supplied anchor sequence backward and forward indefinitely.
    """
    anchor_jdn = gregorian_to_jdn(
        GREAT_WAYEB_ANCHOR_YEAR,
        GREAT_WAYEB_ANCHOR_MONTH,
        GREAT_WAYEB_ANCHOR_DAY_OF_MONTH,
    )
    position = (jdn - anchor_jdn) % GREAT_WAYEB_CYCLE_DAYS

    if position < GREAT_WAYEB_DAYS:
        # Gran Wayebʼ numbering is fixed at 0..12, independently of HAAB_DAY_BASE.
        return "Gran Wayebʼ", position

    # After 12 Gran Wayebʼ, the ordinary Haabʼ resumes at 0 Pop. Between
    # special periods are 51 complete 365-day Haabʼ years plus 360 days of
    # the 52nd year; its regular 0..4 Wayebʼ is replaced by Gran Wayebʼ.
    regular_position = (position - GREAT_WAYEB_DAYS) % REGULAR_HAAB_DAYS
    month = regular_position // 20
    day_zero_based = regular_position % 20
    day_display = day_zero_based if HAAB_DAY_BASE == 0 else day_zero_based + 1
    return HAAB_MONTHS[month], day_display


def haab_from_jdn(jdn: int, mode: Optional[str] = None) -> Tuple[str, int]:
    """Return the Haabʼ label using Community Gran Wayebʼ or standard mode."""
    selected_mode = HAAB_MODE if mode is None else mode
    if selected_mode == "standard":
        return standard_haab_from_jdn(jdn)
    if selected_mode == "great":
        return great_wayeb_haab_from_jdn(jdn)
    raise ValueError("Haabʼ mode must be 'great' or 'standard'.")


def lord_of_the_night_from_jdn(jdn: int) -> str:
    days = jdn - MAYA_EPOCH_JDN
    num = ((_LORD_START_NUMBER - 1 + days) % 9) + 1
    return f"G{num}"


# ===============
# Input Validation
# ===============

def is_leap_year_gregorian(year: int) -> bool:
    """Leap rule for proleptic Gregorian (astronomical internally)."""
    y = year if year > 0 else year + 1
    return (y % 4 == 0) and (y % 100 != 0 or y % 400 == 0)


def validate_gregorian_date(year: int, month: int, day: int) -> bool:
    if year == 0 or not (1 <= month <= 12) or day < 1:
        return False
    dim = [31, 29 if is_leap_year_gregorian(year) else 28, 31, 30, 31, 30,
           31, 31, 30, 31, 30, 31]
    return day <= dim[month - 1]


def parse_gregorian_input(text: str) -> Tuple[int, int, int]:
    """Parse the same Gregorian formats accepted by the HTML converter."""
    match = re.fullmatch(r"(-?\d+)[./-](\d{1,2})[./-](\d{1,2})", text.strip())
    if not match:
        raise ValueError("Use YYYY-MM-DD, YYYY.MM.DD, or YYYY/MM/DD.")

    year, month, day = map(int, match.groups())
    if not validate_gregorian_date(year, month, day):
        raise ValueError("Enter a valid proleptic Gregorian date without year zero.")
    return year, month, day


def parse_long_count_input(text: str) -> Tuple[int, int, int, int, int]:
    """Parse five Long Count components separated by dots or whitespace."""
    parts = re.split(r"(?:\s*\.\s*|\s+)", text.strip())
    if len(parts) != 5 or any(not re.fullmatch(r"-?\d+", part) for part in parts):
        raise ValueError("Use Bʼakʼtun.Kʼatun.Tun.Winal.Kin, for example 13.0.0.0.0.")
    return tuple(map(int, parts))


# ============
# UI / Display
# ============

def display_from_jdn(jdn: int) -> None:
    lc = jdn_to_long_count(jdn)

    # If Bʼakʼtun is outside the canonical 0..19 range, the standard 5-part Long Count
    # becomes ambiguous. In that case we automatically show the Extended Long Count.
    if abs(lc[0]) >= 20:
        print(
            "\nNote: This date exceeds the 0..19 Bʼakʼtun range for the standard Long Count. "
            "Showing the Extended Long Count instead."
        )
        display_extended_from_jdn(jdn)
        return
    cholqij_name, cholqij_num = cholqij_from_jdn(jdn)
    haab_month, haab_day = haab_from_jdn(jdn)
    lord = lord_of_the_night_from_jdn(jdn)
    y, m, d = jdn_to_gregorian(jdn)

    diary = f"{'.'.join(map(str, lc))} - {cholqij_num} {cholqij_name} - {haab_day} {haab_month} - {lord} - {y}-{m:02d}-{d:02d}"
    print(f"\nDiary Format:\n{diary}")
    print("\nLong Count:")
    print(f"{lc[0]} Bʼakʼtun, {lc[1]} Kʼatun, {lc[2]} Tun, {lc[3]} Winal, {lc[4]} Kin")
    print(f"Cholqʼij (Tzolkʼin) (Kʼicheʼ name): {cholqij_num} {cholqij_name}")
    print(f"Haabʼ (Yucatec name): {haab_day} {haab_month}")
    print(f"Lord of the Night: {lord}")
    print(f"Gregorian (proleptic): {y}-{m:02d}-{d:02d}")


def display_extended_from_jdn(jdn: int) -> None:
    """Like display_from_jdn(), but shows the extended Long Count (Alautun..Kin)."""
    ext_lc = jdn_to_extended_long_count(jdn)

    # The extended format is written here with explicit Alautun/Kʼinchiltun/Kalabtun/Piktun labels.
    # If Alautun is outside 0..19, we still show it as an integer, but this is not a standard
    # (historically-attested) way of writing dates.
    if abs(ext_lc[0]) >= 20:
        print(
            "\nDate out of the scope of the current format. "
            "It is shown as 21, 22, 200... Alautun (and beyond) as a practical extension, "
            "but this is not an official/standard way of displaying the date."
        )
    cholqij_name, cholqij_num = cholqij_from_jdn(jdn)
    haab_month, haab_day = haab_from_jdn(jdn)
    lord = lord_of_the_night_from_jdn(jdn)
    y, m, d = jdn_to_gregorian(jdn)

    diary = f"{format_extended_lc(ext_lc)} - {cholqij_num} {cholqij_name} - {haab_day} {haab_month} - {lord} - {y}-{m:02d}-{d:02d}"
    print(f"\nDiary Format (Extended):\n{diary}")

    print("\nExtended Long Count:")
    print(
        f"{ext_lc[0]} Alautun, {ext_lc[1]} Kʼinchiltun, {ext_lc[2]} Kalabtun, {ext_lc[3]} Piktun, "
        f"{ext_lc[4]} Bʼakʼtun, {ext_lc[5]} Kʼatun, {ext_lc[6]} Tun, {ext_lc[7]} Winal, {ext_lc[8]} Kin"
    )
    print(f"Cholqʼij (Tzolkʼin) (Kʼicheʼ name): {cholqij_num} {cholqij_name}")
    print(f"Haabʼ (Yucatec name): {haab_day} {haab_month}")
    print(f"Lord of the Night: {lord}")
    print(f"Gregorian (proleptic): {y}-{m:02d}-{d:02d}")


def haab_mode_label(mode: Optional[str] = None) -> str:
    selected_mode = HAAB_MODE if mode is None else mode
    if selected_mode == "great":
        return "Community Gran Wayebʼ adjustment"
    return "Standard continuous 365-day Haabʼ"


def current_settings_text() -> str:
    base_label = "0-based" if HAAB_DAY_BASE == 0 else "1-based"
    return (
        f"Haabʼ: {haab_mode_label()} | Ordinary Haabʼ days: {base_label} | "
        f"Correlation JDN: {MAYA_EPOCH_JDN}"
    )


def clear_terminal() -> None:
    """Clear an interactive terminal without spawning another process."""
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="", flush=True)


def _read_menu_key() -> str:
    """Read one menu key, including arrow keys, on Windows or POSIX terminals."""
    if os.name == "nt":
        import msvcrt

        key = msvcrt.getwch()
        if key in ("\x00", "\xe0"):
            return {"H": "up", "P": "down", "G": "home", "O": "end"}.get(
                msvcrt.getwch(), "other"
            )
        if key == "\r":
            return "enter"
        if key == "\x03":
            raise KeyboardInterrupt
        return key.lower()

    import termios
    import tty

    file_descriptor = sys.stdin.fileno()
    previous_settings = termios.tcgetattr(file_descriptor)
    try:
        tty.setraw(file_descriptor)
        key = sys.stdin.read(1)
        if key == "\x03":
            raise KeyboardInterrupt
        if key in ("\r", "\n"):
            return "enter"
        if key == "\x1b":
            # Arrow keys arrive as a three-character escape sequence. Reading the
            # two remaining characters directly is more reliable across terminals.
            sequence = sys.stdin.read(2)
            return {
                "[A": "up",
                "OA": "up",
                "[B": "down",
                "OB": "down",
                "[H": "home",
                "OH": "home",
                "[F": "end",
                "OF": "end",
            }.get(sequence, "other")
        return key.lower()
    finally:
        termios.tcsetattr(file_descriptor, termios.TCSADRAIN, previous_settings)


def _numbered_menu(title: str, options: Tuple[str, ...], default_index: int) -> Optional[int]:
    """Fallback menu for redirected input and terminals without raw-key support."""
    while True:
        print(f"\n{title}")
        for index, option in enumerate(options, start=1):
            default_marker = " [default]" if index - 1 == default_index else ""
            print(f"  {index}. {option}{default_marker}")
        response = input("Select a number, press Enter for the default, or Q to go back: ").strip().lower()
        if not response:
            return default_index
        if response in ("q", "quit", "back"):
            return None
        if response.isdigit() and 1 <= int(response) <= len(options):
            return int(response) - 1
        print("Please select one of the listed options.")


def select_menu(
    title: str,
    options: Tuple[str, ...],
    default_index: int = 0,
    context: Optional[str] = None,
) -> Optional[int]:
    """Display an arrow-key menu, with a numbered-input fallback."""
    if not options:
        raise ValueError("A menu must contain at least one option.")

    selected = max(0, min(default_index, len(options) - 1))
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        if context:
            print(context)
        return _numbered_menu(title, options, selected)

    while True:
        clear_terminal()
        print("MAYA CALENDAR\n")
        print(title)
        if context:
            print(f"{context}\n")
        for index, option in enumerate(options):
            marker = "❯" if index == selected else " "
            print(f" {marker} {index + 1}. {option}")
        print("\nUse ↑/↓ and Enter. Number keys also work; Q goes back.")

        key = _read_menu_key()
        if key in ("up", "k", "w"):
            selected = (selected - 1) % len(options)
        elif key in ("down", "j", "s"):
            selected = (selected + 1) % len(options)
        elif key == "home":
            selected = 0
        elif key == "end":
            selected = len(options) - 1
        elif key == "enter":
            return selected
        elif key == "q":
            return None
        elif key.isdigit() and key != "0" and int(key) <= len(options):
            return int(key) - 1


def pause_for_menu() -> None:
    try:
        input("\nPress Enter to return to the menu...")
    except EOFError:
        pass


def show_date_screen(jdn: int, title: str, extended: bool = False) -> None:
    clear_terminal()
    print(f"MAYA CALENDAR — {title}")
    print(current_settings_text())
    if extended:
        display_extended_from_jdn(jdn)
    else:
        display_from_jdn(jdn)
    pause_for_menu()


def choose_haab_mode(title: str = "Choose the Haabʼ calculation") -> bool:
    """Let the user change the session Haabʼ mode. Return False if cancelled."""
    global HAAB_MODE
    options = (
        "Community Gran Wayebʼ — replaces Wayebʼ with 13 days (0–12) every 52 Haabʼ",
        "Standard Haabʼ — continuous 365-day cycle with Wayebʼ 0–4",
    )
    choice = select_menu(title, options, 0 if HAAB_MODE == "great" else 1)
    if choice is None:
        return False
    HAAB_MODE = "great" if choice == 0 else "standard"
    return True


def choose_haab_day_base() -> bool:
    """Let the user change ordinary Haabʼ numbering. Gran Wayebʼ stays 0..12."""
    global HAAB_DAY_BASE
    options = (
        "Zero-based — ordinary periods 0–19 and Wayebʼ 0–4",
        "One-based — ordinary periods 1–20 and Wayebʼ 1–5",
    )
    choice = select_menu(
        "Choose ordinary Haabʼ day numbering",
        options,
        HAAB_DAY_BASE,
        "Gran Wayebʼ remains numbered 0–12 in both settings.",
    )
    if choice is None:
        return False
    HAAB_DAY_BASE = choice
    return True


def change_correlation() -> bool:
    global MAYA_EPOCH_JDN
    clear_terminal()
    print("MAYA CALENDAR — Correlation setting\n")
    print(f"Current correlation JDN: {MAYA_EPOCH_JDN}")
    try:
        response = input(
            "Enter a new integer correlation, press Enter to keep it, or Q to go back: "
        ).strip()
    except EOFError:
        return False
    if not response or response.lower() == "q":
        return False
    try:
        MAYA_EPOCH_JDN = int(response)
    except ValueError:
        print("The correlation must be an integer.")
        pause_for_menu()
        return False
    return True


def settings_menu() -> bool:
    """Edit session settings and report whether a setting was selected."""
    changed = False
    while True:
        options = (
            f"Haabʼ mode — {haab_mode_label()}",
            f"Ordinary Haabʼ numbering — {'0-based' if HAAB_DAY_BASE == 0 else '1-based'}",
            f"Correlation constant — JDN {MAYA_EPOCH_JDN}",
            "Return to main menu",
        )
        choice = select_menu("Settings", options, context=current_settings_text())
        if choice is None or choice == 3:
            return changed
        if choice == 0:
            changed = choose_haab_mode("Change the Haabʼ calculation") or changed
        elif choice == 1:
            changed = choose_haab_day_base() or changed
        elif choice == 2:
            changed = change_correlation() or changed


def prompt_for_gregorian_date() -> Optional[int]:
    while True:
        clear_terminal()
        print("MAYA CALENDAR — Gregorian → Maya calendar\n")
        print("Accepted formats: 2026-09-01, 2026.09.01, or 2026/09/01")
        print("Use a negative year for BCE dates; year zero is not accepted.")
        try:
            response = input("\nGregorian date (or Q to go back): ").strip()
        except EOFError:
            return None
        if response.lower() == "q":
            return None
        try:
            year, month, day = parse_gregorian_input(response)
            return gregorian_to_jdn(year, month, day)
        except ValueError as error:
            print(f"\nError: {error}")
            pause_for_menu()


def prompt_for_long_count() -> Optional[int]:
    while True:
        clear_terminal()
        print("MAYA CALENDAR — Long Count → Gregorian\n")
        print("Format: Bʼakʼtun.Kʼatun.Tun.Winal.Kin")
        print("Example: 13.0.0.0.0")
        print("Out-of-range components are normalized automatically in interactive mode.")
        try:
            response = input("\nLong Count (or Q to go back): ").strip()
        except EOFError:
            return None
        if response.lower() == "q":
            return None
        try:
            components = parse_long_count_input(response)
            normalized = normalize_long_count(*components)
            if components != normalized:
                print(
                    f"\nNormalized Long Count: {'.'.join(map(str, normalized))}"
                )
                pause_for_menu()
            return long_count_to_jdn(*components, strict=False)
        except ValueError as error:
            print(f"\nError: {error}")
            pause_for_menu()


def run_interactive() -> None:
    """Run the browser-like terminal interface used when no conversion flag is passed."""
    if not choose_haab_mode("Welcome — choose the Haabʼ calculation for this session"):
        return

    today = datetime.date.today()
    today_jdn = gregorian_to_jdn(today.year, today.month, today.day)
    last_jdn = today_jdn
    show_date_screen(today_jdn, "Today")

    main_options = (
        "Show todayʼs date",
        "Convert a Gregorian date",
        "Convert a Long Count date",
        "Show the last date in Extended Long Count format",
        "Settings",
        "Exit",
    )

    while True:
        year, month, day = jdn_to_gregorian(last_jdn)
        context = (
            f"{current_settings_text()}\n"
            f"Last displayed date: {year}-{month:02d}-{day:02d}"
        )
        choice = select_menu("Main menu", main_options, context=context)
        if choice is None or choice == 5:
            clear_terminal()
            print("Thank you for using the Maya Calendar converter.")
            return
        if choice == 0:
            last_jdn = today_jdn
            show_date_screen(last_jdn, "Today")
        elif choice == 1:
            converted_jdn = prompt_for_gregorian_date()
            if converted_jdn is not None:
                last_jdn = converted_jdn
                show_date_screen(last_jdn, "Converted date")
        elif choice == 2:
            converted_jdn = prompt_for_long_count()
            if converted_jdn is not None:
                last_jdn = converted_jdn
                show_date_screen(last_jdn, "Converted date")
        elif choice == 3:
            show_date_screen(last_jdn, "Extended Long Count", extended=True)
        elif choice == 4:
            if settings_menu():
                show_date_screen(last_jdn, "Updated settings")


# ======
#  CLI
# ======

def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert between Gregorian and Maya calendars (Long Count, Cholqʼij, Haabʼ, Night Lords)."
    )
    parser.add_argument(
        "--corr", type=int, default=584283,
        help="Correlation constant (JDN) for Long Count 0.0.0.0.0 (default: 584283)."
    )
    parser.add_argument(
        "--haab-day-base", type=int, choices=[0, 1], default=0,
        help=(
            "Ordinary Haabʼ day numbering: 0 = 0..19/0..4 (default), "
            "1 = 1..20/1..5. Gran Wayebʼ remains 0..12."
        ),
    )
    parser.add_argument(
        "--haab-mode", choices=["great", "standard"], default="great",
        help=(
            "Haabʼ calculation: 'great' = Community Gran Wayebʼ replacement "
            "(default), 'standard' = continuous 365-day Haabʼ."
        ),
    )

    # Mutually exclusive non-interactive modes
    sub = parser.add_mutually_exclusive_group()

    # Non-interactive: from Gregorian
    sub.add_argument(
        "--from-gregorian", nargs=3, metavar=("YEAR", "MONTH", "DAY"), type=int,
        help="Non-interactive conversion from Gregorian date (YEAR MONTH DAY)."
    )

    # Non-interactive: from Long Count
    sub.add_argument(
        "--from-lc", nargs=5, metavar=("BAKTUN", "KATUN", "TUN", "UINAL", "KIN"), type=int,
        help="Non-interactive conversion from Long Count (allow out-of-range; auto-normalized)."
    )

    # Optional strict flag for LC inputs (applies only if --from-lc is used)
    parser.add_argument(
        "--strict-lc", action="store_true",
        help="When set with --from-lc, enforce canonical LC component ranges instead of normalizing."
    )

    return parser.parse_args()


def main():
    global MAYA_EPOCH_JDN, HAAB_DAY_BASE, HAAB_MODE
    args = parse_args()
    MAYA_EPOCH_JDN = args.corr
    HAAB_DAY_BASE = args.haab_day_base
    HAAB_MODE = args.haab_mode

    # Non-interactive modes
    if args.from_gregorian:
        print(
            f"[Using correlation JDN = {MAYA_EPOCH_JDN}, "
            f"Haabʼ mode = {HAAB_MODE}, Haabʼ day base = {HAAB_DAY_BASE}]"
        )
        y, m, d = args.from_gregorian
        if not validate_gregorian_date(y, m, d):
            print("Invalid Gregorian date.")
            return
        jdn = gregorian_to_jdn(y, m, d)
        display_from_jdn(jdn)
        return

    if args.from_lc:
        print(
            f"[Using correlation JDN = {MAYA_EPOCH_JDN}, "
            f"Haabʼ mode = {HAAB_MODE}, Haabʼ day base = {HAAB_DAY_BASE}]"
        )
        b, k, t, u, kin = args.from_lc
        try:
            jdn = long_count_to_jdn(b, k, t, u, kin, strict=args.strict_lc)
        except ValueError as e:
            print(f"Error: {e}")
            return
        display_from_jdn(jdn)
        return

    try:
        run_interactive()
    except (KeyboardInterrupt, EOFError):
        clear_terminal()
        print("Exited Maya Calendar converter.")


if __name__ == "__main__":
    main()
