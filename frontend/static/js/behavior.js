$(document).ready(function(){
    // submission button on click event handler
    $("#link_form").submit(function (e) {
        e.preventDefault();

        $("#loading").addClass("spin")
        $("#submit_btn").prop("disabled", true);
        $("#submit_btn").addClass("disabled");
        $("#submit_btn").text("Submitting");

        $.post("/add", $("input"), function(data, status) {
            $("#submit_box").val("");
            $("#submit_btn").prop("disabled", false);
            $("#submit_btn").removeClass("disabled");
            $("#submit_btn").text("Submit Link");
            refresh_elements();
        });
    });

    function toggle_video_info() {
        $(this).siblings().toggle("fast");
    };

    function disable_wrap() {
        $("#np_song").addClass("nowrap");
        $("#chevron").addClass("glyphicon-chevron-down");
        $("#chevron").removeClass("glyphicon-chevron-up");
        $("#banner_detail").hide();
    }

    function toggle_wrap() {
        if($("#np_song").hasClass("nowrap")) {
            $("#np_song").removeClass("nowrap");
            $("#chevron").removeClass("glyphicon-chevron-down");
            $("#chevron").addClass("glyphicon-chevron-up");
            $("#banner_detail").show();
        } else {
            disable_wrap();
        }
    }

    // refreshes the now playing banner and queue
    function refresh_elements() {
        $("#loading").addClass("spin")
        $.get("/now_playing", function(data, status){
            $("#np").empty();
            $("#np").append(data);
            disable_wrap();
        });

        $.get("/queue", function(data, status){
            $("#queue_container").empty();
            $("#queue_container").append(data);
            $("#queue_title").click(refresh_elements);
            $("#queue_title").on("tap", refresh_elements);
        });
    };

    // click on the queue title to refresh things
    $("#queue_title").click(refresh_elements);
    $("#queue_title").on("tap", refresh_elements);

    $("#banner").click(toggle_wrap);
    $("#banner").on("tap", toggle_wrap);
});
