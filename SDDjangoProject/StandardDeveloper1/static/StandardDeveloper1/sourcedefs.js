$(document).ready(function(){
	$.getJSON('http://localhost:8000/StandardDeveloper1/GetRecordSources',{'Study':"{{Study}}"},function(data){
		$.each(JSON.parse(data),function(){
			$("#tbl1").append('<tr><td>'+this['Model']+'</td><td>'+this['Dataset']+'</td><td>'+this['Subset']+'</td><td><input type="checkbox"> </input></td></tr>');
		});
	});

	$.getJSON('http://localhost:8000/StandardDeveloper1/GetStudyDatasets',{'Study':"{{Study}}",'DSName':"{{IGDName}}"},function(data){
		$.each(JSON.parse(data),function(){
			$("#adamds").append('<option>'+this['Dataset']+'</option>');
		});
	});

	var srclist=[]

	$('form').submit(function() {
		var t=document.getElementById('tbl1') ;
		var rows=t.rows ;
		for (r=1;r<rows.length;r++) {
			chosen=rows[r].cells[3].children[0].checked ;
			if (chosen) {
				srclist.push({'Model':rows[r].cells[0].innerHTML,'Dataset':rows[r].cells[1].innerHTML,'Subset':rows[r].cells[2].innerHTML})
			}
		}
		var srcstring=JSON.stringify({'sources':srclist});
		$('[name="sources"]').val(srcstring);
	})

	// When a button is clicked to add a new source
	$('[id^="add"]').click(function(){
		var model=$(this).attr('id').substr(3);

		if (model == "ADaM") {
			var ds=$('#adamds') ;
			var sub=$('#adamsubset') ;
		}

		else {
			var ds=$('#sdtmds') ;
			var sub=$('#sdtmsubset') ;
		}

		// Insert new source into table
		// How. many rows in the existing table
		$("#tbl1").append('<tr><td>SDTM</td><td>'+$(ds).val()+'</td><td>'+$(sub).val()+'</td><td class="w3-center"><input type="checkbox" class="tblsrc" checked></input></td></tr>') ;

		// Clear out text boxes
		$(ds).val(null) ;
		$(ds).attr('placeholder',model+' data set') ;
		$(sub).val(null);
		$(sub).attr('placeholder',model+' subset description (optional)')
		// Add dictionary to the JSON string
	})

})