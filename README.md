# ENGR 3430 Miniproject 1 – USB LED Flasher

A USB-stick style board that plugs into a USB-A port, regulates 5 V down to 3.3 V, and blinks a red LED with a 1 s period using an op-amp relaxation oscillator.

## Folder layout

| Folder | What's in it |
|---|---|
| `kicad/` | KiCad 10 project: schematic, PCB layout, project settings. `kicad/lib/` holds the custom symbol library (`Eclectronics.kicad_sym`) and footprints (`Eclectronics.pretty/`) for the USB plug, MCP1702 and MCP6021. The project's `sym-lib-table` / `fp-lib-table` point at these with `${KIPRJMOD}` paths, so the project opens on any machine with no extra setup. |
| `ltspice/` | LTspice simulation. `sim.asc` is the 500-run Monte Carlo of the oscillator period (1 % resistors, 5 % cap); `sim.log` has the measured period for every run. `Draft1.asc` is the first pass. The 290 MB `sim.raw` waveform file is not committed – rerun `sim.asc` to regenerate it. |
| `docs/` | `MP1_report.md` (design choices + period analysis), `MP1_BOM.csv`, `MP1_schematic.pdf`, the assignment PDF and the allowed parts list. |

## Key numbers

- Period: 1.000 s by hand calculation, 0.987 s mean in simulation, worst case -6.8 % / +7.1 % (spec is +/-10 %).
- Board: 2 layers, 16.1 mm x 14.0 mm, all parts on top, back side is a ground pour. DRC clean.

## Opening the project

Open `kicad/MP1.kicad_pro` in KiCad 10. Note: the LTspice sim names differ from the KiCad schematic (sim R4 = KiCad R5, sim R5 = KiCad R4, sim C1 = KiCad C4); see the report.
