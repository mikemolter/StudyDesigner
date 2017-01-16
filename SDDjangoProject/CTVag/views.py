from django.shortcuts import render
from django.http import HttpResponse
from py2neo import Graph
#graph = Graph('http://neo4j:letsgowings@10.0.0.10:7474/db/data/')
graph = Graph('http://neo4j:letsgowings@localhost:7474/db/data/')

# Create your views here.
def index(request):
	result=graph.cypher.execute('match (a:CT) return a.version as version')
	return render(request,'CTVag/index.html',{'Versions':result})

def dbcodelists(request):
	global chosenversion
	chosenversion=request.GET['CTVersions']
	result=graph.cypher.execute('match (a:CT {version:"'+chosenversion+'"})-[r1:ContainsCodeList]->(b:CodeList) \
		with collect({Name:b.Name, Parent:b.OID,OID:b.OID,AliasName:b.AliasName,child:b.child}) as rows \
		match (a:CodeList)-[r2:BasedOn]->(b:CodeList)<-[r3:ContainsCodeList]-(c:CT {version:"'+chosenversion+'"}) \
		with rows+collect({Name:a.Name, Parent:b.OID,OID:a.OID,AliasName:a.AliasName,child:a.child}) as allrows \
		unwind allrows as row with row.Name as Name,row.Parent as ParentOID,row.OID as OID,row.AliasName as AliasName,row.child as child \
		return Name,ParentOID,OID,AliasName,child order by ParentOID,child')
	return render(request,'CTVag/dbcodelists.html',{'CodeLists':result,'MyVersion':chosenversion})

# def childrenCL(request,codelistoid):
# 	# Retrieve the chosen parent codelist
# 	parentCL=graph.cypher.execute('match (a:CodeList {OID:'+codelistoid+'}) return a.Name as Name,a.Extensible as Extensible,a.AliasName as AliasName')
# 	# Retrieve all the child codelists of the chosen parent codelist
# 	childCL=graph.cypher.execute('match (a:CodeList)-[r:BasedOn]->(b:CodeList {OID:'+codelistoid+'}) return a.OID as OID,a.Name as Name,a.Extensible as Extensible,a.AliasName as AliasName,a.child as child order by a.child')

# 	if childCL:
# 		return render(request,'CTVag/ChildTable.html',{'PCL':parentCL,'CCL':childCL})
# 	else:
# 		return render(request,'CTVag/CodeListItems.html',{'PCL':parentCL})

def ChildrenCL(request):
	# Put all the checked codelists into the SelectedCodeLists list
	global SelectedCodeLists
	SelectedCodeLists=[]
	for k,v in request.POST.iteritems():
		if k[0:2] == 'c_':
			SelectedCodeLists.append(k)

	# Now determine which button was clicked
	for k,v in request.POST.iteritems():
		print request.POST.items()
		if k == "XLOutput":
			return render(request,'CTVag/test.html',{'Items':k})

		elif k == "XMLOutput":
			return render(request,'CTVag/test.html',{'Items':k})

		# A codelist button was clicked to create a child
		elif k[0:2] == 's_':
			# Get the codelist items of the chosen codelist
			codelistitems=graph.cypher.execute('match (a:CT {version:"'+chosenversion+'"})-[*1..2]-(b:CodeList {OID:"'+k[2:]+'"})-[:ContainsCodeListItem]->(c:CodeListItem) \
				return b.OID as OID,b.child as child,b.Extensible as extensible,b.Name as name,b.AliasName as CLalias,c.AliasName as CLIalias, \
				c.CodedValue as codedvalue,c.Decode as decode')
			child=codelistitems[0][1]
			nextchild=child+1
			if child == 0:
				return render(request,'CTVag/childrencl.html',{'Items':codelistitems,'ParentOID':codelistitems[0][0],'ParentExt':codelistitems[0][2],\
					'ParentName':codelistitems[0][3],'ParentAlias':codelistitems[0][4],'NextChild':nextchild})
			else:
				parentcodelist=graph.cypher.execute('match (a:CT{version:"'+chosenversion+'"})-[r1:ContainsCodeList]->(b:CodeList)<-[r2:BasedOn]-(c:CodeList {OID:"'+k[2:]+'"}) \
					return b.OID as parentOID,b.Extensible as parentext,b.Name as parentname,b.AliasName as parentalias')
				return render(request,'CTVag/childrencl.html',{'Items':codelistitems,'ParentOID':parentcodelist[0][0],'ParentExt':parentcodelist[0][1],\
					'ParentName':parentcodelist[0][2],'ParentAlias':parentcodelist[0][3],'NextChild':nextchild})

		elif k == "NewCodeList":
			return render(request,'CTVag/test.html',{'Items':k})

def Back2DBCodeList(request):
	SelectedCodeListItems=[]
	if request.POST['submit'] == 'save':
		nextchildstr=toString(request.POST['NextChild'])
		# Create a CodeList node
		tx=graph.cypher.begin()
		statement = 'match (a:CT{version:"'+chosenversion+'"})-[r:ContainsCodeList]->(b:CodeList {OID:"'+request.POST['ParentOID']+'"}) with b \
			create (c:CodeList {OID:"'+request.POST['ParentOID']+nextchildstr+'", Name:"'+request.POST['ParentName']+' - '+request.POST['newname'] \
			+'", Child: '+nextchildstr+', AliasName: "'+request.POST['Alias']+'", Extensible: "'+request.POST['Extensible']+'"})-[r2:BasedOn]->(b) '
		# Create the CodeListItem nodes and relationships to the CodeList node
		for k,v in request.POST.iteritems():
			if k[0:2] == 'c_':
				SelectedCodeListItems.append(k)

