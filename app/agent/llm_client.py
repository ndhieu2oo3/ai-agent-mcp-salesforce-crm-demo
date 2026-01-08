import requests

class LLMClient:
    def __init__(self, base_url, model):
        """
        base_url: http://localhost:8001
        model: Qwen3-4B-Instruct-2507
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.model = model

    def chat(self, system_prompt, user_prompt, temperature=0.8, top_p=0.95, repetition_penalty=1.1):

        url = f"{self.base_url}/v1/chat/completions"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "top_p": top_p,
            "repetition_penalty": repetition_penalty
        }

        headers = {
            "Content-Type": "application/json"
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()

        data = resp.json()
        return data["choices"][0]["message"]["content"]
    
    
