import os
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class LLMAssistant:
    def __init__(self):
        # We need an OpenAI API key.
        self.api_key = os.environ.get('OPENAI_API_KEY_CHAT') or os.environ.get('OPENAI_API_KEY')
        if self.api_key:
            self.llm = ChatOpenAI(temperature=0.2, api_key=self.api_key, model="gpt-4o")
        else:
            self.llm = None
        self.output_parser = StrOutputParser()

    def answer_question(self, question, profile_data, job_description=""):
        """
        Uses the LLM to answer a free-text question based on the user's profile and the job description.
        It detects the language of the job description/question and responds in the same language (English or Chinese).
        """
        if not self.llm:
            return "Please provide an OpenAI API key in the environment variables to use the AI assistant."

        system_prompt = """You are an expert career assistant helping a user apply for a job.
You have been provided with the user's profile and the job description.
The user is asked a free-text question on the application form.
Your task is to answer the question professionally on behalf of the user, using ONLY the information from their profile.
Do not invent facts.

CRITICAL INSTRUCTION ON LANGUAGE:
- If the question or job description is in Chinese, you MUST answer in Chinese.
- If the question or job description is in English, you MUST answer in English.
- Always output JUST the answer to the question. Do not add conversational filler like "Here is the answer:".

User Profile:
{profile}

Job Description:
{job_desc}
"""
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Question on the application: {question}")
        ])

        chain = prompt_template | self.llm | self.output_parser

        try:
            import json
            profile_str = json.dumps(profile_data, indent=2, ensure_ascii=False)
            response = chain.invoke({
                "profile": profile_str,
                "job_desc": job_description,
                "question": question
            })
            return response.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"
