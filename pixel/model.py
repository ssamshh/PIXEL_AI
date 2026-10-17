"""Optional local Transformers and OpenAI-compatible model backends."""
import json
import threading
import urllib.error
import urllib.request
from .config import settings


class PixelModel:
    """Lazy model adapter. Provider is selected with PIXEL_MODEL_PROVIDER=local|openai."""
    def __init__(self, model_name=None, max_new_tokens=256):
        self.model_name = model_name or settings.model_name
        self.max_new_tokens = max_new_tokens
        self.provider = settings.model_provider if settings.model_provider in {"local", "openai", "openai_compatible"} else "local"
        self.tokenizer = None
        self.model = None
        self.device = "cpu"
        self._lock = threading.Lock()
        self.last_error = None

    def load(self):
        if self.provider != "local" or self.model is not None:
            return
        with self._lock:
            if self.model is not None:
                return
            try:
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                kwargs = {"device_map": "auto", "torch_dtype": torch.float16} if self.device == "cuda" else {}
                self.model = AutoModelForCausalLM.from_pretrained(self.model_name, **kwargs)
                if self.device == "cpu":
                    self.model.to("cpu")
                self.model.eval()
            except Exception as exc:
                self.last_error = f"{type(exc).__name__}: {exc}"
                raise RuntimeError("Could not load the local model. Check internet/model settings and install optional AI dependencies. Details: " + self.last_error) from exc

    def generate(self, messages, temperature=0.7):
        if self.provider in {"openai", "openai_compatible"}:
            return self._generate_remote(messages, temperature)
        self.load()
        import torch
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.inference_mode():
            output = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens,
                do_sample=temperature > 0, temperature=max(temperature, 0.01), top_p=0.9,
                repetition_penalty=1.05, pad_token_id=self.tokenizer.eos_token_id)
        return self.tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()

    def _generate_remote(self, messages, temperature):
        payload = {"model": self.model_name, "messages": messages,
                   "temperature": max(0.0, min(2.0, float(temperature))),
                   "max_tokens": self.max_new_tokens, "stream": False}
        headers = {"Content-Type": "application/json"}
        if settings.api_key:
            headers["Authorization"] = "Bearer " + settings.api_key
        request = urllib.request.Request(settings.api_base_url + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=settings.request_timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            answer = data["choices"][0]["message"]["content"]
            if isinstance(answer, list):
                answer = "\n".join(part.get("text", "") for part in answer if isinstance(part, dict))
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("The model endpoint returned an empty answer.")
            self.last_error = None
            return answer.strip()
        except (urllib.error.URLError, TimeoutError, KeyError, IndexError, ValueError, json.JSONDecodeError) as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            raise RuntimeError("OpenAI-compatible model request failed. Check PIXEL_API_BASE_URL, PIXEL_MODEL, API key, and endpoint status. Details: " + self.last_error) from exc

    def info(self):
        if self.provider == "local":
            loaded = self.model is not None
            available = loaded
        else:
            loaded = False
            available = bool(settings.api_base_url and self.model_name)
        return {"provider": self.provider, "model": self.model_name, "device": self.device,
                "loaded": loaded, "available": available, "last_error": self.last_error,
                "endpoint_configured": bool(settings.api_base_url) if self.provider != "local" else None}
