from dataclasses import dataclass
from typing import Optional, Tuple
import subprocess
import shutil
from hackingBuddyGPT.utils.configurable import configurable


@configurable("ssh", "connects to a remote host via SSH")
@dataclass
class SSHConnection:
    host: str
    hostname: str
    username: str
    password: str
    keyfilename: str
    port: int = 22

    def init(self):
        pass

    def run(self, cmd, *args, **kwargs) -> Tuple[str, str, int]:
        ssh_cmd = [
            "ssh",
            "-o", "HostKeyAlgorithms=+ssh-rsa",
            "-o", "PubkeyAcceptedKeyTypes=+ssh-rsa",
            "-o", "StrictHostKeyChecking=no",
            "-p", str(self.port),
            f"{self.username}@{self.host}",
            cmd
        ]

        if self.keyfilename and self.keyfilename != '':
            ssh_cmd.insert(2, "-i")
            ssh_cmd.insert(3, self.keyfilename)
        elif shutil.which("sshpass"):
            ssh_cmd = ["sshpass", "-p", self.password] + ssh_cmd

        try:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Timeout", -1

    def new_with(self, *, host=None, hostname=None, username=None, password=None, keyfilename=None, port=None) -> "SSHConnection":
        return SSHConnection(
            host=host or self.host,
            hostname=hostname or self.hostname,
            username=username or self.username,
            password=password or self.password,
            keyfilename=keyfilename or self.keyfilename,
            port=port or self.port,
        )
