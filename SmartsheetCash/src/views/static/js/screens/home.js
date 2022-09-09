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
    let diff2 = date.getDate() + day + (day === 0 ? -6 : 1);
    let endDateObj = new Date(date.setDate(diff2));
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
    console.log(startDate, endDate);
}

$(document).ready(function () {
    loadConfigDate();
})
$(document).on('click', '.date-type', function(){
    loadConfigDate();
})
