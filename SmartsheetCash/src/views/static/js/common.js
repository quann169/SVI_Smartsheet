function controlProperty(is_active, propName, target){
	for (var idx = 0; idx < target.length; idx++) {
		$(target[idx]).prop(propName, is_active);
	}
}

function showLoader(){
	$('.loading').show();
}
function hideLoader(){
	$('.loading').hide();
}
function showOverlay(level){
	if (level) {
		$('.overlay' + level).show();
	} else {
		$('.overlay').show();
	}
}


function hideOverlay(level){
	if (level) {
		$('.overlay' + level).hide();
	} else {
		$('.overlay').hide();
	}
}

function cleanOverlay(level){
	if (level) {
		$('.overlay' + level).html('');
	} else {
		$('.overlay').html('');
	}
	
}
function hideAndCleanOverlay(level){
	hideOverlay(level);
	cleanOverlay(level);
}
function addOverlayContent(content, level){
	if (level) {
		$('.overlay' + level).html(content);
	} else {
		$('.overlay').html(content);
	}
	
}

// define class name .close-overlay --> click to hide overlay
$(document).on('click', '.close-overlay', function (e) {
	var level = $(this).data('level');
	if (level){
		hideOverlay(level);
	} else {
		hideOverlay();
	}
    
});

// define class name .close-overlay-clean --> click to hide overlay and clean up overlay element
$(document).on('click', '.close-overlay-clean', function (e) {
	var level = $(this).data('level');
	if (level){
		hideAndCleanOverlay(level);
	} else {
		hideAndCleanOverlay();
	}
});

function customAlert(data){
	if (data.confirm) {
		//confirm
		
		if (confirm(data.message)){
			return true;
		} else {
			return false;
		}
	} else {
		//alert
		alert(data.message);
		return null;
	}
}

function reloadElement(parent, child){
	$(parent).load(location.href + " " + child);
}

function reloadPage(){
	location.reload(true);
}

function checkStatusAndAlert(data){
	var status = data[0];
	var output = data[1];
	if (!status) {
		customAlert({message: output});
		return 0;
	} else {
		return 1;
	}
}

$(document).on('click', '.all-checkbox', function (e) {
	  var checked = $(this).prop('checked');
	  var target = $(this).data('target');
	  var listCheckbox = $(target).find('input');
	  var displayOnly = $(this).data('display-only');
	  listCheckbox.each(function(){
		  var disable = $(this).data('disable');
		  if (!(disable == 'true' || disable == true)) {
			  if (displayOnly == true){
				  if (!$(this).is(':hidden')) {
					  $(this).prop('checked', checked);
				  }
			  } else {
				  $(this).prop('checked', checked);
			  }
		  }		  
	  })
	});

$(document).on('change', '.search', function (e) {
	var value = $(this).val().toLowerCase();
	var target = $(this).data('target');
	var listRow = $(target).find('tr');
	var rowNum = 1;
	var startRow = 1;
	var startRowData = $(this).data('startrow');
	if (startRowData){
		startRow = parseInt(startRowData);
	}
	listRow.each(function(){
		if (rowNum > startRow){
			var content = $(this).html().toLowerCase();
			
			if (content.indexOf(value) != -1){
				$(this).show();
			} else {
				$(this).hide();
			}
		}
		rowNum += 1;
	});
})
////////////////////READMORE///////////
function add_read_more() {
    //This limit you can set after how much characters you want to show Read More.
    var limit = 100;
    // Text to show when text is collapsed
    var readMoreTxt = "...Show More";
    // Text to show when text is expanded
    var readLessTxt = "Show Less";
    //Traverse all selectors with this class and manupulate HTML part to show Read More
    $(".add-read-more:visible").each(function() {
    	//  skip if element is exist readmore state   	
        if ($(this).find(".sec-sec").length){
        	return true;
        }
       
        var allstr = $(this).html();
        if (allstr.length > limit) {
        	var idx = limit;
        	var idx_elm = allstr.indexOf("<");
        	if (idx_elm >= 0 && idx_elm <= limit){
        		idx	= idx_elm;
        	}
            var firstSet = allstr.substring(0, idx);
            var secdHalf = allstr.substring(idx, allstr.length);
            var strtoadd = firstSet + "<span class='sec-sec'>" + secdHalf + "</span><br><span class='read-more'  title='Click to Show More'>" + readMoreTxt + "</span><br><span class='read-less' title='Click to Show Less'>" + readLessTxt + "</span>";
            $(this).html(strtoadd);
        }

    });
    //Read More and Read Less Click Event binding
}

$(document).on('click', function(e){
	if ( $('.add-read-more:visible').length) {
			add_read_more();
    }
		
	
});
$(document).on('change', function(e){
	if ( $('.add-read-more:visible').length) {
			add_read_more();
    }
});
$(window).on('load', function(e){
	if ( $('.add-read-more:visible').length) {
			add_read_more();
    }
});
$(document).on("click", ".read-more,.read-less", function() {
    $(this).closest(".add-read-more").toggleClass("show-less-content show-more-content");
});


$(document).on("mouseenter", ".modal-header", function(){
	if (MODAL_DRAG){
		$('.modal-dialog').draggable({
		    handle: ".modal-header"
		});
	}
	
})
function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function revertHtmlFormat(str) {
    return str.replace(/&amp;/g, "&;").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
}








function loadConsole(data){
	if (COMPLETE_PREVIOUS_PROCESS){
		COMPLETE_PREVIOUS_PROCESS = false;
	    $.ajax({
	    	url: GET_CONSOLE,
	 	   type: "GET",
	 	   async: false,
	 	   data: encodeURIComponent(JSON.stringify(data)),
	 	   success: function(resp){
	 		  var content = resp.result;
	 		content = escapeHtml(content); 
			var oldContent = $('#console_content').html();
	 		var isChange = false;
			content = revertHtmlFormat(content);
			oldContent = revertHtmlFormat(oldContent);
	 		if (content != oldContent) {
	 			$('#console_content').html(content);
	 			isChange = true;
	 		 }
	 		COMPLETE_PREVIOUS_PROCESS = true;
	 		var isScroll = $('#scroll').prop('checked');
 			if (isChange & isScroll){
 				var height = $('#console_content')[0].scrollHeight;
				const element = document.getElementById("console_content");
				element.scrollTop = height;
 			}
	 		 }
	 	 });
	}
}
$(document).on('click', '.close-overlay-clean', function(){
	clearInterval(INTERVAL);
	INTERVAL = null;
})

 function openConsoleModal(path){
	showOverlay();
	var content = '';
	content +='<div class="modal-dialog" role="document" style="max-width: 1000px;">';
	content += '<div class="modal-content">';
	content += '<div class="modal-header p-2 align-items-center">';
	content += '<h5 class="modal-title font-weight-bold">Console</h4>';
	content += '<button class="close-overlay-clean custom-button bg-danger" aria-hidden="true">&times;</button>';
	content += '</div>';
	content += '<div class="modal-body modal-body-custom" style="height: 75vh;">';
	content += '<div id="console_content"></div>';
	content += '</div>';
	content += '<div class="modal-footer p-2 justify-content-start">';
	content += '<input type="checkbox" checked="" id="scroll"><label for="scroll">Scroll</label>';
	content += '</div>';
	content += '</div>';
	content += '</div>';
	addOverlayContent(content);
	var data = {};
    data[PATH] = path;
	COMPLETE_PREVIOUS_PROCESS = true;
    INTERVAL = setInterval(function() {loadConsole(data); }, 1000);
}

$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();   
});