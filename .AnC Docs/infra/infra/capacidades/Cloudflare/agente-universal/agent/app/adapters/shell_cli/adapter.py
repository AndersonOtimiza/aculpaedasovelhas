import os
import shlex
import subprocess
from typing import Any, Dict, Optional


class ShellAdapter:
   def __init__(self, policy=None) -> None:  # policy reservado para uso futuro
      self.policy = policy

   def actions(self) -> list[str]:
      return ["run"]

   def execute(self, action: str, **kwargs: Any) -> Dict[str, Any]:
      if action != "run":
         return {"ok": False, "message": f"Acao nao suportada: {action}"}

      command = self._resolve_command(kwargs)
      if not command:
         return {"ok": False, "message": "Nenhum comando definido"}

      cwd = kwargs.get("cwd", "/workspace")
      env = os.environ.copy()
      extra_env = kwargs.get("env", {})
      if extra_env:
         env.update({key: str(value) for key, value in extra_env.items()})

      process = subprocess.run(  # pylint: disable=subprocess-run-check
         command,
         cwd=cwd,
         capture_output=True,
         text=True,
         env=env,
         shell=isinstance(command, str),
      )

      return {
         "returncode": process.returncode,
         "stdout": process.stdout,
         "stderr": process.stderr,
      }

   def _resolve_command(self, kwargs: Dict[str, Any]) -> Optional[Any]:
      template = kwargs.get("command_template")
      command_args = str(kwargs.get("command_args", "")).strip()
      if template:
         rendered = template.format(args=command_args)
         return rendered if kwargs.get("raw", False) else shlex.split(rendered)

      cmd = kwargs.get("cmd")
      if isinstance(cmd, list):
         return cmd
      if isinstance(cmd, str):
         return shlex.split(cmd)
      return None
