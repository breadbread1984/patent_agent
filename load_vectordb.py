#!/usr/bin/python3

from absl import flags, app
from os import walk
from os.path import exists, join, splitext
from tqdm import tqdm
from langchain_neo4j import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.document_loaders import UnstructuredPDFLoader

FLAGS = flags.FLAGS

def add_options():
  flags.DEFINE_string('input_dir', default = 'patents', help = 'path to directory')
  flags.DEFINE_string('host', defalut = 'bolt://localhost:7687', help = 'neo4j host')
  flags.DEFINE_string('user', default = 'neo4j', help = 'neo4j user name')
  flags.DEFINE_string('password', default = '12345678', help = 'neo4j password')
  flags.DEFINE_string('db', default = 'patents', help = 'neo4j database')

def main(unused_argv):
  embedding = HuggingFaceEmbeddings(model_name = "intfloat/multilingual-e5-base")
  vectordb = Neo4jVector(
    embedding = embedding,
    url = FLAGS.host,
    username = FLAGS.username,
    password = FLAGS.password,
    database = FLAGS.db,
    index_name = "typical_rag",
    search_type = "hybrid",
    pre_delete_collection = True
  )
  for root, dirs, files in tqdm(walk(FLAGS.input_dir)):
    for f in files:
      stem, ext = splitext(f)
      if ext != '.pdf': continue
      loader = UnstructuredPDFLoader(join(root, f), mode = 'single', strategy = 'hi_res', languages = {'en', 'zh-cn', 'zh-tw'})
      docs = loader.load()
      for page_num, doc in enumerate(docs):
        doc.metadata['page_num'] = page_num
        doc.metadata['patent_path'] = join(root, f)
      vectordb.add_documents(docs)

if __name__ == "__main__":
  add_options()
  app.run(main)

