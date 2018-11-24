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
		$('[value=Next]').remove();

		if ($(this).attr('id') == 'ToRecordSourceFromAddDSMD') {
			$('#mf').append('<input type="submit" value="Finish" class="btn btn-success">') ;
		}
		else {
			$('#mf').append('<input type="submit" value="Finish" class="btn btn-success" formaction="EditDS">') ;
		}
	})

	// When finished, store the record sources
	$('form').submit(function() {
		$('[name=RecordSources]').val(JSON.stringify($('#sourcetable').bootstrapTable('getSelections'))) ;
	})
})


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
		$('#LabelRow').append('<div class="col-xs-8 form-group"><input type="text" name="DSLabel" value="'+MDDic['Label']+'"></div>') ;
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

	$.getJSON('http://localhost:8000/StandardDeveloper1/GetStudyDatasets',{'Study':"{{Study}}"},function(data){
		$.each(data,function(){
			$("#adamds").append('<option>'+this['Dataset']+'</option>');
		});
	});

	var mddic=JSON.parse($('[name=MD]').val()) ;

	$('#sourcetable').bootstrapTable({
		url:'http://localhost:8000/StandardDeveloper1/GetRecordSources',
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

