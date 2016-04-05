$(document).ready(function(){
    // submission button on click event handler
    $("#link_form").submit(function (e) {
        e.preventDefault();

        $("#loading").show()
        $("#submit_btn").prop("disabled", true);
        $("#submit_btn").text("Submitting");

        $.post("/add", $("input"), function(data, status) {
            $("#loading").hide()
            $("#link").val("");
            $("#queue_container").empty();
            $("#queue_container").append(data);
            $("#submit_btn").prop("disabled", false);
            $("#submit_btn").text("Submit Link");
            $("#queue_title").click(refresh_elements);
            $("#queue_title").on("tap", refresh_elements);
        });
    });

    // refreshes the now playing banner and queue
    function refresh_elements() {
        $("#loading").show()
        $.get("/now_playing", function(data, status){
            $("#np_song").empty();
            $("#np_song").append(data);
        });

        $.get("/queue", function(data, status){
            $("#queue_container").empty();
            $("#queue_container").append(data);
            $("#queue_title").click(refresh_elements);
            $("#queue_title").on("tap", refresh_elements);
        });
        $("#loading").hide()
    };

    // click on the queue title to refresh things
    $("#queue_title").click(refresh_elements);
    $("#queue_title").on("tap", refresh_elements);

    // click on the now playing label to refresh things
    $("#np").click(refresh_elements);
    $("#np").on("tap", refresh_elements);
});
