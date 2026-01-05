from typing import Any, Dict, List

from playwright.sync_api import sync_playwright


class BrowserAdapter:
   def actions(self) -> list[str]:
      return ["run_steps"]

   def execute(self, action: str, **kwargs: Any) -> Dict[str, Any]:
      if action != "run_steps":
         return {"ok": False, "message": f"Acao nao suportada: {action}"}

      steps: List[Dict[str, Any]] = kwargs.get("steps", [])
      headless = bool(kwargs.get("headless", True))
      base_url = kwargs.get("base_url", "")
      results: List[Dict[str, Any]] = []

      with sync_playwright() as playwright:
         browser = playwright.chromium.launch(headless=headless)
         context = browser.new_context()
         page = context.new_page()

         for step in steps:
            operation = step.get("op")
            if operation == "navigate":
               url = step.get("url") or base_url
               page.goto(url, wait_until="domcontentloaded")
               results.append({"op": operation, "url": page.url, "status": "ok"})
            elif operation == "click":
               selector = step.get("selector")
               page.click(selector)
               results.append({"op": operation, "selector": selector, "status": "ok"})
            elif operation == "type":
               selector = step.get("selector")
               value = step.get("value", "")
               page.fill(selector, value)
               results.append({"op": operation, "selector": selector, "status": "ok"})
            elif operation == "press":
               selector = step.get("selector")
               key = step.get("key", "Enter")
               page.press(selector, key)
               results.append({"op": operation, "selector": selector, "key": key, "status": "ok"})
            elif operation == "wait_for":
               selector = step.get("selector")
               timeout = int(step.get("timeout", 30000))
               page.wait_for_selector(selector, timeout=timeout)
               results.append({"op": operation, "selector": selector, "status": "ok"})
            elif operation == "screenshot":
               path = step.get("path", "/workspace/screenshot.png")
               page.screenshot(path=path, full_page=True)
               results.append({"op": operation, "path": path, "status": "ok"})
            else:
               results.append({"op": operation, "status": "ignored", "reason": "op desconhecida"})

         context.close()
         browser.close()

      return {"steps": steps, "results": results}
