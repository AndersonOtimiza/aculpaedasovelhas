import json
import os
import re
from typing import Dict, List


class Policy:
   def __init__(self, path: str = "/app/policies/allowlist.json") -> None:
      self.path = path
      try:
         with open(self.path, "r", encoding="utf-8") as handle:
            self.rules: Dict[str, Dict] = json.load(handle)
      except Exception:  # pylint: disable=broad-except
         self.rules = {}

   def validate(self, adapter: str, action: str, args: Dict, *, bypass: bool = False) -> bool:
      if bypass:
         return True

      adapter_rules = self.rules.get(adapter, {})

      if adapter == "shell_cli":
         rendered_command = ""
         if (args or {}).get("cmd"):
            rendered_command = str(args.get("cmd"))
         elif (args or {}).get("command_template"):
            template = str(args.get("command_template"))
            rendered_command = template.format(args=str(args.get("command_args", "")))
         command = rendered_command.strip()
         denies: List[str] = adapter_rules.get("deny", [])
         for pattern in denies:
            if re.search(pattern, command):
               raise ValueError(f"Comando bloqueado por deny: {pattern}")
         allows: List[str] = adapter_rules.get("allowedCommands", [])
         if allows:
            if not any(re.search(pattern, command) for pattern in allows):
               raise ValueError("Comando shell nao permitido pelo allowlist.")

      if adapter == "http_rest":
         url = str((args or {}).get("url", ""))
         domains: List[str] = adapter_rules.get("allowedDomains", [])
         if domains and url:
            if not any(re.search(pattern, url) for pattern in domains):
               raise ValueError("Dominio HTTP nao permitido pelo allowlist.")

      if adapter == "browser_playwright":
         steps = (args or {}).get("steps", [])
         max_steps = int(adapter_rules.get("maxSteps", 25))
         if len(steps) > max_steps:
            raise ValueError(f"Excesso de passos no fluxo de UI: {len(steps)} > {max_steps}")

      return True
