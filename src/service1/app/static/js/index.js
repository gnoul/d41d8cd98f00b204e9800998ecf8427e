var dtable = document.getElementById("graphs-table");
var checkall = dtable.querySelector("input[name='select_all']");
var inputs = dtable.querySelectorAll("tbody>tr>td>input");
var addbutton = document.getElementById("addbutton");
var execbutton = document.getElementById("execbutton");

execbutton.addEventListener('click', function () {
    var execoptions = document.querySelector("select[name='actions']");
    if (execoptions.value === 'update') {
        var ids = [];
        dtable.querySelectorAll('tbody>tr>td>input:checked').forEach(function (check) {
            ids.push(check.name);
        });
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", urlforbatchtask);
        xmlhttp.setRequestHeader("Content-Type", "application/json");
        xmlhttp.send(JSON.stringify(ids));
    }
});

addbutton.addEventListener("click", function () {
    window.location = urlforgraph;
});

checkall.addEventListener("change", function () {
    inputs.forEach(function (input) {
        input.checked = checkall.checked;
    });
});
