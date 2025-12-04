from dotenv import load_dotenv
import os
from google import genai
from lib.auto_label.query_engine_config import build_variable_descriptions, get_prompt_template

class GEMINI_GOOGLE:
    def __init__(self):
        load_dotenv()
        self.client = genai.Client()

    def get_response(self, prompt, config=None):
        """Generate Prolog rules based on prompt and config."""
        
        # Build variable descriptions from config
        var_descriptions = build_variable_descriptions(config)
        
        # Get prompt template from config
        template = get_prompt_template(config)
        prompt_template = template.format(
            var_descriptions=var_descriptions,
            user_input=prompt
        )
        
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_template,
        )

        return response.text

if __name__ == "__main__":
    ai = GEMINI_GOOGLE()

    result = ai.get_response(prompt="ถ้าอุณหภูมิเกิน 35 องศา ให้เตือนว่า Danger")
    print(result)
