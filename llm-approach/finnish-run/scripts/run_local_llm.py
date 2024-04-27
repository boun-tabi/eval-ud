from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class TrendyolLLM:
    def __init__(self):
        # trendyol_Trendyol-LLM-7b-chat-v1.0
        self.model_id = 'Trendyol/Trendyol-LLM-7b-chat-v1.0'
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id)
        self.sampling_params = dict(do_sample=True, temperature=0.3, top_k=50, top_p=0.9)
        self.pipe = pipeline('conversational',
                model=self.model,
                tokenizer=self.tokenizer,
                device_map='auto',
                max_new_tokens=1024,
                repetition_penalty=1.1
               )

    def generate_output(self, user_query):
        messages = [
            {'role': 'user', 'content': user_query}
        ]
        outputs = self.pipe(messages, **self.sampling_params)
        return outputs
