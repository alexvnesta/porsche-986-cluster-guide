# Cluster Diagnostics & KWP2000 Protocol Reference

Complete troubleshooting guide and ISO 14230 (KWP2000) diagnostic protocol specification for the Porsche 986 Boxster and 996 911 instrument cluster (`Kombiinstrument`, K-line target address `0x64`).

---

## 1. Built-In On-Car Diagnostic Modes (No Tools Required)

### 1.1 Instrument Cluster Self-Test Mode
The 986/996 cluster includes a built-in gauge and LCD self-test:
1. Turn ignition to **Position 1 / 2** (accessories on, engine off).
2. Press and hold the **left-hand trip odometer reset knob** on the cluster bezel.
3. Turn ignition to **Run** (do not start engine) while continuing to hold the button for ~5–10 seconds.
4. **Behavior:** All analog stepper gauges sweep from minimum to maximum, warning indicators illuminate, and the LCD panels run a segment check.

### 1.2 Climatronic Hidden Digital Speedometer (`Channel 20c`)
On vehicles equipped with automatic climate control (`Climatronic`), you can read the raw road speed pulse signal (`Speedo A` output from cluster `Plug B Pin 13` / `Plug I Pin 13`) in real time to verify whether a speedometer error is caused by the wheel-speed sensor/`K-Zahl` or by the cluster's analog stepper curve (`0x192–0x19B`):
1. With ignition ON, press and hold the **Recirculation (`Umluft`)** button on the A/C panel, then press the **Upper Air Vent (`↑`)** button.
2. `1c` appears on the display. Use the **Temperature `+` / `-`** buttons to scroll to **`20c`**.
3. Press the **A/C (`Snowflake`)** or **Recirculation** button to display the live vehicle speed in **`km/h`** (actual un-buffered road speed without the cluster's analog needle over-read).

---

## 2. KWP2000 Diagnostic Protocol Specification (`Target 0x64`)

Both Early (`93C56B`, `DSN K02–K17`) and Late (`93C86`, `DSN K20–K50`) 986/996 instrument clusters communicate over **KWP2000 (ISO 14230)** on **OBD-II Pin 3**.

### 2.1 Physical Layer & Session Timing

| Parameter | Value | Notes |
|---|---|---|
| **OBD-II Port Pin** | **Pin 3** (`0.35 OR/BL`, Splice `VS 90`) | **Not Pin 7!** Standard OBD-II cables wired only to Pin 7 must bridge or switch Pin 7 → Pin 3 |
| **Cluster Connector Pin** | **Late (`Kombi 2000`):** `Plug A (Green) Pin 28`<br>**Early (MY97–00):** `Plug I (Blue) Pin 21` | Direct K-line connection for bench harnesses |
| **Baud Rate** | **10,400 baud** (`8N1`) | Standard KWP2000 bit rate |
| **ECU Target Address** | **`0x64`** | Instrument Cluster (`Kombiinstrument`) |
| **Tester Source Address** | **`0xF1`** | Diagnostic tool |
| **Initialization** | **Fast Init** (25 ms Low break, 25 ms High idle) |Followed immediately by `StartCommunication` (`81 64 F1 81 57`) |
| **Frame Format** | `[0x80 + DataLen] [0x64] [0xF1] [Data...] [CS]` | Physical addressing with length in header (`1..63` bytes); `CS = sum(all preceding bytes) & 0xFF` |
| **Keep-Alive (`TesterPresent`)** | `81 64 F1 3E 14` → `81 F1 64 7E 54` | Send every `1.5 – 2.0 s` during idle periods (`P3max = 5.0 s`) |
| **Stop Communication** | `81 64 F1 82 58` → `81 F1 64 C2 98` | Cleanly closes the diagnostic session |

#### Fast Init Handshake Example
```text
[25 ms K-Line LOW + 25 ms K-Line HIGH]
TX: 81 64 F1 81 57          (StartCommunication)
RX: 83 F1 64 C1 E9 8F BD    (Positive Response, KeyBytes = E9 8F)
```

---

## 3. ECU Identification (`Service 0x1A`)

| Request | Positive Response | Length | Description & Decoding |
|---|---|---|---|
| `1A 80` | `5A 80 <20 bytes>` | 20 B | **Full VDO / Porsche Hardware & Software Identification Block** (supported on both Early `93C56B` and Late `93C86`) |
| `1A 90` | `5A 90 <17 bytes>` | 17 B | **VIN (`Fahrgestellnummer`):** 17-byte ASCII string from EEPROM `0x000–0x010` (e.g., `WP0ZZZ98Z1S6XXXXX`) |
| `1A 91` | `5A 91 <12 bytes>` | 12 B | Hardware / Blank number metadata |
| `1A 92` | `5A 92 <10 bytes>` | 10 B | Supplier / VDO hardware ID (`0x011–0x01A`) |
| `1A 93` | `5A 93 <3 bytes>` | 3 B | **Software / Dataset Version Index** from EEPROM `0x0E5–0x0E7` (e.g., `22 05 01` on `K21`, `35 48 01` on `K24`, `18 48 01` on `K23`) |
| `1A 94` | `5A 94 <4 bytes>` | 4 B | Internal calibration ID |
| `1A 95` | `5A 95 <6 bytes>` | 6 B | **VDO Production Timestamp #1** (6-byte BCD `DD MM YY HH MM SS` from `0x0D4–0x0D9`) |
| `1A 98` | `5A 98 <6 bytes>` | 6 B | Tester / Workshop Code (`WSC`) |
| `1A 99` | `5A 99 <6 bytes>` | 6 B | **VDO Production Timestamp #2** (6-byte BCD `DD MM YY HH MM SS` from `0x0DA–0x0DF`) |
| `1A 9A` | `5A 9A <6 bytes>` | 6 B | **VDO End-of-Line Timestamp #3** (6-byte BCD `DD MM YY HH MM SS` from `0x0F0–0x0F5`) |
| `1A 9E` | `5A 9E <6 bytes>` | 6 B | **Porsche Part Number (BCD)** from `0x01D–0x022`: e.g., `09 86 64 12 17 00` → **`986.641.217.00`** |
| `1A 9F` | `5A 9F <1 or 3 bytes>` | 1–3 B | **Dataset Number (`DSN`)** from `0x023`: first byte `0x15` = **K21**, `0x17` = **K23**, `0x18` = **K24**, `0x1A` = **K26** (`"K" + str(byte[0])`) |

---

## 4. Fault Memory (`DTCs`) & Freeze Frames (`Services 0x18, 0x17, 0x14`)

### 4.1 Reading Stored Fault Codes (`Service 0x18`)
Unlike standard engine ECUs that accept `18 00 FF 00`, the 986/996 VDO cluster requires the **status mask byte to be `0xFF`** and queries fault memory in two diagnostic groups (`0xFF01` and `0xFF02`):

| Command | Request Hex | Response Format | Notes |
|---|---|---|---|
| **Read Primary DTCs** | `18 FF FF 01` | `58 <Count> [<DTC_Hi> <DTC_Lo> <Status>]...` | Primary internal & sensor fault group |
| **Read Secondary / CAN DTCs** | `18 FF FF 02` | `58 <Count> [<DTC_Hi> <DTC_Lo> <Status>]...` | Secondary / CAN bus fault group (`K20+`) |
| **Read All DTCs** | `18 FF FF 00` | `58 <Count> [<DTC_Hi> <DTC_Lo> <Status>]...` | Combined read (`status_mask` **must** be `0xFF`; `18 00 FF 00` returns `7F 18 12` *subFunctionNotSupported*) |
| **Read Freeze Frame** | `17 <DTC_Hi> <DTC_Lo>` | `57 <9 bytes>` | Reads the environmental snapshot for a specific 16-bit DTC |
| **Clear Fault Memory** | `14 FF 00` | `54 FF 00` | Clears all stored DTCs in `0x600–0x643` |

#### Freeze Frame (`Service 0x17`) 9-Byte Response Layout
When `17 <DTC_Hi> <DTC_Lo>` returns `57 b0 b1 b2 b3 b4 b5 b6 b7 b8`:
- `b0..b1`: DTC code (`uint16 BE`)
- `b2`: Fault status byte (Bit 7 `0x80` = MIL/Warning active, Bit 6–5 = Sporadic/Present state, Bits 0–4 = Fault type code)
- `b3`: Fault occurrence counter (`uint8`)
- `b4..b5`: Odometer stamp (`uint16 BE`, in `10 km` or `1 km` units)

### 4.2 Complete 986/996 Instrument Cluster Fault Code Table (`DTCs`)

| DTC (Hex) | Decimal | Fault Description (English) | Factory German Text (`Klartext`) | Common Cause / Pin Reference |
|---|---|---|---|---|
| **`5555`** | `21845` | **CAN Bus Timeout — ABS / PSM Control Unit** | *CAN-Timeout ABS / PSM* | PSM bit (`0x032` bit 4 `0x10`) coded ON in a car without PSM (ABS 5.3), or CAN Antrieb fault (`A15/A31`) |
| **`9101`** | `37121` | **Engine Speed (RPM) Signal** | *Drehzahlsignal* | Missing `TN-Signal` (`II/15` on Early) or DME CAN timeout (`A15/A31` on Late) |
| **`9102`** | `37122` | **Coolant Temperature Sensor** | *Kühlmitteltemperaturgeber* | Open/short on `Plug B Pin 19` (`Early: II/20`) |
| **`9103`** | `37123` | **Fuel Level Sensor** | *Tankgeber* | Open/short on `Plug B Pins 4 & 20` (`Early: II/3 & II/4`; normal range `13.6–94.2 Ω`) |
| **`9104`** | `37124` | **Fuel Consumption Signal (`KVA`)** | *Kraftstoffverbrauchssignal* | DME injection pulse signal (`Early: II/13`, Late: CAN Antrieb) |
| **`9110`** | `37136` | **Display / Instrument Cluster Internal Fault** | *Anzeige defekt / Steuergerät defekt* | Internal EEPROM checksum error or stepper driver fault |
| **`9111`** | `37137` | **Oil Pressure Sender** | *Öldruckgeber* | Open/short on `Plug B Pin 3` (`Early: II/10`, 5-gauge 996 clusters) |
| **`9112`** | `37138` | **Outside Temperature Sensor** | *Außentemperaturfühler* | Open/short on `Plug B Pins 1 & 17` (`Early: III/5 & III/6`) |
| **`9113`** | `37139` | **Engine Oil Level Sensor** | *Ölstandsgeber* | Open/short on `Plug B Pins 2 & 18` (`Early: I/7 & I/20`) |
| **`9114`** | `37140` | **Speedometer Output Signal (`Speedo A`)** | *Geschwindigkeitssignal Ausgang* | Short to ground/B+ on `Plug B Pin 13` (`Early: I/13` to radio/spoiler/climate) |
| **`9115`** | `37141` | **Road Speed Input Signal** | *Geschwindigkeitssignal Eingang* | Missing ABS wheel speed pulse (`Plug B Pin 14` / `II/16` or CAN) |
| **`9116`** | `37142` | **Engine Oil Temperature Sensor** | *Öltemperaturgeber* | Sensor signal via DME / CAN |
| **`9117`** | `37143` | **Alternator / Generator Terminal `D+` (`Kl. 61`)** | *Generator Klemme D+ / 61* | Charging indicator circuit (`Plug A Pin 22` / `Early: III/15`) |
| **`9118`** | `37144` | **Brake Fluid Level Warning Contact** | *Bremsflüssigkeitsstand* | Sensor input (`Plug B Pin 29` / `Early: II/9`) |
| **`9119`** | `37145` | **Brake Pad Wear Sensor** | *Bremsbelagverschleiß* | Pad wear loop (`Plug A Pin 8` / `Early: II/7`) |
| **`9120`** | `37152` | **Coolant Level Warning Sensor** | *Kühlmittelstand* | Expansion tank float switch (`Plug B Pin 15` / `Early: II/21`) |
| **`9121`** | `37153` | **Washer Fluid Level Sensor** | *Waschwasserstand* | Reservoir switch (`Plug B Pin 31` / `Early: I/12`) |
| **`9130`** | `37168` | **Rear Spoiler Control / Feedback** | *Heckspoilersteuerung* | Spoiler switch/module circuit (`Plug A Pins 9, 10, 26, 27`) |
| **`9131`** | `37169` | **Convertible Top / Roll-Over Bar Warning** | *Verdeck / Überrollbügel* | Soft-top or roll-bar warning input (`Plug A Pin 6` / `Plug B Pin 26`) |
| **`9132`** | `37170` | **Airbag Warning Lamp Circuit** | *Airbag-Warnleuchte* | Fault on `Plug B Pin 25` (`Early: III/14`) or `0x036` driver disabled |
| **`9133`** | `37171` | **Seatbelt Buckle Contact** | *Gurtschlosskontakt* | Seatbelt switch (`Plug B Pin 23` / `Early: III/9`) |
| **`9140`** | `37184` | **CAN Bus — Powertrain (`CAN Antrieb`) Off / Fault** | *CAN-Bus Antrieb gestört* | Twisted pair `Plug A Pin 15 (High)` & `Pin 31 (Low)` open/shorted |
| **`9141`** | `37185` | **CAN Bus Timeout — DME (Engine Control Unit)** | *CAN-Timeout DME* | No CAN frames from DME (`ME7.2` / `ME7.8`) on `A15/A31` |
| **`9142`** | `37186` | **CAN Bus Timeout — Tiptronic Transmission (`EGS`)** | *CAN-Timeout Getriebe* | Coded for Tiptronic without EGS on CAN, or EGS offline |
| **`9143`** | `37187` | **CAN Bus Timeout — Climate Control / Comfort** | *CAN-Timeout Klima / Komfort* | Comfort CAN (`Plug A Pins 14 & 30`) |
| **`9150`** | `37200` | **Terminal 58d Dimmer Output Short Circuit** | *Klemme 58d Kurzschluss* | Instrument illumination PWM output (`Plug A Pin 13` / `II/19`) |
| **`9151`** | `37201` | **Photocell (Ambient Light Sensor) Fault** | *Fototransistor unplausibel* | Internal bezel light sensor (`21 02` byte 10) |
| **`9152`** | `37202` | **Key / Immobilizer Transponder Communication** | *Schlüsselkennung / Wegfahrsperre* | Key-specific menu memory index |

---

## 5. Event Memory (`Ereignisspeicher` — Late `93C86` Clusters)

Separate from the DTC fault memory, late clusters (`DSN K20+`) maintain a 12-flag **Event Memory** at EEPROM `0x6F4–0x6F5` (active bitmask) and `0x644–0x65B` (odometer history):

| Operation | Request Hex | Positive Response | Description |
|---|---|---|---|
| **Read Event Bitmask** | `21 30` | `61 30 <Byte0> <Byte1>` | Reads the 2-byte (`12-bit`) active event mask from `0x6F4–0x6F5` |
| **Read Event Odometer #`n`** | `21 31 <00..0B>` | `61 31 <00..0B> <Hi> <Lo>` | Reads the 2-byte odometer stamp for event `0x00` through `0x0B` (`0x644–0x65B`) |
| **Clear Event Memory** | `31 30` | `71 30` | Resets all 12 event flags (`0x6F4–0x6F5 = 00 00`) and clears event history |

#### Event Memory Bitmask (`21 30` → `61 30 <Byte0> <Byte1>`)

| Index (`21 31 xx`) | Byte & Bit in `21 30` | Warning Event |
|---|---|---|
| `0x00` | Byte 0, Bit 0 (`0x01`) | Brake fluid level warning (`Bremsflüssigkeitsstand`) |
| `0x01` | Byte 0, Bit 1 (`0x02`) | Brake pad wear warning (`Bremsbelagverschleiß`) |
| `0x02` | Byte 0, Bit 2 (`0x04`) | Coolant level warning (`Kühlmittelstand`) |
| `0x03` | Byte 0, Bit 3 (`0x08`) | Coolant over-temperature warning (`Kühlmitteltemperatur zu hoch`) |
| `0x04` | Byte 0, Bit 4 (`0x10`) | Oil pressure warning (`Öldruck`) |
| `0x05` | Byte 0, Bit 5 (`0x20`) | Oil level warning (`Ölstand`) |
| `0x06` | Byte 0, Bit 6 (`0x40`) | Roll-over bar warning (`Überrollbügel`) |
| `0x07` | Byte 0, Bit 7 (`0x80`) | Airbag (`SRS`) warning (`Airbag`) |
| `0x08` | Byte 1, Bit 0 (`0x01`) | Check Engine (`MIL`) lamp triggered (`Check-Engine`) |
| `0x09` | Byte 1, Bit 1 (`0x02`) | ABD / TC / PSM warning (`ABD / TC / PSM`) |
| `0x0A` | Byte 1, Bit 2 (`0x04`) | Brake booster warning (`Bremskraftverstärker`) |
| `0x0B` | Byte 1, Bit 3 (`0x08`) | Engine compartment blower warning (`Motorraumgebläse`) |

---

## 6. Live Measured Values (`Service 0x21` — `ReadDataByLocalIdentifier`)

### 6.1 Late Style (`93C86`, `DSN K20–K50`) Live Data Blocks

| Service | Response Header | Payload Size | Parameter Layout & Physical Scaling |
|---|---|---|---|
| **`21 01`** | `61 01` | **6 bytes** (`d0..d5`) | **Digital Inputs, Warning Switches & Terminal Status:**<br>• `d0`: Bit 0 = Terminal 15 (Ignition), Bit 1 = Terminal 86S (Key in lock), Bit 2 = Driver door contact, Bit 3 = Seatbelt buckle, Bit 4 = Handbrake switch (`B22`), Bit 5 = Brake fluid switch (`B29`), Bit 6 = Brake pad wear (`A8`), Bit 7 = Washer fluid switch (`B31`)<br>• `d1`: Bit 0 = Coolant level switch (`B15`), Bit 1 = Oil pressure switch (`B3`), Bit 2 = Alternator `D+` (`A22`), Bit 3 = Airbag lamp input (`B25`), Bit 4 = High beam (`A20`), Bit 5 = Turn Left (`A21`), Bit 6 = Turn Right (`A5`), Bit 7 = Rear fog (`B10`)<br>• `d2`: OBC stalk inputs (`C21–C24`: Bit 0 = Forward/Select, Bit 1 = Back/Escape, Bit 2 = Up, Bit 3 = Down) & Bezel knobs (Bit 4 = Left knob push, Bit 5 = Right knob push, Bit 6–7 = Right knob twist)<br>• `d3`: Spoiler & Convertible top switches (`A6`, `A10`, `A26`, `A27`)<br>• `d4..d5`: Tiptronic gear / button states & internal status flags |
| **`21 02`** | `61 02` | **11 bytes** (`d0..d10`) | **Analog Sensor Inputs (Battery, Temps, Oil Level, Fuel Sender, Dimming):**<br>• `d0`: **Battery Voltage (Terminal 30):** `V = d0 × 0.1 V` (e.g., `0x7A = 122 → 12.2 V`)<br>• `d1`: **Coolant Temperature:** `T = (d1 × 0.75) - 48 °C` (or raw ADC `0x00` when sensor open)<br>• `d2..d3`: **Outside Temperature ADC / Filtered:** `T = (d2 × 0.5) - 40 °C`<br>• `d4..d5`: **Engine Oil Level Sensor (`uint16 BE`):** Raw thermal-pulse timing value (`0x0084–0x011A`)<br>• `d6..d7`: **Fuel Level Sender Resistance (`uint16 BE`):** `R = value × 0.1 Ω` (e.g., `0x03AE = 942 → 94.2 Ω` Empty; `0x0088 = 136 → 13.6 Ω` Full; `0xFFFF` = Open circuit on `B4/B20`)<br>• `d8`: **Filtered Fuel Volume (Liters):** `L = d8 × 1.0 L` (`0..64 L`)<br>• `d9`: **Instrument Dimmer Rheostat (`Kl. 58d`):** `0..100 %`<br>• `d10`: **Ambient Light Photocell ADC:** `0x00–0xFF` (e.g., `0x64` in room light) |
| **`21 10`** | `61 10` | **3 bytes** (`d0..d2`) | **Total Odometer Reading (`Gesamtwegstrecke`):**<br>• 24-bit unsigned integer (`(d0 << 16) \| (d1 << 8) \| d2`) in **kilometers (`km`)**.<br>• Divide by `1.609344` for miles (e.g., `02 36 B9` = `145,081 km` = **`90,149 miles`**). |
| **`21 40`** | `61 40` | **5 bytes** (`d0..d4`) | **Powertrain Live Values:**<br>• `d0..d1`: Engine Speed (`RPM = uint16_BE / 4` or direct RPM)<br>• `d2`: Vehicle Speed (`km/h`)<br>• `d3`: Coolant Temperature<br>• `d4`: Oil Pressure / Status |
| **`21 70`** | `61 70` | **2 bytes** | **`K-Zahl` (`uint16 LE` at `0x052–0x053`):** `FA 5C` = `23,802 Imp./km` |
| **`21 71`** | `61 71` | **2 bytes** | Factory thresholds (`0x054–0x055`): `78 64` (`[120, 100]`) |
| **`21 72`** | `61 72` | **1 byte** | **Spoiler Extend Speed (`0x051`):** `0x78` = `120 km/h` (986) |
| **`21 73`** | `61 73` | **1 byte** | **Spoiler Retract Speed (`0x050`):** `0x50` = `80 km/h` |
| **`21 74`** | `61 74` | **1 byte** | **Fuel Tank Offset (`Tankabgleichwert`, `0x056`):** `0x4E` |
| **`21 75`** | `61 75` | **12 bytes** | **Fuel Tank Resistance Curve X (`0x21A–0x225`):** `6 × uint16 LE` in `0.1 Ω` |
| **`21 76 <00..07>`** | `61 76 <subid>` | **1–10 bytes** | **Oil Level Sensor Curve (`0x380–0x3AD`):** 8 sub-blocks (`00`..`07`, total 46 bytes) |
| **`21 77`** | `61 77` | **24 bytes** | **12-Point Sensor Linearization Curve (`0x168–0x17F`):** `12 × uint16 LE` |
| **`21 78 00`** | `61 78 00` | **10 bytes** | **Primary Speedometer Stepper Curve (`0x192–0x19B`):** `5 × uint16 LE` |
| **`21 78 01`** | `61 78 01` | **10 bytes** | **Secondary Speedometer Stepper Curve (`0x184–0x18D`):** `5 × uint16 LE` |
| **`21 7B`** | `61 7B` | **16 bytes** | **Fuel Tank Volume Curve Y (`0x226–0x235`):** 16 bytes |
| **`21 7C`** | `61 7C` | **12 bytes** | **Fuel Tank Curve Z (`0x202–0x20D`):** `6 × uint16 LE` |

### 6.2 Early Style (`93C56B`, `DSN K02–K17`) Live Data Blocks

Early MY1997–2000 clusters use a different set of `0x21` local identifiers:
- **`21 10` (5 bytes):** Coding & configuration summary.
- **`21 22` (4 bytes):** Total odometer reading.
- **`21 40` (3 bytes):** Engine speed (`RPM`), road speed (`km/h`), and fuel consumption (`KVA`).
- **`21 41` (2 bytes):** Analog sensor voltages.
- **`21 42` (12 bytes):** Complete analog sensor array (fuel sender Ω, coolant temp, outside temp, oil level, battery voltage, dimmer).
- **`21 43` (9 bytes):** Digital switch and warning indicator inputs.

---

## 7. Coding, Adaptation & The `30 01 xx` Subfunction Trap (Late `93C86`)

### 7.1 Reading & Writing `Parameterkodierung` (`0x032`) and `Menükonfiguration` (`0x03A`)

On late 93C86 clusters (`DSN K20–K50`), the two primary 8-byte coding blocks are accessed via KWP2000 Service `0x30` (`InputOutputControlByLocalIdentifier`) using local identifier `0x01`:

| Operation | Exact Request Payload | Positive Response | EEPROM Target |
|---|---|---|---|
| **Read `Parameterkodierung`** | `30 01 01` | `70 01 01 <8 bytes>` | Reads `0x032–0x039` (Equipment, OBC, Tell-Tale Drivers, Chimes) |
| **Write `Parameterkodierung`** | `30 01 08 <8 bytes>` | `70 01 08 <8 bytes>` | Writes 8 bytes into `0x032–0x039` |
| **Read `Menükonfiguration`** | `30 01 02` | `70 01 02 <8 bytes>` | Reads `0x03A–0x041` (Language, MPH/km/h, MPG/l/100km, °C/°F, 12h/24h) |
| **Write `Menükonfiguration`** | `30 01 09 <8 bytes>` | `70 01 09 <8 bytes>` | Writes 8 bytes into `0x03A–0x041` |

> ⚠️ **CRITICAL FIRMWARE TRAP — Never Send `30 01 08` or `30 01 09` Without 8 Data Bytes!**
> In the VDO cluster firmware, subfunctions `01` and `02` are **Read (`ReturnControl` / `ReportState`)**, whereas subfunctions `08` and `09` are **Write (`StoreParameter`)** and unconditionally copy 8 bytes starting at `RX_Buffer[3..10]` into EEPROM `0x032–0x039` or `0x03A–0x041` without checking the incoming KWP2000 frame length!
> - If a diagnostic script mistakenly sends a 3-byte `30 01 08` or `30 01 09` thinking it is a "read" command, **the cluster immediately overwrites `0x032–0x039` or `0x03A–0x041` with whatever 8 stale bytes were left sitting in its K-line receive buffer from the previous command**, and echoes those corrupted bytes back as `70 01 08 <garbage>`!
> - **Rule:** Use **only** `30 01 01` and `30 01 02` to read. Never send `30 01 08` or `30 01 09` unless followed by the full, validated 8-byte payload.

### 7.2 Calibration & Adaptation Writes (`Service 0x3B` — `WriteDataByLocalIdentifier`)

| Target Parameter | EEPROM Offset | Write Command | Payload Format |
|---|---|---|---|
| **VIN (17 ASCII chars)** | `0x000–0x010` | `3B 90 <17 bytes>` | 17 ASCII bytes (e.g., `WP0ZZZ98Z1S6XXXXX`) |
| **`K-Zahl` (Pulses/km)** | `0x052–0x053` | `3B 70 <2 bytes>` | `uint16 LE` (`FA 5C` = `23,802 Imp./km`) |
| **Factory Thresholds** | `0x054–0x055` | `3B 71 <2 bytes>` | `78 64` |
| **Spoiler Extend Speed** | `0x051` | `3B 72 <1 byte>` | Direct `km/h` (`0x78` = `120 km/h`) |
| **Spoiler Retract Speed** | `0x050` | `3B 73 <1 byte>` | Direct `km/h` (`0x50` = `80 km/h`) |
| **Reset Tank Calibration Offset** | `0x056` | `3B 74 00` | `0x00` resets `Tankabgleichwert` |
| **Fuel Tank Resistance Curve X** | `0x21A–0x225` | `3B 75 <12 bytes>` | `6 × uint16 LE` in `0.1 Ω` |
| **Oil Level Sensor Curve** | `0x380–0x3AD` | `3B 76 <00..07> <data>` | 8 sub-blocks (`00..07`: 10, 10, 5, 5, 5, 5, 5, 1 B) |
| **Primary Speedo Stepper Curve** | `0x192–0x19B` | `3B 78 00 <10 bytes>` | `5 × uint16 LE` (`00 00 C9 04 77 2D 8C 6E 8A 98` for UK 180 mph) |
| **Fuel Tank Volume Curve Y** | `0x226–0x235` | `3B 7B <16 bytes>` | 16 bytes |
| **Fuel Tank Curve Z** | `0x202–0x20D` | `3B 7C <12 bytes>` | `6 × uint16 LE` |

### 7.3 Non-Volatile EEPROM Commit & Hard Reset Sequence (`10 F5` + `11 01`)
After writing any coding or calibration parameter (`30 01 08`, `30 01 09`, or `3B xx`), execute the VDO commit/reboot sequence so the microcontroller flushes its working RAM shadow to the physical 93C86 EEPROM and reloads all gauge/lamp drivers:
```text
1. TX: 82 64 F1 10 F5 6C    → RX: 82 F1 64 50 F5 AC   (VDO Commit Session 0xF5)
2. TX: 82 64 F1 11 01 69    → RX: 82 F1 64 51 01 A9   (ECU Reset — needles & LCD reboot)
3. Wait 5.0 seconds, re-initialize with 81 64 F1 81 57, and read back the modified fields to verify.
```

---

## 8. Actuator Tests & Diagnostic Routines (`Service 0x31`)

> [!WARNING]
> **Service `0x30` (`InputOutputControlByLocalIdentifier`) Is Disabled in Firmware:**
> Although older diagnostic documentation often cites `30 10 00` – `30 1F 00` for instrument cluster actuator testing, empirical bench verification confirms that **Service `0x30` is permanently disabled** in the VDO Kombi 2000 firmware, always returning negative response `7F 30 12` (`SubFunctionNotSupported / ServiceNotSupported`).
>
> On all `Kombi 2000` clusters (`DSN K20–K50`), the factory PIWIS actuator suite is executed exclusively via **KWP2000 Service `0x31` (`StartRoutineByLocalIdentifier`)**.

### 8.1 Complete Factory Diagnostic Routines Matrix (`Service 0x31`)

| Routine ID | Request Hex | Component Tested | Empirical Behavior & Notes |
|---|---|---|---|
| **`0x05`** | `31 05` | **Analog Needle Sweeps** | Sweeps all analog stepper motor needles (Speedometer, Tachometer, Coolant Temp, Fuel, and Oil Pressure on 996) across their full dial range and returns to baseline. Returns `71 05`. |
| **`0x07`** | `31 07` | **Warning Lamp Tell-Tales** | Illuminates all instrument cluster warning lamps and tell-tale LEDs for bulb functional verification. Returns `71 07`. |
| **`0x03`** | `31 03 00` | **Acoustic Gong Chime** | Sounds the electronic multi-tone gong chime (seatbelt / key-in-ignition warning). Returns `71 03`. |
| **`0x04`** | `31 04` | **Acoustic Piezo Buzzer** | Sounds the high-pitch piezo warning buzzer (headlights-on / parking brake reminder). Returns `71 04`. |
| **`0x06 01`** | `31 06 01` | **Backlighting PWM Test** | Steps instrument cluster gauge backlighting through PWM dimming levels. Returns `71 06`. |
| **`0x30`** | `31 30` | **Event Memory Reset** | Clears the 12-channel Event Memory warning history (`0x644–0x65B`). |

---

## 9. Dynamic Center Display Text Injection (`Textausgabe` Routine `31 06 03`)

On late-generation clusters with dot-matrix LCD support (**DSN `K24`+**, MY2002–2005), the VDO firmware implements diagnostic routine `0x06` sub-function `0x03` (`Textausgabe`), allowing an external microcontroller (ESP32, Raspberry Pi, or diagnostic companion tool) to inject custom ASCII text directly onto the center dot-matrix display over K-line:

- **Start Display Service:** `31 06 03 1C 02 <ASCII text bytes...> 00`
- **Positive Response:** `71 06`
- **Stop Display Service:** `32 06` (returns `72 06`)

### Frame Structure
| Byte | Value | Field Description |
|---|---|---|
| `0` | `0x31` | `StartRoutineByLocalIdentifier` |
| `1` | `0x06` | Routine ID: Display Output Control |
| `2` | `0x03` | Sub-Function: `Textausgabe` (Dynamic text output) |
| `3` | `0x1C` | Screen / format descriptor |
| `4` | `0x02` | Line / row selector (dot-matrix region) |
| `5..N-1` | ASCII | Null-terminated string (e.g. `SPEED 65 MPH\0`, `OIL TEMP 92C\0`) |
| `N` | `0x00` | Null terminator |

*(Note: Early clusters such as DSN `K21` return `7F 31 10` GeneralReject because their firmware uses fixed mask-ROM strings without dynamic dot-matrix buffer injection.)*

---

## 10. Fuel Level Gauge Software Damping Behavior (Troubleshooting "0 Fuel" on Swaps)

When a replacement cluster is installed in a car or powered up on the bench with a fuel level sender connected, the analog fuel gauge frequently reads **dead empty (`0`)** with the low-fuel warning light illuminated, even with a half-full or full tank:

- **The Root Cause:** VDO Kombi 2000 firmware implements an intentionally heavy **software RC low-pass filter** (several minutes time constant) on the float sender ADC input (`Pin B21`) to prevent fuel slosh in the tank from causing analog needle movement during acceleration and cornering.
- **Troubleshooting:**
  - This is **normal factory behavior**, NOT a broken wire, blown fuse, or faulty tank sender.
  - If resistance on `Pin B21` measures between ~13.6 Ω (Full) and 94.2 Ω (Empty), the wiring is functional.
  - Allow 3–5 minutes with ignition ON, or cycle Terminal 15 power, and the stepper motor will smoothly slew to true tank capacity.

---

## 11. Direct Memory Reading Over OBD K-Line (`Service 0x23`) — Complete Guide, Pros, Cons & Caveats

### 11.1 How `ReadMemoryByAddress` (`0x23`) Works on Late Clusters (`93C86`)
On MY2001–2005 clusters (`DSN K20–K50`), the VDO microcontroller supports KWP2000 Service `0x23` (`ReadMemoryByAddress`) in the default diagnostic session (`81` / `10 89`) with **no `0x27` SecurityAccess seed/key required**:
- **Request Format:** `23 <AddrHi> <AddrMid> <AddrLo> <Length>`
- **Positive Response:** `63 <Data_0 ... Data_Length-1>`

### 9.2 Complete VDO Microcontroller Address Space Map (`Service 0x23`)

| 24-Bit Address Range | Size | Memory Region | Notes |
|---|---|---|---|
| **`0x000000 – 0x000FFF`** | 4 KB | **Internal MCU Registers & Zero-Page RAM** | Live CPU state, I/O port latches, and K-line RX/TX ring buffers |
| **`0x004000 – 0x0047FF`** | 2 KB | **Extended System RAM** | Stack and runtime variables |
| **`0x00A000 – 0x00FFFF`** | 24 KB | **Lower Mask ROM / Bootloader** | VDO boot & base routines |
| **`0x080000 – 0x0807FF`** | **2,048 B (2 KB)** | **93C86 EEPROM Live RAM Shadow / Mirror** | **1:1 linear byte map (`0x000–0x7FF`) of the 2048-byte 93C86 EEPROM** |
| **`0x090000 – 0x09FFFF`** | 64 KB | **Main Application Program Flash / ROM** | Main VDO cluster firmware & KWP2000 diagnostic dispatch tables |
| **`0x300000 – 0x3000FF`** | 256 B | **Secondary Calibration RAM Window** | Runtime gauge state |

#### Dumping the Full 2048-Byte 93C86 EEPROM Map (`0x080000–0x0807FF`)
Send 128 sequential 16-byte requests from `0x080000` to `0x0807F0`:
```text
Chunk 0   (0x000): TX: 85 64 F1 23 08 00 00 10 15  →  RX: 91 F1 64 63 [16 bytes] [CS]
Chunk 1   (0x010): TX: 85 64 F1 23 08 00 10 10 25  →  RX: 91 F1 64 63 [16 bytes] [CS]
...
Chunk 127 (0x7F0): TX: 85 64 F1 23 08 07 F0 10 0C  →  RX: 91 F1 64 63 [16 bytes] [CS]
```
Concatenating all 128 payloads (`128 × 16 = 2,048 bytes`) produces a complete `.bin` image in ~12 seconds. For maximum reliability over K-line, run **3 consecutive 2048-byte passes** and verify that their SHA-256 checksums match.

### 9.3 Pros, Cons & Critical Caveats of OBD `0x23` Memory Dumping

Understanding what `0x080000–0x0807FF` actually is prevents serious mistakes when backing up or restoring clusters:

#### Pros
1. **100% Non-Invasive:** No steering wheel or cluster removal, no breaking plastic bezel tabs, no desoldering, and no crystal shorting or SOIC-8 clip contact issues through VDO conformal coating.
2. **Native 8-Bit Linear Order:** No 16-bit word byte-swapping confusion.
3. **Perfect for Auditing & Diffing:** Allows you to inspect every single byte of VIN (`0x000`), Part Number (`0x01D`), DSN (`0x023`), `Parameterkodierung` (`0x032`), `Menükonfiguration` (`0x03A`), `K-Zahl` (`0x052`), Speedometer curves (`0x184`, `0x192`), Tank curves (`0x202–0x235`), Oil curve (`0x380–0x3AD`), and Event Memory (`0x644`, `0x6F4`).

#### Cons & Caveats (Read Before Flashing!)
1. **It Is a Live RAM Shadow / Working Buffer, Not a Cold Physical Chip Read:**
   - The address range `0x080000–0x0807FF` is the microcontroller's **memory-mapped RAM shadow** of the 93C86 EEPROM while the cluster OS is actively executing.
   - For all static configuration blocks (VIN, Part Number, DSN, Coding `0x032–0x041`, Speedo/Tank/Oil curves), the RAM shadow is 100% identical to the physical 93C86 chip.
   - However, **dynamic rolling areas** — specifically the Primary (`0x300–0x31F`) and Backup (`0x500–0x51F`) encrypted odometer blocks, fault counters (`0x600+`), and active key shadow (`0x40A`) — reflect live runtime state.
2. **Odometer Primary (`0x300`) vs. Backup (`0x500`) Rolling Parity:**
   - Because the MCU updates `0x300–0x31F` and `0x500–0x51F` sequentially in 1-bit increments as distance accumulates, an OBD dump captured while the cluster is awake can show a 1-bit difference between `0x300` and `0x500` (e.g., `0x319 = 0x2E` vs. `0x519 = 0x3E`).
   - If you ever write an OBD-captured `.bin` to a physical 93C86 chip using an offline programmer (GQ-4X / CH341A), **always copy `0x300–0x31F` over `0x500–0x51F`** first so both blocks match byte-for-byte at cold power-on.
3. **Read-Only via `0x23` (No Raw 2 KB `.bin` Write Over K-Line):**
   - Service `0x23` is strictly `ReadMemoryByAddress`. The cluster does **not** allow raw `WriteMemoryByAddress` (`0x3D`) over `0x080000–0x0807FF` in normal diagnostic sessions.
   - Instead, K-line restoration is performed **field-by-field** using the official KWP2000 write services (`30 01 08`, `30 01 09`, `3B 70`, `3B 72`, `3B 73`, `3B 74`, `3B 75`, `3B 76`, `3B 78 00`, `3B 7B`, `3B 7C`, `3B 90`) followed by `10 F5` + `11 01`.
4. **Why Field-by-Field Restoration Is Safer Than Wholesale `.bin` Flashing:**
   - Never flash another cluster's entire 2 KB `.bin` onto your car's cluster — that overwrites your vehicle's VIN (`0x000`), part number (`0x01D`), DSN (`0x023`), and encrypted odometer blocks (`0x300` & `0x500`).
   - By using `0x23` as a **diff engine** against the known-good reference dumps in [`dumps/`](../dumps/) and writing only the specific corrupted configuration fields via `30 01 08` / `30 01 09` / `3B 78 00` (using a strict **Read-Before → Write-Field → Commit `10 F5` + `11 01` → Read-Back Verify** workflow), your VIN and mileage remain 100% untouched.

---

## 10. Troubleshooting Common Hardware & Electrical Faults

### 10.1 Airbag Warning Light Issues (Stuck ON vs. Dead at Key-On)

| Symptom | Root Cause | Diagnostic & Fix |
|---|---|---|
| **Airbag lamp stays ON continuously after starting** | Latched fault code in Airbag ECU (`POSIP / Bosch AB6.2`, K-line address `0x15` on OBD Pin 3) — commonly seat belt buckle, side airbag harness under seat, or ignition turned ON while cluster/seat/airbag was unplugged | Connect K-line tool to **OBD Pin 3, Target `0x15`** (10,400 baud), read and repair fault, then clear Airbag fault memory. *(Generic OBD-II scanners on Pin 7 cannot talk to the Airbag ECU!)* |
| **Airbag lamp is completely DEAD at ignition key-on (no 4-second bulb check)** | **Cause A (Coding corruption on `93C86`):** EEPROM byte `0x036` was zeroed (`0x00` instead of `0xB5`), disabling the cluster's internal low-side tell-tale driver.<br>**Cause B (Power supply fault):** Blown **Fuse E1 (7.5A)** or faulty Ignition Switch **Terminal 86S** contact (`Plug A Pin 4` / `III/1`). | 1. Read `30 01 01` on cluster `0x64`: if byte 4 (`0x036`) is `0x00`, restore `Parameterkodierung` (`84 02 1F 00 B5 07 00 00` on 986) via `30 01 08`.<br>2. Check **Fuse E1** in footwell fusebox and verify +12V on `A4` with key inserted.<br>3. Verify Airbag ECU (`0x15`) responds on OBD Pin 3 and reports 0 faults. |

### 10.2 Handbrake (`!`) Warning Light Not Working (Late `93C86` Non-PSM Cars)
- **Cause:** Byte 0 of `Parameterkodierung` (`0x032`) has the PSM bit (`0x10` or `0x1A`) set on a car equipped with standard Bosch ABS 5.3 (non-PSM). When coded for PSM, the cluster ignores the mechanical handbrake switch on `Plug B Pin 22` and waits for a CAN message from a PSM unit.
- **Fix:** Restore `0x032` to `0x84` (e.g., `30 01 08 84 02 1F 00 B5 07 00 00`) and clear DTC `5555` (`14 FF 00`).

### 10.3 Speedometer Reading ~15% (+7 to +8 mph) Too High on a UK 180 mph Cluster
- **Cause:** The Primary Speedometer Stepper Curve (`0x192–0x19B`) was overwritten with the Continental European 250 km/h curve (`00 00 7F 02 77 2D 37 63 51 98`, where full-scale `w3 = 253.99 km/h = 157.8 mph`), compressing the 180 mph dial scale.
- **Fix:** Write the factory UK 180 mph curve (`3B 78 00 00 00 C9 04 77 2D 8C 6E 8A 98`) or the True 1:1 GPS curve (`3B 78 00 00 00 49 06 77 2D 28 71 8A 98`), followed by `10 F5` + `11 01`.

### 10.4 Multimeter Sensor Reference Values

| Component | Cluster Pins (Late / Early) | Expected Values |
|---|---|---|
| **Battery Voltage (Term 30)** | `A2, A18` / `III/10, 23` | `12.4 – 12.8 V` (engine off), `13.6 – 14.4 V` (running) |
| **Fuel Level Sender (986 64L)** | `B4` & `B20` / `II/3` & `II/4` | **Empty:** `~94.2 Ω` (`942` in `21 02`) — **Full:** `~13.6 Ω` (`136` in `21 02`) *(Note: Late 986/996 sender is ~94 Ω empty to ~13 Ω full)* |
| **Powertrain CAN Bus (`CAN Antrieb`)** | `A15 (High)` & `A31 (Low)` | `~60 Ω` loop resistance (with DME & cluster connected, battery disconnected); `~2.5 V` quiescent with ignition ON |
