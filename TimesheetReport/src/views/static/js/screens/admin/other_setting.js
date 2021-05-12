
function getVersionInformation(){
    var data = {};
    var output = [];
    $.ajax({
        url: GET_VERSION_INFO,
        type: "POST",
        async: false,
        data: encodeURIComponent(JSON.stringify(data)),
        success: function(resp){
            var result = resp.result;
            output = result;
        }
    });
    return output;
}
function createVersionCardContent (){
    var info = getVersionInformation();
    var verElm = document.getElementById('version_block');
    for (var i = 0; i < info.length; i++) {
        let configName = info[i]['config_name'];
        let configValue = info[i]['config_value'];
        let itemElm = document.createElement("DIV");
        itemElm.className = 'ctcard__content-item';
        let content = '';
        content += `<label>${configName}</label><input type="text" value='${configValue}'>`;
        itemElm.innerHTML = content;
        verElm.appendChild(itemElm);
    }
}

function getDataToUpdate(){
    var data = {};
    data['other_info'] = [];
    
    let verElm = document.getElementById('version_block');
    let listItem = verElm.querySelectorAll('.ctcard__content-item');
    for (var i = 0; i < listItem.length; i++) {
        let itemElm  = listItem[i];
        let labelElm = itemElm.querySelector('label')
        let configName = labelElm.innerHTML;
        let inputElm = itemElm.querySelector('input')
        let configValue = inputElm.value;
        
        if (!configValue.trim()) {
            alert(configName + ' value is empty!');
            return null;
        } 
        data['other_info'].push([configName, configValue]); 
    }
    return data;
}
$(document).ready(function(){
    createVersionCardContent();
    
    $(document).on('change', 'input, select', function(){
        $('#save').prop('disabled', false);
    })
    $('#save').click(function(){
        var data = getDataToUpdate();
        if (data != null) {
            $('#overlay_loader').show();
            $.ajax({
                url: UPDATE_ADMIN_VERSION,
                type: "POST",
                data: encodeURIComponent(JSON.stringify(data)),
                success: function(resp){
                    location.reload();
                }
            });
        } 
    })
})

