    $(document).ready(function(){
        // Begin study-level metadata collection with an introduction
        $('#NewStudy').click(function (){
            $('#mh14').text('Welcome to Study Designer!') ;
            $('#mbc1').append("<div>Study Designer is a tool that facilitates the collection and management of metadata for data design and submission.  You'll begin by answering a few questions about the study.  After you've finished and reviewed your input, you'll then begin the design of the ADSL data set.  Click the Next button below to get started.</div>")
            $('#myModal1').modal('show') ;
            $('input[value=Next]').attr('id','ToStudy1FromIntro') ;
        })

        $('#CurrentStudy').click(function() {
            $('#mh2').text('Welcome to Study Designer!');
            $('#mbc2').append('<div>In order to edit a current study, first select SDTM or ADaM, then choose the study from the dropdown.</div><div class="radio"><label><input type="radio" name="StudyModel" disabled value="SDTM">SDTM</label></div><div class="radio"><label><input type="radio" name="StudyModel" value="ADAM">ADaM</label></div><div class="form-group"><select name=Studies><option selected disabled>Select a Study</option></select></div>')
            $('#myModal2').modal('show');
        })

        $('#myModal1').on('click','[id^=ToStudy1]',function() {
            var id=$(this).attr('id') ;
            $('#mh14').text('Study Information') ;
            $('#mbc1').empty() ;
            $('#mbc1').append('<div class="radio"><p>Select a model</p><label><input type="radio" name="ModelName" disabled value="SDTM">SDTM</label></div><div class="radio"><label><input type="radio" name="ModelName" value="ADAM">ADaM</label></div><div id="sel2" class="form-group"><select name=Versions><option selected disabled>Select a default standard version</option></select></div><div class="form-group"><textarea rows="2" cols="60" id="studyname" placeholder="Enter here the short, external name of the study"></textarea></div><div class="form-group"><textarea rows="2" cols="60" id="protocolname" placeholder="Enter here the sponsor internal name of the study"></textarea></div><div class="form-group"><textarea rows="10" cols="60" id="studydesc" placeholder="Enter here a description of the study"></textarea></div>')
            if (id == 'ToStudy1FromIntro') {
                $('#'+id).attr('id','ToStudy2FromStudy1') ;
            }
        })

        $('#myModal1').on('click','[id^=ToStudy2]',function() {
            var id=$(this).attr('id') ;
            if (id == 'ToStudy2FromStudy1') {
                // Store the information collected in Study1
                $('[name=ModelName]').val($('input[name=ModelName]:checked').val()); 
                $('[name=ModelVersion]').val($('#sel2 :selected').val()) ;
                $('[name=StudyName]').val($('#studyname').val()) ;
                $('[name=StudyDescription]').val($('#studydesc').val()) ;
                $('[name=ProtocolName]').val($('#protocolname').val()) ;
                $('#'+id).attr('id','ToStudy3FromStudy2')
            }
            $('#mbc1').empty() ;
            DisplayDicts() ;
        })

        $('#myModal1').on('click','[id^=ToStudy3]',function() {
            var id=$(this).attr('id') ;
            if (id == 'ToStudy3FromStudy2') {
                // Store the information collected in Study1
                $('[name=ExtDicts]').val(JSON.stringify($('#dicttable').bootstrapTable('getSelections'))) ;
                $('[value=Next]').remove() ;
                $('#mf1').append('<input type="submit" class="btn btn-success" value="Finish"></input>') ;
                // $('#'+id).attr('id','Test') ;
            }

            $('#mbc1').empty() ;
            $('#dicttable').remove() ;
            DisplayDocs() ;
        })



        $('#myModal1').on('change','#dicts',function() {
            var dict=$('#dicts :selected').val() ;
            if (dict == "meddra") {
                $('#EDName').val("MedDRA") ;
                $('#EDDesc').val("Adverse Event Dictionary") ;
                $('#EDName').prop('disabled',true) ;
                $('#EDDesc').prop('disabled',true) ;
            }

            else if (dict == "whodrug") {
                $('#EDName').val("WHODrug") ;
                $('#EDDesc').val("World Health Organization Drug Dictionary") ;
                $('#EDName').prop('disabled',true) ;
                $('#EDDesc').prop('disabled',true) ;
            }

            else {
                $('#EDName').val(null);
                $('#EDDesc').val(null);
                $('#EDName').prop('disabled',false);
                $('#EDDesc').prop('disabled',false);
            }
        })

        $('#myModal1').on('change','#docs',function() {
            var dict=$('#docs :selected').val() ;
            if (dict == "acrf") {
                $('#DocName').val("Annotated Case Report Form") ;
                $('#DocName').prop('disabled',true) ;
            }

            else if (dict == "sdrg") {
                $('#DocName').val("Study Data Reviewers Guide") ;
                $('#DocName').prop('disabled',true) ;
            }

            else if (dict == "adrg") {
                $('#DocName').val("Analysis Data Reviewers Guide") ;
                $('#DocName').prop('disabled',true) ;
            }

            else if (dict == "sap") {
                $('#DocName').val("Statistical Analysis Plan") ;
                $('#DocName').prop('disabled',true) ;
            }

            else {
                $('#DocName').val(null);
                $('#DocName').prop('disabled',false);
            }
        })

        $('#myModal1').on('click','#Test',function(){
            alert ('hello world') ;
            $('[name=Documents]').val(JSON.stringify($('#doctable').bootstrapTable('getSelections'))) ;
        })
        $('form').submit(function() {
            $('[name=Documents]').val(JSON.stringify($('#doctable').bootstrapTable('getSelections'))) ;
        })
    })

        $(document).ready(function() {
          $("#sidebarCollapse").on("click", function() {
            $("#sidebar").toggleClass("active");
            $(this).toggleClass("active");
          });
        });



    function DisplayDicts() {
        $('#mh14').text('Study Information - External Dictionaries') ;
        $('#mbc1').append('<div class="form-group"><p>Define your external dictionaries by selecting an option from the dropdown and providing the version, or enter information in the fields below for a different dictionary.</p><select id="dicts"><option selected disabled>Select a dictionary</option><option value="meddra">Adverse Event Dictionary (Meddra)</option><option value="whodrug">WHO Drug Dictionary</option><option value="other">Other</option></select></div><div class="row form-group"><div class="col-xs-2">Name</div><div class="col-xs-4"><input id="EDName" class="form-control input-sm"></div></div><div class="row form-group"><div class="col-xs-2">Description</div><div class="col-xs-8"><input id="EDDesc" class="form-control input-sm"></div></div><div class="row form-group"><div class="col-xs-2">Version</div><div class="col-xs-4"><input id="EDVersion" class="form-control input-sm"></div></div><div class="form-group"><button type="button" class="btn btn-success" id="addbutton">Add dictionary to table</button></div><div>');
        $('#mb1').append('<table id="dicttable"></table>');
        $('#addbutton').attr('onclick','Add2Table($("#dicttable"),["name","description","version"],[$("#EDName"),$("#EDDesc"),$("#EDVersion")])');
        $('#dicttable').bootstrapTable({
            scrollY:"200px",
            columns:[{
                field:'state',
                checkbox:'true',
                title:'Check/Uncheck all'
            },{
                field:'name',
                title:'Dictionary Name'
            },{
                field:'description',
                title:'Dictionary Description'
            },{
                field:'version',
                title:'Dictionary version'
            }]
        })
    }


    function DisplayDocs() {
        $('#mh14').text('Study Information - External Dictionaries') ;
        $('#mbc1').append('<div class="form-group"><p>Define your external documents by selecting an option from the dropdown and providing the file name, or enter information in the fields below for a different document.</p><select id="docs"><option selected disabled>Select a document</option><option value="acrf">Annotated Case Report Form</option><option value="sdrg">Study Data Reviewers Guide</option><option value="adrg">Analysis Data Reviewers Guide</option><option value="sap">Statistical Analysis Plan</option><option value="other">Other</option></select></div><div class="row form-group"><div class="col-xs-2">Name</div><div class="col-xs-4"><input id="DocName" class="form-control input-sm"></div></div><div class="row form-group"><div class="col-xs-2">File Name (including file extension)</div><div class="col-xs-4"><input id="FileName" class="form-control input-sm"></div></div><div class="form-group"><button type="button" class="btn btn-success" id="addbutton">Add document to table</button></div><div>');
        $('#mb1').append('<table id="doctable"></table>');
        $('#addbutton').attr('onclick','Add2Table($("#doctable"),["name","file"],[$("#DocName"),$("#FileName")])');
        $('#doctable').bootstrapTable({
            scrollY:"200px",
            columns:[{
                field:'state',
                checkbox:'true',
                title:'Check/Uncheck all'
            },{
                field:'name',
                title:'Document Name'
            },{
                field:'file',
                title:'File Name'
            }]
        })
    }