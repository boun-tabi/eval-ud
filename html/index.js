window.onload = function() {
    sent_id_input = document.getElementById("sent_id");
    sent_id_input.addEventListener("change", function(event) {
        console.log(event.target.value);
    });

    // read file
    fetch("http://localhost:8000/tbs/v2_8.json").then(function(response) {
        response.text().then(function(text) {
            console.log(text);
        });
    });
}