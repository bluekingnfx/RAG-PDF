import typing as ty
import os
from streamlit.runtime.uploaded_file_manager import UploadedFile
from pathlib import Path
from uuid import uuid4
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.chains.combine_documents import create_stuff_documents_chain #type:ignore
from langchain.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain #type:ignore
from langchain_ollama import ChatOllama

""" from langchain_core.vectorstores import VectorStoreRetriever """

collection_name:str = os.environ.get('CHROMA_COLLECTION_NAME')#type:ignore

class UploadClass():
    def __init__(self, uploaded_file:UploadedFile, model:str='all-MiniLM-L6-v2'):
        self.result:bool | str = False
        self.splitted_docs:ty.List[Document] = [Document(page_content='')]
        self.uploaded_file = uploaded_file
        self.model = model
        self.saveIntoTempFolder()
        if isinstance(self.result, str) == False: #type:ignore
            self.createDocs()
        if isinstance(self.result, str) == False: #type:ignore
            self.vectorizeAndUploadToStore()
        
    def saveIntoTempFolder(self):
        fileName = uuid4().hex
        tempFolder = Path(f'temp')
        tempFolder.mkdir(exist_ok=True)
        tempfilePath = tempFolder / f'{fileName}.pdf'
        with open(tempfilePath,'wb') as f:
            try:
                f.write(self.uploaded_file.read())
                self.file_path = tempfilePath
            except Exception as e:
                self.result = f'File not uploaded, problem with uploading in the file system. {e}'
    
    def createDocs(self):
        try:
            pdfLoader = PyPDFLoader(self.file_path,extract_images=False,extraction_mode='plain')
            docs = pdfLoader.load()
            rcs = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap = 100
            )
            splitted_docs = rcs.split_documents(docs)
            self.splitted_docs = splitted_docs
        except Exception as e:
            self.result = f'File not uploaded, try again, problem with creating documents, {e}'
        finally: 
            if Path(self.file_path).exists() == True:
                os.remove(self.file_path)
    
    def vectorizeAndUploadToStore(self):
        try:
            embedder = HuggingFaceEmbeddings(
                model = self.model
            )
            chroma = Chroma(
                collection_name = collection_name,
                embedding_function=embedder,
                persist_directory='data/db',
                create_collection_if_not_exists = True
            )
            chroma.add_documents(self.splitted_docs)
            self.result = True
        except Exception as e:
            self.result = f"File not uploaded, try again, Problem with vectoring the input {e}"



class ProcessTheQuestion():
    def __init__(self,role:str='LLM Expert',model:str='all-MiniLM-L6-v2'):
        self.result:str|bool = False
        self.role = role
        self.model = model
        self.prompt_template()
        self.loadTheDb()
        
    def prompt_template(self):
        chtTemplate = ChatPromptTemplate(
            messages=[
                ('system','You experienced {role}'),
                ('human', 'What is your name?'),
                ('ai','My Name is domain knower, I primarily help you with Deep learning.'),
                ('human', '''Given this context: {context}
                Please answer this question: {input}'''),
            ],
            input_variables = ['input','context'],
            partial_variables = {
                'role': self.role
            }
        )
        chtModel = ChatOllama(
            model = 'gemma3:1b',
        )
        self.docChain  = create_stuff_documents_chain(chtModel,chtTemplate)
    def loadTheDb(self):
        
            embedder = HuggingFaceEmbeddings(
                model = self.model
            )
            vectorStore = Chroma(
                collection_name = collection_name,
                embedding_function=embedder,
                persist_directory='data/db',
                create_collection_if_not_exists = True
            )
            self.retriever = vectorStore.as_retriever()
        
    def processPrompt(self,prompt:str) -> ty.Dict[str, ty.Any] | None:
        try:
            retriever_chain = create_retrieval_chain(self.retriever,self.docChain) #type: ignore
            result = retriever_chain.invoke({ "input": prompt})  #type:ignore
            self.result = True
            return {
                'answer': result.get("answer", ''), #type:ignore
                "source_documents": result.get("context", []), #type:ignore
            }
        except Exception as e:
            self.result = f"There is error in ProcessPrompt : {str(e)}"