function getFirstLastDayOfWeek(d) {
    if (d == undefined) {
        var d = new Date();
    }
    // 👇️ clone date object, so we don't mutate it
    let date = new Date(d);
    let day = date.getDay(); // 👉️ get day of week
    // 👇️ day of month - day of week (-6 if Sunday), otherwise +1
    let diff1 = date.getDate() - day + (day === 0 ? -6 : 1);
    let startDateObj = new Date(date.setDate(diff1));
    let startDate = startDateObj.getFullYear() + '-' + String(startDateObj.getMonth() + 1).padStart(2, '0') + '-' + String(startDateObj.getDate()).padStart(2, '0');
    // let diff2 = date.getDate() + day + (day === 0 ? -6 : 1);
    let endDateObj = new Date(startDateObj);
    endDateObj.setDate(endDateObj.getDate() + 6);
    let endDate = endDateObj.getFullYear() + '-' + String(endDateObj.getMonth() + 1).padStart(2, '0') + '-' + String(endDateObj.getDate()).padStart(2, '0');
    return [startDate, endDate];
}

function getFirstLastDayOfMonth(d) {
    if (d == undefined) {
        var d = new Date();
    }
    let date = new Date(d);
    let month = String(date.getMonth() + 1).padStart(2, '0');
    let year = date.getFullYear();
    let startDate = String(year + '-' + month + '-01');
    let endDateObj = new Date(date.getFullYear(), date.getMonth() + 1, 0);
    let endDate = endDateObj.getFullYear() + '-' + String(endDateObj.getMonth() + 1).padStart(2, '0') + '-' + String(endDateObj.getDate()).padStart(2, '0');
    return [startDate, endDate];
  }
  
function loadConfigDate() {
    var dateTypeObj = $('.date-type');
    var fromDateObj = $('.from-date');
    var toDateObj = $('.to-date');
    if (dateTypeObj.val() == 'last_week') {
        var listDate = getFirstLastDayOfWeek();
        var startDate = listDate[0];
        var endDate = listDate[1];
        fromDateObj.val(startDate);
        toDateObj.val(endDate);
        fromDateObj.prop('disabled', true);
        toDateObj.prop('disabled', true);
    } else if (dateTypeObj.val() == 'last_month') {
        var listDate = getFirstLastDayOfMonth();
        var startDate = listDate[0];
        var endDate = listDate[1];
        fromDateObj.val(startDate);
        toDateObj.val(endDate);
        fromDateObj.prop('disabled', true);
        toDateObj.prop('disabled', true);
    } else if (dateTypeObj.val() == 'specific') {
        fromDateObj.prop('disabled', false);
        toDateObj.prop('disabled', false);
    }
}

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
        $('.analyze').prop('disabled', false);
    } else {
        $('.analyze').prop('disabled', true);
    }
}

$(document).on('change', 'input[type="checkbox"]', function(){
    controlSubmitButton();
})

$(document).ready(function () {
    loadConfigDate();
    controlSubmitButton();
})
$(document).on('click', '.date-type', function(){
    loadConfigDate();
})

$(document).on('click', '.analyze', function(){
    // validate input before submit 
    var fromDateObj = $('.from-date');
    var toDateObj = $('.to-date');
    var startDate = fromDateObj.val();
    var endDate = toDateObj.val();
    var path = $(this).data('path');
    // validate date
    if (! (startDate && endDate)) {
        customAlert({message: MESSAGE.EMPTY_DATE});
        return 0;
    } else {
        // validate sheet
        var checkBoxs = $('tbody input[type="checkbox"]');
        var isSelect = false;
        var sheets = [];
        checkBoxs.each(function(){
            if ($(this).prop('checked')) {
                var check = $(this).prop('checked');
                if (check) {
                    var groupIndex = $(this).data('group-index');
                    var srcName = $(this).data('src-name');
                    var desName = $(this).data('des-name');
                    isSelect = true;
                    sheets.push([groupIndex, srcName, desName]);
                }
            }
        })
        if (!isSelect) {
            customAlert({message: MESSAGE.NO_SHEET_SELECTED});
            return 0;
        } else {
            var data = {};
            data[FROM_DATE] = startDate;
            data[TO_DATE] = endDate;
            data[SHEETS] = sheets;
            openConsoleModal(path);
            $('.close-overlay-clean').prop('disabled', true)
            $.ajax({
                url: START_ANALYZE,
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
                        customAlert({message: message});
                        reloadElement('.content', 'table');
                    } else {
                        customAlert({message: message});
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