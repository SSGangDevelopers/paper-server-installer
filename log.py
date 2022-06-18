import subprocess
import sys


def run_command_live_output(command: str):
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    for c in iter(lambda: process.stdout.read(1), b""):
        sys.stdout.buffer.write(c)
        sys.stdout.flush()
