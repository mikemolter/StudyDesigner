from django.shortcuts import render
from django.http import HttpResponse
from py2neo import Graph
import openpyxl
from datetime import datetime
import pandas as pd 
import numpy as np
import sys
from django.http import HttpResponse, JsonResponse


#graph = Graph('http://neo4j:letsgowings@10.0.0.10:7474/db/data/')
graph = Graph('http://neo4j:letsgowings@localhost:7474/db/data/')

# Create your views here.
def index(request):
	return render(request,'StandardDeveloper1/index.html')


def NewStudy(request):
	study=request.GET["newstudyname"]
	parentstandard=request.GET['standards'][0:4]
	parentversion=request.GET['standards'][4:]
	# Create a node for the new study and attach it to the standard to which the parent is attached
	# Also create a copy of the standard ADSL and attach it to the study

	if parentstandard == 'ADAM':
		tx = graph.cypher.begin()
		tx.append(' match (a:Standard {Name:"'+parentstandard+'",Version:"'+parentversion+'"})--(b:ItemGroupDef {Name:"ADSL"}) create (a)<-[:BasedOn]-(c:Study {Name:"'+study+'"})\
			-[:ItemGroupRef]->(d:ItemGroupDef),(d)-[:BasedOn]->(b) set d=b')
		tx.commit()

		Instruction="We begin a new study by defining what every new study needs - an ADSL data set.  The main source of any ADSL data set is SDTM.DM.  "
		Instruction=Instruction+"Provide the subset of SDTM.DM you will use to create ADSL.  Leave it blank if there is no subset.  "
		Instruction=Instruction+"Then click the button to begin defining predecessors from DM. "

		return render(request,'StandardDeveloper1/predsource.html', \
			{'RSType':'MAIN','Action':'Add','NewStudy':'Y','Study':study,'Instruction':Instruction,'IGDName':'ADSL','StandardName':parentstandard,'StandardVersion':parentversion,'Class':'SUBJECT LEVEL ANALYSIS DATASET'})

def NewMerge(request):
	Study=request.POST['Study']
	StandardName=request.POST['StandardName']
	StandardVersion=request.POST['StandardVersion']
	IGDName=request.POST['DSName']

	Instruction="We're now ready to define "+IGDName+" predecessors from other data sets.  "
	Instruction=Instruction+"Fill in the following information about one of the merge data sets.  "
	Instruction=Instruction+"Then click the button to begin defining predecessor variables from that data set."

	return render(request,'StandardDeveloper1/predsource.html', \
		{'RSType':'MERGE','Action':'Add','NewStudy':'N','Study':Study,'Instruction':Instruction,'IGDName':IGDName,'StandardName':StandardName,'StandardVersion':StandardVersion})

def NewModel(request):
	Study=request.POST['Study']
	StandardName=request.POST['StandardName']
	StandardVersion=request.POST['StandardVersion']
	IGDName=request.POST['DSName']
	Class=request.POST['Class']

	Instruction="We're now ready to define other "+IGDName+" model variables.  "
	Instruction=Instruction+"As with predecessors, we'll start by choosing a model variable.  "
	Instruction=Instruction+"We'll then define the metadata along with methods for derived variables."

	Lists=PrepModelLists(StandardName,StandardVersion,Study,IGDName,Class)
	Lists['Study']=Study
	Lists['StandardName']=StandardName
	Lists['StandardVersion']=StandardVersion
	Lists['DSName']=IGDName
	Lists['Class']=Class
	Lists['Instruction']=Instruction
	Lists['RSType']='MODEL'
	Lists['Action']='Add'

	return render(request,'StandardDeveloper1/modelvarlist.html', Lists)

def NewDS(request):
	Study=request.POST["Study"]
	StandardName=request.POST["StandardName"]
	StandardVersion=request.POST["StandardVersion"]
	StandardYN=request.POST['StandardYN']
	DSName=request.POST["DSName"]
	Label=request.POST["Label"]
	Class=request.POST["Class"]
	Structure=request.POST["Structure"]
	Repeat=request.POST["Repeat"]
	Reference=request.POST["Reference"]
	Instruction="To define a new data set, we begin by defining the main source data set. "
	Instruction=Instruction+"Provide the name of the source, and if applicable, a description of the subset of the source"
	Instruction=Instruction+"Then click the button to begin defining predecessors of the source. "

	if StandardYN == 'Y':
		stmt='match (a:Study {Name:"'+Study+'"})-[:BasedOn]->(:Standard {Name:"'+StandardName+'",Version:"'+StandardVersion+'"})-[:ItemGroupRef]->(end:ItemGroupDef \
			{Name:"'+DSName+'"})'
	else:
		stmt='match (a:Study {Name:"'+Study+'"})-[:BasedOn]->(:Standard {Name:"'+StandardName+'",Version:"'+StandardVersion+'"})-[:ItemGroupRef]->(:ItemGroupDef \
			{Name:"'+DSName+'"})-[:BasedOn]->(:Model)-[:ItemGroupRef]->(end:ItemGroupDef {Name:"'+Class+'"})'

	tx=graph.cypher.begin()
	tx.append(stmt+' create (a)-[:ItemGroupRef]->(:ItemGroupDef {Name:"'+DSName+'",Label:"'+Label+'",Repeating:"'+Repeat+'",Structure:"'+Structure+'",IsReferenceData:"'+Reference+'"}) \
		-[:BasedOn]->(end)')
	tx.commit()

	return render(request,'StandardDeveloper1/predsource.html', \
		{'RSType':'MAIN','Action':'Add','NewStudy':'N','Study':Study,'Instruction':Instruction,'IGDName':DSName,'StandardName':StandardName,'StandardVersion':StandardVersion,'Class':Class})


def QueryStudy(request):
	# Get the default standard to which the study is attached

	# When editing a current study
	if 'indexchoice' in request.GET:
		StandardName=request.GET['indexchoice'][4:]
		Study=request.GET['studies']
		StandardVersion=graph.cypher.execute('match (a:Study {Name:"'+Study+'"})-[:BasedOn]->(b:Standard {Name:"'+StandardName+'"}) return b.Version as Version')[0][0]

	# When finished defining the previous data set
	else:
		StandardName=request.GET['StandardName']
		StandardVersion=request.GET['StandardVersion']
		Study=request.GET['Study']

	# Get Standard data sets
	StandardDSRL=QStandardDS(StandardName,StandardVersion)

	# Get Study data sets
	StudyDSRL=QStudyDS(Study)

	# Get a list of standard data sets that does not overlap with the list of study data sets
	StandardList=EliminateDups(StandardDSRL,StudyDSRL)

	# Get the classes for the model
	Classes=graph.cypher.execute('match (:Standard {Name:"'+StandardName+'",Version:"'+StandardVersion+'"})-[:BasedOn]->(:Model)-[:ItemGroupRef]->(a:ItemGroupDef)-\
		[:ItemRef]->(:ItemDef) return distinct a.Name')
	# Turn Classes into proper case
	ClassList=[]
	for x1 in Classes:
		Class=''
		for x2 in x1[0].split():
			Class=Class+x2[0:1]+x2[1:].lower()+' '
		ClassList.append(Class.strip())

	return render(request,'StandardDeveloper1/studyhome.html',{'AddDatasets':StandardList,'StudyDatasets':StudyDSRL,'Study':Study,'StandardName':StandardName,'StandardVersion':StandardVersion,'ClassList':ClassList})

def QueryStudyDS(request):
	StandardName=request.GET['StandardName']
	StandardVersion=request.GET['StandardVersion']
	Study=request.GET['Study']

	# First determine the study data set of interest
	for key,val in request.GET.iteritems():
		if key[0:5] == 'edit_':
			DSName=key[5:]

	# Get data set metadata
	MDDS=QStudyDSMD(Study,DSName)
	print 'MDDS: '
	print MDDS
	print 'REQUEST.GET: '
	print request.GET
	print 'DSNAME: '
	print DSName

	# Get data set class
	Class=QDSClass(Study,DSName)

	# Get all sources for the data set
	Sources=QDSSources(Study,DSName)

	# Get Variable list
	Variables=QStudyDSVarList(Study,DSName)

	return render(request,'StandardDeveloper1/datasethome.html',{'MDDS':MDDS,'Sources':Sources,'Variables':Variables,'Class':Class,'Study':Study,'DSName':DSName,'StandardName':StandardName,'StandardVersion':StandardVersion})

def ESDS(request):
	StandardName=request.POST['StandardName']
	StandardVersion=request.POST['StandardVersion']
	Study=request.POST['Study']
	DSName=request.POST['DSName']
	Label=request.POST['Label']
	Repeat=request.POST['Repeat']
	Structure=request.POST['Structure']
	Reference=request.POST['Reference']
	BeforeDSName=''
	BeforeLabel=''
	BeforeRepeat=''
	BeforeStructure=''
	BeforeReference=''
	if 'BeforeDSName' in request.POST:
		BeforeDSName=request.POST['BeforeDSName']
	if 'BeforeLabel' in request.POST:
		BeforeLabel=request.POST['BeforeLabel']
	if 'BeforeRepeat' in request.POST:
		BeforeRepeat=request.POST['BeforeRepeat']
	if 'BeforeStructure' in request.POST:
		BeforeStructure=request.POST['BeforeStructure']
	if 'BeforeReference' in request.POST:
		BeforeReference=request.POST['BeforeReference']

	print 'REQUEST.POST: '
	print request.POST

	# Edit the data set
	Comma=''
	if BeforeDSName:
		stmt='match (a:Study {Name:"'+Study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+BeforeDSName+'"}) set '
		if BeforeDSName != DSName:
			stmt=stmt+'b.Name = "'+DSName+'"'
			Comma=', '
	else:
		stmt='match (a:Study {Name:"'+Study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+DSName+'"}) set '

	if BeforeLabel and BeforeLabel != Label:
		stmt=stmt+Comma+'b.Label="'+Label+'"'
		Comma=', '

	if BeforeRepeat and BeforeRepeat != Repeat:
		stmt=stmt+Comma+'b.Repeat="'+Repeat+'"'
		Comma=', '

	if BeforeStructure and BeforeStructure != Structure:
		stmt=stmt+Comma+'b.Structure="'+Structure+'"'
		Comma=', '

	if BeforeReference and BeforeReference != Reference:
		stmt=stmt+Comma+'b.Reference="'+Reference+'"'
		Comma=', '

	print 'STMT: '+stmt 
	if Comma:
		tx=graph.cypher.begin()
		tx.append(stmt)
		tx.commit()

	# Get data set metadata
	MDDS=QStudyDSMD(Study,DSName)

	# Get data set class
	Class=QDSClass(Study,DSName)

	# Get all sources for the data set
	Sources=QDSSources(Study,DSName)

	# Get Variable list
	Variables=QStudyDSVarList(Study,DSName)

	return render(request,'StandardDeveloper1/datasethome.html',{'MDDS':MDDS,'Sources':Sources,'Variables':Variables,'Class':Class,'Study':Study,'DSName':DSName,'StandardName':StandardName,'StandardVersion':StandardVersion})


def NewSource(request):
	RSType=request.POST['RSType']
	IGDName=request.POST['DSName']
	Study=request.POST['Study']
	StandardName=request.POST['StandardName']
	StandardVersion=request.POST['StandardVersion']
	ModelClass=request.POST['Class']
	SourceName=request.POST['SourceName']
	SourceDescription=request.POST['SourceDescription']
	VarSource=''

	if RSType == 'MAIN':
		PMPDict=PrepMainPredList(StandardName,StandardVersion,Study,IGDName,ModelClass,VarSource)
		form='mainpredlist'
		PMPDict['SourceJoin']=''
		Instruction='Predecessor variables are those that are copied from one data set to another.  '
		Instruction=Instruction+'Define predecessors from '+SourceName+'.'
	elif RSType == 'MERGE':
		form='mergepredotherlist'
		Instruction='Predecessor variables are those that are copied from one data set to another.  '
		Instruction=Instruction+'Define predecessors from '+SourceName+'.'
		SourceJoin=request.POST["SourceJoin"]
		PMPDict={'StudyVarsRL':QStudyVars(Study,IGDName,'d.Name="'+SourceName+'" and d.Description="'+SourceDescription+'"')}
		PMPDict['SourceJoin']=SourceJoin
	elif RSType == 'MODEL':
		RSType='OTHER'
		form='mergepredotherlist'
		Instruction='ADaM allows for the definition of custom variables under guidelines outlined in the IG. '
		Instruction=Instruction+'Define your next custom variable. '
		SourceName=''
		SourceDescription=''
		PMPDict={}
		PMPDict['SourceJoin']=''

	# Determine SourceOrder by adding 1 to the max SourceOrder that currently exists
	maxOrder=graph.cypher.execute('match (:Study {Name:"'+Study+'"})--(:ItemGroupDef)--(:ItemDef)-[:FromSource]->(a:Source) return max(a.Order) as Order')
	if maxOrder[0][0]:
		SourceOrder=maxOrder[0][0]+1
	else:
		SourceOrder=1

	PMPDict['Class']=ModelClass
	PMPDict['StandardName']=StandardName
	PMPDict['StandardVersion']=StandardVersion
	PMPDict['Study']=Study
	PMPDict['DSName']=IGDName
	PMPDict['RSType']=RSType
	PMPDict['SourceName']=SourceName
	PMPDict['SourceDescription']=SourceDescription
	PMPDict['SourceOrder']=SourceOrder
	PMPDict['Instruction']=Instruction

	return render(request,'StandardDeveloper1/'+form+'.html', PMPDict)

def NewVar(request):
	ReturnTo = request.POST['ReturnTo']
	RSType=request.POST['RSType']
	DSName=request.POST['DSName']
	Study=request.POST['Study']
	StandardName=request.POST['StandardName']
	StandardVersion=request.POST['StandardVersion']
	ModelClass=request.POST['Class']
	SourceName=request.POST['SourceName']
	SourceDescription=request.POST['SourceDescription']
	SourceJoin=request.POST['SourceJoin']
	SourceOrder=request.POST['SourceOrder']
	VarSource=request.POST['VarSource']
	Action=request.POST['Action']
	ParentCLGlobal=request.POST['ParentCodelistGlobal']
	ParentCLStudy=request.POST['ParentCodelistStudy']



	# get the variable metadata
	VarName=request.POST['VarName']
	VarLabel=request.POST['VarLabel']
	VarSASType=request.POST['VarSASType']
	VarOrigin=request.POST['VarOrigin']
	VarSASLength=request.POST['VarSASLength']
	VarMandatory=request.POST['VarMandatory']
	VarOrderNumber=request.POST['VarOrderNumber']
	VarDataType=request.POST['VarDataType']

	if Action == 'Add':

		# Make variables for query parts
		QIGD='(study:Study {Name:"'+Study+'"})--(IGD:ItemGroupDef {Name:"'+DSName+'"}) '
		QID='(ID:ItemDef {Name:"'+VarName+'", Label:"'+VarLabel+'",SASType:"'+VarSASType+'",Origin:"'+VarOrigin+'",SASLength:"'+VarSASLength+'",DataType:"'+VarDataType+'"}) '
		QIR='[:ItemRef {Mandatory:"'+VarMandatory+'", Order:'+VarOrderNumber+',MethodRef:"'+DSName+'",SourceRef:"'+DSName+'"}]'
		QSRC='(src:Source {Name:"'+SourceName+'", Description:"'+SourceDescription+'",Order:'+str(SourceOrder)+',Join:"'+SourceJoin+'"}) '


		# create itemdef node
		ItemDefExist=graph.cypher.execute('return exists((:Study {Name:"'+Study+'"})--(:ItemGroupDef)--(:ItemDef {Name:"'+VarName+'", Label:"'+VarLabel+'",SASType:"'+VarSASType+'",Origin:"'+VarOrigin+'",SASLength:"'+VarSASLength+'",DataType:"'+VarDataType+'"}))')[0][0]
		if ItemDefExist:
			stmt='match '+QIGD+', '+QID+' create (IGD)-'+QIR+'->(ID) '
		else:
			stmt='match '+QIGD+' create (IGD)-'+QIR+'->'+QID


		# create source nodes (if necessary), and connect them to itemdef
		if RSType in ['MAIN','MERGE']:
			# Determine if the source node already exists
			SourceNodeExist=graph.cypher.execute('return exists((:Study {Name:"'+Study+'"})--(:ItemGroupDef)--(:ItemDef)--(:Source {Order:'+str(SourceOrder)+'}))')[0][0]
			if SourceNodeExist:
				stmt=stmt+'with (ID) match (:Study {Name:"'+Study+'"})--(:ItemGroupDef)--(:ItemDef)--(src:Source {Order:'+str(SourceOrder)+'}) with (ID),(src) limit 1 create (ID)-[:FromSource {SourceRef:"'+DSName+'",Type:"'+RSType+'"}]->(src) '
			else:
				stmt=stmt+'-[:FromSource {SourceRef:"'+DSName+'",Type:"'+RSType+'"}]->'+QSRC
		elif RSType in ['MODEL','OTHER']:
			for key,val in request.POST.iteritems():
				if key[0:4] == 'src_':
					SourceOrder=key[4:]
					stmt=stmt+'with (ID) match (:Study {Name:"'+Study+'"})--(:ItemGroupDef)--(:ItemDef)--(src'+str(SourceOrder)+':Source {Order:'+str(SourceOrder)+'}) with (ID),(src'+str(SourceOrder)+') limit 1 create (ID)-[:FromSource {SourceRef:"'+DSName+'",Type:"'+RSType+'"}]->(src'+str(SourceOrder)+') '
				elif key[0:7] == 'newsrc_':
					SourceOrder=key[7:]
					SourceName=request.POST['newds_newsrc_'+SourceOrder]
					SourceDescription=request.POST['newdesc_newsrc_'+SourceOrder]
					SourceJoin=request.POST['newjoin_newsrc_'+SourceOrder]
					QSRC='(:Source {Name:"'+SourceName+'", Description:"'+SourceDescription+'",Order:'+str(SourceOrder)+',Join:"'+SourceJoin+'"}) '
					stmt=stmt+', (ID)-[:FromSource {SourceRef:"'+DSName+'",Type:"'+RSType+'"}]->'+QSRC


		# Create methods
		if RSType in ['MAIN','MERGE']:
			MethodDesc='Copy '+VarName+' from '+SourceName
			methodchoice='freetext'

		elif RSType in ['MODEL','OTHER']:
			MethodDesc=''
			methodchoice=request.POST['methodchoice']

			if methodchoice == 'freetext':
				MethodDesc=request.POST['free']

			elif methodchoice == 'conditions':
				cond={}
				res={}
				elseres=request.POST['else']
				for key,val in request.POST.iteritems():
					if key[0:4] == 'cond':
						cond[key]=val
					elif key[0:3] == 'res':
						res[key]=val
				stmt=stmt+', (ID)-[:MethodRef {MethodRef:"'+DSName+'"}]->(MD:MethodDef) '
				print 'COND: '
				print cond
				for key,val in cond.iteritems():
					Order=key[4:]
					stmt=stmt+', (MD)-[:ContainsConditions]->(:MethodCondition {Order:'+Order+',If:"'+val+'",ElseFL:"N"})-[:IfThen]->(:MethodThen {Then:"'+res['res'+Order]+'"}) '
				stmt=stmt+', (MD)-[:ContainsConditions]->(:MethodCondition {ElseFL:"Y"})-[:IfThen]->(:MethodThen {Then:"'+elseres+'"}) '

		if MethodDesc:
			MethodExist=graph.cypher.execute('return exists((:Study {Name:"'+Study+'"})--(:ItemGroupDef)--(:ItemDef)--(:MethodDef {Description:"'+MethodDesc+'"}))')[0][0]
			if MethodExist:
				stmt=stmt+'with (ID) match (:Study {Name:"'+Study+'"})--(:ItemGroupDef)--(:ItemDef)--(mt:MethodDef {Description:"'+MethodDesc+'"}) with (ID),(mt) limit 1 create (ID)-[:MethodRef {MethodRef:"'+DSName+'"}]->(mt) '
			else:
				stmt=stmt+', (ID)-[:MethodRef {MethodRef:"'+DSName+'"}]->(:MethodDef {Description:"'+MethodDesc+'"}) '


		# Create the BasedOn relationship from the study variable to the Standard/Model variable
		if VarSource == "Model":
			stmt=stmt+'with (ID) match (e:Standard {Name:"'+StandardName+'",Version:"'+StandardVersion+'"})-[:BasedOn]->(f:Model)-[:ItemGroupRef]->(g:ItemGroupDef {Name:"'+ModelClass+'"})-[:ItemRef]->(h:ItemDef {Name:"'+VarName+'"}) \
				create (ID)-[:BasedOn]->(h) '
		elif VarSource == "Standard":
			stmt=stmt+'with (ID) match (e:Standard {Name:"'+StandardName+'",Version:"'+StandardVersion+'"})-[:ItemGroupRef]->(f:ItemGroupDef {Name:"'+DSName+'"})-[:ItemRef]->(g:ItemDef {Name:"'+VarName+'"}) create (ID)-[:BasedOn]->(g) '


		# Controlled Terminology
		
		stdterms=''
		extterms={}

		# Put the standard terms into a list
		for x in request.POST:
			if x[0:8] == 'stdterm_':
				if stdterms:
					stdterms=stdterms+', '
				else:
					stdterms='['
				stdterms=stdterms+"'"+x[8:]+"'"
		if stdterms:
			stdterms=stdterms+']'
			print 'STDTERMS: '+stdterms

		# Put the extended terms into a dictionary
		for k,v in request.POST.iteritems():
			if k[0:8] == 'extterm_':
				extterms[k[8:]]=v
		print 'EXTTERMS: '
		print extterms


		# If there is any controlled terminology...
		if stdterms or extterms:
			CTExt=request.POST['CTExtensible']
			CTAlias=request.POST['CTAlias']
			CTDataType=request.POST['CTDataType']
			CTName=request.POST['CTName']

			# A variable whose standard does not associate CT, but a custom list is based on some standard codelist
			if ParentCLGlobal:
				stdstmt='match (:CT)--(a:CodeList {AliasName:"'+ParentCLGlobal+'"})--(e:CodeListItem) where e.CodedValue in '+stdterms

			elif ParentCLStudy:
				pass

			# CT associated with the variable at the standard level or custom CT
			else:
				# Find the items from the standard that were chosen by the user
				if VarSource == "Standard":
					stdstmt = 'match (a:Standard {Name:"'+StandardName+'",Version:"'+StandardVersion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+DSName+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+VarName+'"}) \
						-[:CodeListRef]->(d:CodeList)-[:ContainsCodeListItem]->(e:CodeListItem) where e.CodedValue in '+stdterms
				elif VarSource == "Model":
					stdstmt = 'match (a:Standard {Name:"'+StandardName+'",Version:"'+StandardVersion+'"})-[:BasedOn]->(a:Model)-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+ModelClass+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+VarName+'"}) \
						-[:CodeListRef]->(d:CodeList)-[:ContainsCodeListItem]->(e:CodeListItem) where e.CodedValue in '+stdterms

			# Create the study codelist
			stmt=stmt+', (ID)-[:CodeListRef]->(CL:CodeList {Extensible:"'+CTExt+'", DataType:"'+CTDataType+'",Name:"'+CTName+'",AliasName:"'+CTAlias+'"}) '

			# Connect the study codelist to the items
			if stdterms:
				stmt=stmt+'with (CL) '+stdstmt+' create (CL)-[:ContainsCodeListItem]->(e) '

			# Connect the study codelist to extended items
			for k,v in extterms.iteritems():
				stmt=stmt+'with (CL) limit 1 create (CL)-[:ContainsCodeListItem]->(:CodeListItem {CodedValue:"'+k+'",Decode:"'+v+'"})'

	print 'NEWVAR STATEMENT: '+stmt
	print 'REQUEST.POST: '
	print request.POST ;

	tx=graph.cypher.begin()
	tx.append(stmt)
	tx.commit()

	if RSType == "MAIN":
		PMPDict=PrepMainPredList(StandardName,StandardVersion,Study,DSName,ModelClass,VarSource)
	elif RSType == "MERGE":
		PMPDict={'StudyVarsRL':QStudyVars(Study,DSName,'d.Name="'+SourceName+'" and d.Description="'+SourceDescription+'" and c.Origin="Predecessor"')}
	elif RSType == "MODEL":
		PMPDict=PrepModelLists(StandardName,StandardVersion,Study,DSName,ModelClass)
	elif RSType == 'OTHER':
		OtherVars=graph.cypher.execute('match (a:Study {Name:"'+Study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+DSName+'"})-[r:ItemRef]->(c:ItemDef) \
			where c.Origin<>"Predecessor" and not (c)-[:BasedOn]->(:ItemDef) return c.Name as Name,c.Label as Label')
		PMPDict={}
		PMPDict['StudyVarsRL']=OtherVars

	print 'STUDYVARSRL: '
	print PMPDict['StudyVarsRL']

	PMPDict['Class']=ModelClass
	PMPDict['StandardName']=StandardName
	PMPDict['StandardVersion']=StandardVersion
	PMPDict['Study']=Study
	PMPDict['DSName']=DSName
	PMPDict['RSType']=RSType
	PMPDict['SourceName']=SourceName
	PMPDict['SourceDescription']=SourceDescription
	PMPDict['SourceJoin']=SourceJoin
	PMPDict['SourceOrder']=SourceOrder

	# return render(request,'StandardDeveloper1/test.html')
	return render(request,'StandardDeveloper1/'+ReturnTo+'.html',PMPDict)

def PrepMainPredList(Standard,Version,Study,DSName,Class,VarSource):

	Instruction='Predecessor variables are those that are copied from one data set to another.  '
	Instruction=Instruction+'We begin by defining predecessors from the main source data set.'

	# Query the database for standard predecessors
	if VarSource != "Model":
		StandardPredsRL=QStandardVars(Standard,Version,DSName,'c.Origin="Predecessor"')
		if StandardPredsRL:
			VarSource='Standard'
		else:
			VarSource='Model'

	# If the standard does not define the data set (assuming that all data sets have at least one predecessor), then go to the model
	if VarSource == "Model":
		ModelInfoRL=graph.cypher.execute('match (a:Standard {Name:"'+Standard+'",Version:"'+Version+'"})-[:BasedOn]->(b:Model) return b.name as Name,b.version as Version')
		ModelName=ModelInfoRL[0][0]
		ModelVersion=ModelInfoRL[0][1]
		StandardPredsRL=QModelVars(ModelName,ModelVersion,Class,'c.Origin="Predecessor"')

	# Get list of study variables
	StudyVarsRL=QStudyVars(Study,DSName)

	# Remove from the standards list variables already in the study
	StandardPredsList=EliminateDups(StandardPredsRL,StudyVarsRL)

	PMPDict={'StandardPredsList':StandardPredsList,'Instruction':Instruction,'StudyVarsRL':StudyVarsRL,'VarSource':VarSource}
	return PMPDict

def PrepModelLists(StandardName,StandardVersion,Study,DSName,ModelClass):
	""" This function creates two lists and a record list.  The record list contains all study model variables.  The lists contain variables in Model
	and standard not in the study (model variables not in the standard)"""

	# Get variables to display
	# Start by getting model variables 
	# To do this, we need to know the model and the class
	model=graph.cypher.execute('match (:Standard {Name:"'+StandardName+'",Version:"'+StandardVersion+'"})-[:BasedOn]->(a:Model) return a.name,a.version')
	modelname=model[0][0]
	modelversion=model[0][1]

	ModelRL=QModelVars(modelname,modelversion,ModelClass,'c.Origin<>"Predecessor"')

	# Now get standard variables
	StandardRL=QStandardVars(StandardName,StandardVersion,DSName,'c.Origin<>"Predecessor"')

	# Now get study variables
	StudyRL=graph.cypher.execute('match (a:Study {Name:"'+Study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+DSName+'"})-[r:ItemRef]->(c:ItemDef) \
		where c.Origin<>"Predecessor" and (c)-[:BasedOn]->(:ItemDef) return c.Name as Name')

	StandardVarList=EliminateDups(StandardRL,StudyRL)
	ModelVarList=[]
	for x in ModelRL:
		ModelVarList.append(x[0])
	for x in StandardVarList:
		if x in ModelVarList:
			ModelVarList.remove(x)
	for x in StudyRL:
		if x[0] in ModelVarList:
			ModelVarList.remove(x[0])

	return {'StudyVarsRL':StudyRL,'StandardList':StandardVarList,'ModelList':ModelVarList}



def QueryStandardDSMD(request):
	StandardName=request.GET["StandardName"]
	StandardVersion=request.GET["StandardVersion"]
	Study=request.GET["Study"]
	Rendered=False

	# If a general structure was selected, then determine which one it was
	# Get the classes for the model
	Classes=graph.cypher.execute('match (:Standard {Name:"'+StandardName+'",Version:"'+StandardVersion+'"})-[:BasedOn]->(:Model)-[:ItemGroupRef]->(a:ItemGroupDef)-\
		[:ItemRef]->(:ItemDef) return distinct a.Name')
	# Turn Classes into proper case 
	for x1 in Classes:
		Class=''
		for x2 in x1[0].split():
			Class=Class+x2[0:1]+x2[1:].lower()+' '
		if Class.strip() in request.GET:
			Rendered=True
			return render(request,'StandardDeveloper1/mdds.html',{'StandardName':StandardName,'StandardVersion':StandardVersion,'Study':Study,'StandardYN':"N",'Class':Class.strip().upper()})
			break

	if not Rendered:
	# If editing a study data set
		if 'editmdds' in request.GET:
			DSName=request.GET['DSName']
			# Get study data set metadata
			# If the following returns anything, then it came from a standard data set
			MDDS=graph.cypher.execute('match (a:Study {Name:"'+Study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+DSName+'"})-[:BasedOn]->(:ItemGroupDef)-[:BasedOn]->(c:ItemGroupDef)<-[:ItemGroupRef]\
				-(:Model) return c.Name as Class,b.Name as DSName,b.Structure as Structure,b.Repeating as Repeat,b.IsReferenceData as Reference,b.Label as Label')
			if MDDS:
				StandardYN='Y'
			
			# Otherwise, if the following returns anything, then we know that the data set was defined from a general model class, not a specific standard data set
			else:
				MDDS=graph.cypher.execute('match (a:Study {Name:"'+Study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+DSName+'"})-[:BasedOn]->(c:ItemGroupDef)<-[:ItemGroupRef]-(:Model) return c.Name as Class,b.Name as DSName,b.Structure as Structure,\
					b.Repeating as Repeat,b.IsReferenceData as Reference,b.Label as Label')
				StandardYN='N'
				# The following will return standard data set metadata, which will tell us which properties the standard has defined.
				# Properties not defined by the standard data set will be left to the user to. populate
			DSMDRL=QStandardDSMD(StandardName,StandardVersion,DSName)

			return render(request,'StandardDeveloper1/mdds.html',{'StandardName':StandardName,'StandardVersion':StandardVersion,'Study':Study,'StandardYN':StandardYN,'StudyDSProps':MDDS,'StandardDSProps':DSMDRL,'DSName':DSName,'Class':MDDS[0]['Class']})

		# If a specific data set was chosen for defining, get the its metadata
		else:
			for k,v in request.GET.iteritems():
				if k[0:4] == "add_":
					DSName=k[4:]
					# Get Standard data set Metadata
					DSMDRL=QStandardDSMD(StandardName,StandardVersion,DSName)
					return render(request,'StandardDeveloper1/mdds.html',{'StandardName':StandardName,'StandardVersion':StandardVersion,'Study':Study,'StandardYN':"Y",'StandardDSProps':DSMDRL,'DSName':DSName,'Class':DSMDRL[0]['Class']})

def SetMDVar(request):
	StandardName=request.POST["StandardName"]
	StandardVersion=request.POST["StandardVersion"]
	Study=request.POST["Study"]
	ReturnTo=request.POST["ReturnTo"]
	DSName=request.POST["DSName"]
	ModelClass=request.POST["Class"]
	SourceName=request.POST['SourceName']
	SourceDescription=request.POST['SourceDescription']
	SourceJoin=request.POST['SourceJoin']
	SourceOrder=request.POST['SourceOrder']
	RSType=request.POST['RSType']

	Instruction="Here we define the metadata for the chosen variable"

	for k,v in request.POST.iteritems():
		if k[0:3] == "add":
			action="Add"
			if k == "add_pred" or k == "add_other":
				# Add a custom predecessor or other custom variable
				return render(request,'StandardDeveloper1/mdvar.html',{'Study':Study,'StandardName':StandardName,'DSName':DSName,'Instruction':Instruction,'RSType':RSType,'SourceName':SourceName,\
					'ReturnTo':ReturnTo,'PredStdYN':"N",'Action':'Add','SourceDescription':SourceDescription,'InstructionCT':'Optionally, you may define a list of allowable values for this variable called a Codelist.  Click one of the buttons to get started.',\
					'CTStdYN':'N','CTExt':'Y','CTTable':'','DecodeYN':'','SourceOrder':SourceOrder,'SourceJoin':SourceJoin,'StandardVersion':StandardVersion
					})
			else:
				if k[0:6] == 'addstd':
					# From modelvarlist, when adding a standard variable 
					varname = k[7:]
					VarSource = 'Standard'
					PredStdYN = ''
				elif k[0:6] == 'addmod':
					# from modelvarlist, when adding a model variable
					varname = k[7:]
					VarSource = 'Model'
					PredStdYN = ''
				else:
					varname=k[4:]
					VarSource=request.POST['VarSource']
					PredStdYN = 'Y'

				# Query the database for the variable metadata 
				if VarSource == "Standard":
					VarRL=QStandardVar(StandardName,StandardVersion,DSName,varname)
					CTRL=QStandardCT(StandardName,StandardVersion,DSName,varname)
					MethodRL=QStandardMethod(StandardName,StandardVersion,DSName,varname)

				elif VarSource == "Model":
					ModelInfoRL=graph.cypher.execute('match (a:Standard {Name:"'+StandardName+'",Version:"'+StandardVersion+'"})-[:BasedOn]->(b:Model) return b.name as Name,b.version as Version')
					ModelName=ModelInfoRL[0][0]
					ModelVersion=ModelInfoRL[0][1]
					VarRL=QModelVar(ModelName,ModelVersion,ModelClass,varname)
					CTRL=QModelCT(ModelName,ModelVersion,ModelClass,varname)
					MethodRL=QModelMethod(ModelName,ModelVersion,ModelClass,varname)

				if CTRL:
					if CTRL[0].Decode:
						DecodeYN='Y'
					else:
						DecodeYN='N'
					
					InstructionCT = 'The standard associates a list of allowable values called a codelist with the variable '+varname+'.  '
					InstructionCT = InstructionCT+'Check only those values relevant in this context.'
					CTExt = CTRL[0]['Extensible']
					CTStdYN = 'Y'
				else:
					InstructionCT = 'Optionally, you may define a list of allowable values for this variable called a Codelist.  Click one of the buttons to get started.'
					CTStdYN = 'N'
					CTExt = 'Yes'
					DecodeYN=''

				return render(request,'StandardDeveloper1/mdvar.html',{'Study':Study,'DSName':DSName,'Instruction':Instruction,'VarMD':VarRL,'CTTable':CTRL,'MethodMD':MethodRL,'RSType':RSType,\
					'PredStdYN':PredStdYN,'CTStdYN':CTStdYN,'CTExt':CTExt,'SourceName':SourceName,'ReturnTo':ReturnTo,'Action':"Add",'InstructionCT':InstructionCT,'DecodeYN':DecodeYN,'StandardName':StandardName,\
					'VarSource':VarSource,'Class':ModelClass,'SourceDescription':SourceDescription,'SourceJoin':SourceJoin,'SourceOrder':SourceOrder,'StandardVersion':StandardVersion})

		elif k[0:8] == 'varedit_':
			action="Edit"
			varname=k[8:]
			VarMDRL=QStudyVar(Study,DSName,varname)
			return render(request,'StandardDeveloper1/mdvar.html',{'Study':Study,'DSName':DSName,'Instruction':Instruction,'VarMD':VarMDRL,'RSType':RSType,'Source':Source,'Action':'Edit'})

def QueryStudyVarMD(request):
	StandardName=request.POST["StandardName"]
	StandardVersion=request.POST["StandardVersion"]
	Study=request.POST["Study"]
	DSName=request.POST["DSName"]

	for k,v in request.POST.iteritems():
		if k[0:8] == 'varedit_':
			varname=k[8:]
			# Get variable metadata 
			VarMDRL=QStudyVarMD(Study,DSName,varname)
			# Get Sources
			VarSources=QStudyVarSources(Study,DSName,varname)
			RSType=VarSources[0]['RSType']




			# Determine if the variable has a codelist
			StudyCLExist=graph.cypher.execute("return exists((:Study {Name:'"+Study+"'})-[:ItemGroupRef]->(:ItemGroupDef {Name:'"+DSName+"'})-[:ItemRef]->(:ItemDef {Name:'"+varname+"'})\
				-[:CodeListRef]->(:CodeList))")[0][0]
			CTStdYN='N'
			DecodeYN=''
			CTTable=''
			StudyList=''
			CTExt='Yes'

			if StudyCLExist:
				# Get the study codelist
				StudyStmt='match (:Study {Name:"'+Study+'"})-[:ItemGroupRef]->(:ItemGroupDef {Name:"'+DSName+'"})-[:ItemRef]->(:ItemDef {Name:"'+varname+'"})\
						-[:CodeListRef]->(d:CodeList)-[:ContainsCodeListItem]->(e:CodeListItem) return d.Name as Name,d.Extensible as Extensible,d.DataType as DataType,\
						d.AliasName as AliasCL,e.CodedValue as CodedValue,e.AliasName as AliasItem,e.Decode as Decode'

				StudyCLRL=graph.cypher.execute(StudyStmt)

				# Put the study terms into a list to pass to the template so we know which ones to check
				StudyList=[]
				for x in StudyCLRL:
					StudyList.append(x['CodedValue'])

				# Determine if the codelist is associated with the standard variable
				# Make a record list that combines the standard codelist with the study codelist
				StdCLExist=graph.cypher.execute('return exists((a:Standard {Name:"'+StandardName+'",Version:"'+StandardVersion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+DSName+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) \
					-[:CodeListRef]->(d:CodeList))')[0][0]

				if not StdCLExist:
					ModelCLExist=graph.cypher.execute('return exists((a:Model {name:"'+modelname+'",version:"'+modelversion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+classname+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) \
						-[:CodeListRef]->(d:CodeList))')[0][0]
					if ModelCLExist:
						CTStdYN='Y'
						CTTable=graph.cypher.execute('match (a:Model {name:"'+modelname+'",version:"'+modelversion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+classname+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) \
							-[:CodeListRef]->(d:CodeList)-[:ContainsCodeListItem]->(e:CodeListItem) return d.Name as Name,d.Extensible as Extensible,d.DataType as DataType,\
							d.AliasName as AliasCL,e.CodedValue as CodedValue,e.AliasName as AliasItem,e.Decode as Decode union '+StudyStmt)
				else:
					CTStdYN='Y'
					CTTable=graph.cypher.execute('match (a:Standard {Name:"'+StandardName+'",Version:"'+StandardVersion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+DSName+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) \
						-[:CodeListRef]->(d:CodeList)-[:ContainsCodeListItem]->(e:CodeListItem) return d.Name as Name,d.Extensible as Extensible,d.DataType as DataType,\
						d.AliasName as AliasCL,e.CodedValue as CodedValue,e.AliasName as AliasItem,e.Decode as Decode union '+StudyStmt)

				# Now see if a custom codelist was built from another standard codelist, if the codelist is not associated with the standard variable
				if CTStdYN == 'N':
					# Get the codelist alias of the study codelist
					StudyAlias=StudyCLRL[0]['AliasName']

					# If StudyAlias exists, then the study codelist must be based on a global codelist
					if StudyAlias:
						CTTable=graph.cypher.execute('match (:CT)--(d:CodeList {AliasName:"'+StudyAlias+'"})--(e:CodeListItem) return d.Name as Name,d.Extensible as Extensible,d.DataType as DataType,\
							d.AliasName as AliasCL,e.CodedValue as CodedValue,e.AliasName as AliasItem,e.Decode as Decode union '+StudyStmt)

					# Otherwise the codelist is custom and not based on a standard codelist
					else:
						CTTable=StudyCLRL

				CTExt=CTTable[0]['Extensible']

			return render(request,'StandardDeveloper1/mdvar.html',{'Study':Study,'DSName':DSName,'Instruction':Instruction,'VarMD':VarMDRL,'CTTable':CTTable,'MethodMD':MethodRL,'RSType':RSType,\
				'PredStdYN':'','CTStdYN':CTStdYN,'CTExt':CTExt,'SourceName':'','ReturnTo':ReturnTo,'Action':"Edit",'InstructionCT':InstructionCT,'DecodeYN':DecodeYN,'StandardName':StandardName,\
				'VarSource':'','Class':ModelClass,'SourceDescription':'','SourceJoin':'','SourceOrder':'','StandardVersion':StandardVersion})




def modvar(request):
	if "SourceDS" in request.POST:
		SourceDS=request.POST["SourceDS"]
	else:
		SourceDS=""
	VarType=request.POST["VarType"]
	for k,v in request.POST.iteritems():
		# Variables defined in the standard
		if k[0:3] == 'add':
			if VarType == "Predecessor":
				varname=k[4:]
				Form='Predecessors'
				RSType=request.POST['RSType']
			elif VarType == "Model":
				varname=k[7:]
				Form='Model'
				RSType='Model'

			varprops=graph.cypher.execute('match(a:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+request.POST["DSName"]+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) return c.Name as Name,c.Label as Label,\
				c.SASType as SASType,c.DataType as DataType,c.Origin as Origin,c.MaxLength as SASLength,c.Core as Core,c.CodeList as CodeList,r.OrderNumber as OrderNumber,r.Mandatory as Mandatory')
			return render(request,'StandardDeveloper1/mdvar.html',{'VarProps':varprops,'SourceDS':SourceDS,'Form':Form,'readonly':'Y','VarType':VarType,'Study':study,'DSName':request.POST["DSName"],'RSType':RSType})

		elif k == 'new_var':
			if VarType == 'Predecessor':
				Form='Predecessors'
				RSType=request.POST['RSType']
			else:
				VarType='Model'
				Form='Model'
				RSType='Other'
			return render(request,'StandardDeveloper1/mdvar.html',{'SourceDS':SourceDS,'Form':Form,'readonly':'N','VarType':VarType,'Study':study,'DSName':request.POST["DSName"],'RSType':RSType})

		elif k == 'merge':
			mergeorderRL=graph.cypher.execute('match (a:Study {Name:"'+study+'"})-->(b:ItemGroupDef {Name:"'+request.POST['DSName']+'"})-->(c:RecordSourceContainer)-->(d:RecordSource {Type:"Merge"}) return count(d) as count')
			mergeorder=mergeorderRL[0][0]+1
			return render(request,'StandardDeveloper1/merge.html',{'MergeOrder':mergeorder,'DSName':request.POST["DSName"]})



def QStandardDS(standardname,standardversion=''):
	""" This function returns a single-column Record List of data sets attached to the given standard """
	stmt='match (a:Standard {Name:"'+standardname+'"'
	if standardversion:
		stmt=stmt+',Version:"'+standardversion+'"'
	stmt=stmt+'})-[:ItemGroupRef]->(c:ItemGroupDef) return c.Name as name'
	standarddatasetsRL=graph.cypher.execute(stmt)
	return standarddatasetsRL

def QStandardDSMD(standardname,standardversion,dsname):
	""" This function gets the metadata, including class, for a single data set """
	standarddatasetRL=graph.cypher.execute('match (a:Standard {Name:"'+standardname+'",Version:"'+standardversion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+dsname+'"})-[:BasedOn]->(c:ItemGroupDef) \
		return b.Name as DSName,b.Repeating as Repeat,b.Reference as Reference,b.Structure as Structure,b.Label as Label,c.Name as Class')
	return standarddatasetRL 

def QStandardVars(standardname,standardversion,dsname,filter=''):
	# Get standard variables
	statement='match (a:Standard {Name:"'+standardname+'",Version:"'+standardversion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+dsname+'"})\
		-[:ItemRef]->(c:ItemDef) '
	if filter:
		statement=statement+'where '+filter
	statement=statement+' return distinct c.Name'
	print 'STATEMENT FROM QSTANDARVARS: '+statement
	stdvars=graph.cypher.execute(statement)
	# stdvars=graph.cypher.execute('match (a:Standard {name:"'+standardname+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+dsname+'"})\
	# 	-[:ItemRef]->(c:ItemDef) return distinct c.Name')
	return stdvars

def QStandardVar(standardname,standardversion,dsname,varname):
	return graph.cypher.execute('match (a:Standard {Name:"'+standardname+'",Version:"'+standardversion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+dsname+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) \
		return distinct c.Name as Name,c.Label as Label,c.SASType as SASType,c.DataType as DataType,c.Origin as Origin,c.MaxLength as SASLength, \
		c.Core as Core,c.CodeList as CodeList,r.OrderNumber as OrderNumber,r.Mandatory as Mandatory')


def QStandardCT(standardname,standardversion,dsname,varname):
	return graph.cypher.execute('match (a:Standard {Name:"'+standardname+'",Version:"'+standardversion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+dsname+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) \
		-[:CodeListRef]->(d:CodeList)-[:ContainsCodeListItem]->(e:CodeListItem) return d.Name as Name, \
		d.Extensible as Extensible,d.DataType as DataType,d.AliasName as AliasCL,e.CodedValue as CodedValue,e.AliasName as AliasItem,e.Decode as Decode') 

def QStandardMethod(standardname,standardversion,dsname,varname):
	return graph.cypher.execute('match (a:Standard {Name:"'+standardname+'",Version:"'+standardversion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+dsname+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) \
		-[:MethodRef]->(d:Method) return d.Description as Description')



def QModelVar(modelname,modelversion,classname,varname):
	return graph.cypher.execute('match (a:Model {name:"'+modelname+'",version:"'+modelversion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+classname+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) \
		return distinct c.Name as Name,c.Label as Label,c.SASType as SASType,c.DataType as DataType,c.Origin as Origin,c.MaxLength as SASLength, \
		c.Core as Core,c.CodeList as CodeList,r.OrderNumber as OrderNumber,r.Mandatory as Mandatory')

def QModelCT(modelname,modelversion,classname,varname):
	return graph.cypher.execute('match (a:Model {name:"'+modelname+'",version:"'+modelversion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+classname+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) \
		-[:CodeListRef]->(d:CodeList)-[:ContainsCodeListItem]->(e:CodeListItem) return d.Name as Name, \
		d.Extensible as Extensible,d.DataType as DataType,d.AliasName as AliasCL,e.CodedValue as CodedValue,e.AliasName as AliasItem,e.Decode as Decode') 

def QModelMethod(modelname,modelversion,classname,varname):
	return graph.cypher.execute('match (a:Model {name:"'+modelname+'",version:"'+modelversion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+classname+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) \
		-[:MethodRef]->(d:Method) return d.Description as Description')


def QModelVars(modelname,modelversion,classname,filter=''):
	statement='match (a:Model {name:"'+modelname+'",version:"'+modelversion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+classname+'"})-[r:ItemRef]->(c:ItemDef)'
	if filter:
		statement=statement+'where '+filter
	statement=statement+' return c.Name'
	ModelVarsRL=graph.cypher.execute(statement)
	#ModelVarsRL=graph.cypher.execute('match (a:Model {name:"'+modelname+'",version:"'+modelversion+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+classname+'"})-[r:ItemRef]->(c:ItemDef)')
	return ModelVarsRL


def QStudyVarMD(studyname,dsname,varname):
	return graph.cypher.execute('match (a:Study {Name:"'+studyname+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+dsname+'"})-[r:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) \
		return distinct c.Name as Name,c.Label as Label,c.SASType as SASType,c.DataType as DataType,c.Origin as Origin,c.SASLength, \
		r.Order as OrderNumber,r.Mandatory as Mandatory')

def QStudyVarSources(studyname,dsname,varname):
	return graph.cypher.execute('match (a:Study {Name:"'+studyname+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+dsname+'"})-[:ItemRef]->(c:ItemDef {Name:"'+varname+'"}) \
		-[r:FromSource]->(b:Source) return distinct r.Type as RSType,b.Name as Name,b.Description as Description,b.Join as Join,b.Order as Order')


def QStudyVars(studyname,dsname,filter=''):
	""" This function returns a record list of all study variables """
	statement='match (a:Study {Name:"'+studyname+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+dsname+'"})-[r:ItemRef]->(c:ItemDef)-[:FromSource]->(d:Source)'
	if filter:
		statement=statement+'where '+filter
	statement=statement+'return distinct c.Name as Name,c.Label as Label,r.Order,d.Name as SourceName,d.Description as SourceDescription order by r.Order'
	return graph.cypher.execute(statement)

def QStudyDS(studyname):
	""" This function returns a two-column Record List of study name, data set names for the given study """
	studydatasetsRL=graph.cypher.execute('match (a:Study {Name:"'+studyname+'"})-[:ItemGroupRef]->(c:ItemGroupDef) return c.Name as dsname,a.Name as studyname')
	return studydatasetsRL

def QStudyDSMD(studyname,dsname):
	return graph.cypher.execute('match (a:Study {Name:"'+studyname+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+dsname+'"}) return b.Name as DSName,b.Structure as Structure,\
		b.Repeating as Repeat,b.IsReferenceData as Reference,b.Label as Label')

def QDSClass(Study,DSName):
	# Returns the class, as a string, to which a study's data set is associated
	return graph.cypher.execute('match (a:Study {Name:"'+Study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+DSName+'"})-[:BasedOn]->(:ItemGroupDef)-[:BasedOn]->(c:ItemGroupDef)<-[:ItemGroupRef] \
		-(:Model) return c.Name union match (a:Study {Name:"'+Study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+DSName+'"})-[:BasedOn]->(c:ItemGroupDef)<-[:ItemGroupRef]-(:Model) return c.Name')[0][0]

def QDSSources(Study,DSName):
	# Get all sources associated with a study's data sets
	return graph.cypher.execute('match (:Study {Name:"'+Study+'"})-[:ItemGroupRef]->(:ItemGroupDef {Name:"'+DSName+'"})-[:ItemRef]->(:ItemDef)-[:FromSource]->(a:Source) \
		return distinct a.Name as Name, a.Description as Description, a.Join as Join, a.Order as Order')

def QStudyDSVarList(Study,DSName):
	# Get a study dataset's variables
	return graph.cypher.execute('match (:Study {Name:"'+Study+'"})-[:ItemGroupRef]->(:ItemGroupDef {Name:"'+DSName+'"})-[:ItemRef]->(a:ItemDef) return a.Name as Name, a.Label as Label')

# def QStudyPreds(studyname,dsname):
# 	""" This function returns a single-column record list of all study variables """
# 	studypredsRL=graph.cypher.execute('match (a:Study {Name:"'+studyname+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+dsname+'"})-[:ItemRef]->(c:ItemDef {Origin:"Predecessor"}) return distinct c.Name as Name')
# 	return studypredsRL 


def EliminateDups(RL1,RL2):
	""" This function returns a list of values from the first column of RecordList1 that are not in the first column of RecordList 2 """
	EDList=[]
	for x in RL1:
		EDList.append(x[0])
	for x in RL2:
		if x[0] in EDList:
			EDList.remove(x[0])
	return EDList

def GetAllGlobalCL(self):
	result=graph.cypher.execute('match (:CT)--(a:CodeList) return a.Name,a.AliasName')
	resultlist=[]
	for x in result:
		resultlist.append({'Name':x[0],'Code':x[1]})
	return JsonResponse(resultlist,safe=False)

def Test1(request):
	return render(request,'StandardDeveloper1/test.html')

def Get1GlobalCodeList(request):
	Code=request.GET['CLCode']
	result=graph.cypher.execute('match (:CT)--(a:CodeList {AliasName:"'+Code+'"})--(b:CodeListItem) return b.CodedValue,b.Decode,b.AliasName,a.Name,a.DataType,a.Extensible ')
	resultlist=[]
	for x in result:
		resultlist.append({'Term':x[0],'Decode':x[1],'Code':x[2],'Name':x[3],'DataType':x[4],'Extensible':x[5]})
	print resultlist
	return JsonResponse(resultlist,safe=False)

def GetStudySources(request):
	Study=request.GET['Study']
	result=graph.cypher.execute('match (:Study {Name:"'+Study+'"})--(:ItemGroupDef)--(:ItemDef)-[:FromSource]-(a:Source) return distinct a.Name,a.Description, \
		a.Join,a.Order order by a.Order')
	resultlist=[]
	for x in result:
		resultlist.append({'Name':x[0],'Description':x[1],'Join':x[2],'Order':x[3]})
	return JsonResponse(resultlist,safe=False)

def GetStandards(request):
	Model=request.GET['Model']
	result=graph.cypher.execute('match (a:Standard {Name:"'+Model+'"}) return a.Name,a.Version')
	resultlist=[]
	for x in result:
		resultlist.append({'Name':x[0],'Version':x[1]})
	return JsonResponse(resultlist,safe=False)

def GetStudies(request):
	Model=request.GET['Model']
	result=graph.cypher.execute('match (a:Study)-[:BasedOn]->(b:Standard {Name:"'+Model+'"}) return a.Name')
	resultlist=[]
	for x in result:
		resultlist.append({'Name':x[0]})
	return JsonResponse(resultlist,safe=False)



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
	elif indexchoice == 'currentstudy':
		study=request.GET["standards"]
		parentstandardRL=graph.cypher.execute('match (a:Study {Name:"'+study+'"})-[:BasedOn]->(b:Standard) return b.name as name')
		parentstandard=parentstandardRL[0][0]

	# Get data sets from standard and study
	standarddatasetsRL=graph.cypher.execute('match (a:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(c:ItemGroupDef) return c.Name as name')
	standarddatasetsLIST=[]
	for x in standarddatasetsRL:
		standarddatasetsLIST.append(x[0])
	studydatasetsRL=graph.cypher.execute('match (a:Study {Name:"'+study+'"})-[:ItemGroupRef]->(c:ItemGroupDef) return c.Name as name')
	for x in studydatasetsRL:
		if x[0] in standarddatasetsLIST:
			standarddatasetsLIST.remove(x[0])
	return render(request,'StandardDeveloper1/datasets.html',{'Study':study,'AddDatasets':standarddatasetsLIST,'StudyDatasets':studydatasetsRL})

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

		elif k[0:4] == 'add_':
			# Determine which data set is chosen
			dataset=k[4:]
			# Determine if the data set is attached directly to a standard.  If so, then its properties are read-only
			readonlyRL=graph.cypher.execute('match (:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(:ItemGroupDef {Name:"'+dataset+'"})')
			if readonlyRL:
				readonly='Y'
			else:
				readonly='N'
			# Now get the data set properties from the  standard
			dsprops = graph.cypher.execute('match (:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(a:ItemGroupDef {Name:"'+dataset+'"})-[:BasedOn]->(c:ItemGroupDef) \
				return a.Name as IGDName,a.Label as Label,a.Repeating as Repeating,a.Reference as Reference,a.Structure as Structure,a.Purpose as Purpose,c.Name as Class')
			return render(request,'StandardDeveloper1/mdds.html',{'Study':study,'mdds':dsprops,'readonly':readonly,'Action':'Add'})

		elif k[0:5] == 'edit_':
			dataset=k[5:]
			# Determine if the data set is attached directly to a standard.  If so, then its properties are read-only
			readonlyRL=graph.cypher.execute('match (:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(:ItemGroupDef {Name:"'+dataset+'"})')
			if readonlyRL:
				readonly='Y'
			else:
				readonly='N'
			# Now get the data set properties from the study
			dsprops = graph.cypher.execute('match (:Study {Name:"'+study+'"})-[:ItemGroupRef]->(a:ItemGroupDef {Name:"'+dataset+'"})-\
				return a.Name as IGDName,a.Label as Label,a.Repeating as Repeating,a.Reference as Reference,a.Structure as Structure,a.Purpose as Purpose,a.DSClass as Class')
			mainsource = graph.cypher.execute('match (:Study {Name:"'+study+'"})-[:ItemGroupRef]->(a:ItemGroupDef {Name:"'+dataset+'"})-->\
				(b:RecordSourceContainer {Type:"Original"})-->(c:RecordSource {Type:"Main"}) return c.Name as Name,c.Description as Description')
			mergesources = graph.cypher.execute('match (:Study {Name:"'+study+'"})-[:ItemGroupRef]->(a:ItemGroupDef {Name:"'+dataset+'"})-->\
				(b:RecordSourceContainer {Type:"Original"})-->(c:RecordSource {Type:"Merge"}) return c.Name as Name')
			return render(request,'StandardDeveloper1/mdds.html',{'Study':study,'mdds':dsprops,'MainSource':mainsource,'MergeSources':mergesources,'readonly':readonly,'Action':'Edit'})

		elif k[0:7] == 'remove_':
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
	tx=graph.cypher.begin()
	# Get the dataset-level metadata, create a dataset node, attach it to the study, and get predecessors to display from the standard
	if 'frommdds' in request.POST:
		statement='match (a:Study {Name:"'+study+'"}) create (a)-[:ItemGroupRef]->(:ItemGroupDef {Name:"'+request.POST["DSName"]+'",Label:"'+request.POST["DSLabel"]+'",Structure:"'+request.POST['DSStructure']+'",\
			DSClass:"'+request.POST['DSClass']+'",Repeating:"'+request.POST['DSRepeat']+'",Reference:"'+request.POST['DSIsRef']+'",Purpose:"'+request.POST["DSPurpose"]+'"})-[:ContainsRecords]->(:RecordSourceContainer {Type:"ORIGINAL"}) \
			-[:ContainsRecordType]->(:RecordSource {Type:"Main",Name:"'+request.POST['DSPredecessor']+'",Description:"'+request.POST['DSSubset']+'",Order:0})'
	# Get variable-level metadata, attach to the data set
	elif 'frommdvar' in request.POST:
		statement='match (a:Study {Name:"'+study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+request.POST["DSName"]+'"})-->(:RecordSourceContainer)-->(b1:RecordSource {Type:"'+request.POST['RSType']+'"}) with b,b1 \
			merge (c:ItemDef {Name:"'+request.POST['VarName']+'",Label:"'+request.POST['VarLabel']+'",SASType:"'+request.POST['VarSASType']+'",\
			Origin:"'+request.POST['VarOrigin']+'",DataType:"'+request.POST['VarDataType']+'",CodeList:"'+request.POST['VarCodeList']+'",MaxLength:"'+request.POST['VarSASLength']+'",\
			Core:"'+request.POST['VarCore']+'",Predecessor:"'+request.POST['DSPredecessor']+'"}) on create set c.OID="ID.'+request.POST['DSName']+'.'+request.POST['VarName']+'" with b,b1,c \
			create (b)-[:ItemRef {OrderNumber:'+request.POST['VarOrderNumber']+',Mandatory:"'+request.POST['VarMandatory']+'"}]->(c)-[:MethodRef]->\
			(d:Method {Description:"Set to '+request.POST['DSPredecessor']+'.'+request.POST['VarName']+'"})-[:MethodSource]->(b1)'

	print 'PREDLIST STATEMENT: '
	print statement
	tx.append(statement)
	tx.commit()
	stdpredvars=graph.cypher.execute('match (a:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+request.POST['DSName']+'"})-[:ItemRef]->(c:ItemDef {Origin:"Predecessor"}) return distinct c.Name as Name')
	stdpredvarsLIST=[]
	for x in stdpredvars:
		stdpredvarsLIST.append(x[0])
	studypredvars=graph.cypher.execute('match (a:Study {Name:"'+study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+request.POST['DSName']+'"})-[:ItemRef]->(c:ItemDef {Origin:"Predecessor"})-->(:Method)-->(:RecordSource {Type:"Main"}) return distinct c.Name as Name,c.Label as Label')
	for x in studypredvars:
		if x[0] in stdpredvarsLIST:
			stdpredvarsLIST.remove(x[0])
	return render(request,'StandardDeveloper1/varlist.html',{'StdVarList':stdpredvarsLIST,'StudyVarList':studypredvars,'VarType':'Predecessor','Study':study,'DSName':request.POST['DSName'],'SourceDS':request.POST['DSPredecessor'],'RSType':'Main'})




def merge(request):
	path='(a:Study {Name:"'+study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+request.POST["DSName"]+'"})'
	path2=':RecordSourceContainer'
	path3=':RecordSource {Type:"Merge",Order:'+request.POST['MergeOrder']+'}'
	addprops='{Type:"Merge",Order:'+request.POST['MergeOrder']+', Name:"'+request.POST['DSPredecessor']+'", Description:"'+request.POST['DSSubset']+'", JoinCondition:"'+request.POST['DSJoinCond']+'"}'
	pathex=graph.cypher.execute('match '+path+' return exists((b)-->('+path2+')) as path2,exists((b)-->('+path2+')-->('+path3+')) as path3')
	if pathex[0][1]:
		statement='match '+path+'-->('+path2+')-->(d'+path3+') set d.Name="'+request.POST['DSPredecessor']+'",d.Description="'+request.POST['DSSubset']+'",d.JoinCondition="'+request.POST['DSJoinCond']+'"'
	elif pathex[0][0]:
		statement='match '+path+'-->(c'+path2+') create (c)-[:ContainsRecordType]->(:RecordSource '+addprops+')'
	else:
		statement='match '+path+' create (b)-[:ContainsRecords]->(c'+path2+')-[:ContainsRecordType]->(:RecordSource '+addprops+')'
	print 'STATEMENT: '
	print statement 
	tx=graph.cypher.begin()
	tx.append(statement)
	tx.commit()

	for k,v in request.POST.iteritems():
		if k == 'frommerge':
			return render(request,'StandardDeveloper1/mdvar.html',{'SourceDS':request.POST['DSPredecessor'],'Form':'Merge','readonly':'N','VarType':'Predecessor','Study':study,'DSName':request.POST["DSName"],'RSType':'Merge','MergeOrder':request.POST['MergeOrder'],'DSSubset':request.POST['DSSubset'],'DSJoin':request.POST['DSJoinCond']})
		elif k == 'frommdvar':
			tx=graph.cypher.begin()
			mergeorder=request.POST['MergeOrder']
			statement='match (a:Study {Name:"'+study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+request.POST["DSName"]+'"})-->(:RecordSourceContainer)-->(b1:RecordSource {Type:"Merge",Order:'+str(mergeorder)+'}) with b,b1 \
				merge (c:ItemDef {Name:"'+request.POST['VarName']+'",Label:"'+request.POST['VarLabel']+'",SASType:"'+request.POST['VarSASType']+'",\
				Origin:"'+request.POST['VarOrigin']+'",DataType:"'+request.POST['VarDataType']+'",CodeList:"'+request.POST['VarCodeList']+'",MaxLength:"'+request.POST['VarSASLength']+'",\
				Core:"'+request.POST['VarCore']+'",Predecessor:"'+request.POST['DSPredecessor']+'"}) on create set c.OID="ID.'+request.POST['DSName']+'.'+request.POST['VarName']+'" with b,b1,c \
				create (b)-[:ItemRef {OrderNumber:'+request.POST['VarOrderNumber']+',Mandatory:"'+request.POST['VarMandatory']+'"}]->(c)-[:MethodRef]->\
				(d:Method {Description:"Set to '+request.POST['DSPredecessor']+'.'+request.POST['VarName']+'"})-[:MethodSource]->(b1)'
			print 'MERGE STATEMENT: '
			print statement 
			tx.append(statement)
			tx.commit()
			studypredvars=graph.cypher.execute('match (a:Study {Name:"'+study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+request.POST['DSName']+'"})-[:ItemRef]->(c:ItemDef {Origin:"Predecessor"})-->(:Method)-->(:RecordSource {Type:"Merge",Order:'+str(request.POST['MergeOrder'])+'}) return c.Name as Name,c.Label as Label')
			return render(request,'StandardDeveloper1/merge.html',{'MergeOrder':mergeorder,'DSName':request.POST["DSName"],'StudyVarList':studypredvars,'DSPredecessor':request.POST['DSPredecessor'],'DSSubset':request.POST['DSSubset'],'DSJoinCond':request.POST['DSJoinCond'],'Study':study})
		elif k == 'merge':
			mergeorder=int(request.POST['MergeOrder'])+1 
			return render(request,'StandardDeveloper1/merge.html',{'MergeOrder':mergeorder,'DSName':request.POST["DSName"],'Study':study})

def model(request):
	if 'frommdvar' in request.POST:
		path='(a:Study {Name:"'+study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+request.POST["DSName"]+'"})'
		path2=':RecordSourceContainer'
		path3=':RecordSource {Type:"'+request.POST['RSType']+'"}'
		addprops='{Type:"Merge",Order:'+request.POST['MergeOrder']+', Name:"'+request.POST['DSPredecessor']+'", Description:"'+request.POST['DSSubset']+'", JoinCondition:"'+request.POST['DSJoinCond']+'"}'
		pathex=graph.cypher.execute('match '+path+' return exists((b)-->('+path2+')) as path2,exists((b)-->('+path2+')-->('+path3+')) as path3')
		if pathex[0][1]:
			statement='match '+path+'-->('+path2+')-->(d'+path3+') with b,d '
		elif pathex[0][0]:
			statement='match '+path+'-->(c'+path2+') create (c)-[:ContainsRecordType]->(d'+path3+') with b,d '
		else:
			statement='match '+path+' create (b)-[:ContainsRecords]->(c'+path2+')-[:ContainsRecordType]->(d'+path3+') with b,d '

		statement=statement+'merge (c:ItemDef {Name:"'+request.POST['VarName']+'",Label:"'+request.POST['VarLabel']+'",SASType:"'+request.POST['VarSASType']+'",\
		Origin:"'+request.POST['VarOrigin']+'",DataType:"'+request.POST['VarDataType']+'",CodeList:"'+request.POST['VarCodeList']+'",MaxLength:"'+request.POST['VarSASLength']+'",\
		Core:"'+request.POST['VarCore']+'"}) on create set c.OID="ID.'+request.POST['DSName']+'.'+request.POST['VarName']+'" with b,d,c \
		create (b)-[:ItemRef {OrderNumber:'+request.POST['VarOrderNumber']+',Mandatory:"'+request.POST['VarMandatory']+'"}]->(c)-[:MethodRef]->\
		(:Method {Description:"Set to '+request.POST['DSPredecessor']+'.'+request.POST['VarName']+'"})-[:MethodSource]->(d)'

		print 'STATEMENT: '
		print statement 
		tx=graph.cypher.begin()
		tx.append(statement)
		tx.commit()

	# Get standard variables
	stdvars=graph.cypher.execute('match (a:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+request.POST["DSName"]+'"})\
		-[:ItemRef]->(c:ItemDef) return distinct c.Name')
	stdvarsLIST=[]
	for x in stdvars:
		stdvarsLIST.append(x[0])
	# Get model variables
	modelvars=graph.cypher.execute('match (a:Standard {name:"'+parentstandard+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+request.POST["DSName"]+'"})\
		-[:BasedOn]->(c:ItemGroupDef)-[:ItemRef]->(d:ItemDef) return distinct d.Name')
	modelvarsLIST=[]
	for x in modelvars:
		if x not in stdvarsLIST:
			modelvarsLIST.append(x[0])
	# Get study variables
	studyvars=graph.cypher.execute('match (a:Study {Name:"'+study+'"})-[:ItemGroupRef]->(b:ItemGroupDef {Name:"'+request.POST['DSName']+'"})-[:ItemRef]->(c:ItemDef)-->(:Method)-->(d:RecordSource) \
		where d.Type="Model" or d.Type="Other" return distinct c.Name as Name,c.Label as Label')
	studyvarsLIST=[]
	for x in studyvars:
		studyvarsLIST.append(x[0])
		if x[0] in modelvarsLIST:
			modelvarsLIST.remove(x[0])
		if x[0] in stdvarsLIST:
			stdvarsLIST.remove(x[0])
	if stdvarsLIST and modelvarsLIST:
		width=30
	else:
		width=45
	return render(request,'StandardDeveloper1/modelvarlist.html',{'StandardVars':stdvarsLIST,'ModelVars':modelvarsLIST,'StudyVars':studyvarsLIST,'Study':study,'DSName':request.POST['DSName'],'width':width})

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

