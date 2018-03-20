if (status != 'notset') {
    check_status();
}

function check_status(){
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", urlforcheckstatus, true);
        xmlhttp.setRequestHeader("Content-Type", "application/json");
        xmlhttp.send(JSON.stringify([graph_id]));
        xmlhttp.onreadystatechange = function () {
            if (xmlhttp.readyState != 4) return;
            if (xmlhttp.status == 200) {

                var resp = JSON.parse(xmlhttp.response)[0]['status'];
                if (resp == 'Ok') {
                    status = resp;
                    window.location = urlforindex;
                }
                else {
                    var div = document.getElementById("statusdiv");
                    div.innerText = "Status: " + resp;

                }
            }

        };
        setTimeout( check_status, 1000 );
    }
