from langchain_huggingface import ChatHuggingFace , HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnableBranch, RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    task = "text-generation"
)

model = ChatHuggingFace(llm=llm)

class classifier(BaseModel):
    output : Literal["General", "Database"] = Field(description="Given the user's question, is it asking for specific data from the database, or is it a general greeting or conceptual question? Answer with 'Database' or 'General'")

parser = PydanticOutputParser(pydantic_object = classifier)

parser2 = StrOutputParser()

prompt1 = PromptTemplate(
    template="Analyze this the query and decide whether this query would require the interaction with database or it is a general query and can be answered directly without the database interaction . \n query : {query} \n {format_instruction}" ,
    input = ['query'],
    partial_variables={'format_instruction' : parser.get_format_instructions()}
)

prompt2 = PromptTemplate(
    template = "you are an ai assistant so answer the query : \n {query}",
    input = ['query']
)

query = "what is database? and tell me the temp of last 2 months from indian ocean."

classifier_chain = prompt1 | model | parser

chain1 = RunnableParallel({
    'classify' : classifier_chain,
    'query' : lambda x:x['query']
})

chain2 = RunnableBranch(
    (lambda x : x['classify'].output == 'General' , prompt2 | model | parser2),
    (RunnableLambda(lambda x: "could not find sentiment"))
)

chain = chain1 | chain2

result = chain.invoke({'query' : query})

print(result)