$(document).ready(function() {
	// When the data set metadata is finished, complete the MD dictionary and move on to record sources
	$('#myModal').on('click','[id^=ToRecordSource]',function() {
		var mddic=JSON.parse($('[name=MD]').val()) ;
		var StandardTF=mddic['StandardTF'] ;

		if (StandardTF == false){
			mddic['Label']=$('[name=DSLabel]').val() ;
			mddic['Name']=$('[name=DSName]').val() ;
		}

		if (mddic['Name'] != "ADSL") {
			mddic['Structure']=$('[name=DSStructure]').val();
			mddic['Repeating']=$('[name=DSRepeating]').val();
			mddic['Reference']=$('[name=DSReference]').val();
			$('[name=MD]').val(JSON.stringify(mddic)) ;
		}

		$('#mb').empty();
		DisplayRecordSources() ;

		// If this is not a BDS data set, then make this the last modal by turning the button into a submit button.
		// Otherwise, move on to defining parameters.
		if (mddic['Class'] != 'BASIC DATA STRUCTURE') {
			$('[value=Next]').attr('id','ToCmtFromSource') ;
		}

		else {
			$('[value=Next]').attr('id','ToParcat1FromRecordSource') ;
		}
	})

	// When finished, store the record sources
	$('form').submit(function() {
		var id=$(this).attr('id') ;

		if (id == 'dsmd') {
			// Process comments
			ProcessMethodComment() ;
		}

		else if (id == 'GenerateADaMSpec' || id == 'GenerateDefine') {
			$('#myModal').modal('hide') ;
		}
	})


	$('#myModal').on('click','[id^=ToParcat1]',function() {
		$('[name=RecordSources]').val(JSON.stringify($('#sourcetable').bootstrapTable('getSelections'))) ;
		// Ask if they plan to define PARCAT variables
		$('#mb').empty() ;
		$('#mb').append('<p>Since the data set you are now defining is a BDS structure, it is now time to start thinking about the parameters this data set will define.</p><p>The ADaM model allows us to categorize our parameters \
			in any number of ways (i.e. PARCAT1...PARCATn).  Indicate below whether or not you want to define parameter categories.</p><div class="radio"><label><input type="radio" name="parcatyn" value="Y">Yes, I want to define parameter \
			categories</label></div><div class="radio"><label><input type="radio" name="parcatyn" value="N">No, I do not need parameter categories</label></div>')
	})

	$('#myModal').on('change','[name=parcatyn]',function() {
		var choice=$('[name=parcatyn]:checked').val() ;
		if (choice == 'Y') {
			// Change the button to take them to parcat definition page
			$('[value=Next]').attr('id','ToParcat2FromParcat1') ;
		}
		else {
			// If the user doesn't need PARCAT, go straight to parameter definitions
			$('[value=Next]').attr('id','ToParmDef1FromParcat1') ;
		}
	})

	// PARCAT definitions
	$('#myModal').on('click','[id^=ToParcat2]',function() {
		var id=$(this).attr('id');
		var mddic=JSON.parse($('[name=MD]').val()) ;

		// First parcat
		if (id == 'ToParcat2FromParcat1') {
			$('#mb').empty() ;
			// Create a partial dictionary, put it in a list, and store it in the hidden variable Parcats
			$('[Name=Parcats]').val(JSON.stringify([{'Name':'PARCAT1'}])) ;
			$('#mh4').text(mddic['Name']+' metadata - PARCAT1') ;
			// Change the id on the Next button
			$('[value=Next]').attr('id','ToParmDef1FromParcat2') ;
			DisplayParcatDef() ;
		}

		// Subsequent parcats
		else if (id == 'ToParcat2FromParcat2') {
			// First proess what was last entered
			var ParcatList=JSON.parse($('[name=Parcats]').val()) ;
			var ParcatNbr=ParcatList.length ;
			var LastDic=ParcatList[ParcatNbr-1] ;
			LastDic['Comment']=$('#ParcatComment').val() ;
			LastDic['CT']=$('#ParcatTable').bootstrapTable('getSelections') ;
			LastDic['ParcatNTF']=$('#ParcatNTF').prop('checked') ;

			// Calculate SASLENGTH
			var saslength=0 ;
			for (x in LastDic['CT']) {
				saslength=Math.max(saslength,LastDic['CT'][x]['term'].length) ;
			}
			LastDic['SASLength']=saslength; 

			// Now add the completed dictionary back into the list
			ParcatList.splice(ParcatNbr-1,1,LastDic);
			// Now add a partial dictionary for the new parcat and save to the hidden variable
			ParcatList.push({'Name':'PARCAT'+(ParcatNbr+1)}) ;
			$('[name=Parcats]').val(JSON.stringify(ParcatList)) ;
			$('#ParcatComment').val(null);
			$('#ParcatTable').bootstrapTable('removeAll') ;
			$('#ParcatNTF').prop('checked',false) ;
			$('#mh4').text(mddic['Name']+' metadata - PARCAT'+(ParcatNbr+1)) ;
		}
	})

	$('#myModal').on('click','[id^=ToParmDef1]',function() {
		var id=$(this).attr('id'); 
		if (id == 'ToParmDef1FromParcat2') {
			// Process the last parameter category
			var ParcatList=JSON.parse($('[name=Parcats]').val()) ;
			var ParcatNbr=ParcatList.length ;
			var LastDic=ParcatList[ParcatNbr-1] ;
			LastDic['Comment']=$('#ParcatComment').val() ;
			LastDic['CT']=$('#ParcatTable').bootstrapTable('getSelections') ;
			LastDic['ParcatNTF']=$('#ParcatNTF').prop('checked') ;

			// Calculate SASLENGTH
			var saslength=0 ;
			for (x in LastDic['CT']) {
				saslength=Math.max(saslength,LastDic['CT'][x]['term'].length) ;
			}
			LastDic['SASLength']=saslength; 

			ParcatList.splice(ParcatNbr-1,1,LastDic);
			$('[name=Parcats]').val(JSON.stringify(ParcatList)) ;

			$('#ToParcat2FromParcat2').remove() ;
			$('#mf').prepend('<button type="button" id="ToParmDef1FromParmDef1" class="btn btn-success">Define another parameter</button');
			$('[value=Next]').attr('id','ToCmtFromParm') ;
		}

		else if (id == 'ToParmDef1FromParmDef1') {
			ProcessParmDef() ;
		}

		else if (id == 'ToParmDef1FromParcat1') {
			$('#mf').prepend('<button type="button" id="ToParmDef1FromParmDef1" class="btn btn-success">Define another parameter</button');
			$('[value=Next]').attr('id','ToCmtFromParm') ;
		}

		$('#mb').empty() ;
		DisplayParmDef() ;
	})

	// Enable/disable DTYPE boxes when Other is chosen/not chosen
	$('#myModal').on('change',$('#dtypes'),function() {
		var sel=$('#dtypes :selected') ;
		if (sel.val() == 'other') {
			$('#dtypevalue').prop('disabled',false);
			$('#dtypedesc').prop('disabled',false);
		}
		else {
			$('#dtypevalue').prop('disabled',true);
			$('#dtypedesc').prop('disabled',true);
		}
	})

	// When the user chooses to edit variables from a chosen data set from the StudyHome page
	$('#pageform').on('click','.EditVarFromHome',function() {
		var rowindex=$(this).closest('tr').data('index'); 
		var ds=$('#dsmdtable').bootstrapTable('getData')[rowindex]['Dataset'] ;
		var igdsource=$('#dsmdtable').bootstrapTable('getData')[rowindex]['IGDSource'] ;
		var DSClass=$('#dsmdtable').bootstrapTable('getData')[rowindex]['Class'] ;
		$('[name=Dataset]').val(ds);
		$('[name=IGDSource]').val(igdsource);
		$('[name=Class').val(DSClass);
		$('#pageform').submit() ;
	})

	$('#myModal').on('click','[id^=ToCmt]',function() {
		var id = $(this).attr('id') ;
		if (id == 'ToCmtFromParm') {
			ProcessParmDef();
			$('#ToParmDef1FromParmDef1').remove();
			$('#ToCmtFromParm').remove() ;
		}

		else {
			$('[value=Next]').remove();
			$('[name=RecordSources]').val(JSON.stringify($('#sourcetable').bootstrapTable('getSelections'))) ;
		}

		$('#mf').append('<input type="submit" value="Finish" class="btn btn-success">');

		$('#mb').empty();
		DisplayMethodComment(type='cds'); 
	})
})



function ProcessParmDef() {
	// Store collected Parameter definitions in Parmdefs hidden variable
	var parmdefdic={'paramcd':$('#paramcd').val(),'param':$('#param').val()} ;
	// Make a list of parcat values
	// Start by using the hidden Parcats variable to see how many parcats there are
	if ($('[name=Parcats]').val()) {
		var parcatnbr=JSON.parse($('[name=Parcats]').val()).length ;
		var parcatlist=[];
		for (x=0; x<parcatnbr; x++) {
			parcatlist.push($('#parcat'+(x+1)).val()) ;
		}
		parmdefdic['parcats']=parcatlist ;
	}
	parmdefdic['dtypes']=$('#dtypetable').bootstrapTable('getSelections') ;

	if ($('[name=Parmdefs]').val()) {
		var ParmdefList=JSON.parse($('[name=Parmdefs]').val()) ;
		ParmdefList.push(parmdefdic) ;
	}

	else {
		ParmdefList=[parmdefdic];
	}

	$('[name=Parmdefs]').val(JSON.stringify(ParmdefList)) ;
}


function DisplayParmDef() {
	$('#mb').append("<p>We are now ready to define our parameters.  This includes a parameter's short and long names (PARAMCD and PARAM), its categories, and if applicable, any derivations necessary.  Please complete \
		the information below.  Then click Next Parameter to define a new parameter, or Finish when all parameters are complete.</p><hr><div class='form-group'><label>Short Name (PARAMCD)</label><br>\
		<input type='text' id='paramcd'></div><div class='form-group'><label>Long Name (PARAM)</label><br><input type='text' size='50' id='param'></div><hr>");

	// Create dropdowns for each PARCAT
	if ($('[name=Parcats]').val()) {
		var parcatlist=JSON.parse($('[name=Parcats]').val()) ;
		$('#mb').append('<p>Now choose values for your parameter categories</p>') ;

		for (x=0; x<parcatlist.length; x++) {
			var ctlist=parcatlist[x]['CT'] ;
			$('#mb').append('<div class="form-group"><select id="parcat'+(x+1)+'"><option disabled selected>PARCAT'+(x+1)+'</option></select></div>') ;
			for (y=0; y<ctlist.length; y++) {
				$('#parcat'+(x+1)).append('<option>'+ctlist[y]['term']) ;
			}
		}
		$('#mb').append('<hr>') ;
	}

	// Ask for DTYPEs
	$('#mb').append('<p>In the BDS data set, ADaM allows us to derive new records within a parameter whose purpose is to summarize in some way the value of AVAL or AVALC.  Such records, and the method used, are identified \
		with the DTYPE variable.  Select from the dropdown below the DTYPEs you need for this parameter.  You can also choose Other and fill in the fields to define a custom DTYPE.</p><div class="form-group"><select id="dtypes">\
		<option disabled selected id="default">Choose DTYPE</option><option value="other">Other (specify)</option></select></div><div class="form-group row"><div class="col-xs-4"><input type="text" disabled placeholder="DTYPE value" id="dtypevalue" class="form-control">\
		</div><div class="col-xs-6"><input type="text" placeholder="DTYPE description" disabled id="dtypedesc" class="form-control"></div></div><div class="form-group"><button type="button" id="adddtype" class="btn btn-success">Add DTYPE</button></div><table id="dtypetable"></table>')
	
	$('#adddtype').attr('onclick','Add2Table($("#dtypetable"),["dtypevalue","dtypedesc"],[$("#dtypevalue"),$("#dtypedesc")])');

	$('#dtypetable').bootstrapTable({
		scrollY:'200px',
		columns:[{
			field:'state',
			checkbox:'true'
		},{
			field:'dtypevalue',
			title:'DTYPE Value'
		},{
			field:'dtypedesc',
			title:'DTYPE Description'
		}]
	})
}


function DisplayParcatDef() {
	$('#mb').append('<p>To define a parameter category, provide a description of the category and enter its allowable values.  Check the box below to include numeric counterparts to the values (i.e. PARCATyN).</p>\
		<div class="form-group"><textarea id="ParcatComment" placeholder="Provide a description of the comment" cols="30" rows="2"></textarea></div><div class="checkbox"><label><input type="checkbox" id="ParcatNTF">\
		Include numeric counterparts (values will correspond to their row in the table below)</label></div><div class="form-group"><label>Enter an allowable value for this parameter category</label>\
		<br><input type="text" id="ParcatValue"></div><div class="form-group"><button type="button" id="addpcatvalue" class="btn btn-success">Add Value</button></div><table id="ParcatTable"></table>')
	//. Add an extra button to define another category
	$('#mf').prepend('<button type="button" id="ToParcat2FromParcat2" class="btn btn-success">Define another category</button>') ;
	$('#addpcatvalue').attr('onclick','Add2Table($("#ParcatTable"),["term"],[$("#ParcatValue")]);');

	$('#ParcatTable').bootstrapTable({
		scrollY:'200px',
		columns:[{
			field:'state',
			checkbox:'true',
			title:'Uncheck to remove'
		},{
			field:'term',
			title:'Term'
		}]
	})
}

function DisplayDatasetMD(MDDic) {

	$('#mb').append('<div class="container">\
		<div class="row" id="NameRow"><div class="col-xs-4">Name</div></div>\
		<div class="row" id="LabelRow"><div class="col-xs-4">Label</div></div>\
		<div class="row" id="StructureRow"><div class="col-xs-4">Structure</div></div>\
		<div class="row" id="RepeatingRow"><div class="col-xs-4">Can subject appear on more than one record?</div></div>\
		<div class="row" id="ReferenceRow"><div class="col-xs-4">Is this reference data (i.e. without subjects)?</div></div>\
		<div class="row" id="ClassRow"><div class="col-xs-4">Class</div><div class="col-xs-8">'+MDDic['Class']+'</div></div>\
		<div class="row" id="PurposeRow"><div class="col-xs-4">Purpose</div><div class="col-xs-8 form-group">Analysis</div></div></div>') ;


	if (MDDic['StandardTF'] == false) {
		$('#NameRow').append('<div class="col-xs-8 form-group"><input type="text" name="DSName" value="'+MDDic['Name']+'"></div>') ;
		//$('#LabelRow').append('<div class="col-xs-8 form-group"><input type="text" name="DSLabel" value="'+MDDic['Label']+'"></div>') ;
		$('#LabelRow').append('<div class="col-xs-8 form-group"><textarea name="DSLabel" value="'+MDDic['Label']+'" cols="30" rows="2"></textarea></div>') ;
	}

	else {
		$('#NameRow').append('<div class="col-xs-8 form-group">'+MDDic['Name']+'</div>') ;
		$('#LabelRow').append('<div class="col-xs-8 form-group">'+MDDic['Label']+'</div>') ;
	}

	if (MDDic['Name'] == 'ADSL') {
		$('#StructureRow').append('<div class="col-xs-8 form-group">'+MDDic['Structure']+'</div>') ;
		$('#RepeatingRow').append('<div class="col-xs-8 form-group">'+MDDic['Repeating']+'</div>') ;
		$('#ReferenceRow').append('<div class="col-xs-8 form-group">'+MDDic['Reference']+'</div>') ;
	}

	else {
		$('#StructureRow').append('<div class="col-xs-8 form-group"><textarea name="DSStructure" cols="30" rows="2"></textarea></div>') ;
		$('#RepeatingRow').append('<div class="col-xs-8 form-group"><select name="DSRepeating"><option value="Yes" selected>Yes</option><option value="No">No</option></select></div>') ;
		$('#ReferenceRow').append('<div class="col-xs-8 form-group"><select name="DSReference"><option value="Yes">Yes</option><option value="No" selected>No</option></select></div>') ;
	}
}


function DisplayRecordSources() {

	$('#mb').append("<p>We now begin to consider the sources from where a programmer will read data.  Study Designer defines a <strong>Record Source</strong> of a data set as \
		a data set from where records are retrieved.  Think of a data set's record source(s) as the data set(s) named on the initial SET statement.  For an ADaM \
		data set, record sources can come from SDTM or ADaM.  Use the below fields to define record sources for this data set.  Click Add Record Source to add \
		your record source to the table.  If you change your mind about a record source, simply uncheck it in the table.</p><div class='form-group'><select \
		id='adamds'><option disabled selected>Select an ADaM record source</option></select></div><p>or</p><div class='form-group'><input type='text' id='sdtmds' \
		size='40' placeholder='Enter the name of an SDTM record source'></div><div class='form-group'><textarea id='subset' cols='50' rows='4' placeholder=\
		'Optionally, enter a description of how the record source is to be subset (e.g. QNAM=ECLSIG)'></textarea></div><div class='form-group'><button type='button' \
		class='btn btn-success' onclick='Add2SourceTable();' id='addsource'>Add Record Source</button></div><table id='sourcetable'></table>")

	$.getJSON($('[name=URLPath]').val()+'GetStudyDatasets',{'Study':$('[name=Study]').val()},function(data){
		$.each(data,function(){
			$("#adamds").append('<option>'+this['Dataset']+'</option>');
		});
	});

	var mddic=JSON.parse($('[name=MD]').val()) ;
	$('#mh4').text(mddic['Name']+' metadata');

	$('#sourcetable').bootstrapTable({
		url:$('[name=URLPath]').val()+'GetRecordSources',
		queryParams:{Study:$('[name=Study]').val(),DSName:mddic['Name']},
		scrollY:"200px",
		columns:[{
			field:'state',
			checkbox:'true',
			title:'Check/Uncheck all'
		},{
			field:'model',
			title:'Source Model'
		},{
			field:'dataset',
			title:'Source Dataset'
		},{
			field:'subset',
			title:'Source Subset'
		}]
	})
}

function Add2SourceTable() {
	if ($('#sdtmds').val()) {
		var Model='SDTM' ;
		var Dataset=$('#sdtmds').val() ;
		$('#sdtmds').val(null);
	}
	else {
		var Model='ADAM';
		var Dataset=$('#adamds').val() ;
		$('#adamds').val(null) ;
	}

	$('#sourcetable').bootstrapTable('append',{
		state:true,
		model:Model,
		dataset:Dataset,
		subset:$('#subset').val()
	})

	$('#subset').val(null);
}

