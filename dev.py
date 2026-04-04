import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

openai_api_key = os.environ['OPENAI_API_KEY_CHAT']

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert DevOps and Platform Engineer.
            Students will ask you questions related to systems, networks,
            Linux comamnds, and internals and you need to provide the correct
            answer and help them internalize the concepts. Your name is Dev and
            you are a Systems Wizard, a real greybeard and you respond as such, but
            your verbiage is medieval for you are Dev the merlin of systems!!!!"""
        ),
        MessagesPlaceholder(variable_name="spell_input"),
    ]
)


def load_LLM():
    llm = ChatOpenAI(temperature=0.7, api_key=openai_api_key)
    return llm


llm = load_LLM()

output_parser = StrOutputParser()

st.set_page_config(page_title="Dev The DevOps Wizard", page_icon=":wizard:")
st.header("Welcome to Dev, the merlin of systems")
st.image('https://cdnb.artstation.com/p/assets/images/images/052/893/029/large/tradeandmagic-official-wizard-refined.jpg?1660917052', width='content')


def get_text():
    input_text = st.text_area(label="Enter your query for the great Dev",
                              placeholder="Present your query squire",
                              key="query")
    submitted = st.button("Submit")
    return input_text


dev_input = get_text()

st.markdown('### Ye Wizard Doth Speaks:')

if dev_input:
    chain = prompt | llm | output_parser
    generated_result = chain.invoke((
        {
            "spell_input": [
                HumanMessage(
                    content=dev_input
                ),
            ],
        }
    ))
    st.write(generated_result)
