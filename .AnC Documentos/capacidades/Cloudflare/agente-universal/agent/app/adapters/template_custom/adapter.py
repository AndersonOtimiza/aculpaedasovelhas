class CustomAdapterTemplate:
   def actions(self) -> list[str]:
      return ["do_something"]

   def execute(self, action: str, **kwargs):
      if action == "do_something":
         return {"ok": True, "eco": kwargs}
      return {"ok": False, "message": f"Acao nao suportada: {action}"}
