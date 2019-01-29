$(document).ready(function(){
	// When a user wants to define custom CT for a non-predecessor not associated with a standard codelist, give them the option of how to begin that process (e.g. from a global list (methodchoice=a), a study list (b), or from scratch (c))
	$('#myModal').on('change','#cstct1',function() {
		// Determine which non-predecessor method choice was made
		var methodchoice=$('#cstct1 :selected').val().substr(6,1) ;
		$('#hidemodal').append('<input type="hidden" name="methodchoice" value="'+methodchoice +'"/>') ;

		if (methodchoice == 'a' || methodchoice == 'b') {
			$('#nopredchoice').remove() ;
			$('#mb').append('<div class="form-group"><label>Choose how to define a set of allowable values</label><select class="form-control" id="cstct2"><option disabled selected></option><option value="cstct2a">Based on a global list</option><option value="cstct2b">Based on a study list</option><option value="cstct2d">Create a list from scratch</option></select></div>') ;
		}

		else if (methodchoice == 'c') {
			$('.btn').attr('id','ToMethodbFromCTCustom') ;
		}
	})

	// If/when an ADaM data set is chosen as a new source, then this will populate the variable list 
	$('#myModal').on('change','#adamds',function() {
		var selectedadamds = $('#adamds :selected').val() ;
		$('#adamvar').empty() ;
		$('#adamvar').append('<option disabled selected>Select ADaM variable</option>')
		$.getJSON($('[name=URLPath]').val()+'GetADaMStudyVars',{'Study':$('[name=Study]').val(),'DSName':selectedadamds},function(data){
			$.each(data,function() {
				$('<option value="'+this['VarName']+'">'+this['VarName']+'</option>').appendTo('#adamvar');
			})
		})
	})

	// When a user wants to define custom CT from scratch, give them a checkbox to tick if they want decodes
	$('#myModal').on('change','#cstct2',function() {
		if ($('#cstct2').val().substr(6,1) == 'd') {
			$('#mb').append('<div class="checkbox"><label><input type="checkbox" id="scratchdecodes">Check here to include decodes with your list</label></div>') ;
		}
	})

	$('#myModal').on('click','[id^=ToListofCodeLists]',function() {
		var id=$(this).attr('id') ;
		var mddic=JSON.parse($('[name=MD]').val()) ;
		if (id == 'ToListofCodeListsFromCTCustom') {
			// Determine how user wants to build a codelist (from a global (a), from a study (b), no codelist (c), from scratch (d)
			var codelistchoice=$('#cstct2').val().substr(6,1) ;
			$('#hide').append('<input type="hidden" name="codelistchoice" value="'+codelistchoice+'"/>');

			// When a user wants to define custom CT based on another codelist, but for a variable not associated with a standard codelist, build a table of codelists
			if (codelistchoice == 'a' || codelistchoice == 'b') {
				$('#mb').empty() ;
				DisplayListofCodeLists(codelistchoice) ;
				$('#ToListofCodeListsFromCTCustom').attr('id','ToACodeListFromListofCodeLists') ;
			}

			// Build a list from scratch 
			else if (codelistchoice == 'd') {
				var mddic=JSON.parse($('[name=MD]').val()) ;
				var DecodeYN=$('#scratchdecodes').prop('checked') ;
				//$('#ct1a').attr('id','ct2');
				$('[name=CT]').val(JSON.stringify({'Extensible':'Yes','DataType':mddic['DataType']})) ;
				$('#mb').empty() ;
				DisplayScratchCodeList(DecodeYN) ;
				$('#ToListofCodeListsFromCTCustom').attr('id','ToCTSummaryFromScratchCodeLists') ;
			}

			// no codelist
			else if (mddic['Origin'] == 'Predecessor') {
				// go to comment page
				$('#mb').empty() ;
				$('#ToListofCodeListsFromCTCustom').attr('id','ToFinalFromComment') ;
				DisplayMethodComment(type='cvar') ;
			}

			else {
				$('#mb').empty() ;
				DisplayMethodbChoice() ;
				$('#'+id).attr('id','mt1b') ;
			}
		}
	})

// Start methods
	$('#myModal').on('click','[id^=ToMethodb]',function() {
		var id = $(this).attr('id');
		// If a codelist name was provided, save it in the CT hidden variable
		if (id == 'ToMethodbFromNoMatchCT') {
			var CTDic=JSON.parse($('[name=CT]').val()) ;
			CTDic['Name']=$('#newCodeListName').val() ;
			$('[name=CT]').val(JSON.stringify(CTDic)) ;
		}
		$('#mb').empty() ;
		DisplayMethodbChoice() ;
		$('.btn').attr('id','mt1b') ;
	})

	// Capture the method choice and call the appropriate function
	$('#myModal').on('click','#mt1b',function() {
		var methodb=$('[name=methodbchoice]:checked').val() ;
		var Action=$('[name=Action]').val();
		$('#mb').empty() ;

		if (methodb == 'freetext') {
			$('.btn').attr('id','ToCommentFromFreeMethod');
			//$('#mb').append('<div class="container"><p>Enter programming instruction in the box below</p><div class="form-group"><textarea cols="65" rows="15" id="free"></textarea></div>') ;
			DisplayMethodComment();

			if (Action == 'Edit') {
				var m1=JSON.parse($('[name=Method1]').val()) ;
				if (m1['MethodType'] == 'FreeText') {
					$('#free').val(m1['MethodValue']) ;
				}
			}
		}

		else {
			DisplayMethodConditions(false) ;
			$('.btn[value=Next]').attr('id','ToCommentFromCondMethod') ;
			if (Action == 'Edit') {
				var m1=JSON.parse($('[name=Method1]').val()) ;
				if (m1['MethodType'] == 'Conditions') {
					for (x=0;x<m1['MethodValue'].length;x++) {
						var ie ;
						if (x == 0) {
							ie='If' ;
						}
						else if (x == m1['MethodValue']-1) {
							ie='Else' ;
						}
						else {
							ie='Else if' ;
						}
						$('#ConditionTable').bootstrapTable('append',{
							IfElse:ie,
							Condition:x['Condition'],
							Result:x['Result']
						})
					}
				}
			}
		}
	})

	// Arrive at comment page 
	$('#myModal').on('click','[id^=ToComment]',function() {
		// Capture the id that got us here
		var id=$(this).attr('id'); 
		var CustomYN=$('[name=CustomYN]').val() ;
		var mddic=JSON.parse($('[name=MD]').val()) ;
		// If arriving here from free text method
		if (id == 'ToCommentFromFreeMethod') {
			//$('[name=Method]').val(JSON.stringify({'MethodType':'FreeText','MethodValue':$('#free').val()})) ;
			ProcessMethodComment(type='m') ;
		}
		// If arriving here from condition method
		else if (id == 'ToCommentFromCondMethod') {
			$('[name=Method]').val(JSON.stringify({'MethodType':'Conditions','MethodValue':$('#ConditionTable').bootstrapTable('getData')})) ;
		}

		else if (id == 'ToCommentFromNoMatchCT') {
			var CTDic=JSON.parse($('[name=CT]').val()) ;
			CTDic['Name']=$('#newCodeListName').val() ;
			$('[name=CT]').val(JSON.stringify(CTDic)) ;
		}

		else if (id == 'ToCommentFromVLM') {
			if (CustomYN == true) {
				mddic['Label']=$('[name=VarLabel]').val() ;
				mddic['SASType']=$('[name=VarSASType]').val() ;
			}

			mddic['DataType']=$('[name=VarDataType]').val() ;
			mddic['OrderNumber']=$('[name=VarOrderNumber]').val() ;
			$('[name=MD]').val(JSON.stringify(mddic)) ;

		}

		$('#mb').empty() ;

		if ($('[name=Class]').val() == 'BASIC DATA STRUCTURE' && id != 'ToCommentFromVLM' && ! ('Subset' in mddic)) {
			DisplayDtypeMethods($('[name=Study]').val(),$('[name=DSName]').val()) ;
		}

		else {
			DisplayMethodComment(type='cvar') ;
			if (id == 'ToCommentFromVLM') {
				$('[id='+id+']').attr('id','ToFinalFromCommentVLM') ;
			}
			else {
				$('[id='+id+']').attr('id','ToFinalFromComment') ;
			}
		}
	})

	$('#myModal').on('click','[id^=ToFinalFromComment]',function() {
		ProcessMethodComment() ;
		$('[value=Next').remove() ;
		$('#mb').empty() ;
		DisplayFinal() ;
		var id=$(this).attr('id'); 
		if (id == 'ToFinalFromCommentVLM'){
			$('#last').attr('formaction','NewVarVLM') ;
		}

	})

	// Enable the radio buttons in the predecessor source table when the first radio button is selected, then ask for predecessor source variable names
	$('#myModal').on('click','#c1',function(){
		$('[name=tableradio]').attr('disabled',false);
	})


	// When a user chooses to define a new source
	$('#mb').on('change','[name=newsource]',function() {
		// For ADaM, create a dropdown list of data sets.  For SDTM, just create a text box
		var model=$('[name=newsource]:checked').val() ;
		$('#radiocontainer').remove() ;
		if (model == 'adam') {
			var dstxt='<label>ADaM data set name</label><select id="newsourceds" class-"form-control"></select>' ;
		}
		else {
			var dstxt='<label>SDTM data set name</label><input type="text" id="newsourceds" class="form-control">' ;
		}
		$('#mb').append('<div id="inputcontainer"><p>Provide the name of the source dataset along with a description of the subset and how it is merged with the main data set.</p><div class="form-group">'+dstxt+'</div><div class="form-group"><label>Description of dataset subset</label><textarea rows="3" id="newsourcesubset" class="form-control"></textarea></div><div class="form-group"><label>Description of merge</label><textarea rows="3" id="newsourcejoin" class="form-control"></textarea></div><div class="form-group"><button type="button" id="'+model+'newsourcebutton" class="btn-success">Add New Source</button></div></div>')
	})

	// When a new source button is clicked then add the information to the table
	$('#mb').on('click','#adamnewsourcebutton,#sdtmnewsourcebutton',function() {
		var model=$(this).attr('id').substr(0,4);
		var Display=model.toUpperCase()+'.'+$('#newsourceds').val() ;
		if ($('#newsourcesubset').val()){
			Display += ' (where '+$('#newsourcesubset').val()+')' ;
		}

		$('#SourceTable').bootstrapTable('append',{
			state:true,
			Models:model.toUpperCase(),
			Display:Display,
			Datasets:$('#newsourceds').val(),
			JConditions:$('#newsourcejoin').val(),
			Subsets:$('#newsourcesubset').val()
		}) ;

		$('#inputcontainer').remove() ;

		$('#mb').append('<div class="container" id="radiocontainer"><div class="radio"><label><input type="radio" name="newsource" value="adam">Define a new ADaM source</label></div><div class="radio"><label><input type="radio" name="newsource" value="sdtm">Define a new SDTM source</label></div></div>') ;
	})

	// When specifying page reference information 
	$('#mb').on('change','[name=pagetype]',function() {
		var pagetype=$('[name=pagetype]:checked').val() ;
		$('#pageinfo').empty() ;
		if (pagetype == 'NamedDestination') {
			$('#pageinfo').append('<label>Enter the name of the PDF named destination</label><input type="text" id="pagetext" class="form-control">') ;
		}
		else {
			$('#pageinfo').append('<label>Enter a space-delimited list of individiual pages (e.g. 3 19 21) or a range of pages separated by a hyphen (e.g. 14-16)</label><input type="text" id="pagetext" class="form-control">') ;
		}
	})
})





	function DisplaySourcePredecessor(Var='',VLM='') {
		$('#mb').append('<p>We now identify the data set and the variable from which the predecessor originated.  Start by either selecting a source data set that has already been defined, or define a new one.  </p><div class="radio"><label><input type="radio" name="sourcetype" id="c1">Select an already existing source.</label></div><table id="PredTable"></table>') ;

		$('#PredTable').bootstrapTable({
			url:$('[name=URLPath]').val()+"GetStudySources",
			//queryParams:"StudySourceParms",
			queryParams:{Study:$('[name=Study]').val(),DSName:$('[name=DSName]').val(),VarName:Var,VLMOID:VLM},
			clickToSelect:'true',
			selectItemName:'tableradio',
			columns:[{
				field:'state',
				radio:'true',
				formatter:{disabled:(Var == '')}
			}, {
				field:'Models',
				class:'hidden'
			}, {
				field:'Display',
				title:'Source'
			}, {
				field:'Datasets',
				class:'hidden',
			}, {
				field:'JConditions',
				class:'hidden'
			}, {
				field:'Subsets',
				class:'hidden'
			}, {
				field:'RecordSourceYN',
				class:'hidden'
			}]
		})

		$('#mb').append('<div class="radio"><label><input type="radio" name="sourcetype" id="c2">Define a new ADaM source</label></div>')

		$('#mb').append('<div class="radio"><label><input type="radio" name="sourcetype" id="c3">Define a new SDTM source</label></div>')
	}

	function DisplaySourceDerived(Var='',VLM='') {
		$('#mb').append('<p>We now identify the data sets from which the variable originated.  Select any number of source data sets that have already been defined, and define any number of new ones.  </p><table id="SourceTable"></table>') ;

		$('#SourceTable').bootstrapTable({
			url:$('[name=URLPath]').val()+"GetStudySources",
			//queryParams:"StudySourceParms",
			queryParams:{Study:$('[name=Study]').val(),DSName:$('[name=DSName]').val(),VarName:Var,VLMOID:VLM},
			clickToSelect:'true',
			columns:[{
				field:'state',
				checkbox:'true'
			}, {
				field:'Models',
				class:'hidden'
			}, {
				field:'Display',
				title:'Source'
			}, {
				field:'Datasets',
				class:'hidden',
			}, {
				field:'JConditions',
				class:'hidden'
			}, {
				field:'Subsets',
				class:'hidden'
			}, {
				field:'RecordSourceYN',
				class:'hidden'
			}]
		})

		$('#mb').append('<div class="container" id="radiocontainer"><div class="radio"><label>\
			<input type="radio" name="newsource" value="adam">Define a new ADaM source</label></div><div class="radio"><label>\
			<input type="radio" name="newsource" value="sdtm">Define a new SDTM source</label></div></div>') ;

		$.getJSON($('[name=URLPath]').val()+'GetADaMStudyDS',{'Study':"{{Study}}"},function(data) {
			$.each(data,function() {
				$('<option value="'+this['DSName']+'">'+this['DSName']+'</option>').appendTo('#adamds') ;
			})
		})
	}


	function DisplayCTCustom() {

		var mddic=JSON.parse($('[name=MD]').val()) ;
		var Origin=mddic['Origin'] ;

		$('#mb').append("<p>It's now time to start thinking about how a programmer will populate this variable.  We begin by thinking about the values allowed for this variable.  Make a selection from the dropdown below.</p>") ;

		if (Origin != 'Predecessor') {
			$('#mb').append('<div id="nopredchoice" class="form-group"><label>Choose here whether to define programming instructions along with allowable values or separate from allowable values.</label><br/>\
				<select id="cstct1"><option disabled selected></option><option value="cstct1a">Define allowable values with programming instructions</option>\
				<option value="cstct1b">Define allowable values separate from programming instructions</option><option value="cstct1c">Not applicable for this variable - skip to programming instructions</option></select></div>') ;
		}

		else {
			$('#mb').append('<div class="form-group"><label>Choose how to define a set of allowable values</label><br/>\
				<select class="format-control" id="cstct2"><option disabled selected></option><option value="cstct2a">Based on a global list</option>\
				<option value="cstct2b">Based on a study list</option><option value="cstct2c">Not applicable</option><option value="cstct2d">Create a list from scratch</option></select></div><br>')
		}
	}

	function DisplayListofCodeLists(codelistchoice) {
		var qp='' ;

		// Choice to start from a global list
		if (codelistchoice == 'a') {
			var url=$('[name=URLPath]').val()+"GetAllGlobalCL" ;
		}

		// Choice to start from a study list
		else if (codelistchoice == 'b') {
			var url=$('[name=URLPath]').val()+"GetAllStudyCL" ;
			//var qp='StudySourceParms' ;
			var qp={Study:"{{Study}}"} ;
		}

		$('#CodeListTable').remove() ;

		$('#mb').append('<div class="form-group"><label>Select a list from the table below on which to base your new list.</label></div><table id="CodeListTable" style="display:block;max-height:200px;overflow-y:auto;-ms-overflow-style:-ms-autohiding-scrollbar"></table>') ;

		$('#CodeListTable').bootstrapTable({
			url:url,
			queryParams:qp,
			scrollY:"200px",
			columns:[{
				field:'state',
				radio:'true'
			}, {
				field:'CLCode',
				title:'Code'
			}, {
				field:'CodeListName',
				title:'CodeList Name'
			}, {
				field:'Extensible',
				class:'hidden',
			}, {
				field:'DataType',
				class:'hidden'
			}, {
				field:'DecodeYN',
				class:'hidden'
			}]
		})
	}

	function DisplayScratchCodeList(DecodeYN) {
		// var DecodeYN=$('#scratchdecodes').prop('checked') ;
		// alert('DECODEYN: '+$('#scratchdecodes').prop('checked')) ;

		$('#mb').append('<div class="form-group"><label>Select from the table below the values allowed for this variable.</label></div>') ;

		if (DecodeYN) {
			ExtCT(true);
			$('#mb').append('<table id="CodeListItemTable" style="display:block;max-height:200px;overflow-y:auto;-ms-overflow-style:-ms-autohiding-scrollbar"></table>') ;
			$('#CodeListItemTable').bootstrapTable({
				scrollY:"200px",
				columns:[{
					field:'state',
					checkbox:'true'
				}, {
					field:'CodedValue',
					title:'Submission Value'
				}, {
					field:'Decode',
					title:'Decode',
				}]
			})
		}

		else {
			ExtCT(false) ;
			$('#mb').append('</div><table id="CodeListItemTable" style="display:block;max-height:200px;overflow-y:auto;-ms-overflow-style:-ms-autohiding-scrollbar"></table>') ;
			$('#CodeListItemTable').bootstrapTable({
				scrollY:"200px",
				columns:[{
					field:'state',
					checkbox:'true'
				}, {
					field:'CodedValue',
					title:'Submission Value'
				}]
			})
		}
	}

	function DisplayMethodbChoice() {
		// Offer choice of how to define method (with conditions or free text)
		$('#mb').append('<p>It is now time to provide explicit instructions for programming.  You can do this either by providing a free text explanation, or by defining conditions and their results.  \
			If you have defined a set of allowable values, be sure your instructions lead to values in that set.</p>\
			<div class="container" id="radiocontainer"><div class="radio"><label><input type="radio" name="methodbchoice" value="freetext">Provide programming instructions with free text</label></div>\
			<div class="radio"><label><input type="radio" name="methodbchoice" value="conditions">Provide programming instructions with conditions</label></div></div>') ;
	}

	function DisplayACodeList(url,qp,Ext,DecodeYN) {
		$('#mb').append('<div class="form-group"><label>Select from the table below the values allowed for this variable.</label></div><table id="CodeListItemTable" style="display:block;max-height:200px;overflow-y:auto;-ms-overflow-style:-ms-autohiding-scrollbar"></table>') ;

		if (Ext == 'Yes') {
			ExtCT(DecodeYN) ;
		}

		if (DecodeYN == true) {
			$('#CodeListItemTable').bootstrapTable({
				url:$('[name=URLPath]').val()+url,
				queryParams:qp,
				scrollY:"200px",
				columns:[{
					field:'state',
					checkbox:'true'
				}, {
					field:'ItemCode',
					title:'Code'
				}, {
					field:'CodedValue',
					title:'Submission Value'
				}, {
					field:'Decode',
					title:'Decode'
				}]
			})
		}

		else {
			$('#CodeListItemTable').bootstrapTable({
				url:$('[name=URLPath]').val()+url,
				queryParams:qp,
				scrollY:"200px",
				columns:[{
					field:'state',
					checkbox:'true'
				}, {
					field:'ItemCode',
					title:'Code'
				}, {
					field:'CodedValue',
					title:'Submission Value'
				}]
			})
		}
	}

	function ExtCT(DecodeYN) {
		$('#mb').append('<p>To add terms to your list, enter the value in the box below (and if applicable, the decode), and then click the Add Term button.</p><div class="container" id="newtermcontainer"><div class="form-group"><textarea cols="35" rows="2" id="code" placeholder="Enter term here"></textarea></div>') ;

		if (DecodeYN) {
			var functioncall="AddTerm(true);" ;
			$('#newtermcontainer').append('<div class="form-group"><textarea cols="35" rows="2" id="decode" placeholder="Enter decode here"></textarea></div>') ;
		}

		else {
			var functioncall="AddTerm(false);"
		}

		$('#newtermcontainer').append('<div class="form-group"><button type="button" onclick="'+functioncall+'" class="btn btn-success" id="addtermbutton">Add Term</button></div>') ;
	}

	function AddTerm(DecodeYN) {
		if (DecodeYN) {
			// $('#CodeListItemTable').bootstrapTable('append',{
			// 	state:true,
			// 	CodedValue:$('#code').val(),
			// 	Decode:$('#decode').val()
			// })
			Add2Table($('#CodeListItemTable'),['CodedValue','Decode'],[$('#code'),$('#decode')]) ;
			//$('#decode').val(null) ;
			$('#decode').attr('placeholder','Enter decode here') ;
		}

		else {
			// $('#CodeListItemTable').bootstrapTable('append',{
			// 	state:true,
			// 	CodedValue:$('#code').val()
			// })
			Add2Table($('#CodeListItemTable'),['CodedValue'],[$('#code')]) ;
		}

		//$('#code').val(null) ;
		$('#code').attr('placeholder','Enter term here') ;
	}

	function DisplayMethodConditions(WithCT) {
		var pi='<p>Defining programming instructions with conditions means that we define conditions and the results that go with them, as well as the final result that is assigned when no defined conditions are met.  Begin by indicating whether the result you are defining comes with a condition or is the "all else fails" result.  If it comes with a condition, populate the Condition box that appears.  ';
		if (WithCT) {
			pi+='Then choose a result from the dropdown, or, if applicable, add a result manually.  '
		}
		else {
			pi+='Then populate the Result box that appears.  '
		}

		pi+='When you are finished, click the button to add to the table or click a row to add before the clicked row.</p>' ;

		$('#mb').append(pi+'<div class="container" id="inputcontainer"><div class="radio"><label><input type="radio" name="ifelse" value="if">Define a condition and a result</label></div><div class="radio"><label><input type="radio" name="ifelse" value="else">Result when all else fails</label></div><div class="form-group"><textarea cols="35" rows="2" id="condition" placeholder="Condition" disabled></textarea></div></div>') ;

		if (WithCT) {

		}
		else {
			$('#inputcontainer').append('<div class="form-group"><textarea cols="35" rows="2" id="result" placeholder="Result" disabled></textarea></div>') ;
		}

		$('#inputcontainer').append('<div class="form-group"><button type="button" onclick="AddCondition();" class="btn btn-success" id="addcondition">Add</button></div>') ;

		$('#mb').append('<table id="ConditionTable" style="display:block;max-height:200px;overflow-y:auto;-ms-overflow-style:-ms-autohiding-scrollbar"></table>') ;

		$('#ConditionTable').bootstrapTable({
			scrollY:"200px",
			columns:[{
				field:'IfElse'
			}, {
				field:'Condition',
				title:'Condition'
			}, {
				field:'Result',
				title:'Result',
			}]
		})
	}

	function DisplayMethodComment(type='') {
		var txt='' ;
		if (type.substr(0,1) == 'c') {
			var x1='comment';
			if (type == 'cds') {
				x2='data set';
			}
			else if (type == 'cvar') {
				x2='variable';
			}
			else if (type == 'cvlm') {
				x2='subset'
			}

			txt += '<p>What else is there to know about your '+x2+'?  '
		}

		else {
			var x1='method'
		}

		txt += 'Place your free text '+x1+' in the box below '
		if (x1 == 'method') {
			txt += '(required).'
		}
		else {
			txt += '(optional).'
		}

		$('#mb').append('<div class="container"><p>'+txt+'</p><div class="form-group"><textarea cols="65" rows="15" id="free"></textarea></div><p>Optionally, you can add a reference to a document.</p>\
			<div class="form-group"><select class="form-control" id="doc"><option disabled selected>Choose a document</option></select></div><div class="radio">\
			<label><input type="radio" name="pagetype" value="NamedDestination">Named Destination</label></div><div class="radio"><label><input type="radio" name="pagetype" value="PhysicalRef">Page Number(s)</label></div><div class="form-group" id="pageinfo"></div></div>') ;

		$.getJSON($('[name=URLPath]').val()+'GetDocs',{'Study':$('[name=Study]').val()},function(data) {
			$.each(data,function() {
				$('<option value="'+this['File']+'">'+this['File']+'</option>').appendTo('#doc') ;
			})
		})
	}

	function ProcessMethodComment(type='c') {
		var dict={'DocName':$('#doc :selected').val(),'pagetype':$('[name=pagetype]:checked').val(),'pagetext':$('#pagetext').val()} ;
		var freevalue=$('#free').val() ;

		if (type.substr(0,1) == 'm') {
			dict['MethodType'] = 'FreeText';
			dict['MethodValue'] = freevalue ;
			$('[name=Method]').val(JSON.stringify(dict)) ;
		}

		else {
			dict['CommentValue'] = freevalue;
			$('[name=Comment]').val(JSON.stringify(dict)) ;
		}
	}
