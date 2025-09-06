# coder.py

# Add this parameter to the API call in coder.py:
max_tokens=100,  # Limits the response length

class Coder:
    def __init__(self, deepseek_client):
        self.client = deepseek_client

    def generate_code(self, prompt):
        """
        Sends the prompt to the DeepSeek Coder model and returns the generated code.
        """
        print(f"[Coder] Generating code for prompt: '{prompt}'")

        # This call is sent to DeepSeek's API because the client is configured with base_url="https://api.deepseek.com/v1"
        response = self.client.chat.completions.create(
            model="deepseek-coder",  # Specifically using DeepSeek's Coder model
            messages=[
                {"role": "system", "content": "You are an expert Python developer. Generate clean, efficient, and correct code based on the user's request. Return only the code, without explanations or markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        generated_code = response.choices[0].message.content
        print(f"[Coder] Code generation complete.")
        return generated_code