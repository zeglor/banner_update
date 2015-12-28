var cServer = 'http://127.0.0.1:8000/';
var csrftoken = "";
var task_state = "idle";

// Checks if given method is crsf safe
function csrfSafeMethod(method){
	// these HTTP methods dont require csrf protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// Gets cookie value
function getCookie(name){
	var cookieValue = null;
	if (document.cookie && document.cookie != ''){
		var cookies = document.cookie.split(';');
		for (var i=0; i<cookies.length; i++){
			var cookie = jQuery.trim(cookies[i]);
			if (cookie.substring(0, name.length + 1) == (name + '=')){
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

// Launches banner update task
function requestBannerUpdate(){
	//get csrf
	csrftoken = getCookie("csrftoken");
	
	$.ajax({
		url: cServer + "request_update/",
		type: "POST",
		contentType: "application/json",
		dataType: "json",
		error: function(error){
			console.log(error);
		},
		success: function(data){
			console.log(data);
		},
	});
}

// Updates progress bar values
function updateProgressBar(current, total, state){
	if(state == "SUCCESS"){
		current = total;
	}
	progress = 0.0;
	if(total > 0){
		progress = current/total;
	}
	else {
		progress = 0.0;
	}
	progress *= 100.0;
	$('#task_progress_bar').text(state + '; ' + current + ' out of ' + total);
	$('#task_progress_bar').attr('aria-valuenow', current).attr('aria-valuemax', total)
		.css('width', progress+'%');
	
	if(state == "PROGRESS"){
		// Add class 'active' once
		if(!$('#task_progress_bar').hasClass("active")){
			$('#task_progress_bar').addClass("active");
		}
	}
	else{
		// Remove class 'active' if it exists
		if($('#task_progress_bar').hasClass("active")){
			$('#task_progress_bar').removeClass("active");
		}
	}
}

// Changes button action and look based on current task state
function updateButton(state){
	if(state == "PROGRESS"){
		$("#updateButton").click(function(){
			alert("Task in progress!");
		});
	}
	else{
		$("#updateButton").click(function(){
			requestBannerUpdate();
		});
	}
}

// Polls server for task status
function statusPoll(){
	var pollInterval = 500;
	
	$.ajax({
		url: cServer + "status/",
		type: "GET",
		contentType: "application/json",
		dataType: "json",
		error: function(error){
			console.log(error);
			pollInterval = 5000;
		},
		success: function(data){
			task_state = data["state"];
			updateProgressBar(data["current"], data["total"], task_state);
			updateButton(task_state);
			pollInterval = 500;
		},
		complete: function(){
			setTimeout(statusPoll, pollInterval);
		}
	});
}

// Main
$(function(){
	$.ajaxSetup({
		beforeSend: function(xhr, settings){
			if (!csrfSafeMethod(settings.type) && !this.crossDomain){
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});
	
	// add onClick event to button
	$("#updateButton").click(function(){
		requestBannerUpdate();
	});
	
	// Start polling task status
	statusPoll();
});
