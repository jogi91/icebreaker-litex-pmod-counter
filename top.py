#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 Sean Cross <sean@xobs.io>
# Copyright (c) 2018 David Shah <dave@ds0.me>
# Copyright (c) 2020 Piotr Esden-Tempski <piotr@esden.net>
# Copyright (c) 2020 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# The iCEBreaker is the first open source iCE40 FPGA development board designed for teachers and
# students: https://www.crowdsupply.com/1bitsquared/icebreaker-fpga

# This target file provides a minimal LiteX SoC for the iCEBreaker with a CPU, its ROM (in SPI Flash),
# its SRAM, close to the others LiteX targets. A more complete example of LiteX SoC for the iCEBreaker
# with more features, examples to run C/Rust code on the RISC-V CPU and documentation can be found
# at: https://github.com/icebreaker-fpga/icebreaker-litex-examples

import argparse

from litex.soc.cores.clock import iCE40PLL
from litex.soc.cores.led import LedChaser
from litex.soc.cores.ram import Up5kSPRAM
from litex.soc.cores.spi_flash import SpiFlash
from litex.soc.cores.uart import UARTWishboneBridge

from litex.soc.integration.builder import *
from litex.soc.integration.soc_core import *

from litex_boards.platforms import icebreaker

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

import platformExtensions
from DipSwitchPmod import DipSwitchPmod
from SevenSegmentPmod import SevenSegmentPmod

kB = 1024
mB = 1024*kB

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_por = ClockDomain(reset_less=True)

        # # #

        # Clk/Rst
        clk12 = platform.request("clk12")
        rst_n = platform.request("user_btn_n")

        # Power On Reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(ClockSignal())
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.submodules.pll = pll = iCE40PLL(primitive="SB_PLL40_PAD")
        self.comb += pll.reset.eq(~rst_n) # FIXME: Add proper iCE40PLL reset support and add back | self.rst.
        pll.register_clkin(clk12, 12e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq, with_reset=False)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~por_done | ~pll.locked)
        platform.add_period_constraint(self.cd_sys.clk, 1e9/sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    # mem_map = {**SoCCore.mem_map, **{"spiflash": 0x80000000}}
    # Statically-define the memory map, to prevent it from shifting across various litex versions.
    SoCCore.mem_map = {
        "sram":             0x10000000,  # (default shadow @0xa0000000)
        "spiflash":         0x20000000,  # (default shadow @0xa0000000)
        "csr":              0xe0000000,  # (default shadow @0x60000000)
        "vexriscv_debug":   0xf00f0000,
    }

    def __init__(self, bios_flash_offset, sys_clk_freq=int(24e6), blink_leds=False, enable_dip=False, enable_7seg=False, enable_control=False, **kwargs):
        platform = icebreaker.Platform()

        # Disable Integrated ROM/SRAM since too large for iCE40 and UP5K has specific SPRAM.
        kwargs["integrated_sram_size"] = 0
        kwargs["integrated_rom_size"]  = 0

        if enable_control:
            kwargs["cpu_type"] = "vexriscv"
            # Set CPU variant / reset address
            if "cpu_variant" not in kwargs:
                kwargs["cpu_variant"] = "lite+debug"

            kwargs["cpu_reset_address"] = self.mem_map["spiflash"] + bios_flash_offset
        else:
            kwargs["with_timer"] = False;

        # Select the crossover UART according to https://wishbone-utils.readthedocs.io/en/latest/wishbone-tool/
        kwargs["uart_name"] = "crossover"


        # SoCCore ----------------------------------------------------------------------------------
        SoCMini.__init__(self, platform, sys_clk_freq,
            ident          = "PMod adjustable Counter",
            ident_version  = True,
            **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        if enable_control: # Add supporting hardware for the cpu
            # UP5K has single port RAM, which is a dedicated 128 kilobyte block.
            # Use this as CPU RAM.
            spram_size = 128 * 1024
            self.submodules.spram = Up5kSPRAM(size=spram_size)
            self.register_mem("sram", self.mem_map["sram"], self.spram.bus, spram_size)

            # The litex SPI module supports memory-mapped reads, as well as a bit-banged mode
            # for doing writes.
            spiflash_size = 16 * 1024 * 1024
            self.submodules.spiflash = SpiFlash(platform.request("spiflash4x"), dummy=6, endianness="little")
            self.register_mem("spiflash", self.mem_map["spiflash"], self.spiflash.bus, size=spiflash_size)
            self.add_csr("spiflash")

            # Add ROM linker region
            self.add_memory_region("rom", self.mem_map["spiflash"] + bios_flash_offset,
                                   spiflash_size - bios_flash_offset, type="cached+linker")

        # No CPU, use Serial to control Wishbone bus
        self.submodules.serial_bridge = UARTWishboneBridge(platform.request("serial"), sys_clk_freq)
        self.add_wb_master(self.serial_bridge.wishbone)

        if blink_leds:
            # Leds -------------------------------------------------------------------------------------
            platform.add_extension(icebreaker.break_off_pmod)
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        if enable_dip:
            # DIP-Switches
            platform.add_extension(platformExtensions.dip_pmod_1b)
            self.submodules.dip = DipSwitchPmod(
                pads = platform.request_all("dip_switch")
            )

        if enable_7seg:
            # 7 Segment
            platform.add_extension(platformExtensions.seven_segment_pmod_1a)
            self.submodules.seven_segment = SevenSegmentPmod(
                pads = platform.request_all("seven_segment"),
                sys_clk_freq = sys_clk_freq
            )

# Flash --------------------------------------------------------------------------------------------

def flash(build_dir, build_name, bios_flash_offset):
    from litex.build.lattice.programmer import IceStormProgrammer
    prog = IceStormProgrammer()
    prog.flash(0x00000000,        f"{build_dir}/gateware/{build_name}.bin")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on iCEBreaker")
    parser.add_argument("--build",               action="store_true", default=True, help="Build bitstream")
    parser.add_argument("--load", action="store_true", default=False, help="Load bitstream")
    parser.add_argument("--flash",               action="store_true", default=True, help="Flash Bitstream")
    parser.add_argument("--sys-clk-freq",        default=21e6,        help="System clock frequency (default: 24MHz)")
    parser.add_argument("--bios-flash-offset",   default=0x40000,     help="BIOS offset in SPI Flash (default: 0x40000)")
    parser.add_argument("--blinky", action="store_true", help="Enable blinky LED block")
    parser.add_argument("--dip", action="store_true", help="Enable dip switch block")
    parser.add_argument("--sevenseg", action="store_true", help="Enable 7 segment LED block")
    parser.add_argument("--control", action="store_true", help="Enable control block (will enable --dip and --7seg, and instantiates a cpu)")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    # Override some default arguments
    args.doc = True
    args.csr_csv = "build/csr.csv"
    print(args)


    soc = BaseSoC(bios_flash_offset=args.bios_flash_offset, sys_clk_freq=int(float(args.sys_clk_freq)), blink_leds=args.blinky, enable_dip=args.dip, enable_7seg=args.sevenseg, enable_control=args.control, **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bin"))

    if args.flash:
        flash(builder.output_dir, soc.build_name, args.bios_flash_offset)

if __name__ == "__main__":
    main()
