$(document).on('click', '.commit', function(){
    var checkBoxs = $('tbody input[type="checkbox"]');
    var srcId = $(this).data('src-id');
    var desId = $(this).data('des-id');
    var groupId = $(this).data('group-id');
    var isSelect = false;
    var ids = [];
    var path = $(this).data('path');
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

        if (! confirm("Are you sure you want to commit all selected data?")) {
			return null;
		} else {
            var data = {};
            data[IDS] = ids;
            data[SRC_ID] = srcId;
            data[DES_ID] = desId;
            data[GROUP_INDEX] = groupId;
            openConsoleModal(path);
            $('.close-overlay-clean').prop('disabled', true)
            $.ajax({
                url: COMMIT,
                type: "GET",
                data: encodeURIComponent(JSON.stringify(data)),
                async: true,
                success: function(resp){
                    // hideLoader();
                    var result = resp.result;
                    var status = result[0];
                    var message = result[1];
                    $('.close-overlay-clean').prop('disabled', false)
                    if (status) {
                        customAlert({message: message})
                        reloadElement('.content', 'table');
                        // reloadPage();
                    } else {
                        customAlert({message: message})
                    }
                    
                },
                error: function(resp) {
                        // hideLoader();
                        $('.close-overlay-clean').prop('disabled', false)
                        customAlert({message: 'Internal Server Error'});
                } 
            });
        }
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
        $('.commit').prop('disabled', false);
    } else {
        $('.commit').prop('disabled', true);
    }
}

$(document).on('change', 'input[type="checkbox"]', function(){
    controlSubmitButton();
})
$(document).ready(function () {
    controlSubmitButton();
})