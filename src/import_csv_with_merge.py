import os
import sys
import pandas as pd
from itertools import islice
import re

from glob import glob
from neo4j import GraphDatabase
from dotenv import load_dotenv
import numpy as np

load_dotenv()


def df_parser_node(df):
    for i in df.iterrows():
        props = i[1].dropna().to_dict()
        props["id"] = str(props["id"])
        yield props

def df_parser_edge(df):
    for i in df.iterrows():
        props = i[1].dropna().to_dict()
        source = str(props.pop('source'))
        target = str(props.pop('target'))
        yield (source, props, target)

def index_nodes(node_type, name):
	with GraphDatabase.driver(os.getenv('NEO4J_URL'), auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))) as driver:
		with driver.session(database="neo4j") as session:
			tx = session.begin_transaction()
			try:
				tx.run("CREATE CONSTRAINT unique_id_%s IF NOT EXISTS  FOR (n:%s) REQUIRE n.id IS UNIQUE"%(name, node_type))
				tx.run("CREATE INDEX index_id_%s IF NOT EXISTS  FOR (n:%s) ON (n.id)"%(name, node_type))
				tx.run("CREATE INDEX index_label_%s IF NOT EXISTS  FOR (n:%s) ON (n.label)"%(name, node_type))
				tx.commit()
			except Exception as e:
				print(e)
				tx.rollback()
			finally:
				tx.close()

def ingest_node(node_type, nodes, limit=10000):
	success = True
	with GraphDatabase.driver(os.getenv('NEO4J_URL'), auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))) as driver:
		with driver.session(database="neo4j") as session:
			skip = 0
			print("Ingesting: %s"%(node_type))
			while skip < len(nodes):
				batch = nodes[skip: skip+limit]
				tx = session.begin_transaction()
				try:
					query = '''
						UNWIND $batch as map
						MERGE (n:%s)
						SET n = map
					'''%(node_type)
					tx.run(query, {"batch": batch})
					skip += limit
					tx.commit()
				except Exception as e:
					print("Error rolling back...")
					print("Exception", e)
					tx.rollback()
					success = False
					break
				finally:
					tx.close()
			else:
				success = True			
	return success

def ingest_edges(relation, meta, source, target, edges, limit=10000):
	success = True
	with GraphDatabase.driver(os.getenv('NEO4J_URL'), auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))) as driver:
		with driver.session(database="neo4j") as session:
			skip = 0
			while skip < len(edges):
				batch = edges[skip: skip+limit]
				tx = session.begin_transaction()
				try:
					query = '''
						UNWIND $batch as row
						MERGE (n:%s), (m:%s)
						WHERE n.id=row.source and m.id=row.target
						CREATE (n)-[r:%s {
							%s
						}]->(m)

					'''%(source, target, relation, meta)
					tx.run(query, {"batch": batch})
					skip += limit
					tx.commit()
				except Exception as e:
					print("Error rolling back...")
					print("Exception", e)
					tx.rollback()
					success = False
					break
				finally:
					tx.close()
			else:
				success = True			
	return success

directories = sys.argv[1:]

node_pattern = "(?P<directory>.+)/(?P<label>.+)\.(?P<entity>.+)\.csv"
edge_pattern = "(?P<directory>.+)/(?P<source_type>.+)\.(?P<relation>.+)\.(?P<target_type>.+)\.(?P<entity>.+)\.csv"
for directory in directories:
    directory = directory.strip()
    for filename in glob(directory + "/*.nodes.csv"):
        match = re.match(node_pattern, filename).groupdict()
        entity = match["entity"]
        label = match["label"].replace("_", " ")
        print(label)
        n = label
        if len(label.split(" ")) > 1:
          n = "`%s`"%label
        # add constraint
        index_nodes(n, label.replace(" ", "_")) 
        print("Ingesting %s nodes..."%label)
        node_dict = {}
        df = pd.read_csv(filename)
        for k,row in df.iterrows():
          v = {}
          for i,j in row.items():
            if type(j) == str:
              v[i] = j
            elif not np.isnan(j):
              v[i] = int(j)
          if k not in node_dict:
            node_dict[k] = {
              "id": k,
              **v
            }
          else:
            node_dict[k] = {
              **node_dict[k],
              **v
            }
        print(n)
        r = ingest_node(n, list(node_dict.values()))

    for filename in glob(directory + "/*.edges.csv"):
        match = re.match(edge_pattern, filename).groupdict()
        entity = match["entity"]
        source_type = "`%s`"%match["source_type"]
        relation = "`%s`"%match["relation"]
  
        print("Ingesting %s edges..."%relation)
        target_type = "`%s`"%match["target_type"]
        # add constraint
        df = pd.read_csv(filename)
        meta = []
        for col in df.columns:
          if (col not in ["source", 'target']):
            meta.append("%s:row.%s"%(col, col))
        edges = list(df.to_dict(orient="index").values())
        print("Ingesting %d %s relation"%(len(edges), relation))
        meta = ",\n".join(meta)
        success = ingest_edges(relation, meta, source_type, target_type, edges)
        if not success:
          break