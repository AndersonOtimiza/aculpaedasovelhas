import json
import os
import re
from typing import Dict, Optional


def _llm_available() -> bool:
   provider = os.getenv("LLM_PROVIDER", "").lower()
   if provider == "ollama":
      return bool(os.getenv("OLLAMA_BASE_URL"))
   if provider == "openai":
      return bool(os.getenv("OPENAI_API_KEY"))
   if provider == "azure_openai":
      return bool(os.getenv("AZURE_OPENAI_API_KEY")) and bool(os.getenv("AZURE_OPENAI_ENDPOINT"))
   return False


def _call_llm(prompt: str) -> str:
   provider = os.getenv("LLM_PROVIDER", "ollama").lower()
   model = os.getenv("MODEL", "llama3.1:instruct")
   try:
      from openai import OpenAI  # type: ignore

      if provider == "ollama":
         client = OpenAI(base_url=os.getenv("OLLAMA_BASE_URL"), api_key="ollama")
      elif provider == "azure_openai":
         from openai import AzureOpenAI  # type: ignore

         client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-08-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
         )
      else:
         client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

      response = client.chat.completions.create(
         model=model,
         messages=[
            {
               "role": "system",
               "content": (
                  "Voce e um planejador. Responda apenas JSON com campos: {adapter, action, target?, args{}}. "
                  "Adapters validos: http_rest, shell_cli, browser_playwright."
               ),
            },
            {"role": "user", "content": prompt},
         ],
         temperature=0.1,
      )
      return response.choices[0].message.content or ""
   except Exception:  # pylint: disable=broad-except
      return ""


def _extract_domain(text: str) -> Optional[str]:
   match = re.search(r"([a-z0-9-]+\.)+[a-z]{2,}", text.lower())
   return match.group(0) if match else None


class IntentRouter:
   def plan(self, text: str, target: Optional[str] = None, adapter: Optional[str] = None) -> Dict:
      if _llm_available():
         raw = _call_llm(
            f"Texto: {text}\nTarget preferido: {target or ''}\nAdapter preferido: {adapter or ''}"
         )
         try:
            data = json.loads(raw.strip("` \n"))
            if isinstance(data, dict) and "adapter" in data and "action" in data:
               if target:
                  data.setdefault("target", target)
               if adapter:
                  data["adapter"] = adapter
               return data
         except Exception:  # pylint: disable=broad-except
            pass

      text_lower = text.lower()
      chosen_target = target
      chosen_adapter = adapter
      chosen_action = "execute"
      args: Dict[str, object] = {}

      domain = _extract_domain(text)

      if not chosen_adapter and "cloudflare" in text_lower:
         chosen_adapter = "shell_cli"
         chosen_target = target or "cloudflare"

      if chosen_adapter == "shell_cli" and ((chosen_target or "") == "cloudflare" or "cloudflare" in text_lower):
         command_args = self._cloudflare_command_args(text_lower, domain)
         chosen_target = chosen_target or "cloudflare"
         args = {"command_args": command_args}
         chosen_action = "run"

      elif chosen_adapter == "http_rest":
         method = "GET"
         for candidate in ("get", "post", "put", "delete"):
            if re.search(rf"\b{candidate}\b", text_lower):
               method = candidate.upper()
               break
         url = ""
         url_match = re.search(r"https?://\S+", text)
         if url_match:
            url = url_match.group(0)
         args = {"method": method, "url": url, "headers": {}, "body": {}}
         chosen_action = "request"

      elif chosen_adapter == "browser_playwright":
         args = {
            "steps": [
               {"op": "navigate", "url": ""},
            ],
            "headless": True,
         }
         chosen_action = "run_steps"

      if not chosen_adapter:
         chosen_adapter = "browser_playwright"
         chosen_target = chosen_target or "default"
         args = {
            "steps": [
               {"op": "navigate", "url": ""},
            ],
            "headless": True,
         }
         chosen_action = "run_steps"

      return {
         "adapter": chosen_adapter,
         "action": chosen_action,
         "target": chosen_target or "default",
         "args": args,
      }

   def _cloudflare_command_args(self, text_lower: str, domain: Optional[str]) -> str:
      if any(keyword in text_lower for keyword in ("limpar cache", "purge", "limpe o cache")):
         zone_part = f" --zone {domain}" if domain else ""
         return f"purge{zone_part}".strip()
      if "dns" in text_lower and any(k in text_lower for k in ("listar", "list")):
         zone_part = f" --zone {domain}" if domain else ""
         return f"dns list{zone_part}".strip()
      if "dns" in text_lower and any(k in text_lower for k in ("criar", "create")):
         tipo_match = re.search(r"tipo\s+(a|cname|txt|mx|aaaa)", text_lower)
         tipo = tipo_match.group(1).upper() if tipo_match else "A"
         nome_match = re.search(r"registro\s+([a-z0-9.-]+)", text_lower)
         nome = nome_match.group(1) if nome_match else "novo"
         conteudo_match = re.search(r"para\s+ip\s+([0-9.]+)", text_lower)
         conteudo = conteudo_match.group(1) if conteudo_match else "0.0.0.0"
         zone_part = f" --zone {domain}" if domain else ""
         return f"dns create{zone_part} --type {tipo} --name {nome} --content {conteudo}".strip()
      return "--ajuda"
