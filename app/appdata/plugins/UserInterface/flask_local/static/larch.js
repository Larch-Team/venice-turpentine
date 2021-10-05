const nextBtns = document.querySelectorAll(".btn");
const larchSteps = document.querySelectorAll(".larch-container");
const progress = document.getElementById("progress");
const progressSteps = document.querySelectorAll(".circle");
const formula = document.getElementById("formula");

let larchStepsNum = 0;

function sendPOST(url, body) {
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "POST", url, false ); // false for synchronous request
    xmlHttp.send(body);
    return JSON.parse(xmlHttp.responseText);
}

function getProof(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'API/worktree', true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            callback(xhr.responseText);
        }
    };
    xhr.send(null);
}

function new_proof(e) {
    let ret = sendPOST('API/new_proof', formula.value);
    if (ret["type"] == "success") {
        getProof('/API/worktree', function(text) {
            document.getElementById('clickable-container').innerHTML = text;
        });
        nextPage();
    } else {
        window.alert(ret["content"])
    }
}

function getRules(branch, tokenID, sentenceID) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'API/rules?branch='+branch+'&tokenID='+tokenID+'&sentenceID='+sentenceID);
    xhr.responseType = 'text';
    xhr.send();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            rules = xhr.response;
            document.getElementById('rules-container').innerHTML = rules;   
            document.getElementById('rules-title').style.display = "block";
        }
    }
}

function use_rule(rule_name, branch, tokenID, sentenceID) {
    var xhr = new XMLHttpRequest();
    var jsonData= {
        "rule":rule_name,
        "branch":branch,
        "context": {
            "tokenID":tokenID,
            "sentenceID":sentenceID
            }
        };
    console.log(jsonData);
    xhr.open('POST', 'API/use_rule', true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.send(JSON.stringify(jsonData));  
}

document.getElementById("new_proof").addEventListener("click", new_proof)
document.getElementById("start").addEventListener("click", nextPage)

function nextPage() {
    larchStepsNum++;
    updateLarchSteps();
    if(larchStepsNum > 1) {
        updateProgressBar();
    }
    if(larchStepsNum >=1) {
        document.getElementById("progressbar").style.display = "block";
    }
    if(larchStepsNum >= 5) {
        document.getElementById("progressbar").style.display = "none";
    }
}

function updateLarchSteps(){
    
    larchSteps.forEach(larchStep => {
        larchStep.classList.contains("larch-container-active") &&
        larchStep.classList.remove("larch-container-active");
    });

    larchSteps[larchStepsNum].classList.add("larch-container-active");
}

function updateProgressBar() {
    progressSteps.forEach((progressStep, idx) => {
        if(idx < larchStepsNum) {
            progressStep.classList.add("progress-step-active");
        } else {
            progressStep.classList.remove("progress-step-active");
        }
    });

    const actives = document.querySelectorAll(".progress-step-active");

    progress.style.width = ((actives.length -1) / (progressSteps.length - 1)) * 100 + "%";
}

// Buttons

document.addEventListener('keydown', (event) => {
    switch (event.key) {
        case "Enter":
            event.preventDefault();
            switch (larchStepsNum) {
                case 0:
                    document.getElementById("start").click()
                    break;
                case 1:
                    document.getElementById("new_proof").click()
                    break;
                case 2:

                default:
                    break;
            }
            break;
    
        default:
            break;
    }
})