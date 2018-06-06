import sys
from py2neo import Graph

graph = Graph('http://neo4j:letsgowings@localhost:7474/db/data/')

result=graph.cypher.execute('match (a:CodeList {Name:"Epoch"})--(b:CodeListItem) return b.CodedValue')

for x in result:
	print x[0]