import subprocess
import os
import json
from abc import ABC, abstractmethod

# Define Adapter locally since the base module is not available
class Adapter(ABC):
    """Base adapter class for all adapters."""

    def __init__(self, id: str, name: str, config: dict):
        self.id = id
        self.name = name
        self.config = config

    @abstractmethod
    def execute(self, command: str, subcommand: str, args: list = None):
        """Execute a command using this adapter."""
        pass

LOG_DIR = "/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)
EXEC_LOG_PATH = os.path.join(LOG_DIR, "agent-exec.log")

def _append_exec_log(entry: dict) -> None:
    try:
        with open(EXEC_LOG_PATH, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:  # pylint: disable=broad-except
        pass

class NodeCLIAdapter(Adapter):
    def __init__(self, id: str, name: str, config: dict):
        super().__init__(id, name, config)
        self.agent_script_path = config.get("agent_script_path", "wp-intelligent-agent.js")
        self.env_file_path = config.get("env_file_path", "../../.env.op")

    def execute(self, command: str, subcommand: str, args: list = None):
        """
        Executa um comando no wp-intelligent-agent.js usando op run.

        :param command: O comando principal (ex: 'wp', 'cf').
        :param subcommand: O subcomando (ex: 'post create', 'cache purge').
        :param args: Uma lista de argumentos para o subcomando.
        """
        if args is None:
            args = []

        # Constrói o comando base
        base_cmd = [
            "op", "run",
            "--env-file", self.env_file_path,
            "--",
            "node", self.agent_script_path,
            command,
        ]

        # Adiciona o subcomando e os argumentos
        full_cmd = base_cmd + subcommand.split() + args

        try:
            print(f"🚀 Executando comando Node.js: {' '.join(full_cmd)}")
            _append_exec_log({"event": "start", "cmd": full_cmd})

            process = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                cwd="/app"
            )

            output = process.stdout or ""
            if process.stderr:
                output += "\n--- STDERR ---\n" + process.stderr

            status = "success" if process.returncode == 0 else "error"
            result = {"status": status, "code": process.returncode, "output": output}
            _append_exec_log({"event": "finish", "result": result})
            return result

        except FileNotFoundError:
            msg = "'op' ou 'node' não encontrado no PATH."
            result = {"status": "error", "output": msg}
            _append_exec_log({"event": "error", "result": result})
            return result
        except Exception as e:  # pylint: disable=broad-except
            result = {"status": "error", "output": str(e)}
            _append_exec_log({"event": "exception", "result": result})
            return result

