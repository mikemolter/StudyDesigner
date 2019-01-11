// When defining a new study, after user chooses SDTM or ADAM, get list of standards for that model and put them in the dropdown in #standardlist

$(document).ready(function(){
	$('#myModal1').on('change','[name=ModelName]',function(){
		var selectedVal = $('input[name=ModelName]:checked').val();

		$.getJSON("{{URLPATH}}GetStandards",{'Model':selectedVal},function(data){
			$.each(data,function() {
				$('<option value="'+this['Version']+'">'+this['Name']+' IG ('+this['Version']+')</option>').appendTo('[name=Versions]');
			})
		})
	})

	$('#myModal2').on('change','[name=StudyModel]',function(){
		var selectedVal = $('input[name=StudyModel]:checked').val();
		$.getJSON("{{URLPATH}}GetStudies",{'Model':selectedVal},function(data){
			$.each(data,function() {
				$('<option value="'+this['StudyName']+'|'+this['StandardVersion']+'">'+this['StudyName']+' ('+this['StandardVersion']+')</option>').appendTo('[name=Studies]');
			})
		})
	})
})