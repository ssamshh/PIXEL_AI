import threading

class PixelModel:
    """Lazy optional Transformers backend; app/API can start even before model download."""
    def __init__(self, model_name, max_new_tokens=256):
        self.model_name=model_name
        self.max_new_tokens=max_new_tokens
        self.tokenizer=None; self.model=None; self.device="cpu"
        self._lock=threading.Lock(); self.last_error=None

    def load(self):
        if self.model is not None: return
        with self._lock:
            if self.model is not None: return
            try:
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer
                self.device="cuda" if torch.cuda.is_available() else "cpu"
                self.tokenizer=AutoTokenizer.from_pretrained(self.model_name)
                kwargs={"device_map":"auto","torch_dtype":torch.float16} if self.device=="cuda" else {}
                self.model=AutoModelForCausalLM.from_pretrained(self.model_name,**kwargs)
                if self.device=="cpu": self.model.to("cpu")
                self.model.eval()
            except Exception as exc:
                self.last_error=f"{type(exc).__name__}: {exc}"
                raise RuntimeError("Could not load the local model. Check internet/model settings and install the optional AI dependencies. Details: "+self.last_error) from exc

    def generate(self, messages, temperature=0.7):
        self.load()
        import torch
        prompt=self.tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        inputs=self.tokenizer(prompt,return_tensors="pt").to(self.device)
        with torch.inference_mode():
            output=self.model.generate(**inputs,max_new_tokens=self.max_new_tokens,
                do_sample=temperature>0,temperature=max(temperature,0.01),top_p=0.9,
                repetition_penalty=1.05,pad_token_id=self.tokenizer.eos_token_id)
        return self.tokenizer.decode(output[0][inputs["input_ids"].shape[1]:],skip_special_tokens=True).strip()

    def info(self):
        return {"model":self.model_name,"device":self.device,"loaded":self.model is not None,
                "available":self.model is not None,"last_error":self.last_error}
