import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model=os.environ.get("GEMINI_EMBEDDING_MODEL"),
    google_api_key=os.environ.get("GEMINI_API_KEY")
)

vec = embeddings.embed_query("Hello world")
print(f"Dimension: {len(vec)}")
