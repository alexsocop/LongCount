import argparse
import datetime
from typing import Tuple, Optional

# =========================
# Configuration / Defaults
# =========================

MAYA_EPOCH_JDN = 584283  # default: GMT correlation
HAAB_DAY_BASE = 0        # 0 => 0..19 (Wayebʼ 0..4) [DEFAULT], 1 => 1..20 (Wayebʼ 1..5)

# Haabʼ and Tzolkʼin names
HAAB_MONTHS = [
    "Pop", "Wo", "Sip", "Sotzʼ", "Sek", "Xul", "Yaxkʼin", "Mol", "Chʼen", "Yax",
    "Sak", "Keh", "Mak", "Kʼankʼin", "Muwan", "Pax", "Kʼayab", "Kumkʼu", "Wayebʼ"
]
TZOLKIN_NAMES = [
    "Imox", "Iqʼ", "Aqʼabʼal", "Kʼat", "Kan", "Kame", "Kej", "Qʼanil", "Toj", "Tzʼiʼ",
    "Bʼatzʼ", "E", "Aj", "Iʼx", "Tzʼikin", "Ajmaq", "Noʼj", "Tijax", "Kawoq", "Ajpuʼ"
]

# Epoch alignments for 0.0.0.0.0: 4 Ajpuʼ, 8 Kumkʼu, G9
_TZ_START_NUMBER = 4
_TZ_START_NAME_INDEX = TZOLKIN_NAMES.index("Ajpuʼ")  # 19
_HAAB_START_ABS_INDEX = 17 * 20 + 8  # 8 Kumkʼu (0-based day)
_LORD_START_NUMBER = 9

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
# Tzolkʼin / Haabʼ / Night 9
# ===========================

def tzolkin_from_jdn(jdn: int) -> Tuple[str, int]:
    days = jdn - MAYA_EPOCH_JDN
    name_idx = (_TZ_START_NAME_INDEX + days) % 20
    number = ((_TZ_START_NUMBER - 1 + days) % 13) + 1
    return TZOLKIN_NAMES[name_idx], number


def haab_from_jdn(jdn: int) -> Tuple[str, int]:
    """Returns (month_name, day_number) with day base per HAAB_DAY_BASE (0 or 1)."""
    days = jdn - MAYA_EPOCH_JDN
    haab_index = (_HAAB_START_ABS_INDEX + days) % 365  # 0..364
    month = haab_index // 20
    day_zero_based = haab_index % 20   # 0..19 (Wayebʼ 0..4)
    day_display = day_zero_based if HAAB_DAY_BASE == 0 else day_zero_based + 1
    return HAAB_MONTHS[month], day_display


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
    if not (1 <= month <= 12) or day < 1:
        return False
    dim = [31, 29 if is_leap_year_gregorian(year) else 28, 31, 30, 31, 30,
           31, 31, 30, 31, 30, 31]
    return day <= dim[month - 1]


# ============
# UI / Display
# ============

def display_from_jdn(jdn: int) -> None:
    lc = jdn_to_long_count(jdn)
    tz_name, tz_num = tzolkin_from_jdn(jdn)
    haab_month, haab_day = haab_from_jdn(jdn)
    lord = lord_of_the_night_from_jdn(jdn)
    y, m, d = jdn_to_gregorian(jdn)

    diary = f"{'.'.join(map(str, lc))} - {tz_num} {tz_name} - {haab_day} {haab_month} - {lord} - {y}-{m:02d}-{d:02d}"
    print(f"\nDiary Format:\n{diary}")
    print("\nLong Count:")
    print(f"{lc[0]} Bʼakʼtun, {lc[1]} Kʼatun, {lc[2]} Tun, {lc[3]} Winal, {lc[4]} Kin")
    print(f"Cholqʼij (Tzolkʼin) (Kʼicheʼ name): {tz_num} {tz_name}")
    print(f"Haabʼ (Yucatec name): {haab_day} {haab_month}")
    print(f"Lord of the Night: {lord}")
    print(f"Gregorian (proleptic): {y}-{m:02d}-{d:02d}")


def display_extended_from_jdn(jdn: int) -> None:
    """Like display_from_jdn(), but shows the extended Long Count (Alautun..Kin)."""
    ext_lc = jdn_to_extended_long_count(jdn)
    tz_name, tz_num = tzolkin_from_jdn(jdn)
    haab_month, haab_day = haab_from_jdn(jdn)
    lord = lord_of_the_night_from_jdn(jdn)
    y, m, d = jdn_to_gregorian(jdn)

    diary = f"{format_extended_lc(ext_lc)} - {tz_num} {tz_name} - {haab_day} {haab_month} - {lord} - {y}-{m:02d}-{d:02d}"
    print(f"\nDiary Format (Extended):\n{diary}")

    print("\nExtended Long Count:")
    print(
        f"{ext_lc[0]} Alautun, {ext_lc[1]} Kʼinchiltun, {ext_lc[2]} Kalabtun, {ext_lc[3]} Piktun, "
        f"{ext_lc[4]} Bʼakʼtun, {ext_lc[5]} Kʼatun, {ext_lc[6]} Tun, {ext_lc[7]} Winal, {ext_lc[8]} Kin"
    )
    print(f"Cholqʼij (Tzolkʼin) (Kʼicheʼ name): {tz_num} {tz_name}")
    print(f"Haabʼ (Yucatec name): {haab_day} {haab_month}")
    print(f"Lord of the Night: {lord}")
    print(f"Gregorian (proleptic): {y}-{m:02d}-{d:02d}")


def show_welcome_message():
    today = datetime.date.today()
    print(f"Welcome! Todayʼs date is {today.strftime('%Y-%m-%d')}.\n")
    jdn_today = gregorian_to_jdn(today.year, today.month, today.day)
    display_from_jdn(jdn_today)


# ======
#  CLI
# ======

def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert between Gregorian and Mayan calendars (Long Count, Tzolkʼin, Haabʼ, Night Lords)."
    )
    parser.add_argument(
        "--corr", type=int, default=584283,
        help="Correlation constant (JDN) for Long Count 0.0.0.0.0 (default: 584283)."
    )
    parser.add_argument(
        "--haab-day-base", type=int, choices=[0, 1], default=0,
        help="Haabʼ day numbering base: 0 = 0..19/0..4 (default), 1 = 1..20/1..5."
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
    global MAYA_EPOCH_JDN, HAAB_DAY_BASE
    args = parse_args()
    MAYA_EPOCH_JDN = args.corr
    HAAB_DAY_BASE = args.haab_day_base

    print(f"[Using correlation JDN = {MAYA_EPOCH_JDN}, Haabʼ day base = {HAAB_DAY_BASE}]")

    # Non-interactive modes
    if args.from_gregorian:
        y, m, d = args.from_gregorian
        if not validate_gregorian_date(y, m, d):
            print("Invalid Gregorian date.")
            return
        jdn = gregorian_to_jdn(y, m, d)
        display_from_jdn(jdn)
        return

    if args.from_lc:
        b, k, t, u, kin = args.from_lc
        try:
            jdn = long_count_to_jdn(b, k, t, u, kin, strict=args.strict_lc)
        except ValueError as e:
            print(f"Error: {e}")
            return
        display_from_jdn(jdn)
        return

    # Interactive mode (fallback)
    show_welcome_message()
    # Track the most recently displayed/converted date so extended output matches the user's last date.
    today = datetime.date.today()
    last_jdn = gregorian_to_jdn(today.year, today.month, today.day)
    while True:
        mode = input("\nChoose input mode to convert a new date: [G]regorian, [L]ong Count, or [N]one (show extended today / exit): ").strip().lower()
        if mode.startswith('g'):
            try:
                year = int(input("Enter the year (e.g., 2024, -200 for 200 BCE): "))
                month = int(input("Enter the month (1-12): "))
                day = int(input("Enter the day (1-31): "))
                if not validate_gregorian_date(year, month, day):
                    print("Invalid date entered. Please enter a valid Gregorian date.")
                    continue
                jdn = gregorian_to_jdn(year, month, day)
                last_jdn = jdn
            except ValueError:
                print("Invalid input. Please enter numeric values for year, month, and day.")
                continue
        elif mode.startswith('l'):
            try:
                b = int(input("Bʼakʼtun (can be negative): "))
                k = int(input("Kʼatun (any int; normalized): "))
                t = int(input("Tun (any int; normalized): "))
                u = int(input("Winal (any int; normalized): "))
                kin = int(input("Kin (any int; normalized): "))

                # Normalize automatically in interactive mode
                jdn = long_count_to_jdn(b, k, t, u, kin, strict=False)
                last_jdn = jdn
            except ValueError:
                print("Invalid input. Please enter integer values for Long Count components.")
                continue
        elif mode.startswith('n'):
            # Skip conversion and optionally show *today* in the extended format.
            show_ext = input(
                "Would you like to show today's date in the extended format (Piktun, Kalabtun, K'inchiltun, Alautun)? (yes/y or no/n): "
            ).strip().lower()

            if show_ext in ("yes", "y"):
                today = datetime.date.today()
                jdn_today = gregorian_to_jdn(today.year, today.month, today.day)
                display_extended_from_jdn(jdn_today)

            break
        else:
            print("Please choose 'G', 'L', or 'N'.")
            continue

        display_from_jdn(jdn)

        another = input("Do you want to convert another date? (yes/y or no/n): ").strip().lower()
        if another in ("yes", "y"):
            continue

        # If the user is done converting dates, optionally show the *last date* in the extended format.
        show_ext = input(
            "Would you like to show this date in the extended format (Piktun, Kalabtun, K'inchiltun, Alautun)? (yes/y or no/n): "
        ).strip().lower()

        if show_ext in ("yes", "y"):
            display_extended_from_jdn(last_jdn)

            # After showing extended output, ask again if they want to convert another date.
            again = input("Do you want to convert another date? (yes/y or no/n): ").strip().lower()
            if again in ("yes", "y"):
                continue

        break


if __name__ == "__main__":
    main()

