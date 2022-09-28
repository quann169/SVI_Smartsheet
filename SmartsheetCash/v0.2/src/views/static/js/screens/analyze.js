$(document).on('click', '.add-to-smartsheet', function(){
    var checkBoxs = $('tbody input[type="checkbox"]');
    var srcId = $(this).data('src-id');
    var desId = $(this).data('des-id');
    var groupId = $(this).data('group-id');
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
        data[SRC_ID] = srcId;
        data[DES_ID] = desId;
        data[GROUP_INDEX] = groupId;
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


$(document).on('click', '.view-detail', function(){
    var srcId = $(this).data('src-id');
    var desId = $(this).data('des-id');
    var groupId = $(this).data('group-id');
    var compareId = $(this).data('compare-id');
    var data = {};
    data[SRC_ID] = srcId;
    data[DES_ID] = desId;
    data[GROUP_INDEX] = groupId;
    data[COMPARE_ID] = compareId;
    showOverlay();
    $.ajax({
        url: GET_COMPARE_DETAIL_MODAL,
        type: "GET",
        async: false,
        data: encodeURIComponent(JSON.stringify(data)),
        success: function(resp){
            var content = resp.result;
            addOverlayContent(content);
            },
        error: function(resp) {
            customAlert({message: 'Internal Server Error'});
            hideLoader();
        } 
      });
})