import openpyxl
from py2neo import Graph

wb = openpyxl.load_workbook('Initial SDTM 1.4 IG 3.2.xlsx')
model_datasets = wb.get_sheet_by_name('SDTM 1.4 domains')
model_vars = wb.get_sheet_by_name('SDTM 1.4 Variables')
model_refs = wb.get_sheet_by_name('SDTM 1.4 itemrefs')
model_specs = wb.get_sheet_by_name('SDTM 1.4 Mapping Specs')

graph = Graph()
tx = graph.cypher.begin()

# Import dataset level metadata
#statement = "CREATE (mc:ModelClass {name: {C1}, transpose: {C2}})"
#tx.append("CREATE (m:Model {name:'SDTM', version:'1.4'})")

#for row in range(2,model_datasets.max_row+1):
  #tx.append(statement,{"C1":model_datasets.cell(row=row,column=1).value, "C2":model_datasets.cell(row=row,column=2).value})

#tx.append("MATCH (m:Model),(mc:ModelClass) CREATE (m)-[r:ContainsClass]->(mc) RETURN r")

# Import variable level metadata
propertynames = ['Name', 'OID', 'Label', 'SASType', 'Length', 'DataType', 'Role', 'Codelist', 'Dictionary', 'Origin','VLMFlag']
for row in range(2,model_vars.max_row+1):
    statement = "CREATE (mv:ModelItem {"
    firstproperty = True
    for col in range(len(propertynames)):
        if model_vars.cell(row=row,column=col+1).value:
            if col !=7 and col !=8:
                if not firstproperty:
                    statement=statement+', '
                statement=statement+propertynames[col]+': "'+str(model_vars.cell(row=row,column=col+1).value)+'" '
                firstproperty = False
    statement=statement+'})'
    tx.append(statement)

# Import relationships
propertynames = ['ItemOID', 'Order', 'VariableRequired', 'Mandatory', 'Key', 'MapSpecOID']
for row in range(2,model_refs.max_row+1):
    statement = "MATCH (n:ModelClass {name: '"+model_refs.cell(row=row,column=1).value+"'}), (m:ModelItem {Name: '"+model_refs.cell(row=row,column=2).value+"'}) "
    statement = statement+"CREATE (n) - [r:ContainsModelItem {"
    firstproperty = True
    for col in range(len(propertynames)):
        if model_refs.cell(row=row,column=col+3).value:
            if not firstproperty:
                statement=statement+', '
            statement=statement+propertynames[col]+': "'+str(model_refs.cell(row=row,column=col+3).value)+'" '
            firstproperty = False
    statement=statement+'}] -> (m)'
    tx.append(statement)

# Import Methods

for row in range(2,model_specs.max_row+1):
    statement = "CREATE (mc:Method {SpecOID: {C1}, MapSpec: {C2}}) WITH mc "
    #Find the variable nodes that are to link to the Methods
    statement=statement+"MATCH ()-[r:ContainsModelItem {MapSpecOID: {C1}}]->(n) "
    # Create the relationship from the variable node to the method node
    statement=statement+"MERGE (n)-[r1:UsesSpec]->(mc)"

    tx.append(statement,{"C1":model_specs.cell(row=row,column=1).value, "C2":model_specs.cell(row=row,column=2).value})

# Create relationships to codelists
for row in range(2,model_vars.max_row+1):
    codelist=str(model_vars.cell(row=row,column=8).value)
    if codelist:
        statement='MATCH (ct:CodeList {OID : "'+codelist+'"}), (mv1:ModelItem {OID: "'+str(model_vars.cell(row=row,column=2).value)+'"}) MERGE (mv1)-[r1:UsesCodeList]->(ct) '
        tx.append(statement)
        #print statement

tx.commit()
