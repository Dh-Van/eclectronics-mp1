# MP1 – USB LED Flasher: Design Choices and Period Analysis

## 1. What the circuit does

The board plugs straight into a USB-A port. It takes the 5 V from USB, drops it to 3.3 V, and uses an op-amp wired up as an oscillator to blink an LED once per second.

Signal path:

$$
\text{USB 5 V} \;\rightarrow\; \text{3.3 V regulator (U1)} \;\rightarrow\; \text{op-amp oscillator (U2)} \;\rightarrow\; \text{resistor + LED}
$$

Part names below are the ones on the KiCad schematic. (The LTspice sim uses slightly different names: sim R4 = KiCad R5, sim R5 = KiCad R4, sim C1 = KiCad C4.)

A note on choices: the assignment only allows parts from the provided parts list. For a lot of the circuit there was really only one option, so "the choice" was mostly about how to use the part, not which part. Where there was an actual choice I say so.

## 2. Power supply

**J1 – Molex 48037-0001 USB-A plug.** This is the only connector on the parts list. It is a plug, not a socket, so the board goes into the computer like a USB stick. Only the VBUS (5 V) and GND pins are used. D+ and D- are left unconnected.

**U1 – MCP1702 3.3 V regulator (LDO).** This is the only regulator on the list, and it happens to be exactly what the assignment asks for: 3.3 V out from the 5 V USB input. It is a fixed 3.3 V part so it needs no setting resistors, and it can supply 250 mA, which is far more than this circuit uses (about 12 mA for the LED and under 1 mA for the op-amp).

**C1 (1 uF) and C3 (10 uF) – regulator capacitors.** The MCP1702 datasheet says it needs at least 1 uF of ceramic capacitance on both the input and the output to be stable. The list only has two caps that big: 1 uF and 10 uF. I used the 1 uF on the input (C1) and the 10 uF on the output (C3). The bigger one goes on the output because that is the side that feeds the whole 3.3 V rail, so it also acts as a bulk cap for the op-amp and LED.

**C5 (1 uF) – op-amp bypass cap.** A bypass cap right next to the op-amp supply pin keeps the supply clean when the output switches. The MCP6021 datasheet recommends 0.1 uF to 1 uF here; I used the 1 uF from the list and placed it right at the pin.

## 3. Oscillator

**U2 – MCP6021 op-amp.** The list has two op-amps: the MCP6021 (single op-amp, SOT-23-5) and the MCP6022 (dual op-amp, TSSOP-8). They are electrically the same part. This circuit only needs one op-amp, so I picked the single one because the package is smaller and easier to route, and there is no unused op-amp to deal with. Either one works for the oscillator because:

- It runs on a single 3.3 V supply,
- Its output swings all the way from 0 V to 3.3 V ("rail-to-rail output")
- Its input bias current is about 1 pA. The timing capacitor is charged through a 3.01 M resistor, so the charging current is under 1 uA. The op-amp input current is about a million times smaller, so it does not affect the timing.

### How the oscillator works

This is a standard relaxation oscillator: a Schmitt trigger with an RC on its input.

1. R1 and R2 (both 4.99 k) divide 3.3 V in half to make a 1.65 V reference, $V_{mid}$.
2. R3 (40.2 k) and R5 (20 k) connect the op-amp's + input to $V_{mid}$ and to the output. This gives the op-amp two switching thresholds, one above $V_{mid}$ and one below it.
3. R4 (3.01 M) and C4 (0.1 uF) are the timer. The output charges C4 through R4, and C4 is connected to the - input.
4. When the output is high (3.3 V), C4 charges up. When the voltage on C4 gets above the upper threshold, the op-amp flips and the output goes low (0 V).
5. Now C4 discharges through R4. When it gets below the lower threshold, the op-amp flips back to high.
6. Repeat forever. The output is a square wave and the LED blinks with it.

### Why these values

The parts list only has 1% resistors in a fixed set of values, and only a handful of capacitor values, so the values were picked to make 1 s out of what is available.

- **C4 = 0.1 uF.** The period is proportional to $R_4 C_4$, so the cap tolerance goes straight into the period. Looking at the list, the 0.1 uF is a 5% part, the 10 uF and 1 uF are 10%, and the 1 nF, 100 pF and, 10 pF are 1% parts. The 1% caps are too small: 1 nF would need a 300 M resistor, and the biggest resistor on the list is 10 M. So the 0.1 uF 5% cap is the best-tolerance cap that gives a usable resistor value.
- **R4 = 3.01 M.** With C4 = 0.1 uF, $R_4 C_4 = 0.301$ s, and the period works out to 1.00 s with the threshold resistors below. The list also has 2 M and 10 M. 10 M would need the thresholds to be within about 20 mV of the rails, which the op-amp cannot do reliably. 2 M would work but needs a wider threshold spread; 3.01 M gave the cleanest match with values on the list.
- **R3 = 40.2 k, R5 = 20 k.** These set how far apart the thresholds are. With the 2:1 ratio the thresholds land at about 0.53 V and 2.77 V, and together with $R_4 C_4$ the period comes out to 1.00 s (see Section 5). Both are standard values on the list.
- **R1 = R2 = 4.99 k.** Equal values give exactly half the supply. 4.99 k is low enough that the divider is "stiff" (R3 does not pull it around much), but high enough that it only wastes about 0.3 mA.

## 4. LED

**D1 (red LED) and R6 (110 Ohm).** The list has three 0805 LEDs (red, green, blue). I picked the red one (LTST-C171KRKT) because it has the lowest forward voltage, which gives the most current and the brightest blink on a 3.3 V supply. The LED anode connects to the op-amp output through R6 and the cathode goes to ground, so the LED is on when the output is high, i.e. half of each period. The current is set by R6:

$$
I_{LED} = \frac{3.3\ \text{V} - V_f}{R_6}
$$

For the red LED ($V_f \approx 2$ V) that is about $(3.3 - 2.0)/110 \approx 12$ mA, which is bright and well within what the MCP6021 output can drive. (The green and blue LEDs have a forward voltage around 3 V, so on a 3.3 V supply they would only get a few mA.)

## 5. Period analysis

### 5.1 Thresholds

The divider R1/R2 makes

$$
V_{mid} = 3.3\ \text{V} \cdot \frac{R_2}{R_1 + R_2} = 1.65\ \text{V}
$$

Looking back into the divider, its resistance is $R_1 \parallel R_2 = 2.5$ k. That 2.5 k is in series with R3, so the effective resistor from $V_{mid}$ to the + input is

$$
R_a = R_3 + R_1 \parallel R_2 = 40.2\ \text{k} + 2.5\ \text{k} = 42.7\ \text{k}
$$

The + input is a weighted average of $V_{mid}$ (through $R_a$) and the output (through $R_5$). When the output is at 3.3 V the upper threshold is

$$
V_{high} = \frac{V_{mid} R_5 + 3.3\ \text{V} \cdot R_a}{R_a + R_5}
        = \frac{1.65 \cdot 20\ \text{k} + 3.3 \cdot 42.7\ \text{k}}{62.7\ \text{k}} = 2.774\ \text{V}
$$

When the output is at 0 V the lower threshold is

$$
V_{low} = \frac{V_{mid} R_5}{R_a + R_5} = \frac{1.65 \cdot 20\ \text{k}}{62.7\ \text{k}} = 0.526\ \text{V}
$$

The thresholds are symmetric about 1.65 V ($1.65 \pm 1.124$ V).

### 5.2 Period

The time for C4 to charge from $V_{low}$ to $V_{high}$ while the output sits at 3.3 V is the usual RC charging formula:

$$
t_{up} = R_4 C_4 \ln\!\left(\frac{3.3 - V_{low}}{3.3 - V_{high}}\right)
       = 0.301\ \text{s} \cdot \ln\!\left(\frac{2.774}{0.526}\right)
       = 0.301 \cdot 1.662 = 0.500\ \text{s}
$$

Because the thresholds are symmetric about half the supply, the discharge time is the same:

$$
t_{down} = R_4 C_4 \ln\!\left(\frac{V_{high}}{V_{low}}\right) = 0.500\ \text{s}
$$

$$
T = t_{up} + t_{down} = 1.000\ \text{s}
$$

Written more compactly with $\beta = R_a/(R_a + R_5) = 0.681$:

$$
T = 2 R_4 C_4 \ln\!\left(\frac{1 + \beta}{1 - \beta}\right)
$$

(If you leave out the 2.5 k from the divider, $\beta$ drops to 0.668 and you get $T = 0.971$ s, so it is worth including.)

### 5.3 How much each part matters

Nudging each part by its tolerance and recomputing $T$:

| Part            | Change | Effect on $T$ |
|-----------------|--------|---------------|
| R4 (3.01 M)     | +1%   | +1.00%       |
| C4 (0.1 uF)     | +5%   | +5.00%       |
| R3 (40.2 k)     | +1%   | +0.46%       |
| R5 (20 k)       | +1%   | -0.48%       |
| R1 or R2        | +1%   | +0.01%       |

So the period is basically $R_4 C_4$ (1% of R4 or C4 = 1% of $T$), the threshold resistors matter about half as much, and the divider hardly matters at all because shifting $V_{mid}$ makes one half-cycle longer and the other shorter by the same amount.

The capacitor is the big one. The resistors are all 1% parts, so most of the error budget goes to the 5% cap. This is why picking the 5% 0.1 uF over a 10% cap mattered.

### 5.4 Worst case

Stack every tolerance in the worst direction (1% resistors, 5% cap):

- Everything pushing $T$ long: $T = 1.071$ s (+7.1%)
- Everything pushing $T$ short: $T = 0.932$ s (-6.8%)

Both are inside the $\pm 10$% spec, with about 3% of margin left.

### 5.5 Monte Carlo simulation (LTspice)

I ran the circuit in LTspice with `.step param run 1 500 1` and Monte Carlo tolerances on every part: `mc(value, 0.01)` on the resistors and `mc(0.1u, 0.05)` on C4. Each run measures the time between two rising edges of the output.

[FIGURE 1 HERE: LTspice plot of measured period vs. run number for the 500 Monte Carlo runs. Caption: "Figure 1. Period of each Monte Carlo run. The dashed lines at 0.9 s and 1.1 s are the $\pm 10$% limits; all 500 runs are inside."]

Results over 500 runs:

| Statistic          | Value     |
|--------------------|-----------|
| Mean period        | 0.987 s   |
| Std. deviation     | 0.030 s   |
| Minimum            | 0.926 s (-7.4%) |
| Maximum            | 1.046 s (+4.6%) |
| Runs inside 0.9-1.1 s | 500 / 500 |


The simulated mean (0.987 s) is about 1.4% under the hand calculation (1.000 s). The difference comes from the op-amp model: a real (or modelled) op-amp does not switch instantly and does not sit exactly on the rails, and the sim uses a generic op-amp model rather than the MCP6021. Either way, every run stayed inside the $\pm 10$% window, which matches the worst-case math above.

## 6. PCB summary

- Two-layer board, 16.1 mm x 14.0 mm, all parts on top, back side is a solid ground pour.
- The USB plug hangs off the left edge like a USB stick. The 5 V pin is right next to the regulator so the input trace is short.
- C5 sits right at the op-amp supply pin. R3, R5, R4 and C4 are grouped around the op-amp so the high-impedance timing node (the - input, 3 M) has a short trace.
- Trace widths: 0.2 mm (8 mil) for signals and 0.5 mm (20 mil) for power, with 0.2 mm (8 mil) spacing. The one exception is the short 3.3 V branch that feeds the op-amp supply pin: it has to pass between the two pads of R4, so it narrows to 0.3-0.4 mm there. That branch carries well under 1 mA, so this is fine. Vias are 0.8 mm (31 mil) with a 0.4 mm (16 mil) drill. These all clear the assignment minimums of 6 mil trace/space and 24 mil / 12 mil vias.
- No vias are placed in or touching any pad (avoids solder paste being pulled into the via and tombstoning).
- Everything is routed on the top layer. The back layer is one unbroken ground pour connected to the pads with thermal reliefs. There is no top-side pour.
- Board bounding box: 16.1 mm x 14.0 mm = 225 mm^2. The height is set by the USB plug's shield pads plus edge clearance, so this is close to the smallest the board can be with this connector.
- DRC passes with no errors.

## 7. Bill of materials

All parts are from the provided parts list. 12 line items, 15 parts total. (Also provided as `MP1_BOM.csv`.)

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

## 8. Things I checked

- The op-amp output must reach the rails. If it stopped 25 mV short of each rail the period would change by less than 0.1%, so this is not a concern with the MCP6021.
- The 3.01 M resistor means the timing current is at most $(3.3 - 0.53)/3.01\ \text{M} \approx 0.9$ uA. The MCP6021's 1 pA input current is a million times smaller, so it does not affect the timing.
- C4 is a 5% capacitor, which is what the worst-case numbers above assume. The tolerance on this one part is what makes or breaks the spec.
