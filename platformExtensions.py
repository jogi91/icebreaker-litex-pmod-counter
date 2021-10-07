from litex.build.generic_platform import *

dip_pmod_1a = [
    ("dip_switch", 0, Pins("PMOD1A:0"), IOStandard("LVCMOS33")),
    ("dip_switch", 1, Pins("PMOD1A:1"), IOStandard("LVCMOS33")),
    ("dip_switch", 2, Pins("PMOD1A:2"), IOStandard("LVCMOS33")),
    ("dip_switch", 3, Pins("PMOD1A:3"), IOStandard("LVCMOS33")),
    ("dip_switch", 4, Pins("PMOD1A:4"), IOStandard("LVCMOS33")),
    ("dip_switch", 5, Pins("PMOD1A:5"), IOStandard("LVCMOS33")),
    ("dip_switch", 6, Pins("PMOD1A:6"), IOStandard("LVCMOS33")),
    ("dip_switch", 7, Pins("PMOD1A:7"), IOStandard("LVCMOS33")),
]

dip_pmod_1b = [
    ("dip_switch", 0, Pins("PMOD1B:0"), IOStandard("LVCMOS33")),
    ("dip_switch", 1, Pins("PMOD1B:1"), IOStandard("LVCMOS33")),
    ("dip_switch", 2, Pins("PMOD1B:2"), IOStandard("LVCMOS33")),
    ("dip_switch", 3, Pins("PMOD1B:3"), IOStandard("LVCMOS33")),
    ("dip_switch", 4, Pins("PMOD1B:4"), IOStandard("LVCMOS33")),
    ("dip_switch", 5, Pins("PMOD1B:5"), IOStandard("LVCMOS33")),
    ("dip_switch", 6, Pins("PMOD1B:6"), IOStandard("LVCMOS33")),
    ("dip_switch", 7, Pins("PMOD1B:7"), IOStandard("LVCMOS33")),
]

seven_segment_pmod_1a = [
    ("seven_segment", 0, Pins("PMOD1A:0"), IOStandard("LVCMOS33")),
    ("seven_segment", 1, Pins("PMOD1A:1"), IOStandard("LVCMOS33")),
    ("seven_segment", 2, Pins("PMOD1A:2"), IOStandard("LVCMOS33")),
    ("seven_segment", 3, Pins("PMOD1A:3"), IOStandard("LVCMOS33")),
    ("seven_segment", 4, Pins("PMOD1A:4"), IOStandard("LVCMOS33")),
    ("seven_segment", 5, Pins("PMOD1A:5"), IOStandard("LVCMOS33")),
    ("seven_segment", 6, Pins("PMOD1A:6"), IOStandard("LVCMOS33")),
    ("seven_segment", 7, Pins("PMOD1A:7"), IOStandard("LVCMOS33")),
]

seven_segment_pmod_1b = [
    ("seven_segment", 0, Pins("PMOD1B:0"), IOStandard("LVCMOS33")),
    ("seven_segment", 1, Pins("PMOD1B:1"), IOStandard("LVCMOS33")),
    ("seven_segment", 2, Pins("PMOD1B:2"), IOStandard("LVCMOS33")),
    ("seven_segment", 3, Pins("PMOD1B:3"), IOStandard("LVCMOS33")),
    ("seven_segment", 4, Pins("PMOD1B:4"), IOStandard("LVCMOS33")),
    ("seven_segment", 5, Pins("PMOD1B:5"), IOStandard("LVCMOS33")),
    ("seven_segment", 6, Pins("PMOD1B:6"), IOStandard("LVCMOS33")),
    ("seven_segment", 7, Pins("PMOD1B:7"), IOStandard("LVCMOS33")),
]