function createNewDoc() {
	clearDialog();
	showDialog();
}

function showDialog() {
	$('#dark').show();
	$('#newdialog').show();
	$('#newdialog').css('margin-top', (-$('#newdialog').outerHeight() / 2) + 'px')
}

function hideDialog() {
	$('#dark').hide();
	$('#newdialog').hide();
}

function clearDialog() {
	$('#newDocName').val('');
	$('#newDocTemplate').val($('#newDocTemplate:first').val());
}

function initDialog() {
	$('#newdialog .cancel').click(function() {
		hideDialog();
	});

	$('#newdialog .ok').click(function() {

	});
}

$(window).ready(function() {
	initDialog();
	$('#create').click(createNewDoc);
	$('#docs').dataTable();
});