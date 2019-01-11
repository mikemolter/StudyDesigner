function Add2Table(TableObject,FieldNames,AddObjects) {
	var data={state:true} ;
	for (x in FieldNames) {
		data[FieldNames[x]]=AddObjects[x].val() ;
		AddObjects[x].val(null) ;
	}
	$(TableObject).bootstrapTable('append',data) ;
}

function GlyphsRemoveEdit() {
	return '<i class="glyphicon glyphicon-trash"></i><i class="glyphicon glyphicon-pencil" id="pencilwithtrash"></i>'
}

function GlyphsEditOnly() {
	return '<i class="glyphicon glyphicon-pencil" id="pencilonly"></i>'
}

function StudySourceParms () {
	//return {Study:'{{Study}}',DSName:'{{DSName}}' };
	return {Study:$('[name=Study]').val(),DSName:$('[name=DSName]').val() };
}

function VarParms(){
	return {Study:$('[name=Study]').val(),DSName:$('[name=DSName]').val(),VarName:$('[name=VarName]').val() };
}