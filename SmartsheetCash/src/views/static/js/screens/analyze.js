$(document).on('click', '.add-to-smartsheet', function(){
    var checkBoxs = $('tbody input[type="checkbox"]');
    var sheet_id = $(this).data('sheet-id');
    var des_id = $(this).data('des-id');
    var isSelect = false;
    var ids = [];
    checkBoxs.each(function(){
        if ($(this).prop('checked')) {
            var check = $(this).prop('checked');
            if (check) {
                var id = $(this).val();
                isSelect = true;
                ids.push(id);
            }
        }
    })
    if (!isSelect) {
        customAlert({message: MESSAGE.NO_ID_SELECTED});
        return 0;
    } else {
        var data = {};
        data[IDS] = ids;
        data[SHEET_ID] = sheet_id;
        data[DES_ID] = des_id;
        var method_get_url = encodeURIComponent(JSON.stringify(data));
		location.href = PREVIEW + '?' + method_get_url;
        
    }
})

function controlSubmitButton(){
    var checkBoxs = $('tbody input[type="checkbox"]');
    var isSelect = false;
    checkBoxs.each(function(){
        if ($(this).prop('checked')) {
            var check = $(this).prop('checked');
            if (check) {
                isSelect = true;
                return null;
            }
        }
    })
    if (isSelect) {
        $('.add-to-smartsheet').prop('disabled', false);
    } else {
        $('.add-to-smartsheet').prop('disabled', true);
    }
}

$(document).on('change', 'input[type="checkbox"]', function(){
    controlSubmitButton();
})
$(document).ready(function () {
    controlSubmitButton();
})