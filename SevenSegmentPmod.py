from migen import *
from migen import Signal
from migen.genlib.misc import WaitTimer

from litex.soc.interconnect.csr import *


class SevenSegmentPmod(Module, AutoCSR):
    """
    7 Segmend Pmod Module

    This module takes integers as inputs from CSR register, converts them to BCD and displays them on the configured 7segment pmod connector
    """

    def __init__(self, pads, sys_clk_freq, period=1e-3):
        self.pads = pads
        self._control = CSRStorage(
            size=1,
            reset=1,
            name="CTRL",
            fields=[
                CSRField(name="EN", size=1, offset=0, description="Global enable bit"),
            ],
            description="Control Register for 7 Segment PMod Display",
        )
        self._values = CSRStorage(
            size=8,
            reset="0",
            name="VALUE",
            fields=[
                CSRField(
                    name="digit0",
                    size=4,
                    offset=0,
                    description="Value of least significant (right) digit",
                ),
                CSRField(
                    name="digit1",
                    size=4,
                    offset=4,
                    description="Value of most significant (left) digit",
                ),
            ],
            description="""
            7 Segment data
                        
            Contains the values of the digits as an unsigned binary integer
            """,
        )

        # # #

        activeOutput = Signal(1)

        timer = WaitTimer(int(period * sys_clk_freq))
        self.comb += timer.wait.eq(~timer.done)
        self.sync += If(timer.done, activeOutput.eq(~activeOutput))

        output0 = Signal(7)
        output1 = Signal(7)

        combinedOutput = Signal(8)
        self.comb += [
            If(activeOutput, combinedOutput.eq(Cat(output0, activeOutput))).Else(
                combinedOutput.eq(Cat(output1, activeOutput))
            )
        ]

        self.submodules += BCDSegment(self._values.storage[0:4], output0), BCDSegment(
            self._values.storage[4:8], output1
        )
        self.submodules += timer

        # Enable Output based on Control register
        # LEDs are enabled via active-low signal
        self.comb += [
            If(self._control.storage == 0, pads.eq(Constant(0xFF))).Else(
                pads.eq(combinedOutput)
            )
        ]

    #     n = len(pads)
    #     chaser = Signal(n)
    #     mode = Signal(reset=_CHASER_MODE)
    #     timer = WaitTimer(int(period * sys_clk_freq / (2 * n)))
    #     self.submodules += timer
    #     self.comb += timer.wait.eq(~timer.done)
    #     self.sync += If(timer.done, chaser.eq(Cat(~chaser[-1], chaser)))
    #     self.sync += If(self._out.re, mode.eq(_CONTROL_MODE))
    #     self.comb += [
    #         If(mode == _CONTROL_MODE, pads.eq(self._out.storage)).Else(pads.eq(chaser))
    #     ]
    #
    # def add_pwm(self, default_width=512, default_period=1024, with_csr=True):
    #     from litex.soc.cores.pwm import PWM
    #
    #     self.submodules.pwm = PWM(
    #         with_csr=with_csr,
    #         default_enable=1,
    #         default_width=default_width,
    #         default_period=default_period,
    #     )
    #     # Use PWM as Output Enable for pads.
    #     self.comb += If(~self.pwm.pwm, self.pads.eq(0))


class BCDSegment(Module):
    def __init__(self, input, output):
        self.input = input
        self.output = output

        cases = {
            0x0: output.eq(~0b0111111),
            0x1: output.eq(~0b0000110),
            0x2: output.eq(~0b1011011),
            0x3: output.eq(~0b1001111),
            0x4: output.eq(~0b1100110),
            0x5: output.eq(~0b1101101),
            0x6: output.eq(~0b1111101),
            0x7: output.eq(~0b0000111),
            0x8: output.eq(~0b1111111),
            0x9: output.eq(~0b1101111),
            0xA: output.eq(~0b1110111),
            0xB: output.eq(~0b1111100),
            0xC: output.eq(~0b0111001),
            0xD: output.eq(~0b1011110),
            0xE: output.eq(~0b1111001),
            0xF: output.eq(~0b1110001),
        }

        self.comb += Case(input, cases)
