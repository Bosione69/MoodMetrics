files = []

// Method which returns a new XMLHttpRequest object
function getConnection() {
    var request;
    if (window.XMLHttpRequest) {
        request = new XMLHttpRequest();
    } else if (window.ActiveXObject) {
        try {
            request = new ActiveXObject("MSXML2.XMLHTTP");
        } catch (e) {
            request = new ActiveXObject("Microsoft.XMLHTTP");
        }
    }
    return request;
}

function downloadFile() {
    for (file of files) {
        filename = file.name + ' - Output.xlsx';
        fetch('/get_file', {
            method: "post",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: filename
            })
        })
            .then(response => response.blob())
            .then(data => open(window.URL.createObjectURL(data)))
            .catch(err => Swal.fire({
                icon: "error",
                title: "Error",
                text: "Ha ocurrido un error obteniendo el resumen",
            })
            );
    }
}

// Allows the web-page to save all the files into a list object
function dropHandler(ev) {
    // Cancel the usual behaviour when dropping files
    ev.preventDefault();

    // Use DataTransferItemList interface to access the file(s)
    files.length = 0;
    [...ev.dataTransfer.items].forEach((item, i) => {
        // If dropped items aren't files, reject them   
        if (item.kind === "file") {
            const file = item.getAsFile();
            if (!file.type && file.size % 4096 == 0) {
                Swal.fire({
                    icon: 'info',
                    text: 'One or more of the inputs was a folder. They have been omitted'
                })
                i--;
            }
            else {
                files[i] = file;
            }
        }
    });

    files = files.flat();

    if (files.length != 0) {
        if (files.length == 1) {
            document.getElementById('drop_zone').innerHTML = `There is 1 file ready for processing`
        } else {
            document.getElementById('drop_zone').innerHTML = `There are ${files.length} files ready for processing`
        }
    }
}

// Cancels the usual behaviour when dragging files
function dragOverHandler(ev) {
    ev.preventDefault();
}

function handlerCheckEmotions() {
    if (files.length > 0) {
        if (document.getElementById("wrapper").hidden == false) {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "Some files are already loading"
            })
        } else {
            checkEmotions();
        }
    } else {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: "You must select at least one file"
        })
    }
}

function checkEmotions() {
    const formData = new FormData();
    // Append each selected file to the FormData object
    for (let i = 0; i < files.length; i++) {
        formData.append("input_file", files[i]);
    }
    let request = getConnection();
    request.open("POST", "/check_emotion");
    document.getElementById("wrapper").hidden = false;
    document.getElementById('drop_zone').innerHTML = `The files are being read`
    request.onreadystatechange = function () {
        if (request.status == 200 && request.readyState == 4) {
            let response = JSON.parse(request.response);
            console.log(response)
            let i = 0;
            let resultList = []
            for (result of response) {
                let str_sentiment = '';
                for (sentiment in result) {
                    str_sentiment += sentiment + ': ' + (result[sentiment] * 100).toFixed(2) + '%\n\n';
                }
                resultList.push({ id: files[i].name, text: str_sentiment });
                i++;
            }
            document.getElementById("wrapper").hidden = true;
            loadReact(resultList)
        } else if (request.status == 400) {
            // If there is an error, a message is shown on screen using SweetAlert
            Swal.fire({
                icon: "error",
                title: "Error",
                text: request.responseText,
            });
        }
    }
    request.send(formData);
}