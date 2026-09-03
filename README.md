# LongCount

**LongCount** is an open-source Maya calendar converter. It converts dates between the proleptic Gregorian calendar and the Maya Long Count and displays the corresponding **Cholqʼij**, **Haabʼ**, and **Lord of the Night**.

The project includes a browser-based interface in `kin.html` and a command-line implementation in `long_count.py`.

- Live application: <https://alexsocop.github.io/LongCount/kin.html>
- Source code: <https://github.com/alexsocop/LongCount>

Contributions, corrections, translation improvements, and culturally informed review are welcome.

---

## Features

The browser application can:

- display todayʼs Maya calendar date automatically;
- convert a Gregorian date to the Long Count and associated cycles;
- convert a Long Count date to the Gregorian calendar;
- calculate the 260-day **Cholqʼij** cycle using Kʼicheʼ day names;
- calculate the **Haabʼ** in either standard or Community Gran Wayebʼ mode;
- calculate the **Lords of the Night** (`G1`–`G9`);
- display the calendar in a two-column Mayan-numeral arrangement;
- optionally display the Extended Long Count from Alautun through Kin;
- switch automatically to the Extended Long Count for sufficiently distant dates;
- accept signed Long Count components and normalize noncanonical input;
- select an interface language from the page;
- detect the userʼs preferred browser language;
- remember a manually selected language when browser storage is available; and
- support right-to-left layout for Arabic.

The Python version also provides an arrow-key terminal interface, preserves command-line use, and supports configurable correlation, Haabʼ numbering, and strict Long Count validation.

---

## Calendar systems displayed

The application combines several independent counts:

- **Long Count:** a continuous count of elapsed days;
- **Cholqʼij (Tzolkʼin):** a 260-day cycle formed from 13 numbers and 20 day names;
- **Haabʼ:** a 365-day cycle consisting of 18 periods of 20 days plus Wayebʼ;
- **Community Gran Wayebʼ adjustment:** an alternative, community-informed way of labeling the Haabʼ around the end of a 52-Haab block; and
- **Lords of the Night:** a repeating nine-day sequence from `G1` to `G9`.

These counts advance from the same absolute date, but they are calculated independently. Switching the Haabʼ mode changes only the Haabʼ designation. It does not change the Gregorian date, Julian Day Number, Long Count, Cholqʼij, or Lord of the Night.

---

## Diary format

The summarized output uses this order:

```text
Long Count - Cholqʼij - Haabʼ - Lord of the Night - Gregorian
```

Because the HTML currently opens in Community Gran Wayebʼ mode, its default result for December 21, 2012 is:

```text
13.0.0.0.0 - 4 Ajpuʼ - 8 Kumkʼu - G9 - 2012-12-21
```

For the same physical date, standard continuous Haabʼ mode produces:

```text
13.0.0.0.0 - 4 Ajpuʼ - 3 Kʼankʼin - G9 - 2012-12-21
```

This difference is intentional. The Long Count, Cholqʼij, Lord of the Night, and Gregorian date remain unchanged; only the selected Haabʼ model differs.

### Detailed output

The converter also displays:

- the Long Count components;
- a two-column calendar arrangement using Unicode Mayan numerals;
- the Cholqʼij number and day name;
- the Haabʼ day and period;
- the Lord of the Night; and
- the Gregorian date.

### Extended Long Count

Both the browser and command-line versions can display:

```text
Alautun.Kʼinchiltun.Kalabtun.Piktun.Bʼakʼtun.Kʼatun.Tun.Winal.Kin
```

The larger units are:

| Unit | Equivalent | Days |
|---|---:|---:|
| Piktun | 20 Bʼakʼtun | 2,880,000 |
| Kalabtun | 20 Piktun | 57,600,000 |
| Kʼinchiltun | 20 Kalabtun | 1,152,000,000 |
| Alautun | 20 Kʼinchiltun | 23,040,000,000 |

In `kin.html`, users can select **Show the Extended Long Count** in the calculation settings. For an ordinary contemporary date, the four higher positions are zero. When the normalized Bʼakʼtun position reaches `20` or `-20`, the browser displays the extended form automatically, even if the option has not been selected.

For example:

```text
20.0.0.0.0
```

is displayed automatically in extended form as:

```text
0.0.0.1.0.0.0.0.0
```

The extended notation used by this project is a practical computational representation. Extremely large Alautun values should not be interpreted as a claim about historically attested calendrical notation.

### Mayan numeral display

The browser displays numerical coefficients with the Unicode **Mayan Numerals** characters `U+1D2E0–U+1D2F3`, representing the values `0–19`.

The regular display follows a two-column, zig-zag reading order:

| Left column | Right column |
|---|---|
| Bʼakʼtun | Kʼatun |
| Tun | Winal |
| Kin | Cholqʼij |
| Haabʼ | Lord of the Night |

When the Extended Long Count is displayed, its four higher positions are placed before Bʼakʼtun while the remaining calendrical values retain their order.

The numeral font is hosted locally rather than loaded from an external service:

```text
assets/fonts/NotoSansMayanNumerals-Regular.woff2
```

Its license is stored alongside it:

```text
assets/fonts/OFL.txt
```

The relative directory structure must be preserved. Uploading `kin.html` without the `assets/fonts/` files may cause the specialized Mayan numeral characters to depend on fonts installed on the visitorʼs device.

---

## Core conversion model: Julian Day Number

All conversions pass through a **Julian Day Number (JDN)**, an integer that identifies a day in a continuous sequence:

```text
Gregorian ⇄ JDN ⇄ Maya calendar counts
```

Once a date has been converted to a JDN, the program can:

- measure elapsed days from the Long Count epoch;
- break the result into Long Count units;
- advance the Cholqʼij, Haabʼ, and Lords of the Night independently; and
- locate a date within the repeating Community Gran Wayebʼ model.

The HTML uses proleptic Gregorian calculations. Negative years represent BCE dates using historical year numbering, so `-1` means 1 BCE. Year zero is not accepted.

---

## Correlation constant

The project currently uses the GMT correlation constant:

```text
JDN 584283
```

In the HTML this is stored in `CORR_JDN`; the Python implementation refers to the corresponding Maya epoch JDN.

The correlation establishes:

```text
Long Count 0.0.0.0.0 = JDN 584283
```

The classical epoch alignments used by the calculation are:

```text
0.0.0.0.0 - 4 Ajpuʼ - 8 Kumkʼu - G9
```

The `8 Kumkʼu` alignment belongs to **Long Count `0.0.0.0.0`**, not to `13.0.0.0.0`. After advancing 13 Bʼakʼtuns, the standard continuous Haabʼ result for December 21, 2012 is `3 Kʼankʼin`.

The Community Gran Wayebʼ anchor is separate from the GMT correlation. Changing Haabʼ modes does not move the Long Count epoch or change the Gregorian conversion.

---

## Long Count calculation

The Long Count uses mixed place values:

| Unit | Relationship | Days |
|---|---:|---:|
| Kin | 1 day | 1 |
| Winal | 20 Kin | 20 |
| Tun | 18 Winal | 360 |
| Kʼatun | 20 Tun | 7,200 |
| Bʼakʼtun | 20 Kʼatun | 144,000 |

The program first calculates:

```text
days_since_epoch = JDN - CORR_JDN
```

It then divides the elapsed days into Bʼakʼtun, Kʼatun, Tun, Winal, and Kin. Most positions use a factor of 20, while one Tun contains 18 Winal, or 360 days.

---

## Cholqʼij calculation

The **Cholqʼij** is formed by combining:

- a number cycle from `1` to `13`; and
- a cycle of 20 Kʼicheʼ day names.

Because 13 and 20 return to their starting combination every 260 days:

```text
LCM(13, 20) = 260
```

The HTML implementation uses the Kʼicheʼ-oriented identifiers:

```javascript
CHOLQIJ_NAMES
cholqijFromDays(days)
cholqijFull
```

The day names are:

```text
Imox, Iqʼ, Aqʼabʼal, Kʼat, Kan, Keme, Kej, Qʼanil, Toj, Tzʼiʼ,
Bʼatzʼ, E, Aj, Iʼx, Tzʼikin, Ajmaq, Noʼj, Tijax, Kawoq, Ajpuʼ
```

The project uses **Keme**, rather than `Kame`, in the current Kʼicheʼ naming set.

The Gran Wayebʼ adjustment does not alter the Cholqʼij. It continues to advance one position for each actual day.

---

## Standard continuous Haabʼ

Standard mode preserves an uninterrupted 365-day Haabʼ:

```text
18 × 20 + 5 = 365 days
```

The periods are:

```text
Pop, Wo, Sip, Sotzʼ, Sek, Xul, Yaxkʼin, Mol, Chʼen, Yax,
Sak, Keh, Mak, Kʼankʼin, Muwan, Pax, Kʼayab, Kumkʼu, Wayebʼ
```

The first 18 periods contain 20 days each. Wayebʼ contains five days.

With zero-based numbering, the sequence is:

```text
0 Pop ... 19 Pop
0 Wo  ... 19 Wo
...
0 Kumkʼu ... 19 Kumkʼu
0 Wayebʼ ... 4 Wayebʼ
0 Pop
```

The day position is calculated from the Long Count epoch alignment:

```text
haab_index = (HAAB_START_ABS_INDEX + days_since_epoch) mod 365
```

No extra or replacement days are used in standard mode.

---

## Community Gran Wayebʼ adjustment

The HTML also includes a community-informed model based on a count supplied by an **Ajqʼij**.

In this model, a 13-day **Gran Wayebʼ** replaces the regular five-day `0–4 Wayebʼ` at the end of each 52-Haab block. It is not added after a completed five-day Wayebʼ.

The special period is numbered:

```text
0 Gran Wayebʼ
1 Gran Wayebʼ
...
12 Gran Wayebʼ
```

Exactly 13 days numbered from zero therefore run from `0` through `12`.

### Confirmed anchor

The supplied count establishes:

```text
2013-01-02 = 13.0.0.0.12 = 3 E = 0 Gran Wayebʼ = G3
```

The 13-day sequence ends with:

```text
2013-01-14 = 12 Gran Wayebʼ
```

and the next day begins the ordinary Haabʼ at:

```text
2013-01-15 = 0 Pop
```

The preceding boundary dates are:

| Gregorian date | Long Count | Cholqʼij | Community Haabʼ | Night Lord |
|---|---|---|---|---|
| 2012-12-21 | 13.0.0.0.0 | 4 Ajpuʼ | 8 Kumkʼu | G9 |
| 2013-01-01 | 13.0.0.0.11 | 2 Bʼatzʼ | 19 Kumkʼu | G2 |
| 2013-01-02 | 13.0.0.0.12 | 3 E | 0 Gran Wayebʼ | G3 |
| 2013-01-14 | 13.0.0.1.4 | 2 Kʼat | 12 Gran Wayebʼ | G6 |
| 2013-01-15 | 13.0.0.1.5 | 3 Kan | 0 Pop | G7 |

### Cycle length

Because Gran Wayebʼ replaces a regular five-day Wayebʼ, the repeating block is:

```text
(52 × 365) - 5 + 13 = 18,988 days
```

Equivalently, it contains:

```text
51 complete 365-day Haabʼ years
+ 360 days of the 52nd Haabʼ
+ 13 days of Gran Wayebʼ
= 18,988 days
```

This differs from an additive model such as `52 × 365 + 13`. The current code does **not** use that additive model.

The relevant constants are:

```javascript
const GREAT_WAYEB_ANCHOR_YEAR = 2013;
const GREAT_WAYEB_ANCHOR_MONTH = 1;
const GREAT_WAYEB_ANCHOR_DAY_OF_MONTH = 2;
const GREAT_WAYEB_DAYS = 13;
const HAAB_YEARS_PER_GREAT_CYCLE = 52;
const REGULAR_HAAB_DAYS = 365;
const REGULAR_WAYEB_DAYS = 5;

const ORDINARY_DAYS_PER_GREAT_CYCLE =
  HAAB_YEARS_PER_GREAT_CYCLE * REGULAR_HAAB_DAYS
  - REGULAR_WAYEB_DAYS;

const GREAT_WAYEB_CYCLE_DAYS =
  ORDINARY_DAYS_PER_GREAT_CYCLE + GREAT_WAYEB_DAYS;
```

### Applying the rule backward and forward

The program converts the anchor to JDN and calculates:

```text
position = floor_mod(date_JDN - anchor_JDN, 18,988)
```

Floor-modulo keeps the position non-negative, allowing the same rule to be extrapolated backward and forward:

```text
position 0  → 0 Gran Wayebʼ
position 1  → 1 Gran Wayebʼ
...
position 12 → 12 Gran Wayebʼ
position 13 → 0 Pop
```

For ordinary Haabʼ dates after the special period:

```text
regular_position = (position - 13) mod 365
```

The month and day are then derived from that regular position.

### Cultural and interpretive scope

The Community Gran Wayebʼ option represents a **specific community-informed calendrical model**. It is kept separate from the standard continuous Haabʼ so that the interface does not present two different interpretive traditions as though they were the same calculation.

The Ajqʼij also shared an excerpt from:

> *Concepción Maya del Tiempo y sus Ciclos: Texto para Docentes*, by Virginia Ajxup Pelicó, Pedro Eligio Ajxup Poroj, and Juan Zapil Xivir.

The photographed passage describes a 13-day Gran Wayebʼ observed at the completion of each 52-year block. The publication year, publisher, edition, and page number should be added when the full bibliographic information becomes available.

The code extrapolates the supplied rule mathematically. This should not be read as a claim that the model represents every Maya community, language, historical period, or scholarly interpretation.

---

## Why the other counts do not change

The Community Gran Wayebʼ mode changes how a physical date is **labeled within the Haabʼ model**. It does not insert fictional days into JDN or elapsed time.

For a fixed Gregorian date:

| Value | Changes when Haabʼ mode changes? |
|---|---:|
| Gregorian date | No |
| JDN | No |
| Long Count | No |
| Cholqʼij | No |
| Lord of the Night | No |
| Haabʼ designation | Yes |

---

## Haabʼ numbering

The current HTML uses zero-based numbering:

```text
ordinary Haabʼ periods → 0–19
regular Wayebʼ         → 0–4
Gran Wayebʼ            → 0–12
```

This is controlled for the ordinary Haabʼ by:

```javascript
const HAAB_DAY_BASE = 0;
```

Gran Wayebʼ remains `0–12` in the community model because those values are part of the supplied anchor sequence.

---

## Lords of the Night

The Lords of the Night repeat every nine days:

```text
G1, G2, G3, G4, G5, G6, G7, G8, G9
```

The application advances this sequence once per physical day. The selected Haabʼ mode does not alter it.

---

## Browser version

Open `kin.html` directly in a modern browser or serve it through GitHub Pages. The page does not require a build step.

### Gregorian input

Accepted formats include:

```text
2026-12-31
2026.12.31
2026/12/31
```

The required order is:

```text
Year, Month, Day
```

Negative years can be used for BCE dates. Year zero is rejected. The input hint and validation message explain this order in every supported interface language.

### Long Count input

Enter five signed integer components:

```text
Bʼakʼtun.Kʼatun.Tun.Winal.Kin
```

Example:

```text
13.0.13.16.2
```

Negative components are accepted, allowing dates before `0.0.0.0.0`. Components outside their canonical ranges are converted to total elapsed days and normalized automatically. For example:

```text
0.0.0.0.-1  → -1.19.19.17.19
13.0.0.0.-1 → 12.19.19.17.19
```

The converter accepts either dots or whitespace between the five components. The resulting normalized count uses the canonical ranges:

```text
Kʼatun: 0–19
Tun:    0–19
Winal:  0–17
Kin:    0–19
```

Unlike the Python command-line programʼs optional `--strict-lc` mode, the browser always normalizes valid signed integer input.

### Extended display setting

Open **Haabʼ calculation settings** and select **Show the Extended Long Count** to display:

```text
Alautun.Kʼinchiltun.Kalabtun.Piktun.Bʼakʼtun.Kʼatun.Tun.Winal.Kin
```

The setting updates todayʼs date and any visible conversion immediately. It affects presentation only; it does not alter the JDN or any calendar calculation.

For normalized dates at or beyond `±20 Bʼakʼtun`, extended display is automatic. A translated notice explains why the longer format is being shown.

---

## Multilingual interface

The browser interface currently includes:

- English;
- Spanish;
- Kʼicheʼ;
- Traditional Chinese (Taiwan);
- Japanese;
- Arabic;
- Hindi;
- Bahasa Indonesia;
- Portuguese; and
- Bengali.

The Kʼicheʼ version has been revised independently within the project. Technical calendar names are retained where replacing them would require terminology that has not yet been established for this implementation.

The interface uses **Cholqʼij** as the primary Kʼicheʼ-oriented name, with **Tzolkʼin** included parenthetically in some interface labels for cross-reference. Internal variables and functions likewise use `cholqij` rather than `tzolkin`.

Calendar notations and names such as `13.0.13.16.2`, `Iqʼ`, `Ajpuʼ`, `Keme`, `Kumkʼu`, `Wayebʼ`, and `Gran Wayebʼ` remain calendar terms across interface languages.

The Gregorian input example, Year–Month–Day explanation, signed Long Count guidance, Extended Long Count setting, and automatic-display notice are available in all ten interface languages. Community review and corrections to translations remain welcome.

---

## Python command-line version

### Interactive terminal mode

```bash
python long_count.py
```

When started without a conversion flag, the program opens a terminal interface that:

- asks the user to select the Community Gran Wayebʼ or standard Haabʼ calculation at startup;
- displays todayʼs Maya calendar date automatically;
- accepts Gregorian dates in the same one-line formats as the HTML;
- accepts a five-part Long Count on one line;
- remembers the last displayed date during the session;
- can show that date in Extended Long Count format;
- allows the Haabʼ mode, day-numbering base, and correlation constant to be changed without restarting; and
- recalculates the last displayed date after a setting changes.

In an interactive terminal, navigate with `↑` and `↓`, then press `Enter`. Number keys can select an item directly, and `Q` returns to the preceding menu. When raw-key navigation is unavailable, the program automatically presents an ordinary numbered menu instead.

The interactive interface uses only the Python standard library; it does not require an additional menu package.

### Convert from Gregorian

```bash
python long_count.py --from-gregorian 2026 1 22
```

### Convert from Long Count

```bash
python long_count.py --from-lc 13 0 0 0 0
```

### Select a correlation

```bash
python long_count.py --corr 584283 --from-gregorian 2012 12 21
```

### Select the Haabʼ mode

Community Gran Wayebʼ mode is the default, matching the browser application:

```bash
python long_count.py --haab-mode great --from-gregorian 2012 12 21
```

Use the uninterrupted 365-day Haabʼ with:

```bash
python long_count.py --haab-mode standard --from-gregorian 2012 12 21
```

### Strict Long Count input

```bash
python long_count.py --from-lc 13 0 0 0 0 --strict-lc
```

Under the existing command-line design, normal mode can normalize out-of-range components, while `--strict-lc` enforces canonical component ranges. Run the following command for the options supported by the version on your system:

```bash
python long_count.py --help
```

### Engine differences between Python and HTML

The two implementations now share the principal conversion behavior, including signed five-part Long Count input, automatic normalization, Extended Long Count output, and the two Haabʼ modes. Some deliberate differences remain:

- Python integers have arbitrary precision, while the browser implementation uses JavaScript safe integers.
- Python provides optional strict Long Count validation through `--strict-lc`; the HTML normalizes input automatically.
- Python can change the correlation constant and Haabʼ day-numbering base at runtime; the HTML keeps GMT JDN `584283` and zero-based Haabʼ numbering fixed.
- The terminal and browser interfaces are intentionally different. The browser prioritizes a compact graphical presentation, while Python provides keyboard-driven menus and command-line flags.

---

## Mathematical principles

The implementation relies on:

1. **Absolute day counting:** Gregorian dates and Long Count dates are connected through JDN.
2. **Mixed-radix representation:** elapsed days are divided into Long Count units.
3. **Modular arithmetic:** the 20-name, 13-number, 365-day, 9-day, and 18,988-day cycles wrap to their starting positions.
4. **Independent counts:** Long Count, Cholqʼij, Haabʼ, and the Lords of the Night advance according to their own rules.
5. **Selectable Haabʼ interpretations:** the browser can preserve the standard 365-day model or display the community-informed Gran Wayebʼ model.

---

## Current implementation summary

- Haabʼ numbering is zero-based.
- The standard Haabʼ remains a continuous 365-day cycle.
- Community Gran Wayebʼ mode is the default browser setting.
- Community Gran Wayebʼ mode is also the default Python setting and can be changed with `--haab-mode standard`.
- Gran Wayebʼ replaces the final regular five-day Wayebʼ of each 52-Haab block.
- Gran Wayebʼ contains 13 days numbered `0–12`.
- The confirmed anchor is `2013-01-02 = 0 Gran Wayebʼ`.
- The complete community-adjusted cycle is 18,988 days.
- The rule is extrapolated backward and forward with floor-modulo arithmetic.
- The 2012 boundary sequence runs from `8 Kumkʼu` through `19 Kumkʼu`, followed by `0–12 Gran Wayebʼ`, then `0 Pop`.
- The standard result for `13.0.0.0.0` is `4 Ajpuʼ, 3 Kʼankʼin`.
- Internal 260-day-cycle identifiers use `cholqij` terminology.
- The Kʼicheʼ day name is `Keme`.
- The HTML supports bidirectional Gregorian/Long Count conversion.
- Gregorian guidance uses `2026-12-31` to make the Year–Month–Day order explicit in every interface language.
- The HTML accepts negative and noncanonical five-part Long Count input and normalizes it automatically.
- The HTML provides optional Extended Long Count output and activates it automatically at `±20 Bʼakʼtun` and beyond.
- The Mayan-numeral display expands to include higher Long Count positions when extended output is active.
- Unicode Mayan numerals are arranged in two columns and read row by row in zig-zag order.
- `NotoSansMayanNumerals-Regular.woff2` is hosted locally under `assets/fonts/`.
- The browser interface supports ten languages and right-to-left layout for Arabic.

---

## License

See the repositoryʼs main license file for the terms that apply to the projectʼs source code.

The locally hosted **Noto Sans Mayan Numerals** font is distributed under the SIL Open Font License. Its license text is included separately at:

```text
assets/fonts/OFL.txt
```

The font license does not replace or modify the license applied to the projectʼs own source code.
