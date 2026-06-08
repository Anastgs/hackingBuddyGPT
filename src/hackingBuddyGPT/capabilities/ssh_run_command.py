import re
from dataclasses import dataclass
from typing import Tuple
from hackingBuddyGPT.utils import SSHConnection
from hackingBuddyGPT.utils.shell_root_detection import got_root
from .capability import Capability

@dataclass
class SSHRunCommand(Capability):
    conn: SSHConnection
    timeout: int = 10
    max_output_lines: int = 50

    def describe(self) -> str:
        return "give a command to be executed and I will respond with the terminal output when running this command over SSH on the linux machine. The given command must not require user interaction. Do not use quotation marks in front and after your command."

    def get_name(self):
        return "exec_command"

    def __call__(self, command: str) -> Tuple[str, bool]:
        if command.startswith(self.get_name()):
            cmd_parts = command.split(" ", 1)
            if len(cmd_parts) == 1:
                command = ""
            else:
                command = cmd_parts[1]

        stdout, stderr, returncode = self.conn.run(command)

        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        output = ansi_escape.sub("", stdout)
        lines = output.splitlines()
        last_line = lines[-1] if lines else ""

        if len(lines) > self.max_output_lines:
            truncated = lines[:self.max_output_lines]
            output = "\n".join(truncated) + f"\n... [output tronqué: {len(lines)} lignes total, seules les {self.max_output_lines} premières affichées]"

        return output, got_root(self.conn.hostname, last_line)