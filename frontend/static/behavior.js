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

    function refresh_elements() {
        $.get("/queue", function(data, status){
            $("#queue_container").empty();
            $("#queue_container").append(data);
            $("#queue_title").click(refresh_queue);
        });
    };

    // click on the queue title to refresh list
    $("#queue_title").click(refresh_elements);
});
