# LongCount

These are a couple of scripts to convert dates between the **Gregorian calendar** and the **Mayan calendar**.

This project outputs the Mayan calendar in two ways:

- **Diary format** (a single summarized line)
- A **detailed breakdown** of the Long Count and related cycles

Feel free to revise the code, contribute, and share. For now the program is a simple script, in the future I will work on a graphical interface and portability to different systems (Linux, Android, Mac, Windows).

---

## What this script does

The main script (`long_count.py`) converts dates between:

- **Gregorian** dates (e.g. `2026-01-22`)
- **Mayan Long Count** (e.g. `13.0.0.0.0`)
- **Extended Long Count** (adds Piktun, Kalabtun, K’inchiltun, and Alautun)
- **Tzolk’in / Cholq’ij** (260-day ritual cycle)
- **Haab’** (365-day solar cycle, with an optional community Gran Wayeb’ adjustment)
- **Lords of the Night** (9-day cycle)

It supports both:

- **Interactive mode** (the program asks you what to input)
- **Command-line mode** (you pass arguments like `--from-gregorian`)

The HTML version also provides a browser-based interface that can:

- automatically display today’s Mayan calendar date
- convert a Gregorian date to the Long Count and associated cycles
- convert a Long Count date back to the Gregorian calendar
- display the Haab’ using either the standard continuous 365-day cycle or the community **Gran Wayeb’** adjustment
- automatically select an interface language based on the user’s browser language
- allow the user to manually select the interface language

---

## Output format

For any input date, the script prints a **Diary Format** line:

```text
LongCount - Tzolk’in - Haab’ - Night Lord - Gregorian
```

Example layout:

```text
13.0.0.0.0 - 4 Ajpuʼ - 8 Kumkʼu - G9 - 2012-12-21
```

Then it prints a detailed breakdown, like:

- Long Count components (B’ak’tun, K’atun, Tun, Winal, Kin)
- Tzolk’in name + number
- Haab’ month + day
- Night Lord (G1–G9)
- Gregorian date

### Extended output (optional)

When running in interactive mode, the script can also display an **Extended Diary Format**:

```text
Alautun.K’inchiltun.Kalabtun.Piktun.B’ak’tun.K’atun.Tun.Winal.Kin - Tzolk’in - Haab’ - Night Lord - Gregorian
```

This extended format is shown only when requested by the user.

**Units beyond B’ak’tun (bigger than 144,000 days)**

After B’ak’tun, the Long Count can continue in the same pattern:

- Piktun = 20 B’ak’tun
- Kalabtun = 20 Piktun
- K’inchiltun = 20 Kalabtun
- Alautun = 20 K’inchiltun

In days (to have a better understanding of the scale):

- 1 Piktun = 20 × 144,000 = 2,880,000 days
- 1 Kalabtun = 57,600,000 days
- 1 K’inchiltun = 1,152,000,000 days
- 1 Alautun = 23,040,000,000 days

These are enormous spans of time.

---

## Core idea: everything becomes a day number (JDN)

The most important concept in this script is that **all calendars are converted through a single day counter**:

### **Julian Day Number (JDN)**

A **Julian Day Number** is just an integer that counts days in sequence.

So the script workflow is:

**Gregorian ⇄ JDN ⇄ Mayan calendars**

This makes conversions simple because once a date is a single number, the script can:

- add or subtract days easily
- compare dates easily
- compute repeating cycles using remainders (`%`)

The same JDN is also useful for the community **Gran Wayeb’** calculation because it allows the program to measure exactly how many days a date is before or after the selected Gran Wayeb’ anchor date.

---

## What does the `%` symbol mean in Python?

In Python, the `%` symbol is called the **modulo operator**.

It gives you the **remainder** after dividing one number by another.

Example:

```python
10 % 3
```

- `10 / 3 = 3` with a remainder of `1`
- so the result is `1`

So:

- `10 % 3 = 1`
- `11 % 3 = 2`
- `12 % 3 = 0`  ← this is important because it “wraps around”

### Why `%` is useful for calendars

Calendars like the Tzolk’in (260 days), Haab’ (365 days), and Night Lords (9 days) are **repeating cycles**.

Modulo is a simple way to “loop” back to the beginning of a cycle:

- `% 20` means “repeat every 20 steps”
- `% 13` means “repeat every 13 steps”
- `% 365` means “repeat every 365 days”
- `% 9` means “repeat every 9 days”

The community Gran Wayeb’ calculation also uses modulo, but its complete repeating block is longer:

```text
52 × 365 + 13 = 18,993 days
```

Therefore:

```text
% 18993
```

can be used to determine a date’s position inside one complete community Gran Wayeb’ cycle.

That is why this script uses `%` many times to compute day names and day numbers.

---

## What does `...` mean when you see it in examples?

In this documentation, `...` (three dots) means:

> “some value goes here, but we are not writing the full expression”

It is just a **placeholder** to keep the examples short and readable.

For example, when you see:

```python
(... + days_since_epoch) % 20
```

It means:

- there is some starting offset (a number) that the script uses,
- then it adds `days_since_epoch`,
- and finally applies `% 20` to stay inside the 20-name cycle.

So you can read it as:

> “start at the correct beginning point, move forward by the number of days, then wrap around the cycle”

**Important:** in real Python code, `...` can exist as a special object called `Ellipsis`, but **this script is not using it as code**. Here it is only used in the README examples as a shorthand.

---

## The “correlation constant” (epoch alignment)

The Mayan Long Count needs a starting point that links it to modern dates.

This script uses a constant called:

- `MAYA_EPOCH_JDN` (default: `584283`)

That value is the **GMT correlation constant**, a widely used mapping between:

- **Long Count `0.0.0.0.0`**
and
- a specific **JDN**

### Why this matters

If you change the correlation constant, *all* conversions shift.

You can change it using:

```bash
python long_count.py --corr 584283 ...
```

The **Gran Wayeb’ adjustment is a separate calculation** from the GMT correlation. The GMT constant continues to determine the relationship between the Gregorian calendar and the Long Count.

In other words:

- GMT correlation controls the **Long Count ↔ Gregorian** alignment
- the Gran Wayeb’ configuration controls the **community-adjusted Haab’** alignment

Changing the Haab’ mode does **not** change the Long Count itself.

---

## How the Long Count calculation works

The Long Count is a way of counting days using place values (similar to how time uses hours/minutes/seconds).

### Long Count units

| Unit | Meaning | Days |
|------|---------|------|
| Kin | 1 day | 1 |
| Winal (Uinal) | 20 Kin | 20 |
| Tun | 18 Winal | 360 |
| K’atun | 20 Tun | 7,200 |
| B’ak’tun | 20 K’atun | 144,000 |

**Important detail:** most steps are base-20, but **Tun = 18×20 = 360 days**, which is close to a solar year and helps keep the system aligned with seasonal timekeeping.

### Converting JDN → Long Count

1. Compute how many days have passed since the Mayan epoch:

```text
days_since_epoch = JDN - MAYA_EPOCH_JDN
```

2. Break that number into components using division + remainder:

- B’ak’tun is `days // 144000`
- K’atun is the next remainder divided by `7200`
- Tun uses `360`
- Winal uses `20`
- Kin is what remains

This is the mathematical idea of **positional representation** (mixed-radix counting).

---

## How the Tzolk’in calculation works (260-day cycle)

The **Tzolk’in** is a repeating cycle of **260 days**.

It is formed by combining:

- a **13-number cycle** (1–13)
- a **20-name cycle** (20 day names)

Because 13 and 20 “sync up” every 260 days, the full combination repeats every:

```text
LCM(13, 20) = 260
```

The script computes the correct name/number using modular arithmetic:

- `(... + days_since_epoch) % 20` for the name
- `(... + days_since_epoch) % 13` for the number

The Gran Wayeb’ adjustment does **not** modify this cycle. Tzolk’in / Cholq’ij continues advancing one position for every actual day.

---

## How the Haab’ calculation works

The project provides **two ways of calculating the Haab’**:

1. **Standard continuous 365-day Haab’**
2. **Community Gran Wayeb’ adjustment**

The user can select which interpretation to display in the HTML interface.

The **community Gran Wayeb’ mode is currently the default in the HTML version**.

---

## Standard Haab’ calculation (365-day cycle)

The standard **Haab’** is a solar calendar of **365 days**:

- 18 months × 20 days = 360 days
- plus **Wayeb’** = 5 extra days
- total = 365 days

The 19 named periods used by the program are:

1. Pop
2. Wo
3. Sip
4. Sotz’
5. Sek
6. Xul
7. Yaxk’in
8. Mol
9. Ch’en
10. Yax
11. Sak
12. Keh
13. Mak
14. K’ank’in
15. Muwan
16. Pax
17. K’ayab
18. Kumk’u
19. Wayeb’

The first 18 periods have 20 days each.

Wayeb’ has 5 days.

The script computes a “day-of-year index”:

```text
haab_index = (... + days_since_epoch) % 365
```

Then it converts that into:

- month = `haab_index // 20`
- day = `haab_index % 20`

This produces an uninterrupted cycle:

```text
0 Pop
1 Pop
...
19 Pop
0 Wo
...
19 Kumk’u
0 Wayeb’
1 Wayeb’
2 Wayeb’
3 Wayeb’
4 Wayeb’
0 Pop
```

Under this method there are no additional days inserted into the cycle.

---

## Community Gran Wayeb’ adjustment

The HTML version also includes an alternative Haab’ calculation based on information provided by an **Ajq’ij** from the Maya community.

In this model, after a block of **52 ordinary Haab’ years**, an additional period called **Gran Wayeb’** is introduced.

The implementation uses:

```text
52 ordinary Haab’ years × 365 days = 18,980 days
```

and:

```text
Gran Wayeb’ = 13 days
```

Therefore, one complete adjusted cycle contains:

```text
18,980 + 13 = 18,993 days
```

or:

```text
52 × 365 + 13 = 18,993 days
```

### Important terminology

In the program:

- **Wayeb’** means the normal 5-day period at the end of an ordinary Haab’ year.
- **Gran Wayeb’** means the additional 13-day period used by this community-based 52-Haab adjustment.

They are therefore treated as **different periods** in the calculation.

The normal Wayeb’ remains:

```text
0 Wayeb’
1 Wayeb’
2 Wayeb’
3 Wayeb’
4 Wayeb’
```

The Gran Wayeb’ is displayed separately as:

```text
1 Gran Wayeb’
2 Gran Wayeb’
3 Gran Wayeb’
...
13 Gran Wayeb’
```

### Current Gran Wayeb’ anchor

The information received from the Ajq’ij identified:

```text
2012-12-21
```

as corresponding to a **Gran Wayeb’**.

However, the information did not specify which of the 13 Gran Wayeb’ days it represented.

For this reason, the current implementation makes the explicit working assumption:

```text
2012-12-21 = 1 Gran Wayeb’
```

This is configurable in the HTML code.

The relevant constants are conceptually:

```javascript
GREAT_WAYEB_ANCHOR_YEAR = 2012
GREAT_WAYEB_ANCHOR_MONTH = 12
GREAT_WAYEB_ANCHOR_DAY_OF_MONTH = 21
GREAT_WAYEB_ANCHOR_DAY = 1
GREAT_WAYEB_DAYS = 13
HAAB_YEARS_PER_GREAT_CYCLE = 52
REGULAR_HAAB_DAYS = 365
```

The complete cycle length is then calculated as:

```javascript
GREAT_WAYEB_CYCLE_DAYS =
    HAAB_YEARS_PER_GREAT_CYCLE * REGULAR_HAAB_DAYS
    + GREAT_WAYEB_DAYS
```

which gives:

```text
52 × 365 + 13 = 18,993 days
```

### How the Gran Wayeb’ position is calculated

First, the Gregorian anchor date is converted to JDN:

```text
anchor_JDN = JDN of 2012-12-21
```

The program then calculates how far the requested date is from the anchor and wraps that value inside the complete 18,993-day cycle:

```text
position = (JDN - anchor_JDN) % 18993
```

Because `2012-12-21` is currently configured as Gran Wayeb’ day 1:

```text
position = 0
```

means:

```text
1 Gran Wayeb’
```

The first 13 positions therefore correspond to:

```text
position 0  → 1 Gran Wayeb’
position 1  → 2 Gran Wayeb’
position 2  → 3 Gran Wayeb’
...
position 12 → 13 Gran Wayeb’
```

Mathematically:

```text
if position < 13:
    Gran Wayeb’ day = position + 1
```

### What happens after Gran Wayeb’

After the 13 Gran Wayeb’ days have finished, the ordinary Haab’ cycle begins again at:

```text
0 Pop
```

The program removes the 13 Gran Wayeb’ days from the position:

```text
regular_position = position - 13
```

and then maps the remaining position into an ordinary 365-day Haab’:

```text
haab_position = regular_position % 365
```

The usual Haab’ calculation can then be applied:

```text
month = haab_position // 20
day = haab_position % 20
```

### Example around the 2012 anchor

With the current configuration:

```text
2012-12-20 → 4 Wayeb’
2012-12-21 → 1 Gran Wayeb’
2012-12-22 → 2 Gran Wayeb’
2012-12-23 → 3 Gran Wayeb’
...
2013-01-01 → 12 Gran Wayeb’
2013-01-02 → 13 Gran Wayeb’
2013-01-03 → 0 Pop
```

The ordinary Haab’ then continues normally for 52 × 365 days before the next Gran Wayeb’ period.

### Why the adjustment repeats every 18,993 days

A complete community-adjusted cycle consists of:

```text
13 Gran Wayeb’ days
+
52 × 365 ordinary Haab’ days
```

which equals:

```text
18,993 days
```

Modulo arithmetic allows the same calculation to work for dates both before and after the 2012 anchor:

```text
position = (date_JDN - anchor_JDN) % 18993
```

Therefore the program can extrapolate the same pattern backward and forward in time without maintaining a table of every Gran Wayeb’ date.

### The Gran Wayeb’ anchor is configurable

The current assignment:

```text
2012-12-21 = 1 Gran Wayeb’
```

is an explicit implementation assumption based on the information available when this functionality was added.

If more precise information becomes available—for example, if an Ajq’ij establishes that `2012-12-21` should instead correspond to day 5 of Gran Wayeb’—the anchor can be adjusted without changing the rest of the algorithm.

Conceptually, the program supports:

```text
GREAT_WAYEB_ANCHOR_DAY = 1..13
```

If the anchor day changes, the program shifts the effective beginning of the 18,993-day cycle accordingly.

---

## Standard Haab’ vs community Gran Wayeb’ mode

These two options should not be confused.

### Standard mode

Uses:

```text
18 × 20 + 5 = 365 days
```

and repeats continuously:

```text
Haab’ → Haab’ → Haab’ → Haab’ ...
```

The normal Wayeb’ always contains five days:

```text
0..4 Wayeb’
```

### Community Gran Wayeb’ mode

Uses the same ordinary 365-day Haab’, including its normal 5-day Wayeb’, but adds a separate 13-day Gran Wayeb’ after each 52-Haab block:

```text
52 × 365 + 13 = 18,993 days
```

The Gran Wayeb’ contains:

```text
1..13 Gran Wayeb’
```

The 13 days are therefore **not a replacement for the five normal Wayeb’ days in every year**.

Instead, the implementation treats Gran Wayeb’ as an **additional intercalary period associated with the 52-Haab cycle**.

---

## Why the Haab’ changes but the Long Count does not

This distinction is important.

The **Long Count** counts actual days continuously from its epoch:

```text
days_since_epoch = JDN - MAYA_EPOCH_JDN
```

The **Cholq’ij** also advances continuously one day at a time.

The **Lords of the Night** also advance continuously one day at a time.

The Gran Wayeb’ adjustment does not add fictional days to JDN and does not modify elapsed physical time.

Instead, it changes **how a real JDN is labelled inside the Haab’ cycle**.

Therefore, for a given Gregorian date:

- Gregorian date → unchanged
- JDN → unchanged
- Long Count → unchanged
- Cholq’ij → unchanged
- Lord of the Night → unchanged
- Haab’ → may differ depending on the selected Haab’ mode

For example, changing between the standard and community Gran Wayeb’ modes does not change a Long Count such as:

```text
13.0.13.16.2
```

It only changes the corresponding Haab’ designation.

---

## Haab’ day base (0-based vs 1-based)

This repo currently defaults to **0-based** Haab’ numbering for the ordinary Haab’:

- normal months: `0..19`
- Wayeb’: `0..4`

This is controlled by:

- `HAAB_DAY_BASE = 0`

You can change the display style with:

```bash
python long_count.py --haab-day-base 1 ...
```

The community **Gran Wayeb’** is displayed differently and currently uses:

```text
1..13
```

rather than:

```text
0..12
```

This is intentional in the current implementation.

So, with the default settings:

```text
ordinary Haab’ month → 0..19
Wayeb’              → 0..4
Gran Wayeb’         → 1..13
```

---

## Note about the Gran Wayeb’ interpretation

The repository distinguishes the **standard continuous 365-day Haab’ calculation** from the **community Gran Wayeb’ adjustment** intentionally.

The standard mode preserves the ordinary mathematical Haab’ cycle:

```text
18 × 20 + 5 = 365 days
```

The Gran Wayeb’ mode was added to represent information communicated by an Ajq’ij after an earlier version of this project was shared with members of a Maya scholarly/community network.

Because the precise historical and community interpretations of calendar practices can differ, the code does not replace the standard Haab’ calculation permanently. Instead, both calculations are retained so that users can select the model they intend to use.

The current Gran Wayeb’ implementation should therefore be understood as a **specific configurable calendar model**, with:

```text
2012-12-21 = 1 Gran Wayeb’
```

serving as its present anchor.

If more precise information about the anchor or the 52-Haab adjustment becomes available, the relevant constants can be revised without affecting the Long Count, Cholq’ij, Gregorian, or Lords of the Night calculations.

---

## Lords of the Night (9-day cycle)

The **Lords of the Night** repeat every 9 days:

- `G1` through `G9`

The script calculates this using:

```text
(... + days_since_epoch) % 9
```

Like the Long Count and Cholq’ij, this cycle is independent of the selected Haab’ calculation mode.

---

## Long Count input rules (normalization vs strict)

This script supports two ways to handle Long Count inputs:

### 1) Normal mode (default): auto-normalize

If you input values that are out of range (example: 25 Kin), the script:

1. converts the components into total days
2. converts back into a normalized Long Count

This is convenient for users and helps avoid “invalid” inputs.

### 2) Strict mode (optional)

If you pass `--strict-lc`, the script enforces canonical ranges:

- K’atun, Tun, Kin must be `0..19`
- Winal must be `0..17`

Example:

```bash
python long_count.py --from-lc 13 0 0 0 0 --strict-lc
```

---

## How to run

### Interactive mode

```bash
python long_count.py
```

The program will ask if you want to input:

- `G` for Gregorian
- `L` for Long Count
- `N` to skip conversions and optionally show the extended format

### Convert from Gregorian (command line)

```bash
python long_count.py --from-gregorian 2026 1 22
```

### Convert from Long Count (command line)

```bash
python long_count.py --from-lc 13 0 0 0 0
```

---

## HTML version

The browser version can be used without installing Python.

When hosted through GitHub Pages, an HTML file can be opened directly in a web browser.

The interface automatically calculates today’s date and displays:

```text
Long Count - Cholq’ij - Haab’ - Night Lord - Gregorian
```

It also includes a date converter that supports:

### Gregorian → Mayan calendar

Accepted Gregorian input formats include:

```text
2026-09-01
2026.09.01
2026/09/01
```

### Long Count → Gregorian

Long Count input uses:

```text
B’ak’tun.K’atun.Tun.Winal.Kin
```

For example:

```text
13.0.13.16.2
```

The converter returns:

- Diary Format
- Long Count
- Cholq’ij
- Haab’
- Lord of the Night
- Gregorian date

The user can also switch between:

- **Community Gran Wayeb’ adjustment**
- **Standard continuous 365-day Haab’**

Changing this setting recalculates the Haab’ designation while keeping the Long Count, Cholq’ij, Lord of the Night, JDN, and Gregorian date unchanged.

---

## Multilingual HTML interface

The HTML interface also includes multilingual support.

The browser attempts to select the interface language automatically using the user’s browser language preferences.

The user can also manually change the language using the language selector at the top of the page.

The calendar notation itself remains the same regardless of interface language.

For example:

```text
13.0.13.16.2
```

and calendar names such as:

```text
Iqʼ
Ajpuʼ
Mol
Mak
Kumkʼu
Wayebʼ
Gran Wayebʼ
```

remain calendar terms rather than being translated into unrelated equivalents.

The currently supported interface languages include:

- English
- Spanish
- K’iche’
- Traditional Chinese (Taiwan)
- Japanese
- Arabic
- Hindi
- Bahasa Indonesia
- Portuguese
- Bengali

For right-to-left languages such as Arabic, the interface direction changes appropriately while calendar numbers and date notation remain left-to-right.

---

## Summary of the math principles used

This script is based on several simple ideas:

1. **Absolute day counting (JDN):** convert dates into a single day index.
2. **Modular arithmetic (`%`):** compute repeating calendar cycles like 260, 365, 9, and the 18,993-day community Gran Wayeb’ cycle.
3. **Mixed-radix counting (Long Count):** represent total days in units like B’ak’tun/K’atun/Tun/Winal/Kin.
4. **Independent calendar cycles:** the Long Count, Cholq’ij, Haab’, and Lords of the Night are calculated from the same absolute day but follow their own rules.
5. **Configurable Haab’ interpretation:** the HTML can calculate either the standard continuous 365-day Haab’ or the community Gran Wayeb’ model.

For the community Gran Wayeb’ mode, the main mathematical relationship is:

```text
52 × 365 + 13 = 18,993 days
```

and the current anchor is:

```text
2012-12-21 = 1 Gran Wayeb’
```

---

## Notes from recent updates

In the last commits a few functions were updated:

1. The base for Haab' is now **zero**
2. The script uses the **Long Count as the base** for time keeping
3. The input accepts **Long Count or Gregorian formats**
4. It accepts **negative B’ak’tun numbers** and handles special cases
5. Added an **Extended Long Count** option (Piktun, Kalabtun, K’inchiltun, Alautun)
6. When requested, the script shows the **extended format for the last converted date** (not always today's date)
7. Added a browser-based **Gregorian ⇄ Long Count date converter**
8. Added a selectable **community Gran Wayeb’ Haab’ calculation**
9. The Gran Wayeb’ model currently uses **2012-12-21 as 1 Gran Wayeb’**
10. The Gran Wayeb’ model inserts **13 additional days after each 52-Haab block**
11. The complete community-adjusted cycle is therefore **18,993 days**
12. The original **standard continuous 365-day Haab’** remains available as an alternative
13. Changing the Haab’ mode does **not** alter the Long Count, Cholq’ij, Lord of the Night, Gregorian date, or JDN
14. Added a **multilingual HTML interface**
15. Added automatic browser-language detection and manual language selection
16. Added right-to-left interface support for languages such as Arabic
