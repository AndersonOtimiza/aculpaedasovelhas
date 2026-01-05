import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from app.core.intent import IntentRouter
from app.core.registry import Registry
from app.core.policy import Policy

load_dotenv()

# Diretório de logs
LOG_DIR = "/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)
API_LOG_PATH = os.path.join(LOG_DIR, "agent-api.log")
EXEC_LOG_PATH = os.path.join(LOG_DIR, "agent-exec.log")

def _append_api_log(entry: dict) -> None:
   try:
      with open(API_LOG_PATH, "a", encoding="utf-8") as handle:
         handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
   except Exception:  # pylint: disable=broad-except
      pass

app = FastAPI(title="Agente Universal", version="1.0.0")

router = IntentRouter()
policy = Policy()
registry = Registry(policy=policy)


class CommandIn(BaseModel):
   text: str
   target: str | None = None
   adapter: str | None = None
   args: dict | None = None
   dry_run: bool | None = None


@app.get("/health")
def health() -> dict:
   return {"status": "ok", "adapters": list(registry.adapters.keys())}


@app.post("/command")
def command(ci: CommandIn) -> dict:
   try:
      plan = router.plan(ci.text, ci.target, ci.adapter)
      if ci.args:
         plan["args"] = {**plan.get("args", {}), **ci.args}

      dry_run_default = os.getenv("DRY_RUN", "false").lower() == "true"
      dry_run = ci.dry_run if ci.dry_run is not None else dry_run_default

      adapter_name = plan.get("adapter")
      action = plan.get("action")
      args = plan.get("args", {})
      target = plan.get("target")

      adapter = registry.get(adapter_name)
      if not adapter:
         return {"ok": False, "message": f"Adapter nao encontrado: {adapter_name}", "plan": plan}

      target_conf = registry.get_target(target)
      if target_conf:
         args = registry.enrich_with_target(args, target_conf)

      policy.validate(adapter_name, action, args, bypass=os.getenv("ALLOWLIST_BYPASS", "false").lower() == "true")

      if dry_run:
         response = {"ok": True, "dry_run": True, "plan": plan, "args": args}
         _append_api_log({"event": "dry_run", "response": response})
         return response

      result = adapter.execute(action, **args)
      response = {"ok": True, "plan": plan, "result": result}
      _append_api_log({"event": "execute", "response": response})
      return response
   except Exception as exc:  # pylint: disable=broad-except
      raise HTTPException(status_code=500, detail=str(exc)) from exc
