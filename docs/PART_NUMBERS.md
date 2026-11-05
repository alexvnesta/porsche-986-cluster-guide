# Porsche 986 / 996 Instrument Cluster Part Numbers, DSNs & Variants

This guide documents the complete part-number structure, factory option codes, **Datensatznummern (DSNs)**, display hardware generations, and swap compatibility across all 1997–2004 Porsche 986 Boxster and 1998–2005 Porsche 996 911 VDO instrument clusters.

---

## 1. Part Number Decoder (`986.641.xxx.xx` & `996.641.xxx.xx`)

Unlike early community guides that listed only `996.641.xxx.xx` numbers, **Porsche 986 Boxster clusters carry `986.641.xxx.xx` part numbers** (stored in BCD at EEPROM offset `0x01D–0x022` on late clusters and reported via KWP2000 `1A 9E`), while **996 Carrera / Turbo / GT2 / GT3 clusters carry `996.641.xxx.xx` part numbers**.

### Structure: `PPP . 641 . GTM . RR [Color]`

| Segment | Meaning | Values & Rules |
|---|---|---|
| **`PPP`** | **Vehicle Platform** | • `986` = Boxster / Boxster S (3-dial cluster)<br>• `996` = 911 Carrera / C4 / C4S / Turbo / GT2 / GT3 (5-dial cluster) |
| **`641`** | **Main Group / Subgroup** | `6` (Electrical Equipment) → `41` (Instruments / Kombiinstrument) |
| **`G`** (1st digit of `GTM`) | **Hardware Generation** | • `1xx` = **Early Generation (MY1997–2000 986 / MY1998–2000 996)**: 3×26-pin connectors (Blue/White/Black), **93C56B** (256-byte) EEPROM, discrete analog/pulse wiring (no CAN bus).<br>• `2xx` = **Late Generation ("Kombi 2000", MY2001–2004 986 / MY2001–2005 996)**: 3×32-pin connectors (Green/Blue/Grey), **93C86** (2048-byte) EEPROM, 500 kbps CAN bus + K-line.<br>• `98x` = **Exclusive / Painted Dial Face Variants** (`IX45` interior-color dials, `IX71` aluminum dials, leather trim). |
| **`T`** (2nd digit of `GTM`) | **Engine / Model Tier & Sub-Generation** | **On `1xx` (Early):**<br>• `10x` = 986 Boxster 2.5L / 2.7L (MY1997–2000, 250 km/h / 160 mph scale)<br>• `11x` = 986 Boxster S 3.2L (`M008`, MY2000, 280 km/h / 180 mph scale)<br>**On `2xx` (Late "Kombi 2000"):**<br>• `20x` = MY2001 Boxster 2.7L (DSN `K21`, 250 km/h / 160 mph scale)<br>• `21x` = MY2001 Boxster S 3.2L (`M008`, DSN `K21`, 280 km/h / 180 mph scale)<br>• `22x` = MY2002–2004 Boxster 2.7L (DSN `K24` / `K26`, with `M659` OBC)<br>• `23x` = MY2002–2004 Boxster S 3.2L (`M008`, DSN `K24` / `K26`, with `M659` OBC)<br>• `24x` = MY2004 Boxster S "550 Spyder" Anniversary (`M091`) |
| **`M`** (3rd digit of `GTM`) | **Market Scale & Transmission Parity** | **Odd vs. Even (Transmission):**<br>• **Odd (`5`, `7`)** = **Manual Transmission** (`M481` 5-speed / `M480` 6-speed)<br>• **Even (`6`, `8`)** = **Tiptronic S Automatic** (`M249`, includes PRNDM gear matrix)<br>**`5/6` vs. `7/8` (Speedometer Dial Scale):**<br>• **`x05` / `x15` / `x25` / `x35`** = **km/h Dial** + **Manual** (RDW / Europe / RoW)<br>• **`x06` / `x16` / `x26` / `x36`** = **km/h Dial** + **Tiptronic** (RDW / Europe / RoW)<br>• **`x07` / `x17` / `x27` / `x37`** = **MPH Dial** + **Manual** (UK `GB` / USA)<br>• **`x08` / `x18` / `x28` / `x38`** = **MPH Dial** + **Tiptronic** (UK `GB` / USA) |
| **`RR`** | **Revision / Trim Suffix** | • `.00` = Base hardware part number reported in EEPROM (`0x01D`) and KWP2000 (`1A 9E`)<br>• `.01` – `.08` = Catalog supersession and dial bezel/face finish (`70C` rally black, `EOD`/`FHB` black/silver for Boxster S, `EMS` metal grey/black, `EMR`/`EBN` ocean jade / zenith blue) |

### Examples Decoded
* **`986.641.217.00`** (Catalog `986 641 217 03`):
  * `986` (Boxster) · `641` (Cluster) · `2` (MY2001+ 93C86) · `1` (MY2001 Boxster S `M008`) · `7` (MPH Dial + Manual 6-speed `M480`) · `.00` (Hardware base; `.03` black/silver Boxster S face).
* **`986.641.237.00`** (Catalog `986 641 237 02`):
  * `986` (Boxster) · `641` (Cluster) · `2` (MY2001+ 93C86) · `3` (MY2002–2004 Boxster S `M008`) · `7` (MPH Dial + Manual 6-speed `M480`) · `.00` (Hardware base).
* **`996.641.227.00`**:
  * `996` (911 Carrera) · `641` (Cluster) · `2` (MY2001+ 93C86) · `2` (MY2002 Carrera) · `7` (MPH Dial + Manual 6-speed) · `.00`.

---

## 2. Dataset Numbers (`DSN` / `Datensatznummer`) Explained

On all Porsche 986/996 clusters, the internal firmware/parameter revision is identified by a **Dataset Number (`DSN` / `Datensatznummer`)**:
* Stored in the 93C86 EEPROM at **offset `0x0023`** (as a 1-byte unsigned integer, e.g., `0x15` = decimal `21` = **`K21`**; `0x18` = decimal `24` = **`K24`**; `0x17` = decimal `23` = **`K23`**).
* Queried over KWP2000 (`0x64`) via service **`1A 9F`** (`ReadEcuIdentification` → `5A 9F <DSN>`).

### Complete 9x6 Cluster DSN Matrix

| DSN (Hex at `0x023`) | Generation / Family | EEPROM & Connectors | Vehicle & Model Year Application | Diagnostic / Hardware Notes |
|---|---|---|---|---|
| **`K02`, `K03`, `K04`** | Early (`9x6_Kombi` `01`–`04`, `03n`) | 93C56B (256 B)<br>3×26-pin (Blue/White/Black) | MY1997–1999 986 Boxster & MY1998–1999 996 Carrera | No CAN bus; no onboard DTC fault memory (`18` not supported). Sub-variant `03n` supports `23 30 00 xx 10` 256-byte EEPROM read. |
| **`K06`–`K09`, `K14`, `K15`** | Early (`9x6_Kombi` `06`–`11`) | 93C56B (256 B)<br>3×26-pin | Early regional & MY1999–2000 revisions | Same 256-byte 93C56B architecture. |
| **`K16`** | Transitional (`9x6_Kombi_05`) | 93C56B (256 B)<br>3×26-pin | MY2000 986 Boxster / Boxster S (`105.05`–`118.00`) | First E-Gas (ME7.2) year on 986, but cluster still uses 3×26-pin discrete harness + 93C56B. |
| **`K20`** | Late (`9x6_Kombi_2000_02`) | 93C86 (2048 B)<br>3×32-pin (Green/Blue/Grey) | MY2001 996 Carrera | First 93C86 + CAN bus cluster on 996 (`K-Zahl` RDW = 23,400). |
| **`K21` (`0x15`)** | Late (`9x6_Kombi_2000_02`) | 93C86 (2048 B)<br>3×32-pin (Green/Blue/Grey) | **MY2001 986 Boxster & Boxster S** (`205.06`–`218.03`) | First 93C86 + 500 kbps CAN bus cluster on 986 (`K-Zahl` RDW = 23,802). 3-window segmented LCD. Full KWP2000 DTCs (`18 FF FF 01/02`), Event Memory (`21 30`), and `0x23` read at `0x080000`. |
| **`K22`, `K23` (`0x16`, `0x17`)** | Late (`9x6_Kombi_2000_01`) | 93C86 (2048 B)<br>3×32-pin (Green/Blue/Grey) | MY2001–2002 996 Turbo / GT2 & MY2002 996 Carrera (`996.641.227.00`) | Supports boost pressure gauge (`Byte 2 bit 5 = 0x20` on Turbo/GT2). |
| **`K24` (`0x18`)** | Late (`9x6_Kombi_2000_02`) | 93C86 (2048 B)<br>3×32-pin (Green/Blue/Grey) | **MY2002 986 Boxster & Boxster S** (`225.04`–`238.02`) | Direct MY2002 dataset evolution of `K21`. Identical 3-window segmented LCD and pinout. |
| **`K25`, `K255`** | Late (`9x6_Kombi_2000_02`) | 93C86 (2048 B)<br>3×32-pin | MY2002 996 / Service replacement dataset | Shares `Kombi_2000_02` coding structure. |
| **`K26` (`0x1A`)** | Late (`9x6_Kombi_2000_02`) | 93C86 (2048 B)<br>3×32-pin (Green/Blue/Grey) | **MY2003–2004 986 Boxster & Boxster S** | Final 986 Boxster dataset (MOST infotainment era; `PCM_0` bit `Byte 1 bit 2` used whenCDR23/PCM2 fitted). Still uses the 3-window segmented LCD. |
| **`K27`–`K38`** | Late Facelift (`9x6_Kombi_2000_03`) | 93C86 (2048 B)<br>3×32-pin (Green/Blue/Grey) | **MY2002–2005 996 Facelift (Carrera / Turbo / C4S / GT3)** | **5-dial 996 cluster with center Dot-Matrix display.** Adds Tire Pressure Monitoring (`RDK`, DTC `9152`) and expanded unit menus. |
| **`K50` (`0x32`)** | Carrera GT (`9x6_Kombi_2000_GT`) | 93C86 (2048 B)<br>3×32-pin | MY2004–2006 Porsche Carrera GT (980) | Derived from `Kombi_2000` architecture. |

---

## 3. Display Hardware Myth-Busting & `K21` ↔ `K24` / `K26` Interchangeability

### Myth: "Does `K24` or `K26` have a center dot-matrix or LED screen on a 986 Boxster?"
* **Fact:** **No.** Every factory 986 Boxster and Boxster S cluster from MY1997 through MY2004 (`K02` through `K26`) is a **3-dial instrument cluster with three 7-segment/custom-segment LCD windows** (left: clock / outside temp / OBC; center: digital speed / odometer / trip; right: fuel level segments).
* Porsche **never** fitted the 996's center dot-matrix display (`K27–K38`) to a 3-dial 986 cluster. (A 5-dial 996 cluster can be physically retrofitted into a 986 dashboard pod, which is how a dot-matrix screen ends up in a Boxster).
* Third-party tools (such as Durametric) label the entire MY2001–2004 986 cluster family generically as `"Instrument Cluster K21"`, even when the cluster Inside is actually `K24` (MY02) or `K26` (MY03–04).

### Hardware Interchangeability: `K21` (MY01) vs. `K24` (MY02) vs. `K26` (MY03–04)
* **Physical & Electrical Plug-and-Play:** A `K24` cluster (e.g., `986.641.237.00`, VDO `110.080.039/041`) is a **100% direct physical and electrical plug-and-play replacement** for a `K21` cluster (e.g., `986.641.217.00`):
  * Identical 3×32-pin Tyco/AMP connectors (Green Plug A, Blue Plug B, Grey Plug C).
  * Identical 500 kbps Powertrain CAN (`A15`/`A31`) and Comfort CAN (`A14`/`A30`).
  * Identical K-line diagnostics on Green Plug `A28` (OBD Pin 3, address `0x64`).
  * Identical road-speed pulse scaling (`K-Zahl` = `23,802` pulses/km, `FA 5C` at `0x052`).
  * Identical 2048-byte 93C86 EEPROM layout (`0x000–0x7FF`, memory-mapped at `0x080000–0x0807FF`).
  * Identical `Parameterkodierung` (`0x032`), `Menükonfiguration` (`0x03A`), and primary speedometer curve (`0x192`).
* **Important Caveats When Using a `K24` Cluster or Dump as a Reference for `K21`:**
  1. **Never flash a donor cluster's entire 2048-byte EEPROM image wholesale onto your car's cluster:** Doing so overwrites your car's **VIN (`0x000–0x010`)**, **Part Number (`0x01D–0x022`)**, **DSN (`0x023`)**, and **Primary/Backup Odometer blocks (`0x300–0x31F` & `0x500–0x51F`)**, which is both a legal/mileage issue and can cause audio/immobilizer mismatches.
  2. **Field-Level Reference Only:** While `Parameterkodierung` (`0x032–0x039`), `Menükonfiguration` (`0x03A–0x041`), and `Tacho_Kennlinie_1X` (`0x192–0x19B`) share the exact same encoding between `K21` and `K24`, internal VDO tables (such as the secondary curve at `0x184–0x18D` or software version bytes at `0x0E5–0x0E7`, which read `22 05 01` on `K21` vs. `35 48 01` on `K24`) can differ between dataset years. Always restore or modify only the specific configuration records needed.

---

## 4. Complete 986 Boxster & Boxster S Factory Part Number Catalog

### A. Early 986 Clusters (MY1997–2000 — 93C56B 256-Byte EEPROM, 3×26-Pin Connectors)

| Part Number | Model Years | Model & Engine | Trans | Market / Scale | Option Codes & Dial Color |
|---|---|---|---|---|---|
| `986 641 105 01` | 1997–1999 | Boxster 2.5L | 5-spd Manual (`M481`) | EU / RDW (km/h) | `M016` Standard (`70C` rally black) |
| `986 641 105 03` | 1998–1999 | Boxster 2.5L | 5-spd Manual (`M481`) | EU / RDW (km/h) | `M011` (`EMR` ocean jade / `EBN` zenith blue) |
| `986 641 105 04` | 1998–1999 | Boxster 2.5L | 5-spd Manual (`M481`) | EU / RDW (km/h) | `M012` (`EMS` metal grey/black) |
| `986 641 105 05` | 2000 | Boxster 2.7L | 5-spd Manual (`M481`) | EU / RDW (km/h) | `M016` (`70C` rally black, DSN `K16`) |
| `986 641 105 08` | 2000 | Boxster 2.7L | 5-spd Manual (`M481`) | EU / RDW (km/h) | `M012` (`EMS` metal grey/black, DSN `K16`) |
| `986 641 106 01` | 1997–1999 | Boxster 2.5L | Tiptronic (`M249`) | EU / RDW (km/h) | `M016` (`70C` rally black) |
| `986 641 106 03` | 1998–1999 | Boxster 2.5L | Tiptronic (`M249`) | EU / RDW (km/h) | `M011` (`EMR` ocean jade / `EBN` zenith blue) |
| `986 641 106 04` | 1998–1999 | Boxster 2.5L | Tiptronic (`M249`) | EU / RDW (km/h) | `M012` (`EMS` metal grey/black) |
| `986 641 106 05` | 2000 | Boxster 2.7L | Tiptronic (`M249`) | EU / RDW (km/h) | `M016` (`70C` rally black, DSN `K16`) |
| `986 641 106 08` | 2000 | Boxster 2.7L | Tiptronic (`M249`) | EU / RDW (km/h) | `M012` (`EMS` metal grey/black, DSN `K16`) |
| `986 641 107 01` | 1997–1999 | Boxster 2.5L | 5-spd Manual (`M481`) | UK / US (MPH) | `M016` (`70C` rally black, 160 mph dial) |
| `986 641 107 03` | 1998–1999 | Boxster 2.5L | 5-spd Manual (`M481`) | UK / US (MPH) | `M011` (`EMR` / `EBN`) |
| `986 641 107 04` | 1998–1999 | Boxster 2.5L | 5-spd Manual (`M481`) | UK / US (MPH) | `M012` (`EMS` metal grey/black) |
| `986 641 107 05` | 2000 | Boxster 2.7L | 5-spd Manual (`M481`) | UK / US (MPH) | `M016` (`70C` rally black, DSN `K16`) |
| `986 641 107 08` | 2000 | Boxster 2.7L | 5-spd Manual (`M481`) | UK / US (MPH) | `M012` (`EMS` metal grey/black, DSN `K16`) |
| `986 641 108 01` | 1997–1999 | Boxster 2.5L | Tiptronic (`M249`) | UK / US (MPH) | `M016` (`70C` rally black) |
| `986 641 108 03` | 1998–1999 | Boxster 2.5L | Tiptronic (`M249`) | UK / US (MPH) | `M011` (`EMR` / `EBN`) |
| `986 641 108 04` | 1998–1999 | Boxster 2.5L | Tiptronic (`M249`) | UK / US (MPH) | `M012` (`EMS` metal grey/black) |
| `986 641 108 05` | 2000 | Boxster 2.7L | Tiptronic (`M249`) | UK / US (MPH) | `M016` (`70C` rally black, DSN `K16`) |
| `986 641 108 08` | 2000–2001 | Boxster 2.7L | Tiptronic (`M249`) | UK / US (MPH) | `M012` (`EMS` metal grey/black) |
| `986 641 115 00` | 2000 | **Boxster S 3.2L** (`M008`) | 6-spd Manual (`M480`) | EU / RDW (km/h) | `EOD` black/silver, 280 km/h dial (DSN `K16`) |
| `986 641 116 00` | 2000 | **Boxster S 3.2L** (`M008`) | Tiptronic (`M249`) | EU / RDW (km/h) | `EOD` black/silver, 280 km/h dial (DSN `K16`) |
| `986 641 117 00` | 2000 | **Boxster S 3.2L** (`M008`) | 6-spd Manual (`M480`) | UK / US (MPH) | `EOD` black/silver, 180 mph dial (DSN `K16`) |
| `986 641 118 00` | 2000 | **Boxster S 3.2L** (`M008`) | Tiptronic (`M249`) | UK / US (MPH) | `EOD` black/silver, 180 mph dial (DSN `K16`) |

### B. Late 986 "Kombi 2000" Clusters (MY2001–2004 — 93C86 2048-Byte EEPROM, 3×32-Pin Connectors, CAN + K-Line)

| Part Number (EEPROM Base `.00`) | Model Years | DSN | Model & Engine | Trans | Market / Scale | Option Codes & Dial Color |
|---|---|---|---|---|---|---|
| `986 641 205 06` / `.07` | 2001 | `K21` | Boxster 2.7L | 5-spd Manual (`M481`) | EU / RDW (km/h) | `.06` = `70C` rally black; `.07` = `EMS` metal grey |
| `986 641 206 06` / `.07` | 2001 | `K21` | Boxster 2.7L | Tiptronic (`M249`) | EU / RDW (km/h) | `.06` = `70C` rally black; `.07` = `EMS` metal grey |
| `986 641 207 06` / `.07` | 2001 | `K21` | Boxster 2.7L | 5-spd Manual (`M481`) | UK / US (MPH) | `.06` = `70C` rally black; `.07` = `EMS` metal grey (160 mph) |
| `986 641 208 06` / `.07` | 2001 | `K21` | Boxster 2.7L | Tiptronic (`M249`) | UK / US (MPH) | `.06` = `70C` rally black; `.07` = `EMS` metal grey (160 mph) |
| `986 641 215 00` / `.03` | 2001 | `K21` | **Boxster S 3.2L** (`M008`) | 6-spd Manual (`M480`) | EU / RDW (km/h) | `FHB` black/silver (280 km/h scale) |
| `986 641 216 00` / `.03` | 2001 | `K21` | **Boxster S 3.2L** (`M008`) | Tiptronic (`M249`) | EU / RDW (km/h) | `FHB` black/silver (280 km/h scale) |
| **`986 641 217 00`** / `.03` | 2001 | **`K21`** | **Boxster S 3.2L** (`M008`) | 6-spd Manual (`M480`) | **UK / US (MPH)** | `FHB` black/silver (**180 mph / 280 km/h scale**) |
| `986 641 218 00` / `.03` | 2001 | `K21` | **Boxster S 3.2L** (`M008`) | Tiptronic (`M249`) | UK / US (MPH) | `FHB` black/silver (180 mph scale) |
| `986 641 225 04` / `.05` | 2002–2004 | `K24`/`K26` | Boxster 2.7L | 5-spd Manual (`M481`) | EU / RDW (km/h) | `M659` OBC (`.04` `70C` black; `.05` `EMS` grey) |
| `986 641 226 04` / `.05` | 2002–2004 | `K24`/`K26` | Boxster 2.7L | Tiptronic (`M249`) | EU / RDW (km/h) | `M659` OBC (`.04` `70C` black; `.05` `EMS` grey) |
| `986 641 227 04` / `.05` | 2002–2004 | `K24`/`K26` | Boxster 2.7L | 5-spd Manual (`M481`) | UK / US (MPH) | `M659` OBC (`.04` `70C` black; `.05` `EMS` grey) |
| `986 641 228 04` / `.05` | 2002–2004 | `K24`/`K26` | Boxster 2.7L | Tiptronic (`M249`) | UK / US (MPH) | `M659` OBC (`.04` `70C` black; `.05` `EMS` grey) |
| `986 641 235 00` / `.02` | 2002–2004 | `K24`/`K26` | **Boxster S 3.2L** (`M008`) | 6-spd Manual (`M480`) | EU / RDW (km/h) | `M659` OBC, `FHB` black/silver (280 km/h scale) |
| `986 641 236 00` / `.02` | 2002–2004 | `K24`/`K26` | **Boxster S 3.2L** (`M008`) | Tiptronic (`M249`) | EU / RDW (km/h) | `M659` OBC, `FHB` black/silver (280 km/h scale) |
| **`986 641 237 00`** / `.02` | 2002–2004 | **`K24`/`K26`** | **Boxster S 3.2L** (`M008`) | 6-spd Manual (`M480`) | **UK / US (MPH)** | `M659` OBC, `FHB` black/silver (**180 mph scale**) |
| `986 641 238 00` / `.02` | 2002–2004 | `K24`/`K26` | **Boxster S 3.2L** (`M008`) | Tiptronic (`M249`) | UK / US (MPH) | `M659` OBC, `FHB` black/silver (180 mph scale) |
| `986 641 245 00` – `248 00` | 2004 | `K26` | **Boxster S "550 Spyder"** (`M091`) | Manual (`245`/`247`)<br>Tip (`246`/`248`) | km/h (`245`/`246`)<br>MPH (`247`/`248`) | `70C` rally black with chrome bezel rings (`M091`) |
| `986 641 980 xx` – `983 xx` | 2001–2004 | `K21`–`K26` | Exclusive Option Clusters | Manual / Tip | km/h / MPH | `IX71` Aluminum dial face or `IX45` interior-color lacquered dial |

### C. Common 996 Carrera / Turbo / GT3 Clusters (`996.641.xxx.xx`)

| Part Number | Model Years | DSN | Model | Notes |
|---|---|---|---|---|
| `996.641.103.xx` / `105.xx` | 1998–2000 | `K02`–`K16` | 996 Carrera 3.4L (US / EU) | Early 5-dial cluster, 93C56B (256 B), 3×26-pin connectors |
| `996.641.107.xx` / `108.xx` | 1998–2000 | `K02`–`K16` | 996 Carrera 3.4L (MPH) | Frequently used for early 996-into-986 5-dial retrofits |
| `996.641.205.xx` / `207.xx` | 2001 | `K20` | 996 Carrera 3.4L | MY2001 93C86 (2048 B), 3×32-pin, 3-window segmented LCD |
| `996.641.227.00` | 2002 | `K23` | 996 Carrera 2 (UK/US MPH, Manual) | Verified in Geoff Mge reference dump (`09 96 64 12 27 00`, DSN `0x17`) |
| `996.641.603.xx` – `707.xx` | 2002–2005 | `K27`–`K38` | 996.2 Facelift / C4S / Turbo / GT3 | 93C86 (2048 B), 3×32-pin, center dot-matrix display |

---

## 5. Cross-Generation & Cross-Model Swap Matrix

| Source Cluster | Target Vehicle | Physical Fit | Harness Plug Fit | Required Modifications |
|---|---|---|---|---|
| **Early 986 ↔ Early 986** (`1997–2000`) | `1997–2000` 986 | 100% Direct | 100% Direct (3×26-pin) | Copy 93C56B mileage (`0x00–0x0F`), VIN (`0x18–0x28`), and enable OBC (`0x47 = 1F`) if needed. |
| **Early 996 → Early 986** (`1998–2000`) | `1997–2000` 986 | Fits with 996 pod | 100% Direct (3×26-pin) | In 93C56B: set Vehicle Type `0x35–0x36 = 09 86`, PST2 Mode `0x3B = 06`, copy 986 tank calibration, wire oil pressure sender for gauge (`0x49 = 3C`). |
| **Late 986 (`K21`) ↔ Late 986 (`K24`/`K26`)** | `2001–2004` 986 | 100% Direct | 100% Direct (3×32-pin) | **100% hardware interchangeable.** Transfer VIN (`3B 90` or `0x000`), mileage, and verify `Parameterkodierung` (`30 01 08` / `0x032`) & `Menükonfiguration` (`30 01 09` / `0x03A`). |
| **Late 986 2.7L ↔ Late 986 S 3.2L** | `2001–2004` 986 | 100% Direct | 100% Direct (3×32-pin) | Must match **Speedometer Stepper Curve (`21 78 00` / `0x192`)** to the physical dial face (160 mph / 250 km/h base dial vs. 180 mph / 280 km/h Boxster S dial), or needle will read ~15% (+7 mph) off! |
| **Early (`1997–2000`) ↔ Late (`2001–2004`)** | Cross-generation | Physical pod fits | **INCOMPATIBLE** (3×26-pin vs. 3×32-pin) | Requires custom adapter harness AND note that Late clusters expect RPM, coolant temp, and PSM/ABS state over **500 kbps CAN (`A15`/`A31`)**, which pre-2000 DME 5.2.2 cars do not broadcast. |

---

## 6. Comparative Architecture & Empirical Differences: DSN K21 vs. K24

Empirically verified across isolated bench units and live vehicle installation (swapping a `986.641.217.00` DSN `K21` with a `986.641.237.00` DSN `K24` on a 2001 Boxster S):

| Capability / Feature | DSN `K21` (MY2001, `SW 22.05`) | DSN `K24` (MY2002–2004, `SW 25.04`) | Engineering & Architectural Notes |
|---|---|---|---|
| **Harness & Pinout** | 3×32-pin (Green/Blue/Grey) | 3×32-pin (Green/Blue/Grey) | **100% pin-for-pin interchangeable.** Direct drop-in swap. |
| **CAN Bus Protocol** | 500 kbps High-Speed CAN | 500 kbps High-Speed CAN | Communicates identically with DME 7.2 (`0x11`), ABS 5.3 (`0x1F`), and PSM 5.7 (`0x18`). |
| **Driver Unit Selection** | Fixed via EEPROM Coding | **Driver-Selectable in Menu** | On K24, the driver can toggle units (miles/km, °C/°F, MPG US/MPG UK/l/100km) directly via the OBC stalk. On K21, units are fixed via EEPROM `0x03C`. |
| **Dynamic Text Injection (`31 06 03`)** | ❌ **Rejected (`7F 31 10`)** | ✅ **Supported (`71 06`)** | K24 firmware implements diagnostic routine `31 06 03` (`Textausgabe`) for dynamic center display telemetry injection. K21 uses fixed mask-ROM strings. |
| **Diagnostic Services** | Full KWP2000 (`0x64`) | Full KWP2000 (`0x64`) | Identical service support: `1A` Identification, `18` DTCs, `21` Local Identifiers, `23` Memory Read, and `31` Actuators. |
| **EEPROM Architecture** | Microchip 93C86 (2048 B) | Microchip 93C86 (2048 B) | 100% shared calibration structures: tank curves X/Y/Z, stepper curves, K-Zahl, tell-tale bits, and dual-buffer odometer mapping. |

