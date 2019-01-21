$(document).ready(function(){
	// Build the variable-level metadata for the variable being defined by VLM
	$.getJSON("{{URLPATH}}GetStudyVar",{'Study':$('[name=Study]').val(),'DSName':$('[name=DSName]').val(),'VarName':$('[name=VarName]').val(),'VLMOID':''},function(data){
		$('#varsummary').append('<div class="row" id="NameRow">\
			<div class="col-xs-4">Name</div><div class="col-xs-8">'+data[0]['Name']+'</div></div>\
			<div class="row" id="LabelRow">\
			<div class="col-xs-4">Label</div><div class="col-xs-8">'+data[0]['Label']+'</div></div>\
			<div class="row" id="SASTypeRow">\
			<div class="col-xs-4">SAS Type</div><div class="col-xs-8">'+data[0]['SASType']+'</div></div>\
			<div class="row" id="OrderNumberRow">\
			<div class="col-xs-4">Dataset Position</div><div class="col-xs-8">'+data[0]['OrderNumber']+'</div></div>\
			<div class="row" id="DataTypeRow">\
			<div class="col-xs-4">Data Type</div><div class="col-xs-8">'+data[0]['DataType']+'</div></div>');
	});

	// Capture the chosen subset, store the information, and ask about sources
	$('#subsettable').on('click','.glyphicon-plus',function() {
		var rowindex=$(this).closest('tr').data('index'); 
		var chosensubsetdic=$('#subsettable').bootstrapTable('getData')[rowindex] ;
		$('[name=Action]').val('Add');
		$('[name=CustomYN]').val(false) ;
		// Store all subset data in MD
		$('[name=MD]').val(JSON.stringify({'Subset':{'DTYPE':chosensubsetdic['DTYPE'],'PARAMCD':chosensubsetdic['PARAMCD'],'dop':chosensubsetdic['dop'],'pop':chosensubsetdic['pop'],'wcOID':chosensubsetdic['wcOID'],'_merge':chosensubsetdic['_merge'],'wcOID4VarinStudyTF':chosensubsetdic['wcOID4VarinStudyTF']}}))

		$('#mh4').text($('[name=VarName]').val()+' where '+DisplayConditionColumn('',chosensubsetdic));
		DisplaySource1() ;
		$('#mf').append('<input type="button" class="btn btn-success" value="Next"/>');
		$('#myModal').modal('show') ;
	})

	// Edit a subset
	// First determine which subset was chosen
	$('.container').on('click','.glyphicon-pencil',function() {
		var rowindex=$(this).closest('tr').data('index'); 
		var chosensubsetdic=$('#subsettable').bootstrapTable('getData')[rowindex] ;
		var chosenOID=chosensubsetdic['wcOID']
		var Origin=chosensubsetdic['Origin'] ;

		$('[name=MD1]').val(JSON.stringify({'Subset':{'DTYPE':chosensubsetdic['DTYPE'],'PARAMCD':chosensubsetdic['PARAMCD'],'dop':chosensubsetdic['dop'],'pop':chosensubsetdic['pop'],'wcOID':chosensubsetdic['wcOID'],'_merge':chosensubsetdic['_merge'],'wcOID4VarinStudyTF':chosensubsetdic['wcOID4VarinStudyTF']},'Origin':Origin})) ;
		$('[name=MD]').val(JSON.stringify({'Subset':{'DTYPE':chosensubsetdic['DTYPE'],'PARAMCD':chosensubsetdic['PARAMCD'],'dop':chosensubsetdic['dop'],'pop':chosensubsetdic['pop'],'wcOID':chosensubsetdic['wcOID'],'_merge':chosensubsetdic['_merge'],'wcOID4VarinStudyTF':chosensubsetdic['wcOID4VarinStudyTF']}}))
		$('[name=Action]').val('Edit');

		// Store method information
		$.getJSON('{{URLPATH}}GetStudyVarMethod',{'Study':$('[name=Study]').val(),'DSName':$('[name=DSName]').val(),'VarName':$('[name=VarName]').val(),'VLMOID':chosenOID},function(data) {
			$('#hidemodal').append('<input type="hidden" name="methodchoice" value="'+data[0]['methodchoice'] +'"/>') ;

			if (data[0]['Description'] != '') {
				$('[name=Method1]').val(JSON.stringify({'MethodType':'FreeText','MethodValue':data[0]['Description']})) ;
			}

			else {
				var MethodList=[]
				$.each(data,function() {
					MethodList.push({'Condition':this['If'],'Result':this['Then']})
				})
				$('[name=Method1]').val(JSON.stringify({'MethodType':'Conditions','MethodValue':MethodList})) ;
			}
		})

		DisplaySource1(Origin) ;
		$('#mf').append('<input type="button" class="btn btn-success" value="Next"/>');
		$('[name=Origin]').change() ;

		// Put into modal header
		$('#mh4').text($('[name=VarName]').val()+' where '+DisplayConditionColumn('',chosensubsetdic));

		$('#myModal').modal() ;
	})

	// When Origin is chosen, change the ID of the button
	$('#myModal').on('change','[name=Origin]',function(){
		if ($('[name=Origin] :selected').text() == 'Assigned') {
			$('.btn').attr('id','ToVLMDFromSource1') ;
		}
		else {
			$('.btn').attr('id','ToSource2FromSource1') ;
		}
	})

	// When the Value-level Source question is answered...
	$('#myModal').on('click','[id^=ToSource2]',function(){
		var id=$(this).attr('id') ;
		var Action=$('[name=Action]').val() ;

		if (id == 'ToSource2FromSource1') {
			// Determine which Origin choice was selected
			var Origin=$('[name=Origin] :selected').val() ;
			// Pass this on to a hidden variable for access later
			var MDDic=JSON.parse($('[name=MD]').val()) ;
			MDDic['Origin']=Origin ;
			$('[name=MD]').val(JSON.stringify(MDDic)) ;
			$('#mb').empty();

			if (Action == 'Edit') {
				var subset=JSON.parse($('[name=MD1]').val())['Subset'] ;
				var OID=subset['wcOID'];
				var Origin1=JSON.parse($('[name=MD1]').val())['Origin'] ;
			}

			// If a predecessor, get source info about predecessor
			if (Origin == 'Predecessor') {
				if (Action == 'Add' || Origin1 != 'Predecessor') {
					DisplaySourcePredecessor() ;
				}

				else {
					DisplaySourcePredecessor(Var=$('[name=VarName]').val(),VLM=OID) ;
					$('#PredTable').on('load-success.bs.table',function(e) {
						var currentsources=$('#PredTable').bootstrapTable('getSelections') ;
						$('[name=Sources1]').val(JSON.stringify(currentsources)) ;
						if (currentsources.length) {
							$('#c1').prop('checked',true) ;
						}
					})
				}

				$(this).attr('id','ToPredVarFromPredSource') ;
			}

			else {
				if (Action == 'Add' || Origin1 == 'Predecessor') {
					DisplaySourceDerived() ;
				}

				else {
					DisplaySourceDerived(Var=$('[name=VarName]').val(),VLM=OID) ;
					$('#SourceTable').on('load-success.bs.table',function(e) {
						var currentsources=$('#SourceTable').bootstrapTable('getSelections') ;
						$('[name=Sources1]').val(JSON.stringify(currentsources)) ;
					})
				}

				$(this).attr('id','ToVLMDFromDerivedSource') ;
			}
		}
	})

	// When the Next button is clicked from choosing a predecessor source
	$('#myModal').on('click','[id^=ToPredVar]',function(){
		//$('#varpredsourcebutton').attr('id','varpredsourcevarbutton') ;
		var id=$(this).attr('id') ;
		if (id == "ToPredVarFromPredSource") {
		// Determine whether user chose to select a pre-defined source (c1), to define a new ADaM source (c2), or define a new SDTM source (c3), and save this choice in a hidden variable
			var predsource=$('[name=sourcetype]:checked').attr('id') ;
			$('#hide').append('<input type="hidden" name="predsource" value="'+predsource+'"/>') ;

			// If user chose a pre-defined source
			if (predsource == 'c1') {
				// Determine which row was selected (particularly, if the first row, which has the record sources, was chosen)
				var SourceDic=$('#PredTable').bootstrapTable('getSelections')[0]
				var RecordSourceYN=SourceDic['RecordSourceYN'] ;
				$('#mb').empty() ;
				DisplayPredVarPreDefined(SourceDic,RecordSourceYN) ;
			}

			// Else if user chose to define a new SDTM source
			else if (predsource == 'c3') {
				$('#mb').empty() ;
				DisplayPredVarSDTM() ;
				SourceDic={'Models':'SDTM'} ;
			}

			// User chose to define a new ADaM source
			else if (predsource == 'c2') {
				$('#mb').empty() ;
				DisplayPredVarADAM() ;
				SourceDic={'Models':'ADAM'} ;
			}

			$('#ToPredVarFromPredSource').attr('id','ToVLMDFromPredVar') ;
			$('[name=Sources]').val(JSON.stringify([SourceDic])) ;
		}
	})

	$('#myModal').on('click','[id^=ToVLMD]',function() {
		var id=$(this).attr('id') ;
		var MDDic=JSON.parse($('[name=MD]').val()) ;

		if (id == 'ToVLMDFromPredVar') {
			// Start by collecting the predecessor variable information and storing in Sources hidden variable
			var predsource = $('[name=predsource]').val() ;
			var SourceObj = JSON.parse($('[name=Sources]').val()) ;
			var SourceDic = SourceObj[0] ;

			if (predsource == 'c1') {
				var DatasetList = SourceDic['Datasets'] ;
				var VarList = [] ;
				var VLMSubList=[];
				var method='Copy ' ;
				for (x=0; x<DatasetList.length; x++) {
					VarList.push($('#var_'+DatasetList[x]).val()) ;
					VLMSubList.push($('#sub_'+DatasetList[x]).val())
					if (x>0) {
						method += ', ' ;
					}
					method += DatasetList[x]+"."+$('#var_'+DatasetList[x]).val()+' (where '+ $('#sub_'+DatasetList[x]).val()+')';
				}

				// Store the method in hidden variable
				$('[name=Method]').val(JSON.stringify({MethodType:"FreeText",MethodValue:method})); 

				SourceDic['Vars'] = VarList ;
				SourceDic['VLMSub'] = VLMSubList ;
			}

			else if (predsource == 'c2') {
				SourceDic['Vars'] = $('#adamvar').val() ;
				SourceDic['Datasets'] = $('#adamds').val() ;
				SourceDic['JConditions'] = $('#adamjoin').val() ;
				SourceDic['VLMSub'] = $('#adamvlmsub').val();
				$('[name=Method]').val(JSON.stringify({MethodType:"FreeText",MethodValue:'Copy '+$('#adamds').val()+'.'+$('#adamvar').val()})); 
			}

			else if (predsource == 'c3') {
				SourceDic['Vars'] = $('#sdtmvar').val() ;
				SourceDic['Datasets'] = $('#sdtmds').val() ;
				SourceDic['JConditions'] = $('#sdtmjoin').val() ;
				SourceDic['VLMSub'] = $('#sdtmvlmsub').val();
				$('[name=Method]').val(JSON.stringify({MethodType:"FreeText",MethodValue:'Copy '+$('#sdtmds').val()+'.'+$('#sdtmvar').val()})); 
			}

			$('[name=Sources]').val(JSON.stringify([SourceDic])) ;
		}

		else if (id == 'ToVLMDFromDerivedSource') {
			// Collect source information and store in hidden variable
			$('[name=Sources]').val(JSON.stringify($('#SourceTable').bootstrapTable('getSelections'))) ;
		}

		else if (id == 'ToVLMDFromSource1') {
			MDDic['Origin']=$('[name=Origin] :selected').val() ;
			$('[name=MD]').val(JSON.stringify(MDDic)) ;
		}

		// Then form the parameters to the DisplayVarMD function, and then call it
		$('#mb').empty() ;
		//$('#varpredsourcevarbutton').attr('id','varmd') ;
		var Action=$('[name=Action]').val() ;
		var IGDSource=$('[name=IGDSource]').val() ;
		var CustomYN=$('[name=CustomYN]').val() ;
		var VarName=$('[name=VarName]').val() ;
		

		if (Action == 'Edit') {
			var wcOID=JSON.parse($('[name=MD1]').val())['Subset']['wcOID'] ;
			DisplayVLMD($('[name=Study]').val(),$('[name=DSName]').val(),VarName,wcOID,"Edit")
		}

		else {
			DisplayVLMD($('[name=Study]').val(),$('[name=DSName]').val(),VarName,"","Add")
		}

		$(this).attr('id','ToCT1FromVLMD') ;
	})

	// Once the VLM has been defined, move on to controlled terminology
	$('#myModal').on('click','[id^=ToCT1]',function() {
		var Action=$('[name=Action').val() ;
		var id=$(this).attr('id') ;
		var mddic=JSON.parse($('[name=MD]').val()) ;

		if (id == 'ToCT1FromVLMD') {
			// Store variable-level metadata
			mddic['Name']=$('[name=VLMName').val();
			mddic['Label']=$('[name=VLMLabel').val();
			mddic['Length']=$('[name=VLMLength]').val() ;
			mddic['DataType']=$('[name=VLMDataType]').val() ;
			mddic['Mandatory']=$('[name=VLMMandatory]').val() ;

			$('[name=MD]').val(JSON.stringify(mddic)) ;
		}

		$('#mb').empty() ;

		if (Action == "Add") {
			DisplayCTCustom() ;
			$('#'+id).attr('id','ToListofCodeListsFromCTCustom') ;
		}

		else {
			var StudyCT=$('[name=CT1]').val();
			if (StudyCT) {
				DisplayACodeList('Get1StudyCodeList',{Study:$('[name=Study]').val(),CLCode:'',StudyCLName:StudyCT},$('[name=CTExt]').val() ,$('[name=CTDecodeYN]').val())
				$('#'+id).attr('id','ToCTSummaryFromACodeList') ;
				$('[name=CT]').val(JSON.stringify({'Code':$('[name=CTCode]').val(),'Extensible':$('[name=CTExt]').val(),'DataType':mddic['DataType']})) ;
			}

			else {
				DisplayCTCustom() ;
				$('#'+id).attr('id','ToListofCodeListsFromCTCustom') ;
			}
		}
	})

	// Now that a base codelist has been chosen, display its terms
	$('#myModal').on('click','[id^=ToACodeList]',function() {
		var id=$(this).attr('id') ;
		var Action=$('[name=Action').val() ;
		var mddic=JSON.parse($('[name=MD]').val()) ;

		if (id == 'ToACodeListFromListofCodeLists') {
			var methodchoice=$('[name=methodchoice]').val() ;
			var codelistchoice=$('[name=codelistchoice]').val(); 

			// If user chose to create a codelist from an existing global or study codelist, then collect information from that codelist
			var CodeListDic=$('#CodeListTable').bootstrapTable('getSelections')[0] ;
			var Ext = CodeListDic['Extensible'] ;
			var DecodeYN = CodeListDic['DecodeYN'] ;
			// Store Codelist-level properties (except Name, we'll save that for later)
			$('[name=CT]').val(JSON.stringify({'Code':CodeListDic['CLCode'],'Extensible':Ext,'DataType':CodeListDic['DataType']})) ;

			// Use a global list as a base
			if (codelistchoice == 'a') {
				var url='Get1GlobalCodeList';
				var qp={CLCode:CodeListDic['CLCode'],StandardCLName:CodeListDic['CodeListName']} ;
				$('[name=StandardCTName]').val(CodeListDic['CodeListName']);
				$('[name=CTCode]').val(CodeListDic['CLCode']) ;
			}

			// Use any study list as a base
			else if (codelistchoice == 'b') {
				var url='Get1StudyCodeList';
				var qp={Study:"{{Study}}",CLCode:CodeListDic['CLCode'],StudyCLName:CodeListDic['CodeListName']} ;
			}
		}

		$('#mb').empty();
		if (methodchoice == 'b' || mddic['Origin'] == 'Predecessor') {
			DisplayACodeList(url,qp,Ext,DecodeYN) ;
			$('#'+id).attr('id','ToCTSummaryFromACodeList') ;
		}
	})


	// Once a codelist has been defined, see if it matches other study codelists or the global codelist off of which it is based.  If not, ask the user for a new codelist name
	$('#myModal').on('click','[id^=ToCTSummary]',function() {
		var id = $(this).attr('id');
		var mddic=JSON.parse($('[name=MD]').val()) ;
		var PredYN=(mddic['Origin'] == 'Predecessor') ;

		// Collect all the terms from the table
		TermList=JSON.stringify($('#CodeListItemTable').bootstrapTable('getSelections')) ;

		// Determine if the newly defined codelist already exists
		$.getJSON('{{URLPATH}}CompareCT',{'Study':$('[name=Study]').val(),'StandardCLName':'','StandardCode':'','CT':TermList},function(data) {
			// Get what is already in the CT hidden variable and add to it
			var CTDic=JSON.parse($('[name=CT]').val()) ;
			CTDic['Match']=data['Match'] ;
			CTDic['MatchType']=data['MatchType'] ;
			
			if (data['Match']) {
				$('#mb').empty();

				if (PredYN) {
					$('#'+id).attr('id','ToFinalFromMatchCT');
				}
				else {
					$('#'+id).attr('id','ToMethodbFromMatchCT');
				}

				if (data['MatchType'] == 'Study') {
					if (data['Code']) {
						$('#mb').append('<p>NOTE: The codelist you have defined matches the following study-defined codelist: </p><p>'+data['Name']+' ('+data['Code']+')</p>')
					}

					else {
						$('#mb').append('<p>NOTE: The codelist you have defined matches the following study-defined codelist: </p><p>'+data['Name']+'</p>')
					}
				}

				else {
					$('#mb').append('<p>NOTE: You have chosen the following global codelist: </p><p>'+data['Name']+' ('+data['Code']+')</p>')
				}

				CTDic['Name']=data['Name'] ;
			}

			else {
				CTDic['CT']=$('#CodeListItemTable').bootstrapTable('getSelections') ;
				$('#mb').empty();

				if (PredYN) {
					$('#'+id).attr('id','ToFinalFromNoMatchCT');
				}
				else {
					$('#'+id).attr('id','ToMethodbFromNoMatchCT');
				}

				$('#mb').append('<p>The codelist you have defined is new to this study.  Please provide a name for this new codelist.</p><div class="form-group"><label>New Codelist name</label><input type="text" id="newCodeListName" class="form-control"/></div>') ;
				if (data['Name']) {
					$('#mb').append('<p>Name of global codelist off of which the current codelist is based: <b>'+data['Name']+'</b></p>') ;
				}
			}

			$('[name=CT]').val(JSON.stringify(CTDic)) ;
		})
	})

})



function DisplayConditionColumn(value,row){
	var subset='PARAMCD '+row['pop']+' '+row['PARAMCD'] ;
	if (row['DTYPE']) {
		subset+=' and DTYPE '+row['dop']+' '+row['DTYPE'] ;
	}
	return subset ;
}

function WhichVLMGlyph(value,row){
	if (row['wcOID4VarinStudyTF']){
		return GlyphsRemoveEdit() ;
	}
	else {
		return '<i class="glyphicon glyphicon-plus"></i>'
	}
}

function DisplaySource1(Origin='') {
	$('#mb').append('<p>We start by thinking about where this subset is coming from.  Is it copied from another variable?  \
		Derived from another variable?  Does it come straight from the protocol?\
		</p><div class="form-group"><select class="form-control" name="Origin"><option disabled selected></option>\
		<option value="Assigned">Assigned</option><option value="Protocol">Protocol</option><option value="Derived">Derived</option><option value="Predecessor">Predecessor</option></select></div>')

	if (Origin) {
		$('option[value='+Origin+']').prop('selected',true) ;
	}

}

function DisplayPredVarPreDefined(SourceDic,RSYN) {
	$('#mb').append('<p>In the box(es) below, provide the name of the variable in the source data set being mapped to this predecessor, as well as a description of the subset of source records.</p>')
	if (RSYN == 'Y') {
		for (x=0; x<SourceDic['Datasets'].length; x++) {
			var desc = SourceDic['Models'][x]+'.'+SourceDic['Datasets'][x]
			if (SourceDic['Subsets'][x]) {
				desc += ' where '+SourceDic['Subsets'][x]
			}
			if (SourceDic['Models'][x] == 'SDTM') {
				$('#mb').append('<div class="row"><div class="col-xs-4 form-group"><label>'+desc+' variable name</label><input maxlength="8" id="var_'+SourceDic['Datasets'][x]+'" type="text" class="form-control"></div>\
					<div class="col-xs-10 form-group"><label>'+desc+' source records</label><input type="text" id="sub_'+SourceDic['Datasets'][x]+'" class="form-control" placeholder="e.g. LBTESTCD=ALB"></div></div>');
			}
			else {
				$('#mb').append('<div class="form-group"><label>'+desc+' variable name</label><select id="var_'+SourceDic['Datasets'][x]+'" class="form-control"></select></div>');
				$.getJSON('http://localhost:8000/StandardDeveloper1/GetADaMStudyVars',{'Study':"{{Study}}",'DSName':"{{DSName}}"},function(data){
					$.each(data,function() {
						$('<option value="'+this['VarName']+'">'+this['VarName']+'</option>').appendTo('#var_'+SourceDic['Datasets'][x]);
					})
				})
				$('#mb').append('<div class="col-xs-10 form-group"><label>'+desc+' source records</label><input type="text" id="sub_'+SourceDic['Datasets'][x]+'" class="form-control" placeholder="e.g. LBTESTCD=ALB"></div>')
			}
		}
	}

	else {
		var desc = SourceDic['Models']+'.'+SourceDic['Datasets']
		if (SourceDic['Subsets']) {
			desc += ' where '+SourceDic['Subsets']
		}
		if (SourceDic['Models'] == 'SDTM') {
			$('#mb').append('<div class="form-group"><label>'+desc+'</label><input maxlength="8" id="var_'+SourceDic['Datasets']+'" type="text" class="form-control"></div>');
		}
		else {
			$('#mb').append('<div class="form-group"><label>'+desc+'</label><select id="var_'+SourceDic['Datasets']+'" class="form-control"></select></div>');
			$.getJSON('http://localhost:8000/StandardDeveloper1/GetADaMStudyVars',{'Study':"{{Study}}",'DSName':"{{DSName}}"},function(data){
				$.each(data,function() {
					$('<option value="'+this['VarName']+'">'+this['VarName']+'</option>').appendTo('#var_'+SourceDic['Datasets']);
				})
			})
		}
	}
}

	function DisplayPredVarSDTM() {
		$('#mb').append('<p>In the boxes below, provide information about the SDTM source</p><div class="row"><div class="col-xs-4 form-group"><label>SDTM data set name</label>\
			<input type="text" id="sdtmds" class="form-control"></div></div><div class="row"><div class="col-xs-4 form-group"><label>SDTM variable name</label>\
			<input type="text" id="sdtmvar" class="form-control"></div></div><div class="row"><div class="form-group col-xs-10"><label>Source records</label>\
			<input type="text" id="sdtmvlmsub" class="form-control" placeholder="e.g. LBTESTCD=ALB">\
			</div></div><div class="form-group"><label>Description of merge</label>\
			<textarea rows="3" cols="20" id="sdtmjoin" class="form-control"></textarea></div>') ;
	}

	function DisplayPredVarADAM() {
		$('#mb').append('<div class="form-group"><label>ADaM data set name</label><select id="adamds" class-"form-control"></select>\</div>')
		$.getJSON('http://localhost:8000/StandardDeveloper1/GetADaMStudyDS',{'Study':"{{Study}}"},function(data) {
			$.each(data,function() {
				$('<option value="'+this['DSName']+'</option>').appendTo('#adamds') ;
			})
		})
		$('#mb').append('<p>In the boxes below, provide information about the ADaM source</p><div class="row"><div class="col-xs-4 form-group"><label>ADaM data set name</label>\
			<input type="text" id="adamds" class="form-control"></div></div><div class="row"><div class="col-xs-4 form-group"><label>ADaM variable name</label>\
			<input type="text" id="adamvar" class="form-control"></div></div><div class="row"><div class="form-group col-xs-10"><label>Source records</label>\
			<input type="text" id="adamvlmsub" class="form-control" placeholder="e.g. LBTESTCD=ALB">\
			</div></div><div class="form-group"><label>Description of merge</label>\
			<textarea rows="3" cols="20" id="adamjoin" class="form-control"></textarea></div>') ;
	}


function DisplayVLMD(Study,IGDName,VarNameIn,OID,Action) {

	$('#mb').append('<div class="container">\
		<div class="row"><div class="col-xs-4">Subset Name</div><div class="col-xs-8 form-group"><input type="text" name="VLMName"></div></div>\
		<div class="row"><div class="col-xs-4">Subset Description</div><div class="col-xs-8 form-group"><input type="text" name="VLMLabel"></div></div>\
		<div class="row"><div class="col-xs-4">Length</div><div class="col-xs-8 form-group"><input type="number" min="1" max="200" name="VLMLength"></div></div>\
		<div class="row"><div class="col-xs-4">Mandatory</div><div class="col-xs-8 form-group"><select name="VLMMandatory">\
		<option selected disabled></option><option value="No">No</option><option value="Yes">Yes</option></select></div></div>\
		<div class="row"><div class="col-xs-4">Data Type</div><div class="col-xs-8 form-group"><select name="VLMDataType">\
		<option selected disabled></option><option value= "text">text</option><option value="integer">integer</option><option value="float">float</option>\
		<option value="date">date</option><option value="datetime">datetime</option></select></div></div></div>') ;

	if (Action == "Edit") {
		$.getJSON('{{URLPATH}}GetStudyVar',{'Study':Study,'DSName':IGDName,'VarName':VarNameIn,'VLMOID':OID},function(data) {
			$('[name=VLMName]').val(data[0]['Name']);
			$('[name=VLMLabel]').val(data[0]['Label'])
			$('[name=VLMLength]').val(data[0]['Length']) ;
			$('option[value='+data[0]['Mandatory']+']').prop('selected',true);
			$('option[value='+data[0]['DataType']+']').prop('selected',true);

			$('[name=CT1]').val(data[0]['CodeListNameStudy']) ;
			// Store in hidden dictionary that represents original study metadata
			var md1dic=JSON.parse($('[name=MD1]').val()) ;
			$('[name=MD1]').val(JSON.stringify({'Subset':md1dic['Subset'],'Name':data[0]['Name'],'Label':data[0]['Label'],'DataType':data[0]['DataType'],'Origin':data[0]['Origin'],'Length':data[0]['Length'],'Mandatory':data[0]['Mandatory']})) ;

		}) ;
	}
}

function DisplayFinal(){
	$('#mb').append('<p>Your subset is complete!</p><br><input class="btn btn-success" type="submit" value="Finish" id="last"/>');
	$('#mf').empty();
}

