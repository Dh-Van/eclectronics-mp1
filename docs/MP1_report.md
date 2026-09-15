# MP1 – USB LED Flasher: Design Choices and Period Analysis

## 1. Overview

The board plugs straight into a USB-A port, drops the 5 V to 3.3 V, and uses an op-amp relaxation oscillator to blink a red LED with a 1 s period.

$$
\text{USB 5 V} \;\rightarrow\; \text{3.3 V regulator (U1)} \;\rightarrow\; \text{op-amp oscillator (U2)} \;\rightarrow\; \text{R6 + LED}
$$

![Circuit schematic. J1 is the USB-A plug, U1 the 3.3 V regulator, U2 the op-amp oscillator, D1 the LED. Full-size copy in `MP1_schematic.pdf`.](schematic.png)

Only parts from the provided parts list were allowed. That list has one connector, one regulator, two op-amps (single/dual versions of the same part), three LED colours, seven capacitor values and a set of 1% resistors. So most parts had no alternative; the real choices were the oscillator topology, the timing values, single vs. dual op-amp, and the LED colour. Part names are the KiCad ones (the LTspice sim uses sim R4 = KiCad R5, sim R5 = KiCad R4, sim C1 = KiCad C4).

**Why an op-amp oscillator.** There is no 555, microcontroller or crystal on the list, so the timer has to be built from the op-amp. A relaxation oscillator (Schmitt trigger + RC) needs one op-amp, one capacitor and a few resistors, gives a square wave that drives the LED directly, and has a simple period formula, which makes the tolerance analysis clean.

## 2. Power supply

- **J1 – Molex 48037-0001 USB-A plug.** Only connector on the list. Only VBUS and GND are used; D+/D- are left open since the board only takes power. Average draw is about 7 mA (1 mA op-amp + 12 mA LED half the time), well under the 100 mA a port gives without enumeration.
- **U1 – MCP1702 3.3 V LDO.** Only regulator on the list; fixed 3.3 V so no setting resistors; 250 mA rating vs. 7 mA used. Dissipation is about 12 mW.
- **C1 = 1 uF in, C3 = 10 uF out.** The MCP1702 datasheet needs at least 1 uF ceramic on both pins. The list only has 1 uF and 10 uF; the 10 uF goes on the output because that rail feeds everything and supplies the 12 mA LED step.
- **C5 = 1 uF op-amp bypass**, right at the V+ pin. The datasheet suggests 0.1-1 uF; 1 uF holds the pin steadier during the LED step, and it keeps the 0.1 uF (the only 5% cap) free for the timer.

## 3. Oscillator

**U2 – MCP6021.** Single op-amp in SOT-23-5. The MCP6022 is the same part but dual; only one is needed, so the single is smaller and leaves no unused op-amp. It works here because it runs on a single 3.3 V supply, has rail-to-rail output (the timing math assumes the output sits at the rails), has ~1 pA input current (negligible against the ~1 uA timing current), and can drive ~30 mA so no LED transistor is needed.

**How it works.** R1/R2 (4.99 k each) make a 1.65 V mid-rail reference $V_{mid}$, needed because there is no negative supply. R3 (40.2 k) and R5 (20 k) feed the + input from $V_{mid}$ and the output, giving two thresholds either side of $V_{mid}$. R4 (3.01 M) charges C4 (0.1 uF) on the - input from the output. When C4 crosses the upper threshold the output flips low and C4 discharges; when it crosses the lower threshold the output flips high again. The output is a square wave and the LED follows it.

**Why these values.**

- **C4 = 0.1 uF.** The period is proportional to $R_4 C_4$, so the cap tolerance goes straight into the period. On the list the 0.1 uF is 5% ("J" in the part number); the 1 uF and 10 uF are 10%, which would fail the spec (Section 5.3); the 1% C0G parts (1 nF and below) would need a 300 M resistor, and the list stops at 10 M.
- **R4 = 3.01 M.** Gives $R_4 C_4 = 0.301$ s and a period of 1.00 s with the thresholds below. 10 M would need thresholds within 20 mV of the rails; 2 M works but pushes the thresholds much closer to the rails than 3.01 M.
- **R3 = 40.2 k, R5 = 20 k.** Thresholds too close to the rails make the period sensitive to how close the output really gets to the rails; too close to $V_{mid}$ makes the cap swing small so offset (0.5 mV) and noise matter. The 2:1 ratio puts the thresholds about 0.5 V from each rail, a good compromise.
- **R1 = R2 = 4.99 k.** Equal values give exactly half the supply, so the two half-cycles are equal (50% duty). 4.99 k is stiff enough that R3 barely loads it, and wastes only 0.3 mA.

## 4. LED

**D1 red LED (LTST-C171KRKT), R6 = 110 Ohm.** Red has the lowest forward voltage (~2 V) of the three LEDs, so on 3.3 V it gets the most current; green/blue (~3 V) would only get a few mA. The LED is driven straight from the output (anode to op-amp, cathode to ground), so it is on for half of each period:

$$
I_{LED} = \frac{3.3 - V_f}{R_6} = \frac{3.3 - 2.0}{110} \approx 12\ \text{mA}
$$

That is bright, with margin under the LED's 20 mA and the op-amp's ~30 mA limits. The 12 mA load pulls the high output down by ~0.1-0.2 V; that makes the charge half slightly longer and the discharge half slightly shorter, and the two nearly cancel (about +0.1% on the period, duty 50% to 52%).

## 5. Period analysis

### 5.1 Thresholds and period

The divider gives $V_{mid} = 1.65$ V and looks like $R_1 \parallel R_2 = 2.5$ k in series with R3, so the effective resistor from $V_{mid}$ to the + input is $R_a = 40.2 + 2.5 = 42.7$ k. The + input is a weighted average of $V_{mid}$ (through $R_a$) and the output (through $R_5$):

$$
V_{high} = \frac{V_{mid} R_5 + 3.3\,R_a}{R_a + R_5} = 2.774\ \text{V}, \qquad
V_{low} = \frac{V_{mid} R_5}{R_a + R_5} = 0.526\ \text{V}
$$

These are symmetric about 1.65 V. Charging from $V_{low}$ to $V_{high}$ with the output at 3.3 V, and discharging back, each take

$$
t_{up} = R_4 C_4 \ln\!\left(\frac{3.3 - V_{low}}{3.3 - V_{high}}\right)
      = 0.301 \cdot \ln\!\left(\frac{2.774}{0.526}\right) = 0.500\ \text{s},
\qquad
t_{down} = R_4 C_4 \ln\!\left(\frac{V_{high}}{V_{low}}\right) = 0.500\ \text{s}
$$

$$
T = t_{up} + t_{down} = 2 R_4 C_4 \ln\!\left(\frac{1 + \beta}{1 - \beta}\right) = 1.000\ \text{s}, \qquad \beta = \frac{R_a}{R_a + R_5} = 0.681
$$

(Leaving out the divider's 2.5 k gives 0.971 s, so it matters.)

### 5.2 Sensitivity

| Part            | Change | Effect on $T$ |
|-----------------|--------|---------------|
| R4 (3.01 M)     | +1%    | +1.00%        |
| C4 (0.1 uF)     | +5%    | +5.00%        |
| R3 (40.2 k)     | +1%    | +0.46%        |
| R5 (20 k)       | +1%    | -0.48%        |
| R1 or R2        | +1%    | +0.01%        |

The period is essentially $R_4 C_4$; the threshold resistors count about half; the divider barely matters because shifting $V_{mid}$ lengthens one half-cycle and shortens the other. With 1% resistors, almost the whole error budget is the 5% cap.

### 5.3 Worst case

Stacking every tolerance the same way: $T = 1.071$ s (+7.1%) or $T = 0.932$ s (-6.8%). Both are inside +/-10% with about 3% to spare. With a 10% cap the worst case would be about +/-12% and fail, which is why the 5% 0.1 uF was chosen. Other effects are small: output 25 mV short of the rails (<0.1%), LED load droop (+0.1%), 0.5 mV input offset (0.02%), 1 pA bias current (negligible), 100 ppm/C resistors over 20 C (0.2%).

### 5.4 Monte Carlo (LTspice)

The sim uses the generic `UniversalOpAmp2` (no MCP6021 model exists) on a 3.3 V single supply, `.ic V(vn)=0` for a repeatable start, and measures the time between the 2nd and 3rd rising edges to skip the startup transient. `.step param run 1 500 1` with `mc(value, 0.01)` on every resistor and `mc(0.1u, 0.05)` on C4 gives 500 runs with the real part tolerances.

![Period of each Monte Carlo run. The y-axis spans 0.92-1.05 s; the +/-10% limits are 0.9 s and 1.1 s, so every run is inside.](mc_period.png)

| Statistic          | Value     |
|--------------------|-----------|
| Mean period        | 0.987 s   |
| Std. deviation     | 0.030 s   |
| Minimum            | 0.926 s (-7.4%) |
| Maximum            | 1.046 s (+4.6%) |
| Runs inside 0.9-1.1 s | 500 / 500 |

The mean is 1.4% under the hand value because the modelled op-amp does not switch instantly or sit exactly on the rails. Every run is inside the window, matching the worst-case math.

## 6. PCB

- **Size.** 16.1 x 14.0 mm (225 mm^2). Height is set by the plug's shield pads plus edge clearance; width by fitting the parts in columns beside the plug. The board edge sits on the line the Molex footprint marks for it, and the plug is centred.
- **Placement.** U1 sits at J1's VBUS pin (2.4 mm trace) with C1 and C3 at its pins. U2 is in the middle with R3/C4 to its left, R5 above, R4 below, so the high-impedance - input trace is ~2 mm. C5 is at the V+ pin. R6 and D1 are at the far end so the LED is visible when plugged in.
- **Layers.** Two layers, all parts on top. Everything is routed on top; the back is an unbroken ground pour. Each ground pad reaches it through a via (0.8 mm / 0.4 mm drill); nearby grounds (U1, C1, C3, D1) share one. No via is in or touching a pad, to avoid paste wicking and tombstoning. The plug's through-hole pads join the pour with thermal reliefs. There is no top pour.
- **The one crossing.** The op-amp pinout forces one trace crossing. Instead of a back-side jumper (which would slot the ground plane), the 3.3 V feed to V+ runs between R4's pads.
- **Trace widths.** Power is 0.5 mm (20 mil), signals 0.2 mm (8 mil), 0.2 mm clearance, vias 31/16 mil, all above the 6 mil / 24-12 mil minimums. The one exception is the 3.3 V branch to the op-amp V+ pin: it narrows to 0.3-0.4 mm for ~4 mm because the gap between R4's pads is only 0.85 mm and a 0.5 mm trace would violate clearance. That branch carries about 1 mA, so it makes no difference.
- **Silkscreen / fab.** 0.8 mm reference designators kept off all pads; the plug's off-board silk outline removed; F.Fab has outlines, references and values for assembly; the back silk has the board name, author and revision.
- **Checks.** DRC: 0 errors, 0 warnings, 0 unconnected. Schematic/PCB parity clean. Footprints are imperial 0603/0805, SOT-23-3 and SOT-23-5 as on the parts list. IC pin numbers match the datasheets (MCP1702: 1 GND, 2 VOUT, 3 VIN; MCP6021: 1 OUT, 2 VSS, 3 IN+, 4 IN-, 5 VDD).

## 7. Bill of materials

All parts are from the provided parts list: 12 line items, 15 parts. (Also provided as `MP1_BOM.csv`.)

| # | Ref | Qty | Value | Description | Manufacturer Part # | Digi-Key # | Tol. | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | J1 | 1 | 48037-0001 | CONN PLUG USB 4POS RT ANG PCB | 0480370001 | WM17117-ND |  | USB-A plug; only VBUS and GND used |
| 2 | U1 | 1 | MCP1702T-3302E/CB | IC REG LIN 3.3V 250MA SOT23A-3 | MCP1702T-3302E/CB | MCP1702T-3302E/CBCT-ND |  | 3.3 V LDO regulator |
| 3 | U2 | 1 | MCP6021T-E/OT | IC OPAMP GP 10MHZ RRO SOT23-5 | MCP6021T-E/OT | MCP6021T-E/OTCT-ND |  | Rail-to-rail op-amp (oscillator) |
| 4 | D1 | 1 | LED | LED RED CLEAR 0805 SMD | LTST-C171KRKT | 160-1427-1-ND |  | Red LED |
| 5 | C1,C5 | 2 | 1u | CAP CER 1UF 25V X7R 0603 | C0603C105K3RACTU | 399-7376-1-ND | 10% | C1 = LDO input cap; C5 = op-amp bypass |
| 6 | C3 | 1 | 10u | CAP CER 10UF 16V X5R 0603 | GRT188R61C106KE13D | 490-12317-1-ND | 10% | LDO output / bulk cap |
| 7 | C4 | 1 | 0.1u | CAP CER 0.1UF 50V X7R 0603 | CC0603JRX7R9BB104 | 311-1779-1-ND | 5% | Timing capacitor |
| 8 | R1,R2 | 2 | 4.99k | RES SMD 4.99K OHM 1% 1/10W 0603 | RC0603FR-074K99L | 311-4.99KHRCT-ND | 1% | Mid-rail divider |
| 9 | R3 | 1 | 40.2k | RES SMD 40.2K OHM 1% 1/10W 0603 | RC0603FR-0740K2L | 311-40.2KHRCT-ND | 1% | Threshold resistor |
| 10 | R4 | 1 | 3.01M | RES SMD 3.01M OHM 1% 1/10W 0603 | RC0603FR-073M01L | 311-3.01MHRCT-ND | 1% | Timing resistor |
| 11 | R5 | 1 | 20k | RES SMD 20K OHM 1% 1/10W 0603 | RC0603FR-0720KL | 311-20.0KHRCT-ND | 1% | Threshold / positive feedback resistor |
| 12 | R6 | 1 | 110 | RES SMD 110 OHM 1% 1/10W 0603 | RC0603FR-07110RL | 311-110HRCT-ND | 1% | LED current-limit resistor |

**Project files.** All KiCad design files, the custom symbol/footprint library, the LTspice simulation, this report and the BOM are at:

https://github.com/Dh-Van/eclectronics-mp1
