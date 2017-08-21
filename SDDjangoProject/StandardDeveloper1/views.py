from django.shortcuts import render
from django.http import HttpResponse
from py2neo import Graph
import openpyxl
from datetime import datetime

#graph = Graph('http://neo4j:letsgowings@10.0.0.10:7474/db/data/')
graph = Graph('http://neo4j:letsgowings@localhost:7474/db/data/')

# Create your views here.
def index(request):
	currentstandards=graph.cypher.execute('match (a:Standard) return a.name as standard')
	currentstudies=graph.cypher.execute('match (a:Study) return a.name as study')
	return render(request,'StandardDeveloper1/index.html',{'Standards':currentstandards,'Studies':currentstudies})

def dfnew(request):
	global parentmodel
	global study
	global parentstandard

	indexchoice=request.GET['indexchoice']
	if indexchoice == 'newstudy':
		study=request.GET["newstudyname"]
		parentstandard=request.GET['standards']
		# Create a node for the new study and attach it to the standard to which the parent is attached
		tx = graph.cypher.begin()
		tx.append(' match (a:Standard {name:"'+parentstandard+'"}) create (c:Study {Name:"'+study+'"})-[:BasedOn]->(a)')
		tx.commit()
		# Find the model to which the parent standard is attached and attach the new standard to it
		# parentmodelRL=graph.cypher.execute('match (a:Standard {name:"'+parentstandard+'"})-[:BasedOn]->(b:Model) return b.name as name')
		# parentmodel=parentmodelRL[0][0]
		# Get data sets from parent standard
		parentdatasetsRL=graph.cypher.execute('match (a:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(c:ItemGroupDef) return c.Name as name')
		# parentdatasetsLIST=[]
		# for x in parentdatasetsRL:
		# 	parentdatasetsLIST.append(x[0])
		return render(request,'StandardDeveloper1/datasets.html',{'Study':study,'AddDatasets':parentdatasetsRL,'StudyDatasets':''})

def modds(request):
	for k,v in request.GET.iteritems():
		if k == 'add_BDS':
			DSClass="BASIC DATA STRUCTURE"
			modelitemdefs = graph.cypher.execute('match (:Model {name:"'+parentmodel+'"})-[:ItemGroupRef]->(:ItemGroupDef {Name:"'+DSClass+'"})- \
				[r:ItemRef]->(b:ItemDef) return b.Name as Name,b.OID as OID order by r.OrderNumber')
			return render(request,'StandardDeveloper1/vars1.html',{'Itemdefs':modelitemdefs,'Name':'','Label':'','Class':DSClass,'Structure':'One record per parameter per time point per subject',\
				'Reference':'No','Repeating':'Yes'})

		elif k == 'add_Occur':
			DSClass="OCCURRENCE DATA STRUCTURE"
			modelitemdefs = graph.cypher.execute('match (:Model {name:"'+parentmodel+'"})-[:ItemGroupRef]->(:ItemGroupDef {Name:"'+DSClass+'"})- \
				[r:ItemRef]->(b:ItemDef) return b.Name as Name,b.OID as OID order by r.OrderNumber')
			return render(request,'StandardDeveloper1/vars1.html',{'Itemdefs':modelitemdefs,'Name':'','Label':'','Class':DSClass,'Structure':'One record per occurrence per subject',\
				'Reference':'No','Repeating':'Yes'})

		elif k == 'add_ADSL':
			# adslprops = graph.cypher.execute('match (:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(a:ItemGroupDef {Name:"ADSL"})-[r:ItemRef]->(b:ItemDef), (a)-[:BasedOn]->(c:ItemGroupDef) \
			# 	return a.Name as IGDName,a.Label as Label,a.Repeating as Repeating,a.Reference as Reference,a.Structure as Structure,a.Purpose as Purpose,c.Name as Class,b.Name as Name,b.OID as OID order by r.OrderNumber')
			adslprops = graph.cypher.execute('match (:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(a:ItemGroupDef {Name:"ADSL"})-[:BasedOn]->(c:ItemGroupDef) \
				return a.Name as IGDName,a.Label as Label,a.Repeating as Repeating,a.Reference as Reference,a.Structure as Structure,a.Purpose as Purpose,c.Name as Class')
			#return render(request,'StandardDeveloper1/vars1.html',{'Itemdefs':adslprops})
			return render(request,'StandardDeveloper1/mdds.html',{'Study':study,'mdds':adslprops,'readonly':'Y'})

		elif k[0:4] == 'add_':
			# Get dataset attributes and variables
			dataset=k[4:]
			dsitemdefs = graph.cypher.execute('match (:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(a:ItemGroupDef {Name:"'+dataset+'"})- \
				[r:ItemRef]->(b:ItemDef) return a.Label as Label,a.Structure as Structure,a.Repeating as Repeating,a.Reference as Reference, \
				b.Name as Name,b.OID as OID order by r.OrderNumber')
			# Get the dataset class
			DSClassRL = graph.cypher.execute('match (a:ItemGroupDef {Name:"'+dataset+'"})-[r:BasedOn]->(b:ItemGroupDef) return b.Name')
			DSClass=DSClassRL[0][0]

			# Now get model variables
			modelitemdefs = graph.cypher.execute('match (:Model {name:"'+parentmodel+'"})-[:ItemGroupRef]->(:ItemGroupDef {Name:"'+DSClass+'"})- \
				[r:ItemRef]->(b:ItemDef) return b.Name as Name,b.OID as OID order by r.OrderNumber')
			return render(request,'StandardDeveloper1/vars2.html',{'Itemdefs1':dsitemdefs,'Itemdefs2':modelitemdefs,'Name':dataset,'Class':DSClass, \
				'Structure':dsitemdefs[0][1],'Label':dsitemdefs[0][0],'Repeating':dsitemdefs[0][2],'Reference':dsitemdefs[0][3]})

		elif k[0:7] == 'remove_':
			pass
		elif k[0:5] == 'edit_':
			pass

		elif k == 'Export':
			# Get standard data sets
			getStandardDS()
			# Get standard variables
			standardvarsRL = graph.cypher.execute('match (a:Standard {name:"'+standard+'"})-[:ItemGroupRef]->(b:ItemGroupDef)-[r:ItemRef]->(c:ItemDef) \
				return r.OrderNumber as OrderNumber,b.Name as DSName,c.Name as VarName,c.Label,c.DataType,c.MaxLength as Length,r.Mandatory as \
				Mandatory,c.CodeList as CodeList,c.Origin as Origin,r.MethodOID as MethodOID,c.Predecessor as Predecessor order by b.Name,r.OrderNumber')
			# Create Excel workbook
			wb = openpyxl.Workbook()
			sheet = wb.active
			sheet.title = "Datasets"
			sheet['A1'] = 'Dataset'
			sheet['B1'] = 'Description'
			sheet['C1'] = 'Class'
			sheet['D1'] = 'Structure'
			sheet['E1'] = 'Purpose'
			sheet['F1'] = 'Key Variables'
			sheet['G1'] = 'Repeating'
			sheet['H1'] = 'Reference Data'
			sheet['I1'] = 'Comment'
			row = 1
			for x1 in standarddatasetsRL:
				row = row+1
				sheet.cell(row=row,column=1).value=x1[0]
				sheet.cell(row=row,column=2).value=x1[1]
				sheet.cell(row=row,column=3).value=x1[5]
				sheet.cell(row=row,column=4).value=x1[3]
				sheet.cell(row=row,column=5).value="Analysis"
				sheet.cell(row=row,column=7).value=x1[2]
				sheet.cell(row=row,column=8).value=x1[4]

			vars = wb.create_sheet('Variables')
			vars['A1'] = 'Order'
			vars['B1'] = 'Dataset'
			vars['C1'] = 'Variable'
			vars['D1'] = 'Label'
			vars['E1'] = 'Data Type'
			vars['F1'] = 'Length'
			vars['G1'] = 'Significant Digits'
			vars['H1'] = 'Format'
			vars['I1'] = 'Mandatory'
			vars['J1'] = 'Codelist'
			vars['K1'] = 'Origin'
			vars['L1'] = 'Pages'
			vars['M1'] = 'Method'
			vars['N1'] = 'Predecessor'
			vars['O1'] = 'Role'
			vars['P1'] = 'Comment'
			row=1
			lastds=''
			for x1 in standardvarsRL:
				if x1["DSName"] == lastds:
					order=order+1
				else:
					order=1
				row=row+1
				lastds=x1["DSName"]
				vars.cell(row=row,column=1).value=order
				vars.cell(row=row,column=2).value=x1["DSName"]
				vars.cell(row=row,column=3).value=x1["VarName"]
				vars.cell(row=row,column=4).value=x1["c.Label"]
				vars.cell(row=row,column=5).value=x1["c.DataType"]
				vars.cell(row=row,column=6).value=x1["Length"]
				vars.cell(row=row,column=9).value=x1["Mandatory"]
				vars.cell(row=row,column=10).value=x1["Codelist"]
				vars.cell(row=row,column=11).value=x1["Origin"]
				vars.cell(row=row,column=13).value=x1["MethodOID"]
				vars.cell(row=row,column=14).value=x1["Predecessor"]

			filename = standard+'-'+datetime.now().isoformat()+'.xlsx'
			wb.save(filename)

			return render(request,'StandardDeveloper1/datasets.html',{'Standard':standard,'AddDatasets':parentdatasetsLIST, \
				'StandardDatasets':standarddatasetsRL,'Message':'Standard '+standard+' has been saved to '+filename})

def predlist(request):


	
def modvar(request):
	print "POST: "
	print request.POST 
	if request.POST['submit'] == 'Save':
		# Create a data set and attach it to the Standard with ItemGroupRef relationship and to ItemGroupDef under the model with a BasedOn relationship
		tx=graph.cypher.begin()
		statement = 'match (b:Standard {name:"'+standard+'"}) \
			create (a:ItemGroupDef {Name:"'+request.POST['DSName']+'", Label:"'+request.POST['DSLabel']+'", Structure:"'+request.POST['DSStructure']+'", \
			Repeating:"'+request.POST['DSRepeat']+'", IsReferenceData:"'+request.POST['DSIsRef']+'"})<-[:ItemGroupRef]-(b) \
			with a,b match (b)-[:BasedOn]->(c:Model)-[:ItemGroupRef]->(d:ItemGroupDef {Name:"'+request.POST['DSClass']+'"}) create (a)-[:BasedOn]->(d) with a,d '

		# Create itemdefs and itemref relationships to the itemgroupdef.  Get ItemRef properties from the properties of the ItemRef that goes back to the model
		firstitem=True 
		newvarorder=1000
		for k,v in request.POST.iteritems():
			# Relationships to model itemdefs
			if k[0:2] == 'm_':
				if not firstitem:
					statement=statement+' with a,d '
				firstitem=False
				statement=statement+'match (b:ItemDef {OID:"'+k[2:]+'"})-[r2:ItemRef]-(d) create (a)-[r1:ItemRef]->(b) set r1=r2 '
			# Relationships to dataset itemdefs
			if k[0:2] == 'd_':
				if not firstitem:
					statement=statement+' with a,d '
				firstitem=False
				statement=statement+'match (b:ItemDef {OID:"'+k[2:]+'"})-[r2:ItemRef]-(:ItemGroupDef {Name:"'+request.POST['DSName']+'"}) \
					<-[:ItemGroupRef]-(:Standard {name:"'+parentstandard+'"}) create (a)-[r1:ItemRef]->(b) set r1=r2 '
			# itemdefs for custom variables and relationships to them.
			if k[0:2] == 'n_':
				varname=k[2:]
				newvarorder=newvarorder+1
				if not firstitem:
					statement=statement+' with a,d '
				firstitem=False
				statement=statement+'create (a)-[:ItemRef {OrderNumber:'+str(newvarorder)+'}]->(b:ItemDef {Name:"'+varname+'", Label:"'+request.POST['nh_'+varname]+'", \
				 OID:"ID.'+standard+'.'+request.POST['DSName']+'.'+varname+'"})'
		print 'STATEMENT: '+statement
		tx.append(statement)
		tx.commit()

		getStandardDS()
		return render(request,'StandardDeveloper1/datasets.html',{'Standard':standard,'AddDatasets':parentdatasetsLIST,'StandardDatasets':standarddatasetsRL})
		#return HttpResponse('Hello World')

def getStandardDS():
	global parentdatasetsLIST
	global standarddatasetsRL

	standarddatasetsLIST=[]
	standarddatasetsRL=graph.cypher.execute('match (a:Standard {name:"'+standard+'"})-[:ItemGroupRef]->(b:ItemGroupDef)-[:BasedOn]->(c:ItemGroupDef) \
		return b.Name as Name,b.Label as Label,b.Repeating as Repeating,b.Structure as Structure,b.IsReferenceData as IsReferenceData,c.Name as Class')
	for x in standarddatasetsRL:
		standarddatasetsLIST.append(x[0])

	parentdatasetsRL=graph.cypher.execute('match (a:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(c:ItemGroupDef) return c.Name as name')
	parentdatasetsLIST=[]
	for x in parentdatasetsRL:
		if x[0] not in standarddatasetsLIST:
			parentdatasetsLIST.append(x[0])

