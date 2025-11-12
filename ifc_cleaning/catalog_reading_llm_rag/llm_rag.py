from openai import OpenAI
from pydantic import BaseModel



def summarise_OpenAi(text, max_word, api_key):

  class Summary(BaseModel):
    summary: list[str]

  client = OpenAI(
      api_key=api_key,
  )

  response = client.beta.chat.completions.parse(
      model="gpt-4o-mini",
       messages = [
      {"role": "user", "content": f"Summarise {text} and generate {max_word} keywords from the text in the orignal language"},
      ],
      response_format= Summary
  )

  outout = response.choices[0].message.parsed
  return outout

def get_embedding(text, api_key, model="text-embedding-ada-002", dimensions = 384):

  client = OpenAI(
      api_key=api_key,
  )

  response = client.embeddings.create(
      input=text,
      model="text-embedding-3-small",
      dimensions=dimensions
  )

  return response.data[0].embedding