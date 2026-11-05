# Porsche 986 / 996 Instrument Cluster Wiring, Pinouts & Bench Power Guide

The Porsche 986 Boxster and 996 911 instrument clusters use **two completely different electrical architectures and connector systems** depending on model year:

1. **Early Style (MY1997–2000, 93C56B EEPROM):**
   * **Connectors:** **3 × 26-pin** connectors (**Plug I = Blue**, **Plug II = White**, **Plug III = Black**).
   * **Signal Architecture:** **100% Discrete / Analog + K-Line.** There is **no CAN bus** on early clusters. Engine RPM (`TN-Signal`), vehicle speed pulses (`Speed RL`), fuel consumption (`KVA`), coolant temperature, and all warning lamps run over individual dedicated wires.
2. **Late Style ("Instrument Cluster 2000", MY2001–2004 986 / MY2001–2005 996, 93C86 EEPROM):**
   * **Connectors:** **3 × 32-pin** AMP/Tyco connectors (**Plug A = Green**, **Plug B = Blue**, **Plug C = Grey**).
   * **Signal Architecture:** **Dual CAN Bus (500 kbps) + K-Line + Discrete Sensors.** High-speed powertrain signals (RPM, coolant temp, DME/ABS/PSM status, Tiptronic gear) arrive over **CAN Antrieb** (`A15`/`A31`), HVAC data runs over **CAN Komfort** (`A14`/`A30`), diagnostics run over **K-Line** (`A28` → OBD Pin 3), while critical safety tell-tales (Airbag `B25`, Handbrake `B22`, Brake Fluid `B29`, Oil Pressure Switch `A13`) and analog senders (Fuel `B4`, Oil Level `B2`, Outside Temp `B1`) remain hardwired.

---

## 1. Bench Power-Up & Diagnostic Harness Quick Guide

### A. Late Cluster (MY2001–2005, 93C86 — 3×32-Pin Green / Blue / Grey)
To power up, test, or dump a late cluster on the bench over K-line, **you only need Plug A (the 32-pin Green connector)**. Every power, ground, CAN, and K-line pin lives on **Plug A (Green)**:

| Function | Terminal Name | Plug & Pin | Wire Color (Factory) | Bench Connection |
|---|---|---|---|---|
| **Chassis / Electronics Ground** | Terminal 31 | **Plug A (Green) Pin 1 & Pin 17** | `0.35 BN/BU` (Brown/Blue) | Connect to **PSU Ground (-)** and **OBD Pin 4 & 5** |
| **Permanent Battery +12V** | Terminal 30 (Fuse B1) | **Plug A (Green) Pin 2 & Pin 18** | `0.5 RD/BK` (Red/Black) | Connect to **+12.5V DC Power Supply (+)** and **OBD Pin 16** |
| **Switched Ignition +12V** | Terminal 15 (Fuse B10) | **Plug A (Green) Pin 3** | `0.35 BK/RD` (Black/Red) | Connect to **+12.5V DC (Ignition ON switch)** |
| **Key-In Contact +12V** | Terminal 86S (Fuse E1) | **Plug A (Green) Pin 4** | `0.35 OG` (Orange) | Connect to **+12.5V DC** (simulates key inserted) |
| **K-Line Diagnostics (`0x64`)** | Diagnosis K-Lead | **Plug A (Green) Pin 28** | `0.35 OG/BU` (Orange/Blue) | Connect to **Diagnostic Interface K-Line** *(Vehicle OBD Pin 3; or Pin 7 on a generic USB KKL bench cable)* |
| **Powertrain CAN High** | `CAN Antrieb High` | **Plug A (Green) Pin 15** | `0.35 BU/WH` (Blue/White) | *(Optional on bench)* 500 kbps CAN-H |
| **Powertrain CAN Low** | `CAN Antrieb Low` | **Plug A (Green) Pin 31** | `0.35 GY/WH` (Grey/White) | *(Optional on bench)* 500 kbps CAN-L |
| **Comfort CAN High** | `CAN Komfort High` | **Plug A (Green) Pin 14** | `0.35 YE` (Yellow) | *(Optional on bench)* Comfort CAN-H |
| **Comfort CAN Low** | `CAN Komfort Low` | **Plug A (Green) Pin 30** | `0.35 BK` (Black) | *(Optional on bench)* Comfort CAN-L |

> **Important Note on OBD-II Pin 3 vs. Pin 7:**
> * **In the vehicle:** Porsche routes the DME (Engine ECU) and Immobilizer on **OBD-II Pin 7 (K-Line 1)**, and routes the Instrument Cluster (`0x64`), Airbag, ABS/PSM, and Climate Control on **OBD-II Pin 3 (K-Line 2)** via splice `VS 90`. If connecting through the car's OBD port with a standard KKL cable, your adapter must route K-line to **OBD Pin 3** (or bridge Pin 3 and Pin 7).
> * **On the bench:** If wiring a standard USB KKL / FTDI cable directly to the cluster pins, connect your cable's K-line pin (Pin 7 on the OBD-II female pigtail) directly to **Green Plug A Pin 28** (Late) or **Blue Plug I Pin 21** (Early).

### B. Early Cluster (MY1997–2000, 93C56B — 3×26-Pin Blue / White / Black)
On early clusters, power and ground are on **Plug III (Black, 26-pin)** and K-line is on **Plug I (Blue, 26-pin)**:

| Function | Terminal Name | Plug & Pin | Wire Color (Factory) | Bench Connection |
|---|---|---|---|---|
| **Chassis / Electronics Ground** | Terminal 31 | **Plug III (Black) Pin 8 & Pin 21** | `0.5 BR/BL` (Brown/Blue) | Connect to **PSU Ground (-)** and **OBD Pin 4 & 5** |
| **Permanent Battery +12V** | Terminal 30 (Fuse B1) | **Plug III (Black) Pin 10 & Pin 23** | `0.5 RE/BK` (Red/Black) | Connect to **+12.5V DC Power Supply (+)** and **OBD Pin 16** |
| **Switched Ignition +12V** | Terminal 15 (Fuse B10) | **Plug III (Black) Pin 12 & Pin 25** | `0.5 BK/RE` (Black/Red) | Connect to **+12.5V DC (Ignition ON switch)** |
| **Key-In Contact +12V** | Terminal 86S (Fuse E1) | **Plug III (Black) Pin 1** | `0.35 OR` (Orange) | Connect to **+12.5V DC** |
| **K-Line Diagnostics (`0x64`)** | Diagnosis K-Lead | **Plug I (Blue) Pin 21** | `0.35 OR/BL` (Orange/Blue) | Connect to **Diagnostic Interface K-Line** *(Vehicle OBD Pin 3; or Pin 7 on generic USB KKL bench cable)* |

---

## 2. Complete Pinout: Late Cluster ("Instrument Cluster 2000", MY2001–2005, 3×32-Pin)

Sourced from Porsche Factory Workshop Manual Wiring Diagrams (986 MY2001+ Sheet 10–12, *Instrument Cluster 2000*).

### Plug A — Green 32-Pin Connector (`PLUG "A" = GN` / Mitchell `C1`)
*Carries main power, ground, CAN buses, K-line diagnostics, spoiler controls, and alternator/oil pressure switches.*

| Pin | Signal Name | Wire Size & Color | Destination / Notes |
|---|---|---|---|
| **A1** | **TERM 31 (Ground)** | `0.35 BN/BU` | Electronics Ground (`GP Electronics` / `G205` right center of dash) |
| **A2** | **TERM 30 (Battery +12V)** | `0.5 RD/BK` | Fuse Holder B, **Fuse B1 (15A)** — Hot at all times |
| **A3** | **TERM 15 (Ignition +12V)** | `0.35 BK/RD` | Fuse Holder B, **Fuse B10 (15A)** — Hot in Run or Start |
| **A4** | **KEY CONTACT (Term 86S)** | `0.35 OG` | Fuse Holder E, **Fuse E1 (7.5A/15A)** via splice `BS 13/1` — Hot with key in lock |
| **A5** | **BUTTON SPOILER EXTENSION** | `0.35 GN/BK` | Footwell manual spoiler extend switch |
| **A6** | **INDICATOR SPOILER EXTENDED** | `0.35 GY/BN` | Spoiler warning indicator |
| **A7** | **REL. SPOILER EXTENSION** | `0.35 WH/GN` | Rear spoiler extend relay coil control |
| **A8–A11** | *(Not Used)* | — | Empty |
| **A12** | **CHARGE INDICATOR (Term 61 / D+)** | `0.5 BU` | Alternator regulator `D+` / `KL 61` (via splice `VS 39`) |
| **A13** | **OIL PRESSURE SWITCH** | `0.35 GN/WH` | Engine oil pressure switch (closes to ground when pressure low) |
| **A14** | **CAN KOMFORT HIGH** | `0.35 YE` | Comfort CAN-H to Klimatronik (A/C control unit) |
| **A15** | **CAN ANTRIEB HIGH** | `0.35 BU/WH` | **Powertrain CAN-H (500 kbps)** to DME ME7.2/7.8 & ABS/PSM 5.3/5.7 |
| **A16** | **BRAKE PAD WEAR -** | `0.35 BN/BK` | Brake pad wear sensor return loop |
| **A17** | **TERM 31 (Ground)** | `0.35 BN/BU` | Electronics Ground (`GP Electronics` / `G205`) |
| **A18** | **TERM 30 (Battery +12V)** | `0.5 RD/BK` | Fuse Holder B, **Fuse B1 (15A)** — Hot at all times |
| **A19** | **TERM 58 (Illumination)** | `0.35 GY` | Exterior light switch parking/headlight illumination feed |
| **A20** | **DOOR CONTACT** | `0.35 BN/GN/WH` | Alarm / Central Locking CU (`M534`) door open status |
| **A21** | **BUTTON SPOILER RETRACTION** | `0.35 GN/RD` | Footwell manual spoiler retract switch |
| **A22** | **SPOILER RETRACTED** | `0.35 GY/GN` | Rear spoiler retracted limit microswitch |
| **A23** | **REL. SPOILER RETRACTION** | `0.35 BK/WH` | Rear spoiler retract relay coil control |
| **A24–A27** | *(Not Used)* | — | Empty |
| **A28** | **DIAGNOSIS (K-Line)** | `0.35 OG/BU` | **OBD-II DLC Pin 3** via splice `CP 90` / `VS 90` (10,400 baud KWP2000 `0x64`) |
| **A29** | **CLS LOCKED** | `0.35 BU/WH/BN` | Alarm / Central Locking CU central lock status |
| **A30** | **CAN KOMFORT LOW** | `0.35 BK` | Comfort CAN-L to Klimatronik (A/C control unit) |
| **A31** | **CAN ANTRIEB LOW** | `0.35 GY/WH` | **Powertrain CAN-L (500 kbps)** to DME ME7.2/7.8 & ABS/PSM 5.3/5.7 |
| **A32** | **BRAKE PAD WEAR +** | `0.35 BN/BK` | Brake pad wear sensor series loop feed (all 4 wheels) |

### Plug B — Blue 32-Pin Connector (`PLUG "B" = BU` / Mitchell `C2`)
*Carries analog level/temp sensors, dedicated sensor grounds, dimmer outputs, Speedometer A output, and discrete safety tell-tale inputs (Airbag, Handbrake, Seatbelt, Brake Fluid, Turn Signals, High Beam).*

| Pin | Signal Name | Wire Size & Color | Destination / Notes |
|---|---|---|---|
| **B1** | **EXTERIOR TEMPERATURE** | `0.35 BK/BU` | Front bumper left outside ambient temperature NTC sensor (Pin 1) |
| **B2** | **OIL LEVEL** | `0.35 GN/BU` | Engine sump oil level thermal sensor |
| **B3** | **SUN SENSOR** | `0.35 BK/RD` | Dashboard solar sensor (for Climatronic) |
| **B4** | **FUEL LEVEL SENSOR** | `0.35 VT` | Fuel tank float sender signal (`~30 Ω` full to `~250 Ω` empty) |
| **B5** | **OIL PRESSURE SENSOR** | — | *(Used on 5-dial 996 clusters for analog oil pressure gauge; unused on 3-dial 986)* |
| **B6–B9** | *(Not Used)* | — | Empty |
| **B10** | **DIM LAMP BULB** | `0.35 GY/BU` | Incandescent switch illumination dimmer output |
| **B11** | **DIM LED TERM 58d** | `0.5 GY/BU/RD` | PWM dimmer output (+ve) to dash switches, radio, HVAC, hazard switch (`VS 42`) |
| **B12** | **DIM LED TERM 31d** | `0.5 GY/BU/BN` | Dimmer reference ground return |
| **B13** | **SPEEDOMETER A (Speed Pulse Out)** | `0.5 GY/PK` | buffered road speed pulse output to Alarm CU (`A14`), Radio (`GAL`), Convertible Top, Navigation, DSP Amp |
| **B14–B16** | *(Not Used)* | — | Empty |
| **B17** | **GROUND EXTERIOR TEMPERATURE** | `0.35 BN/WH` | Dedicated sensor ground for Outside Temp Sensor (Pin 2) |
| **B18** | **GROUND OIL LEVEL** | `0.35 BN/OG` | Dedicated sensor ground for Oil Level Sensor |
| **B19** | **GROUND SUN SENSOR** | `0.35 BN/OG` | Dedicated sensor ground for Sun Sensor |
| **B20** | **GROUND FUEL LEVEL SENSOR** | `0.35 BN/OG` | Dedicated sensor ground for Fuel Tank Sender |
| **B21** | **SEAT BELT WARNING** | `0.35 BN/RD` | Driver seat belt buckle switch (grounds when unbuckled) |
| **B22** | **PARKING BRAKE** | `0.5 BN/YE` | Handbrake lever switch (`G206`) & Convertible Top CU *(ignored if PSM bit `0x10` is miscoded!)* |
| **B23** | **COOLING WATER LEVEL** | `0.35 YE/BU/RD` | Coolant expansion tank low-level float switch |
| **B24** | **WASHING FLUID LEVEL** | `0.35 YE/VT` | Windshield washer reservoir low-level float switch |
| **B25** | **AIRBAG WARNING** | `0.35 YE/RD` | Bosch Airbag Triggering Unit (`M563`) Pin 7 lamp control |
| **B26** | **TURN SIGNALS LEFT** | `0.35 BK/WH` | Left turn signal indicator feed |
| **B27** | **TURN SIGNALS RIGHT** | `0.35 BK/GN` | Right turn signal indicator feed |
| **B28** | **HIGH BEAM** | `0.35 WH` | High beam headlight indicator feed |
| **B29** | **BRAKE FLUID LEVEL** | `0.5 VT/RD` | Master cylinder reservoir brake fluid level switch (w/o PSM) |
| **B30** | **COVER OPEN DISPLAY** | `0.35 GY/RD` | Alarm CU (`M534`) luggage compartment lid open indicator |
| **B31–B32** | *(Not Used)* | — | Empty |

### Plug C — Grey 32-Pin Connector (`PLUG "C" = GY` / Mitchell `C3`)
*Carries On-Board Computer (OBC) stalk switches, Cruise Control (Tempostat), Tiptronic steering wheel inputs, Convertible Top indicator, and PCM/Infosystem clock/data lines.*

| Pin | Signal Name | Wire Size & Color | Destination / Notes |
|---|---|---|---|
| **C1** | **CRUISE CONTROL OFF** | — | Cruise control cancel input |
| **C2** | *(Not Used)* | — | Empty |
| **C3** | **INDICATOR LIGHTS POWER TOP** | `0.35 YE/GN` | Convertible top control unit warning lamp |
| **C4** | **CRUISE CONTROL SET** | — | Cruise control set/decelerate |
| **C5** | **TIPTRONIC 1 (`W0`)** | `0.35 PK/BN` | Tiptronic transmission selector wire 0 |
| **C6** | **TIPTRONIC 2 (`W1`)** | `0.35 BU/YE` | Tiptronic transmission selector wire 1 |
| **C7** | **TIPTRONIC 3 (`W3`)** | `0.35 BU/WH` | Tiptronic transmission selector wire 3 |
| **C8** | **TIPTRONIC 4 (`HS-BUTTON`)** | `0.35 BU/BK` | Tiptronic manual mode / steering switch |
| **C9** | **TIPTRONIC 5 (`RS-BUTTON`)** | — | Tiptronic steering switch |
| **C10** | **INFOSYSTEM IN (Clock/Data)** | `0.35 GY/YE` | PCM1 / Infosystem display clock (`Pin 20`) |
| **C11** | **INFOSYSTEM OUT (RXD)** | `0.35 VT` | PCM1 / Infosystem data (`Pin 21`) |
| **C12** | *(Not Used)* | — | Empty |
| **C13** | **SIGNAL ENGINE RUN** | `0.35 BU/RD/GN` | Daytime running lights relay (`Engine Running` output) |
| **C14–C16** | *(Not Used)* | — | Empty |
| **C17** | **TEMPOSTAT RESUME** | — | Cruise control resume |
| **C18** | **INDIKATOR SENSOR OVERTURN** | — | Roll-over protection bar warning lamp |
| **C19** | **CLUTCH SWITCH** | — | Clutch pedal switch input |
| **C20** | *(Not Used)* | — | Empty |
| **C21** | **OBC LEVER FRONT (Select/Enter)** | `0.35 GY/BN` | On-Board Computer (`M659`) stalk — Push Forward (grounds to `G206` via stalk Pin 1 `BN/BU`) |
| **C22** | **OBC LEVER DOWN** | `0.35 YE/BN` | On-Board Computer (`M659`) stalk — Push Down |
| **C23** | **OBC LEVER UP** | `0.35 WH/BN` | On-Board Computer (`M659`) stalk — Push Up |
| **C24** | **OBC LEVER REAR (Back/Reset)** | `0.35 BU/BN` | On-Board Computer (`M659`) stalk — Pull Back |
| **C25** | **OBC LEVER INSIDE** | — | Secondary stalk button (where fitted) |
| **C26** | **INPUT PARKING ASSISTANT** | `0.35 RD/YE` | ParkAssist control unit chime/display trigger |
| **C27–C31** | *(Not Used)* | — | Empty |
| **C32** | **TEMPOSTAT DISTANCE** | — | ACC distance (unused on 986) |

> [!IMPORTANT]
> **OBC Stalk Retrofit Pitfall — Inverted UP/DOWN Lever Movement:**
> When retrofitting the 4-stalk steering column switch assembly (`M659`), a common issue is finding that pushing the stalk **UP** moves the OBC display **DOWN**, and pushing **DOWN** moves it **UP**.
> - **Hardware Reality:** The cluster microcontroller pins for **C22** and **C23** are discrete digital switch pull-ups wired directly to MCU GPIO lines.
> - **Software Myth:** There is **no software inversion bit** in the EEPROM (`Parameterkodierung` or `Menükonfiguration`). The direction cannot be flipped via PIWIS coding or hex editing.
> - **The Fix:** If the lever direction is inverted, physically de-pin and swap **Pin C22** (`YE/BN`) and **Pin C23** (`WH/BN`) inside the 32-pin Grey harness connector (Plug C).

---

## 3. Complete Pinout: Early Cluster (MY1997–2000, 93C56B, 3×26-Pin)

Sourced from Porsche Factory Workshop Manual Wiring Diagrams (986 MY1997–2000 Sheet 3, *Instrument Cluster and Sensor*).

### Plug I — Blue 26-Pin Connector (`PLUG I = BLUE` / Mitchell `C1`)

| Pin | Signal Name | Wire Size & Color | Destination / Notes |
|---|---|---|---|
| **I/1** | **ABS-SILA (Warning Lamp)** | `0.5 WT/YE` | ABS 5.3 Control Unit warning lamp |
| **I/2** | **PARKING BRAKE** | `0.5 BR/YE` | Handbrake lever switch (`G206`) |
| **I/3** | **ASR/ABD INFO** | `0.5 GN/BK` | Traction control (`M222`) indicator |
| **I/4** | **ASR/ABD SILA (TC Lamp)** | `0.5 WT/RE` | Traction control warning lamp |
| **I/5** | *(Not Used)* | — | Empty |
| **I/6** | **TURN SIGNALS LEFT** | `0.35 BK/WT` | Left turn signal indicator |
| **I/7** | **TURN SIGNALS RIGHT** | `0.35 BK/GN` | Right turn signal indicator |
| **I/8** | **HIGH BEAM** | `0.35 WT` | High beam indicator |
| **I/9** | *(Not Used)* | — | Empty |
| **I/10** | **DIM LED TERM. 58d** | `0.5 GR/BL/RE` | Dash switch LED illumination PWM dimmer |
| **I/11** | **DIM LAMP BULB TERM. 58d** | `0.5 GR/BL` | Incandescent bulb illumination dimmer |
| **I/12** | **SPOILER EXT REL** | `0.5 WT/GN` | Rear spoiler extend relay |
| **I/13** | **SPEEDOMETER A (Speed Out)** | `0.5 GR/PK` | Buffered vehicle speed signal out to Radio, Cruise, Top, Alarm |
| **I/14–15** | *(Not Used)* | — | Empty |
| **I/16** | **CRUISE CONTROL** | `0.35 OR/RE` | Cruise control indicator (`M009+M454`) |
| **I/17** | **EXTERIOR TEMPERATURE** | `0.35 BR/BL` | Front bumper ambient temperature sensor |
| **I/18** | **COOLING WATER TEMPERATURE** | `0.35 BL/RE` | Engine coolant temperature gauge NTC sender |
| **I/19** | **OIL LEVEL** | `0.35 GN/BL` | Engine oil level thermal sensor |
| **I/20** | **FUEL LEVEL SENSOR** | `0.5 VI` | Fuel tank float sender |
| **I/21** | **DIAGNOSIS K (K-Line)** | `0.35 OR/BL` | **OBD-II DLC Pin 3** via splice `VS 90` |
| **I/22** | **FUEL STATUS** | `0.35 VI/BK` | Fuel tank status output to DME (`Pin 39`) for EVAP diagnostics |
| **I/23** | **BRAKE PAD WEAR** | `0.35 BR/BK` | Brake pad wear sensor loop |
| **I/24** | **ANALOG GROUND** | `0.5 BR/OR` | Dedicated sensor ground for Coolant Temp, Oil Level, Fuel Level, Outside Temp |
| **I/25** | **SPOILER EXT REL** | `0.5 BK/WT` | Rear spoiler control |
| **I/26** | **SIGNAL ENGINE RUN** | `0.35 BL/RE/GN` | Daytime running lights relay (`G8`) |

### Plug II — White 26-Pin Connector (`PLUG II = WHITE` / Mitchell `C2`)

| Pin | Signal Name | Wire Size & Color | Destination / Notes |
|---|---|---|---|
| **II/1** | *(Not Used)* | — | Empty |
| **II/2** | **TIPTRONIC POS. WIRE 4** | `0.35 BL/BK` | Tiptronic selector (`M249`) |
| **II/3** | **TIPTRONIC POS. WIRE 3** | `0.35 BL/WT` | Tiptronic selector (`M249`) |
| **II/4** | **BRAKE FLUID LEVEL** | `0.5 VI/RE` | Brake fluid reservoir float switch |
| **II/5** | **COOLING WATER LEVEL SWITCH** | `0.35 YE/BL/RE` | Coolant expansion tank level switch |
| **II/6** | **OIL PRESSURE SWITCH** | `0.35 GN/WT` | Low oil pressure warning switch |
| **II/7** | **WASHING FLUID LEVEL** | `0.5 YE/VI` | Washer fluid reservoir level switch |
| **II/8** | **LOCK CENTRAL LOCKING SYSTEM** | `0.35 BL/WT/BR` | Alarm / Central Locking CU (`M531/M534/M535`) |
| **II/9** | **SPOILER EXTEND IND** | `0.5 GR/BR` | Spoiler indicator |
| **II/10** | **SPOILER RET IN** | `0.5 GN/RE` | Spoiler retract switch |
| **II/11** | **SPOILER EXTEND IN** | `0.5 GN/BK` | Spoiler extend switch |
| **II/12** | **DOOR CONTACT** | `0.35 BR/GN/WT` | Door contact switch via Alarm CU |
| **II/13** | **KVA DME (Fuel Consumption)** | `0.35 YE` | DME fuel injection pulse width consumption signal (`KVA`) |
| **II/14** | **TERM. 58 (Illumination)** | `0.35 GR` | Exterior light switch illumination trigger |
| **II/15** | **ENGINE SPEED (`TN-SIGNAL`)** | `0.35 VI/GN` | DME tachometer RPM square-wave pulse output (`VS 109`) |
| **II/16** | **SPEED RL (Vehicle Speed In)** | `0.5 WT/BR` | ABS Rear-Left wheel speed pulse output |
| **II/17** | **TIPTRONIC STATUS** | `0.35 WT/GR` | Tiptronic transmission status (`M249`) |
| **II/18** | **TIPTRONIC POS. WIRE 1** | `0.35 PK/BR` | Tiptronic selector (`M249`) |
| **II/19** | **TIPTRONIC POS. WIRE 2** | `0.35 BL/YE` | Tiptronic selector (`M249`) |
| **II/20** | **OBC LEVER UP** | `0.35 WT/BR` | On-Board Computer (`M659`) stalk Up (Pin 2) |
| **II/21** | **OBC LEVER DOWN** | `0.35 YE/BR` | On-Board Computer (`M659`) stalk Down (Pin 3) |
| **II/22** | **OBC LEVER FRONT** | `0.35 GR/BR` | On-Board Computer (`M659`) stalk Forward (Pin 4) |
| **II/23** | **CHARGE INDICATOR (Term 61)** | `0.5 BL` | Alternator charging indicator |
| **II/24** | **SEAT BELT WARNING** | `0.5 BR/RE` | Seat belt buckle contact |
| **II/25** | **OBC LEVER REAR** | `0.35 BL/BR` | On-Board Computer (`M659`) stalk Back (Pin 5) |
| **II/26** | **SPOILER RET IND** | `0.5 GR/GN` | Spoiler retracted indicator |

### Plug III — Black 26-Pin Connector (`PLUG III = BLACK` / Mitchell `C3`)

| Pin | Signal Name | Wire Size & Color | Destination / Notes |
|---|---|---|---|
| **III/1** | **KEY CONTACT TERM. 86s** | `0.35 OR` | Fuse E1 (`7.5A`) — Ignition key inserted |
| **III/2** | **MALFUNCTION INDICATOR LAMP (CEL)** | `0.35 BL/YE` | DME Check Engine Light (`MIL`) |
| **III/3–5** | *(Not Used)* | — | Empty |
| **III/6** | **INFOSYSTEM IN** | `0.35 GR/YE` | Becker / PCM Infosystem (`M662`) |
| **III/7** | *(Not Used)* | — | Empty |
| **III/8** | **TERM. 31 (Ground)** | `0.5 BR/BL` | Electronics Ground (`G206`) |
| **III/9** | **INPUT PARKING ASSISTANT** | `0.35 RE/YE` | ParkAssist CU (`M635`) |
| **III/10** | **TERM. 30 (Battery +12V)** | `0.5 RE/BK` | Fuse B1 (`15A`) — Permanent battery power |
| **III/11** | **INFOSYSTEM OUT** | `0.35 VI` | Becker / PCM Infosystem (`M662`) |
| **III/12** | **TERM. 15 (Ignition +12V)** | `0.5 BK/RE` | Fuse B10 (`15A`) — Switched ignition power |
| **III/13** | **BRAKE PAD WEAR +** | `0.35 BR/BK` | Brake pad wear loop |
| **III/14** | **AIRBAG WARNING LAMP** | `0.5 YE/RE` | Airbag ECU (`M562/M563`) Pin 7 |
| **III/15** | *(Not Used)* | — | Empty |
| **III/16** | **INDICATOR LIGHTS POWER TOP** | `0.35 YE/GN` | Convertible top control module |
| **III/17** | **CRUISE CONTROL** | `0.35 OR/RE` | Cruise control (`M008+M454`) |
| **III/18–20** | *(Not Used)* | — | Empty |
| **III/21** | **TERM. 31 (Ground)** | `0.5 BR/BL` | Electronics Ground (`G206`) |
| **III/22** | *(Not Used)* | — | Empty |
| **III/23** | **TERM. 30 (Battery +12V)** | `0.5 RE/BK` | Fuse B1 (`15A`) — Permanent battery power |
| **III/24** | **DIM LED TERM. 31d** | `0.5 GR/BL/BR` | Illumination dimmer ground return |
| **III/25** | **TERM. 15 (Ignition +12V)** | `0.5 BK/RE` | Fuse B10 (`15A`) — Switched ignition power |
| **III/26** | **IDLE PERIOD (A/C)** | `0.35 OR/GN` | Air conditioning system (`M573`) |

---

## 4. Airbag Warning Lamp & Terminal 86S Power Topology

A frequent point of confusion when diagnosing dark or stuck Airbag warning lights (`H14`) on 986/996 vehicles is how the cluster and the Bosch Airbag Triggering Unit (`M563`) interact electrically:

```text
[Ignition Switch Lock (4A0 905 849 B)] ──(KL.86S contact)──> [Welding Splice VS 117]
                                                                    │
                 ┌──────────────────────────────────────────────────┴────────────────────────────────────┐
                 ▼                                                                                       ▼
         [Fuse E1 (7.5A/15A)]                                                                 [Unfused 0.5 OR wire]
                 │                                                                                       │
   [Radio + Cluster Term 86S (A4 / III/1)]                                              [Airbag ECU (M563) Pin 5 (+12V Power)]
                                                                                                         │
                                                                                                (Key-On Self-Test)
                                                                                                         │
                                                    [Cluster Airbag Pin (B25 / III/14)] <── [Airbag ECU Pin 7 (Lamp Driver)]
```

1. **Physical Hardware Path:**
   * Unlike DME, ABS, and Alarm (which run on Terminal 15/30), the 986 Airbag ECU (`M563`, bolted to the center tunnel forward of the shifter) receives its operating power from **Terminal 86S** (`Pin 5`, `0.5 OR`), while its chassis ground is on `Pin 6` (`0.5 BR`), its K-line (to OBD Pin 3) is on `Pin 9` (`0.35 OR/BL`), and its warning lamp output is on `Pin 7` (`0.5 GN/WT` → `0.35 YE/RD` to Cluster `B25` on Late / `III/14` on Early).
   * If the ignition switch electrical portion (Audi/VW part `4A0 905 849 B`) has a worn `86S` contact, the Airbag ECU receives `0V`, will not respond on OBD Pin 3, and cannot drive its warning lamp output properly.
2. **Cluster Microcontroller Lamp Driver Gate (Late 93C86 Clusters):**
   * On late clusters (`Kombi 2000`), the cluster microcontroller also gates its internal solid-state tell-tale drivers based on the factory baseline bytes in `Parameterkodierung` (`0x032–0x039`, specifically `0x032 = 0x84` and `0x036 = 0xB5`).
   * If `0x032` / `0x036` are accidentally zeroed during custom EEPROM or KWP2000 coding writes, the cluster suppresses the key-on Airbag bulb-check sweep, seatbelt warning lamp, and lights-on chime even when all bulbs and external modules are healthy.
   * **Important Safety Rule:** Restoring `0x036 = 0xB5` restores the *cluster's* tell-tale driver and bulb-check sweep, **but a working bulb check alone does not prove the Airbag system is fault-free**—always verify that the Airbag ECU itself answers on OBD Pin 3 (`M563`) with zero stored faults.

---

## 5. OBC (On-Board Computer `M659`) Retrofit Wiring Summary

If retrofitting the 4-stalk column switch (`996.613.215.10` / `996.613.219.10`) to add On-Board Computer control (or wiring a discrete 4-way momentary toggle switch):
* **Common Ground (`Pin 1` on OBC 5-pin plug, `BN/BU`):** Connect to dash ground (`G206` or cluster ground).
* **4 Momentary Switch Inputs (Active-Low to Ground):**

| OBC Stalk Action | OBC 5-Pin Plug | Early Cluster (1997–2000) | Late Cluster (2001–2004) | Wire Color |
|---|---|---|---|---|
| **Common Ground** | Pin 1 | Ground (`III/8` or `G206`) | Ground (`A1` or `G206`) | `BN/BU` (Brown/Blue) |
| **Push Up (Cycle Up)** | Pin 2 | **Plug II (White) Pin 20** | **Plug C (Grey) Pin 23** | `WH/BN` (White/Brown) |
| **Push Down (Cycle Down)** | Pin 3 | **Plug II (White) Pin 21** | **Plug C (Grey) Pin 22** | `YE/BN` (Yellow/Brown) |
| **Push Forward (Select/Enter)** | Pin 4 | **Plug II (White) Pin 22** | **Plug C (Grey) Pin 21** | `GY/BN` (Grey/Brown) |
| **Pull Back (Reset/Back)** | Pin 5 | **Plug II (White) Pin 25** | **Plug C (Grey) Pin 24** | `BU/BN` (Blue/Brown) |

*(Note: Even before fitting the physical stalk, enabling OBC in the EEPROM (`0x047 = 1F` on Early / `0x034 = 1F` on Late) immediately enables the ambient outside temperature display on the cluster LCD once the bumper NTC sensor is connected to `I/17` & `I/24` on Early or `B1` & `B17` on Late!)*
