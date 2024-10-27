import datetime

# Constants for the Haab' and Tzolk'in calendars
HAAB_MONTHS = ["Pop", "Wo", "Sip", "Sotz'", "Sek", "Xul", "Yaxk'in", "Mol", "Ch'en", "Yax", "Sak", "Keh", "Mak", "K'ank'in", "Muwan", "Pax", "K'ayab", "Kumk'u", "Wayeb'"]

TZOLKIN_NAMES = ["Imox", "Iq'", "Aq'ab'al", "K'at", "Kan", "Kame", "Kej", "Q'anil", "Toj", "Tz'i'", "B'atz'", "E", "Aj", "I'x", "Tz'ikin", "Ajmaq", "No'j", "Tijax", "Kawoq", "Ajpu'"]

def gregorian_to_jdn(year, month, day):
    # Adjust year for astronomical year numbering (BCE to astronomical year)
    if year < 0:
        year += 1  # Adjusting for astronomical year numbering; there is no year 0 in historical BCE/CE transition

    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

    return jdn

def jdn_to_maya_long_count(jdn):
    long_count_start_jdn = 584283  # Base date for Maya Long Count
    days_since_start = jdn - long_count_start_jdn

    baktun = days_since_start // 144000
    days_since_start %= 144000

    katun = days_since_start // 7200
    days_since_start %= 7200

    tun = days_since_start // 360
    days_since_start %= 360

    uinal = days_since_start // 20
    k_in = days_since_start % 20
    return (baktun, katun, tun, uinal, k_in)

def calculate_tzolkin(jdn):
    days_since_start = jdn - 584283 - 1  # Adjusting by subtracting one day
    day_number = (days_since_start + 4) % 13 + 1  # Adjust for Tzolk'in start in relation to the GMT correlation
    day_name = days_since_start % 20
    return TZOLKIN_NAMES[day_name], day_number

def calculate_haab(jdn):
    days_since_start = jdn - 584283 - 1  # Adjusting by subtracting one day
    haab_day = (days_since_start + 348) % 365  # Adjust for Haab' start in relation to the GMT correlation
    month = haab_day // 20
    day = haab_day % 20
    return HAAB_MONTHS[month], day + 1

def calculate_lord_of_the_night(jdn):
    # Adjusting the calculation by subtracting one additional day to align correctly
    lord_index = (jdn - 584283 - 1) % 9  # Subtract 1 more day to correct the alignment
    return f"G{lord_index + 1}"

def validate_date(year, month, day):
    # Check if month and day are valid
    if month < 1 or month > 12:
        return False
    if day < 1 or day > 31:
        return False
    
    # For BCE years, we skip datetime.date validation
    if year < 0:
        return True

    # Handle specific days in each month, considering leap years
    days_in_month = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if day > days_in_month[month - 1]:
        return False

    try:
        datetime.date(year, month, day)
        return True
    except ValueError:
        return False

def is_leap_year(year):
    if year < 0:
        year = -year  # Leap year rules don't apply to BCE, but this handles negative years for simplicity
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# Welcome message

def show_welcome_message():
    today = datetime.date.today()
    print(f"Welcome! Today's date is {today.strftime('%Y-%m-%d')}.\n")
    jdn_today = gregorian_to_jdn(today.year, today.month, today.day)
    long_count_today = jdn_to_maya_long_count(jdn_today)
    tzolkin_name_today, tzolkin_number_today = calculate_tzolkin(jdn_today)
    haab_month_today, haab_day_today = calculate_haab(jdn_today)
    lord_of_the_night_today = calculate_lord_of_the_night(jdn_today)

    # Diary Format
    diary_format = f"{'.'.join(map(str, long_count_today))} - {tzolkin_number_today} {tzolkin_name_today} - {haab_day_today} {haab_month_today} - {lord_of_the_night_today} - {today.strftime('%Y-%m-%d')}"
    print(f"Diary Format:\n{diary_format}")

    # Descriptive Long Count
    print("\nToday's Long Count:")
    print(f"{long_count_today[0]} Bʼakʼtun, {long_count_today[1]} Kʼatun, {long_count_today[2]} Tun, {long_count_today[3]} Winal, {long_count_today[4]} Kin")

    # Cholq'ij (Tzolk'in) Day
    print(f"\nToday's Cholq'ij (Tzolk'in) Day (K'iche' name):\n{tzolkin_number_today} {tzolkin_name_today}")

    # Haab' Day
    print(f"\nToday's Haab' Day (Yucatec name):\n{haab_day_today} {haab_month_today}")

    # Lord of the Night
    print(f"\nToday's Lord of the Night:\n{lord_of_the_night_today}")

    #print(f"Starting day of the long count: -3114-09-06")

# Main program
if __name__ == "__main__":
    show_welcome_message()  # Display the welcome message with today's Mayan calendar date.
    while True:
        try:
            year = int(input("\nEnter the year (e.g., 2024, -200 for 200 BCE): "))
            month = int(input("Enter the month (1-12): "))
            day = int(input("Enter the day (1-31): "))

            if validate_date(year, month, day):
                jdn = gregorian_to_jdn(year, month, day)
                long_count = jdn_to_maya_long_count(jdn)
                haab_month, haab_day = calculate_haab(jdn)
                tzolkin_name, tzolkin_number = calculate_tzolkin(jdn)
                lord_of_the_night = calculate_lord_of_the_night(jdn)

                # Display the calculated values
                diary_format = f"{'.'.join(map(str, long_count))} - {tzolkin_number} {tzolkin_name} - {haab_day} {haab_month} - {lord_of_the_night} - {year}-{month:02d}-{day:02d}"
                print(f"\nDiary Format:\n{diary_format}")
                print("\nLong Count:")
                print(f"{long_count[0]} Bʼakʼtun, {long_count[1]} Kʼatun, {long_count[2]} Tun, {long_count[3]} Winal, {long_count[4]} Kin")
                print(f"Tzolk'in: {tzolkin_number} {tzolkin_name}")
                print(f"Haab': {haab_day} {haab_month}")
                print(f"Lord of the Night: {lord_of_the_night}")
            else:
                print("Invalid date entered. Please enter a valid date.")

        except ValueError:
            print("Invalid input. Please enter numeric values for year, month, and day.")
        
        another = input("Do you want to enter another date? (yes/y or no/n): ").strip().lower()
        if another not in ['yes', 'y']:
            break
