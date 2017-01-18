from django.shortcuts import render
from django.http import HttpResponse
from py2neo import Graph
import openpyxl

#graph = Graph('http://neo4j:letsgowings@10.0.0.10:7474/db/data/')
graph = Graph('http://neo4j:letsgowings@localhost:7474/db/data/')

# Create your views here.
def index(request):
	result=graph.cypher.execute('match (a:CT) return a.version as version')
	return render(request,'CTVag/index.html',{'Versions':result})

def dbcodelists(request):
	global chosenversion
	global FirstCodeListQuery
	chosenversion=request.GET['CTVersions']
	FirstCodeListQuery=graph.cypher.execute('match (a:CT {version:"'+chosenversion+'"})-[r1:ContainsCodeList]->(b:CodeList) \
		with collect({Name:b.Name, Parent:b.OID,OID:b.OID,AliasName:b.AliasName,child:b.child,DataType:b.DataType}) as rows \
		match (a:CodeList)-[r2:BasedOn]->(b:CodeList)<-[r3:ContainsCodeList]-(c:CT {version:"'+chosenversion+'"}) \
		with rows+collect({Name:a.Name, Parent:b.OID,OID:a.OID,AliasName:a.AliasName,child:a.child,DataType:b.DataType}) as allrows \
		unwind allrows as row with row.Name as Name,row.Parent as ParentOID,row.OID as OID,row.AliasName as AliasName,row.child as child, \
		row.DataType as DataType return Name,ParentOID,OID,AliasName,child,DataType order by ParentOID,child')
	return render(request,'CTVag/dbcodelists.html',{'CodeLists':FirstCodeListQuery,'MyVersion':chosenversion,'Selected':'[]'})

def ChildrenCL(request):
	# Put all the checked codelists into the SelectedCodeLists list
	global SelectedCodeLists
	SelectedCodeLists=[]
	for k,v in request.POST.iteritems():
		if k[0:2] == 'c_':
			SelectedCodeLists.append(k[2:])

	# Now determine which button was clicked
	for k,v in request.POST.iteritems():
		print request.POST.items()
		if k == "XLOutput":
			if SelectedCodeLists:
				wb = openpyxl.Workbook()
				sheet = wb.active
				sheet.title = "Codelists"
				sheet['A1'] = 'ID'
				sheet['B1'] = 'Name'
				sheet['C1'] = 'NCI Codelist Code'
				sheet['D1'] = 'Data Type'
				sheet['E1'] = 'Order'
				sheet['F1'] = 'Term'
				sheet['G1'] = 'NCI Term Code'
				sheet['H1'] = 'Decoded Value'
				row = 1
				for x in SelectedCodeLists:
					result = graph.cypher.execute('match (a:CT {version:"'+chosenversion+'"})-[*1..2]->(b:CodeList {OID:"'+x+'"})- \
						[r2:ContainsCodeListItem]->(c:CodeListItem) return b.OID,b.AliasName,b.DataType,c.CodedValue, \
						c.AliasName,c.Decode order by c.CodedValue')
					print 'RESULT'
					print result
					order=1
					for x1 in result:
						row = row+1
						sheet.cell(row=row,column=1).value=x1[0]
						sheet.cell(row=row,column=2).value=x1[0]
						sheet.cell(row=row,column=3).value=x1[1]
						sheet.cell(row=row,column=4).value=x1[2]
						sheet.cell(row=row,column=5).value=order
						sheet.cell(row=row,column=6).value=x1[3]
						sheet.cell(row=row,column=7).value=x1[4]
						sheet.cell(row=row,column=8).value=x1[5]
						order = order + 1
				filename = 'ct-'+datetime.now().isoformat()+'.xlsx'
				wb.save(filename)


		elif k == "XMLOutput":
			return render(request,'CTVag/test.html',{'Items':k})

		# A codelist button was clicked to create a child
		elif k[0:2] == 's_':
			# Get the codelist items of the chosen codelist
			codelistitems=graph.cypher.execute('match (a:CT {version:"'+chosenversion+'"})-[*1..2]-(b:CodeList {OID:"'+k[2:]+'"})-[:ContainsCodeListItem]->(c:CodeListItem) \
				return b.OID as OID,b.child as child,b.Extensible as extensible,b.Name as name,b.AliasName as CLalias,b.DataType as DataType, \
				c.CodedValue as codedvalue,c.Decode as decode')
			child=codelistitems[0][1]
			nextchild=child+1
			if child == 0:
				return render(request,'CTVag/childrencl.html',{'Items':codelistitems,'ParentOID':codelistitems[0][0],'ParentExt':codelistitems[0][2],\
					'ParentName':codelistitems[0][3],'ParentAlias':codelistitems[0][4],'NextChild':nextchild,'DataType':codelistitems[0][5]})
			else:
				parentcodelist=graph.cypher.execute('match (a:CT{version:"'+chosenversion+'"})-[r1:ContainsCodeList]->(b:CodeList)<-[r2:BasedOn]-(c:CodeList {OID:"'+k[2:]+'"}) \
					return b.OID as parentOID,b.Extensible as parentext,b.Name as parentname,b.AliasName as parentalias,b.DataType as DataType')
				return render(request,'CTVag/childrencl.html',{'Items':codelistitems,'ParentOID':parentcodelist[0][0],'ParentExt':parentcodelist[0][1],\
					'ParentName':parentcodelist[0][2],'ParentAlias':parentcodelist[0][3],'NextChild':nextchild,'DataType':parentcodelist[0][4]})

		elif k == "NewCodeList":
			return render(request,'CTVag/test.html',{'Items':k})

def Back2DBCodeList(request):
	print request.POST
	print "SELECTEDCODELISTS: "
	print SelectedCodeLists
	if request.POST['submit'] == 'Save':
		nextchildstr=str(request.POST['NextChild'])

		# Create a CodeList node
		tx=graph.cypher.begin()
		statement = 'match (a:CT{version:"'+chosenversion+'"})-[r:ContainsCodeList]->(b:CodeList {OID:"'+request.POST['ParentOID']+'"}) with b \
			create (c:CodeList {OID:"'+request.POST['ParentOID']+nextchildstr+'", DataType:"'+request.POST['DataType']+'", Name:"'+request.POST['ParentName']
		if request.POST['newname']:
			statement=statement+'- '+request.POST['newname'] 
		statement=statement+'", Child: '+nextchildstr+', AliasName: "'+request.POST['Alias']+'", Extensible: "'+request.POST['Extensible']+'"})-[r2:BasedOn]->(b) with c '

		# Create the CodeListItem nodes and relationships to the CodeList node
		firstitem=True 
		for k,v in request.POST.iteritems():
			# Relationships to already-existing codelist items
			if k[0:2] == 'c_':
				if not firstitem:
					statement=statement+' with c '
				firstitem=False
				statement=statement+'match (:CT{version:"'+chosenversion+'"})-[:ContainsCodeList]->(:CodeList {OID:"'+request.POST['ParentOID']+'"}) \
					-[:ContainsCodeListItem]->(d:CodeListItem {CodedValue:"'+k[2:]+'"}) with c,d create (c)-[:ContainsCodeListItem]->(d) '
			# Creation of and Relationships to extension items
			if k[0:3] == 'ec_':
				extval=k[3:]
				if not firstitem:
					statement=statement+' with c '
				firstitem=False
				statement=statement+'create (c)-[:ContainsCodeListItem]->(:CodeListItem {CodedValue:"'+extval+'", '
				if request.POST['e_'+extval]:
					statement=statement+'Decode:"'+request.POST['e_'+extval]+'", '
				statement=statement+'extendedValue:"Yes"}) '

		tx.append(statement)
		tx.commit()
		print "STATEMENT"
		print statement

		NewCodeListQuery=graph.cypher.execute('match (a:CT {version:"'+chosenversion+'"})-[r1:ContainsCodeList]->(b:CodeList) \
			with collect({Name:b.Name, Parent:b.OID,OID:b.OID,AliasName:b.AliasName,child:b.child,DataType:b.DataType}) as rows \
			match (a:CodeList)-[r2:BasedOn]->(b:CodeList)<-[r3:ContainsCodeList]-(c:CT {version:"'+chosenversion+'"}) \
			with rows+collect({Name:a.Name, Parent:b.OID,OID:a.OID,AliasName:a.AliasName,child:a.child,DataType:b.DataType}) as allrows \
			unwind allrows as row with row.Name as Name,row.Parent as ParentOID,row.OID as OID,row.AliasName as AliasName,row.child as child, \
			row.DataType as DataType return Name,ParentOID,OID,AliasName,child,DataType order by ParentOID,child')

		return render(request,'CTVag/dbcodelists.html',{'CodeLists':NewCodeListQuery,'MyVersion':chosenversion,'Selected':SelectedCodeLists})

	else:
		return render(request,'CTVag/dbcodelists.html',{'CodeLists':FirstCodeListQuery,'MyVersion':chosenversion,'Selected':SelectedCodeLists})

