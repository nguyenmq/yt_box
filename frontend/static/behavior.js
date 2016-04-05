$(document).ready(function(){
    // submission button on click event handler
    $("#link_form").submit(function (e) {
        e.preventDefault();

        $("#queue_title").append('<img src="/static/loading_spinner.gif" id="loading">');
        $("#submit_btn").prop("disabled", true);
        $("#submit_btn").text("Submitting");

        $.post("/add", $("input"), function(data, status) {
            $("#link").val("");
            $("#loading").remove()
            $("#queue_container").empty();
            $("#queue_container").append(data);
            $("#submit_btn").prop("disabled", false);
            $("#submit_btn").text("Submit Link");
        });
    });

    // refreshes the now playing banner and queue
    function refresh_elements() {
        $.get("/queue", function(data, status){
            $("#queue_container").empty();
            $("#queue_container").append(data);
            $("#queue_title").click(refresh_elements);
            $("#queue_title").on("tap", refresh_elements);
        });

        $.get("/now_playing", function(data, status){
            $("#np_song").empty();
            $("#np_song").append(data);
            $("#np").click(refresh_elements);
            $("#np").on("tap", refresh_elements);
        });
    };

    // click on the queue title to refresh things
    $("#queue_title").click(refresh_elements);
    $("#queue_title").on("tap", refresh_elements);

    // click on the now playing label to refresh things
    $("#np").click(refresh_elements);
    $("#np").on("tap", refresh_elements);
});
