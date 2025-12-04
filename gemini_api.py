from dotenv import load_dotenv
import os
from google import genai

class GEMINI_GOOGLE:
    def __init__(self):

        load_dotenv()
        self.client = genai.Client()

    def get_response(self, prompt):

        prompt = "Translate to First Order Logic Prolog in English (Output only code 1 rule per line, no markdown and description): {}".format(prompt)

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text

if __name__ == "__main__":
    ai = GEMINI_GOOGLE()

    result = ai.get_response(prompt="ถ้าอุณหภูมิเกิน 35 องศา ให้เตือนว่า Danger")
    print(result)
