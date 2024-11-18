# Import m5 library and available SimObjects
import m5
from m5.objects import *

# Add the caches scripts to our path
m5.util.addToPath("../../")

from learning_gem5.part1.caches import *

import argparse

parser = argparse.ArgumentParser(description='A simple system with 2-level cache.')
parser.add_argument("--binary", default="", type=str,
                    help="Path to the binary to execute.")
parser.add_argument("--l1i_size",
                    help=f"L1 instruction cache size. Default: 16kB.")
parser.add_argument("--l1d_size",
                    help="L1 data cache size. Default: Default: 64kB.")
parser.add_argument("--l2_size",
                    help="L2 cache size. Default: 256kB.")

options = parser.parse_args()

# Create the system, setup clock and power for clock
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Memory configuration
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("8192MB")]

system.cpu = [X86MinorCPU(cpu_id=i) for i in range(2)]
system.membus = SystemXBar()

# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

# Setting up memory controller to connect to the membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

if(options.binary == ""):
    binary = "configs/assignments/MSCS531_Assignment6/daxpy"
else:
    binary = options.binary

# Setting up workload
system.workload = SEWorkload.init_compatible(binary)

process = Process(executable=binary, cmd = [binary, 2])

# Simulation Configuration
root = Root(full_system=False, system=system)
for cpu in root.system.cpu:
    cpu.workload = process
    cpu.createThreads()
    cpu.createInterruptController()
    cpu.interrupts[0].pio = root.system.membus.mem_side_ports
    cpu.interrupts[0].int_requestor = root.system.membus.cpu_side_ports
    cpu.interrupts[0].int_responder = root.system.membus.mem_side_ports

    # Create a memory bus, a coherent crossbar, in this case
    cpu.l2bus = L2XBar()

    # Create an L1 instruction and data cache
    cpu.icache = L1ICache()
    cpu.dcache = L1DCache()

    # Connect the instruction and data caches to the CPU
    cpu.icache.connectCPU(cpu)
    cpu.dcache.connectCPU(cpu)

    # Hook the CPU ports up to the l2bus
    cpu.icache.connectBus(cpu.l2bus)
    cpu.dcache.connectBus(cpu.l2bus)

    # Create an L2 cache and connect it to the l2bus
    cpu.l2cache = L2Cache()
    cpu.l2cache.connectCPUSideBus(cpu.l2bus)

    # Connect the L2 cache to the L3 bus
    cpu.l2cache.connectMemSideBus(root.system.membus)

m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()

print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

