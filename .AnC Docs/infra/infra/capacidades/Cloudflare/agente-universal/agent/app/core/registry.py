import json
import os
from typing import Any, Dict, Optional

from app.adapters.http_rest.adapter import HTTPAdapter
from app.adapters.browser_playwright.adapter import BrowserAdapter
from app.adapters.shell_cli.adapter import ShellAdapter
from app.adapters.node_cli import NodeCLIAdapter


class Registry:
   def __init__(self, policy) -> None:
      self.policy = policy
      self.adapters = {
         "http_rest": HTTPAdapter(),
         "browser_playwright": BrowserAdapter(),
         "shell_cli": ShellAdapter(policy=policy),
         "node_cli": NodeCLIAdapter(
            id="node_cli", 
            name="Node.js CLI Agent", 
            config={
               "agent_script_path": "/app/wp-intelligent-agent.js",
               "env_file_path": "/app/.env.op"
            }
         ),
      }
      self.targets = self._load_targets()

   def _load_targets(self) -> Dict[str, Dict[str, Any]]:
      path = "/app/targets/targets.json"
      try:
         with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
      except Exception:  # pylint: disable=broad-except
         return {"default": {"adapter": "browser_playwright", "base_url": "https://example.com"}}

   def get(self, name: Optional[str]):
      if not name:
         return None
      return self.adapters.get(name)

   def get_target(self, name: Optional[str]) -> Optional[Dict[str, Any]]:
      if not name:
         return None
      return self.targets.get(name)

   def enrich_with_target(self, args: Dict[str, Any], target_conf: Dict[str, Any]) -> Dict[str, Any]:
      output = dict(args or {})
      if "base_url" in target_conf and not output.get("base_url"):
         output["base_url"] = target_conf["base_url"]
         if not output.get("url") and target_conf.get("base_url"):
            output["url"] = target_conf["base_url"]

      auth = target_conf.get("auth", {})
      if auth.get("type") == "basic_env":
         user = os.getenv(auth.get("user_env", "")) or ""
         password = os.getenv(auth.get("pass_env", "")) or ""
         output["basic_auth"] = {"user": user, "pass": password}
      elif auth.get("type") == "bearer_env":
         token = os.getenv(auth.get("token_env", "")) or ""
         output["bearer_token"] = token

      if target_conf.get("adapter") == "shell_cli" and target_conf.get("base_path"):
         output.setdefault("cwd", target_conf["base_path"])

      if "command_template" in target_conf:
         output["command_template"] = target_conf["command_template"]

      if target_conf.get("env"):
         env = {key: str(value) for key, value in target_conf["env"].items()}
         output["env"] = {**env, **dict(output.get("env", {}))}

      return output
