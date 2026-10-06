import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class PixelModel:
    def __init__(self, model_name: str, max_new_tokens: int = 256):
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None

    def load(self) -> None:
        if self.model is not None:
            return
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        kwargs = {}
        if self.device == "cuda":
            kwargs.update(dtype=torch.float16, device_map="auto")
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, **kwargs)
        if self.device == "cpu":
            self.model.to(self.device)
        self.model.eval()

    def generate(self, messages: list[dict], temperature: float = 0.7, top_p: float = 0.9) -> str:
        self.load()
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.inference_mode():
            output = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=temperature > 0,
                temperature=max(temperature, 0.01),
                top_p=top_p,
                repetition_penalty=1.05,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        new_tokens = output[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    def info(self) -> dict:
        return {"model": self.model_name, "device": self.device, "loaded": self.model is not None}
