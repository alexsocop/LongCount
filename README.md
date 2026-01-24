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
- **Haab’** (365-day solar cycle)
- **Lords of the Night** (9-day cycle)

It supports both:

- **Interactive mode** (the program asks you what to input)
- **Command-line mode** (you pass arguments like `--from-gregorian`)

---

## Output format

For any input date, the script prints a **Diary Format** line:

```
LongCount - Tzolk’in - Haab’ - Night Lord - Gregorian
```

Example layout:

```
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

```
Alautun.K’inchiltun.Kalabtun.Piktun.B’ak’tun.K’atun.Tun.Winal.Kin - Tzolk’in - Haab’ - Night Lord - Gregorian
```

This extended format is shown only when requested by the user.

**Units beyond B’ak’tun (bigger than 144,000 days)**

After B’ak’tun, the Long Count can continue in the same pattern:
- Piktun = 20 B’ak’tun
- Kalabtun = 20 Piktun
- K’inchiltun = 20 Kalabtun
- Alautun = 20 K’inchiltun

In days (to have a better understanding of the scale)
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

**Important detail:** most steps are base‑20, but **Tun = 18×20 = 360 days**, which is close to a solar year and helps keep the system aligned with seasonal timekeeping.

### Converting JDN → Long Count

1. Compute how many days have passed since the Mayan epoch:

```
days_since_epoch = JDN - MAYA_EPOCH_JDN
```

2. Break that number into components using division + remainder:

- B’ak’tun is `days // 144000`
- K’atun is the next remainder divided by `7200`
- Tun uses `360`
- Winal uses `20`
- Kin is what remains

This is the mathematical idea of **positional representation** (mixed‑radix counting).

---

## How the Tzolk’in calculation works (260‑day cycle)

The **Tzolk’in** is a repeating cycle of **260 days**.

It is formed by combining:

- a **13‑number cycle** (1–13)
- a **20‑name cycle** (20 day names)

Because 13 and 20 “sync up” every 260 days, the full combination repeats every:

```
LCM(13, 20) = 260
```

The script computes the correct name/number using modular arithmetic:

- `(... + days_since_epoch) % 20` for the name
- `(... + days_since_epoch) % 13` for the number

---

## How the Haab’ calculation works (365‑day cycle)

The **Haab’** is a solar calendar of **365 days**:

- 18 months × 20 days = 360 days
- plus **Wayeb’** = 5 extra days
- total = 365 days

The script computes a “day-of-year index”:

```
haab_index = (... + days_since_epoch) % 365
```

Then it converts that into:

- month = `haab_index // 20`
- day = `haab_index % 20`

### Haab’ day base (0-based vs 1-based)

This repo currently defaults to **0-based** Haab’ numbering:

- normal months: `0..19`
- Wayeb’: `0..4`

This is controlled by:

- `HAAB_DAY_BASE = 0`

You can change the display style with:

```bash
python long_count.py --haab-day-base 1 ...
```

---

## Lords of the Night (9‑day cycle)

The **Lords of the Night** repeat every 9 days:

- `G1` through `G9`

The script calculates this using:

```
(... + days_since_epoch) % 9
```

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

## Summary of the math principles used

This script is based on three simple ideas:

1. **Absolute day counting (JDN):** convert dates into a single day index.
2. **Modular arithmetic (`%`):** compute repeating calendar cycles like 260, 365, and 9.
3. **Mixed‑radix counting (Long Count):** represent total days in units like B’ak’tun/K’atun/Tun/Winal/Kin.

---

## Notes from recent updates

In the last commit a few functions were updated:

1. The base for Haab' is now **zero**
2. The script uses the **Long Count as the base** for time keeping
3. The input accepts **Long Count or Gregorian formats**
4. It accepts **negative B’ak’tun numbers** and handles special cases
5. Added an **Extended Long Count** option (Piktun, Kalabtun, K’inchiltun, Alautun)
6. When requested, the script shows the **extended format for the last converted date** (not always today's date)
