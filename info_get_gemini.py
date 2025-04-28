from google import genai
from typing import Literal
import os
from dotenv import load_dotenv
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch, GenerateContentResponse
import json
import re


class GeminiAPIClient:
    def __init__(
            self,
            api_key: str | None = None,
            model_name: Literal[
                "gemini-2.0-flash",
                "gemini-2.0-flash-001"] = "gemini-2.0-flash") -> None:

        if not api_key:
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def query(self, schema, context: str):
        try:
            prompt = f"""
            You are a JSON generator. You will be given a text and a schema. Your task is to extract the information from the text and generate a JSON object that matches the schema. The schema is in JSON format. The text is in markdown format.
            The text is:
            {context}.

            i will provide you with a schema.
            """
            config = GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=schema,
                temperature=0
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            results = response.parsed
            return results

        except Exception as e:
            return f"An error occurred while querying the Gemini API: {e}"

    def query_with_search(self, schema: dict, search_query: str):

        sys_instructions = f"you are smart search agent that take '\
                a schema of needed data to fill and search for info to get accurate info to fill or answer this fields: \
                take given schema"

        prompt = f"give me info about {schema['title']}: '{search_query}', \n\n response Schema: json```{schema}```"

        google_search_tool = Tool(
            google_search=GoogleSearch()
        )

        response = self.client.models.generate_content(
            model=self.model_name,

            contents=prompt,

            config=GenerateContentConfig(
                system_instruction=sys_instructions,
                tools=[google_search_tool],
                response_modalities=["TEXT"],
                temperature=0
            )
        )
        parsed = self.parse_response(response)
        return parsed

    def parse_response(self, response: GenerateContentResponse):

        try:

            response_content = ''.join(
                part.text
                for part in
                response.candidates[0].content.parts  # type: ignore
                if part.text)

            # Regular expression to find JSON blocks marked with ```json
            json_pattern = r'```json\s*({.*?})\s*```'

            # Find all matches in the string
            matches = re.findall(json_pattern, response_content, re.DOTALL)

            if not matches:
                return "No JSON object found in the string."

            return json.loads(matches[-1])

        except Exception as e:
            return f"An error occurred: {e}"
