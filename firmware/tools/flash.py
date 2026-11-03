"""Flash/verify a complete RevC HEX over SWD. Never performs automatic recovery."""
import argparse, subprocess
from pathlib import Path
from verify_build import check_hex

def quoted(value):
    return '"' + str(value).replace("\\","\\\\").replace('"','\\"').replace("$","\\$").replace("[","\\[").replace("\n","\\n") + '"'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hex",type=Path,required=True)
    parser.add_argument("--interface",choices=["cmsis-dap","jlink"],default="cmsis-dap")
    parser.add_argument("--target-config",default="target/nrf52.cfg")
    parser.add_argument("--probe-serial")
    args = parser.parse_args()
    image = args.hex.resolve(strict=True)
    check_hex(image)
    commands = ["transport select swd","adapter speed 1000","reset_config none"]
    if args.probe_serial: commands.append("adapter serial " + quoted(args.probe_serial))
    commands.extend([
        "init", "halt",
        "set fidget_part [lindex [read_memory 0x10000100 32 1] 0]",
        'if {$fidget_part != 0x00052810} {error "Target is not nRF52810; no image was written"}',
        "program " + quoted(image.as_posix()) + " verify reset exit",
    ])
    command = ["openocd","-f","interface/"+args.interface+".cfg","-f",args.target_config]
    for value in commands: command.extend(["-c",value])
    print("CR2450 must be removed; one3.0-3.3V source, common ground, verified five-pin cable.")
    subprocess.run(command,check=True)
    print("Stored image verified. Disconnect programmer power before refitting CR2450.")
if __name__ == "__main__": main()
