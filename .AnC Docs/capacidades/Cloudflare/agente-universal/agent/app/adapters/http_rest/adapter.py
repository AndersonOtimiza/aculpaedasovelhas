import json
from typing import Any, Dict, Optional

import requests


class HTTPAdapter:
   def actions(self) -> list[str]:
      return ["request"]

   def execute(self, action: str, **kwargs: Any) -> Dict[str, Any]:
      if action != "request":
         return {"ok": False, "message": f"Acao nao suportada: {action}"}

      method = (kwargs.get("method", "GET") or "GET").upper()
      url = kwargs.get("url") or kwargs.get("base_url")
      headers: Dict[str, str] = dict(kwargs.get("headers") or {})
      body: Optional[Dict[str, Any]] = kwargs.get("body")

      auth = None
      if "basic_auth" in kwargs:
         basic = kwargs["basic_auth"]
         if basic.get("user"):
            auth = (basic.get("user"), basic.get("pass"))
      if "bearer_token" in kwargs and kwargs["bearer_token"]:
         headers = {**headers, "Authorization": f"Bearer {kwargs['bearer_token']}"}

      response = requests.request(
         method,
         url,
         headers=headers,
         json=None if method == "GET" else body,
         timeout=90,
         auth=auth,
      )
      try:
         data = response.json()
      except json.JSONDecodeError:
         data = {"text": response.text}

      return {"status": response.status_code, "data": data, "headers": dict(response.headers)}
