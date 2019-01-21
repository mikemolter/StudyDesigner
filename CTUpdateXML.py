from lxml import etree
import pandas as pd 
import numpy as np
from py2neo import Graph
from py2neo.packages.httpstream import http
http.socket_timeout = 9999
filename='TestCT.xml'
CTVersion = '2017-03-31'
nsmap={'ns':"http://www.cdisc.org/ns/odm/v1.3",'nci':"http://ncicb.nci.nih.gov/xml/odm/EVS/CDISC"}
graph = Graph('http://neo4j:neo4j@localhost:7474/db/data/')

# Read in the new XML file with the latest version of CT
doc = etree.parse(filename)
root = doc.getroot()
CVList=[]
OIDList=[]

# For each codelist read...
for x in doc.findall('.//ns:CodeList', namespaces=nsmap):
    # Get the value of the OID attribute
    OID = x.xpath('@OID')
    Name = x.xpath('@Name')
    DataType = x.xpath('@DataType')
    AliasName = x.path('@nci:ExtCodeID')
    Extensible = x.path('@nci:CodeListExtensible')
    PreferredTerm = x.findtext('nci:PreferredTerm', namespaces=nsmap)
    Synonym = x.findtext('nci:CDISCSynonym', namespaces=nsmap)
    Definition = x.findtext('ns:Description/ns:TranslatedText', namespaces=nsmap)
    # For each enumerated item within the codelist...
    for y in x.findall('.//ns:EnumeratedItem', namespaces=nsmap):
        # Get the CodedValue attribute
        CodedValue=y.get('CodedValue')
        # Append OID and CodedValue attributes to lists
        OIDList.append(OID)
        CVList.append(CodedValue)
# Create a dictionary of OID and CodedValue values
dict = {'OID':OIDList, 'CodedValue':CVList}
# Turn the dictionary into a dataframe
newdf = pd.DataFrame(dict)
print 'NEWDF: '
print newdf

# Get the current database
results=graph.cypher.execute('match (a:CT)-[:ContainsCodeList]->(b:CodeList)-[:ContainsCodeListItem]->(c:CodeListItem) \
    where b.OID in ["ACN","SIXMW1TC"] return a.version as version,"CL."+b.AliasName+"."+b.OID as OID,c.CodedValue as CodedValue')

# Convert into a dataframe
olddf = pd.DataFrame(results.records,columns=results.columns)
print 'OLDDF: '
print olddf

# Merge the current database (OLDDF) with the new version (NEWDF)
all = pd.merge(olddf,newdf,how='outer',on=['OID','CodedValue'],indicator=True)
# Create the boolean variable MATCH whose value is True on records that came from OLDDF and NEWDF
all2=all.assign(match=lambda x: x._merge=='both')
print 'ALL2: '
print all2
# Get the minimum value of the MATCH boolean for each VERSION/OID combination
all3=all2.groupby(['version','OID'],as_index=False).agg({'match':np.min})
print 'ALL3: '
print all3
# Keep only the rows where the minimum value is True
# These rows represent codelists from the new version that are exactly the same as they are for some version in the current database    
all4=all3[all3['match']==True]
print 'ALL4: '
print all4
# Merge the list of new codelists that match existing codelists back with the new set of codelists
all5=pd.merge(newdf,all4,how='left',on='OID',indicator=True)
all5.version=all5.version.fillna('NA')
print 'ALL5: '
print all5
# Now update the database
tx=graph.cypher.begin()
tx.append('create (:CT {version:"'+CTVersion+'"}) ')
for name,group in all5.groupby(['OID','version']):
    print name
    print group['version']
    statement1='match (a:CT {version:"'+CTVersion+'"}) '
    if name[1]=='NA':
        statement1=statement1+'create (a)-[:ContainsCodeList {Child:0}]->(b:CodeList {OID:"'+name[0].split('.')[2]+'"}) '
        print 'STATEMENT1: '
        print statement1
        tx.append(statement1)
        for index, row in group.iterrows():
            statement=' match (b:CodeList {OID:"'+name[0].split('.')[2]+'"})'
            statement=statement+' merge (c:CodeListItem {CodedValue:"'+row['CodedValue']+'"}) '
            statement=statement+' create (b)-[:ContainsCodeListItem]->(c) '
            print 'STATEMENT: '
            print statement
            tx.append(statement)
            #statement=statement+'create (b)-[:ContainsCodeListItem]->(:CodeListItem {CodedValue:"'+row['CodedValue']+'"}) '
    else:
        statement=statement1+', (b:CT {version:"'+name[1]+'"})-[:ContainsCodeList]->(c:CodeList {OID:"'+name[0].split('.')[2]+'"}) create (a)-[:ContainsCodeList {Child:0}]->(c) '
        print 'STATEMENT: '
        print statement
        tx.append(statement)

tx.commit()

        # if pd.notnull(row['version']):
        #     print 'MISSING'
        # else:
        #     print 'NON-MISSING'
#graph = Graph('http://neo4j:letsgowings@10.0.0.10:7474/db/data/')
# graph = Graph()
# tx = graph.cypher.begin()

# tx.append('CREATE (ct:CT {version: "2016-06-24"})')

# clipropnames=['AliasName','CodedValue','Synonym','Definition','Decode']
# clicolumns=[1,5,6,7,8]
# clpropnames=['AliasName','Extensible','Name','OID','Synonym','Definition','PreferredTerm']
# clcolumns=[1,3,4,5,6,7,8]

#for row in range(2,ct.max_row+1):
#for row in range(2,18579):
# for row in range(2,100):
#     firstproperty=True
#     if ct.cell(row=row,column=2).value:
#         statement='MERGE (cli:CodeListItem {'
#         for col in range(len(clipropnames)):
#             if not firstproperty:
#                 statement=statement+', '
#             statement=statement+clipropnames[col]+': "'+str(ct.cell(row=row,column=clicolumns[col]).value)+'"'
#             firstproperty=False
#         statement=statement+'}) WITH cli MATCH (cl:CodeList {Aliasname: "'+str(ct.cell(row=row,column=2).value)+'"}) CREATE (cl)-[r:ContainsCodeListItem]->(cli)'
#     else:
#         statement='CREATE (cl:CodeList {'
#         for col in range(len(clpropnames)):
#             if not firstproperty:
#                 statement=statement+', '
#             statement=statement+clpropnames[col]+': "'+str(ct.cell(row=row,column=clcolumns[col]).value)+'"'
#             firstproperty=False
#         statement=statement+'})'
#     tx.append(statement)
# tx.commit()

# Changes to make
# 1) Add relationships from version to codelist
# 2) Add child=0 to all parents
# 3) Add DataType=text to all parents
# 4) Add YESONLY BasedOn relationship with child=1
# 5) Use Decode flag to differentiate which codelists use enumerateditems and which don't
