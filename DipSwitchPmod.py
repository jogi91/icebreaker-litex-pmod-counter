#
# For now: simply display the State of 8 pads in a status register
#
# One could for example imagine extending this with a debouncing functionality or limiting the values based on a control register

from litex.soc.interconnect.csr import *
from migen.genlib.cdc import MultiReg


class DipSwitchPmod(Module, AutoCSR):
    def __init__(self, pads):
        assert len(pads) == 8
        self.pads = pads
        self._in = CSRStatus(
            size=len(pads),
            fields=[
                CSRField(
                    "S1", size=1, offset=0, description="Dip switch state 1"
                ),
                CSRField(
                    "S2", size=1, offset=1, description="Dip switch state 2"
                ),
                CSRField(
                    "S3", size=1, offset=2, description="Dip switch state 3"
                ),
                CSRField(
                    "S4", size=1, offset=3, description="Dip switch state 4"
                ),
                CSRField(
                    "S5", size=1, offset=4, description="Dip switch state 5"
                ),
                CSRField(
                    "S6", size=1, offset=5, description="Dip switch state 6"
                ),
                CSRField(
                    "S7", size=1, offset=6, description="Dip switch state 7"
                ),
                CSRField(
                    "S8", size=1, offset=7, description="Dip switch state 8"
                ),
            ],
            name="STATE",
            description="Contains the current value of the PMod DIP Switch bank.",
        )
        self.specials += MultiReg(pads, self._in.status)


