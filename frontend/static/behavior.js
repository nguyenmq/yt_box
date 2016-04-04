$(document).ready(function(){
    // submission button on click event handler
    $("#link_form").submit(function (e) {
        e.preventDefault();

        $("#queue_title").append('<img src="/static/loading_spinner.gif" id="loading">');

        $.post("/add", $("input"), function(data, status) {
            $("#link").val("");
            $("#loading").remove()
            $("#queue_container").empty();
            $("#queue_container").append(data);
        });
    });
});
