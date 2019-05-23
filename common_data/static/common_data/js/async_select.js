// identify the select widget

//the box object includes the model-name, the app-name, select-widget-id
/**
 * 
 {
     'model':,
     'app'
     'id'
 }
 */
//for each page stores a mapping of the latest objects to their 
//objects

function hasLatest(model, app, id){
    //checks if a select widget has the latest element
    $.get('/base/models/get-latest/' + app + '/' + model
    ).then(function(resp){
        if(resp.data === -1){
            return true
        }else{
            var id = resp.data[0];
            var isPresent = false;
            $('#'+ id + " > option").each(function(){
                if(this.value === id){
                    isPresent = true;
                }
            })
            return isPresent;
        }
    })
}

function insertLatest(id, value, representation){
    //appends the latest element to the select widget
    $('#' + id).append("<option value='" + value + "'>" + representation + "</option>")
}

function updateSelectBox(box){
    $.get('/base/models/get-latest/' + box.app + '/' + box.model
    ).then(function(resp){
        if(resp.data === -1){
            return
        }else{
            var id = resp.data[0];
            var isPresent = false;
            $('#'+ box.id + "  option").each(function(){
                if(this.value === id.toString()){
                    isPresent = true;
                }
            })
            if(!isPresent){
                insertLatest(box.id, resp.data[0], resp.data[1])
            }
        }
    })

}


function trackSelectBox(box, index, array){
    var select = document.getElementById(box.id);
    select.addEventListener('focus', function(){
        updateSelectBox(box);
    })

}
function trackSelectBoxes(boxes){
    boxes.forEach(trackSelectBox);
}
if($("#box-array").length > 0 ){
    var boxArray = JSON.parse(decodeURIComponent($("#box-array").val()))
    if (boxArray.length === 0){
        alert('No data provided');
    }else{
        /**
         * [{
        'id': 'id_supplier',
        'model': 'supplier',
        'app': 'inventory'
    }]
        */
        trackSelectBoxes(boxArray);

}
}

