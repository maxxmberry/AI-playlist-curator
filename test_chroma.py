from langchain_chroma import Chroma
from langchain_core.documents import Document

# testing with fake embeddings
from langchain_core.embeddings import FakeEmbeddings
embeddings = FakeEmbeddings(size=1536)

# embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

test_docs = [
    Document(page_content="Python is a programming language.", metadata={"source": "test"}),
    Document(page_content="The capital of France is Paris.", metadata={"source": "test"}),
    Document(page_content="Machine learning is a subset of AI.", metadata={"source": "test"}),
]

vectorstore = Chroma.from_documents(test_docs, embeddings, collection_name="test")
retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

results = retriever.invoke("What programming languages exist?")
for doc in results:
    print(doc.page_content)