function confirm_loggin() {
	var user_name = $('#user_name').val();
	var password = $('#password').val();
	var remember = $('#remember').prop('checked');
	if (remember) {
		remember = 1;
	} else {
		remember = 0;
	}
	var data = {}
	data[SESSION_PASSWORD] = password;
	data[SESSION_USERNAME] =  user_name;
	data['remember'] =  remember;
	var out = null;
	$('#overlay_loader').show();
	document.getElementById('error_div').style.display = 'none';
	$.ajax({
	     url: AUTH,
	     type: "POST",
	     data: encodeURIComponent(JSON.stringify(data)),
		 async: false,
	     success: function(resp){
     				$('#overlay_loader').hide();
	                 var result = resp.result;
	                 if (result[0]) {
	                	 out = true;
	                 } else {
	                	 out = false;
	                	 document.getElementById('error_content').innerHTML = result[1];
	                	 document.getElementById('error_div').style.display = 'block';
	                 } 
	         }
	 });
	return out;
}

$(document).ready(function() {
	$('#login_form').submit(function() {
		var result = confirm_loggin();
	    return result; 
	})
})
