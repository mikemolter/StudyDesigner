import openpyxl
from py2neo import Graph
from py2neo.packages.httpstream import http
http.socket_timeout = 9999

wb = openpyxl.load_workbook('ct-sdtm-ncievs-2016-06-24.xlsx')
ct = wb.get_sheet_by_name('SDTM Terminology 2016-06-24')
#ct = wb['SDTM Terminology 2016-06-24']

graph = Graph('http://neo4j:letsgowings@10.0.0.10:7474/db/data/')
tx = graph.cypher.begin()

tx.append('CREATE (ct:CT {version: "2016-06-24"})')

clipropnames=['AliasName','CodedValue','Synonym','Definition','Decode']
clicolumns=[1,5,6,7,8]
clpropnames=['AliasName','Extensible','Name','OID','Synonym','Definition','PreferredTerm']
clcolumns=[1,3,4,5,6,7,8]

#for row in range(2,ct.max_row+1):
#for row in range(2,18579):
for row in range(2,100):
    firstproperty=True
    if ct.cell(row=row,column=2).value:
        statement='MERGE (cli:CodeListItem {'
        for col in range(len(clipropnames)):
            if not firstproperty:
                statement=statement+', '
            statement=statement+clipropnames[col]+': "'+str(ct.cell(row=row,column=clicolumns[col]).value)+'"'
            firstproperty=False
        statement=statement+'}) WITH cli MATCH (cl:CodeList {Aliasname: "'+str(ct.cell(row=row,column=2).value)+'"}) CREATE (cl)-[r:ContainsCodeListItem]->(cli)'
    else:
        statement='CREATE (cl:CodeList {'
        for col in range(len(clpropnames)):
            if not firstproperty:
                statement=statement+', '
            statement=statement+clpropnames[col]+': "'+str(ct.cell(row=row,column=clcolumns[col]).value)+'"'
            firstproperty=False
        statement=statement+'})'
    tx.append(statement)
tx.commit()
