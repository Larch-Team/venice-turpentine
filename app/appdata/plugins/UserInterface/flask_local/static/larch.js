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
    xhr.open("GET", url, true);
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
    xhr.open('POST', 'API/use_rule', true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.send(JSON.stringify(jsonData));
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            getProof('/API/worktree', function(text) {
                document.getElementById('clickable-container').innerHTML = text;
            });
        }
    };
}

function branchCheckPage() {
    getProof('API/contratree', function(text) {
        document.getElementById('checking-container').innerHTML = text;
    });
    nextPage();
}

function getBranch(branch_name) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'API/branch?branch='+branch_name, true);
    xhr.responseType = 'text';
    xhr.send();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            branch = xhr.response;
            document.getElementById("checking-window").classList.add("active");
            document.getElementById("overlay").classList.add("active");
            document.getElementById('check-branch-name').innerHTML = `Gałąź "${branch_name}"`
            document.getElementById("branch-container").innerHTML = branch;
        }
    };
}

var sentenceID1;
var sentenceID2;
var i = 0;
var checkingBranch;

function forCheckBranch(branch, sentenceID) {
    if(i==0) {
        checkingBranch = branch;
        sentenceID1 = sentenceID;
        i++;
        document.getElementById("btn"+sentenceID).disabled = true;
    }
    else if(i==1) {
        sentenceID2 = sentenceID;
        i++;
        document.getElementById("btn"+sentenceID).disabled = true;
    }
    else if(i>1) {
        document.getElementById("btn"+sentenceID1).disabled = false;
        document.getElementById("btn"+sentenceID2).disabled = false;
        sentenceID1 = sentenceID;
        document.getElementById("btn"+sentenceID1).disabled = true;
        i = 1;
    }
}

function checkBranch() {
    closeWindow();
    var xhr = new XMLHttpRequest();
    var jsonData= {
        "branch":checkingBranch,
        "sentenceID1":sentenceID1,
        "sentenceID2":sentenceID2
        };
    xhr.open('POST', 'API/contra', true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.send(JSON.stringify(jsonData));
    getProof('API/contratree', function(text) {
        document.getElementById('checking-container').innerHTML = text;
    });
}

function closeWindow() {
    document.getElementById("checking-window").classList.remove("active");
    document.getElementById("overlay").classList.remove("active");
    i = 0;
}

function finishProofPage() {
    getProof('API/contratree', function(text) {
        document.getElementById('final-tree').innerHTML = text;
    });
    document.getElementById("formula-end").innerHTML ="<mark>" + formula.value + "</mark>";
    nextPage();
}

function tautologyCheck() {
    var tautology;
    if (document.getElementById("is-tautology").checked || document.getElementById("is-not-tautology").checked) {
        tautology = document.getElementById("is-tautology").checked;
    }
    else {
        return; // TODO: DOPISAĆ JAKĄŚ PROŚBĘ O ZAZNACZENIE CZY COŚ
    };
    var jsonData = {
        "tautology":tautology
    };
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'API/finish', true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.send(JSON.stringify(jsonData));
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            var lastPage = JSON.parse(xhr.responseText);
            if (lastPage["content"] == "correct") {
                document.getElementById("decision").appendChild(document.getElementById("right"));
                nextPage();
            }
            else if (lastPage["content"] == "not all closed") {
                document.getElementById("decision").appendChild(document.getElementById("wrong"));
                nextPage();
            }
            else if (lastPage["content"] == "wrong decision") {
                document.getElementById("decision").appendChild(document.getElementById("wrong"));
                nextPage();
            }
            else if (lastPage["content"] == "wrong rule") {
                document.getElementById("decision").appendChild(document.getElementById("wrong"));
                nextPage();
            }
            else if (lastPage["content"] == "not finished") {
                document.getElementById("decision").appendChild(document.getElementById("wrong"));
                nextPage();
            }
        };
    };
}

document.getElementById("hint-x2").addEventListener('click', hideHint2)
document.getElementById("qm2").addEventListener('click', showHint2)
document.getElementById("hint-x").addEventListener('click', hideHint)
document.getElementById("qm").addEventListener('click', showHint)
document.getElementById("new_proof").addEventListener("click", new_proof)
document.getElementById("start").addEventListener("click", nextPage)
document.getElementById("finish-proof").addEventListener("click", finishProofPage)
document.getElementById("check").addEventListener("click", branchCheckPage)
document.getElementById("check-branch-btn").addEventListener("click", checkBranch)
document.getElementById("close-window-btn").addEventListener("click", closeWindow)
document.getElementById("btn-check").addEventListener("click", tautologyCheck)

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

function showHint() {
    document.getElementById("hint-window").classList.add("active");
    document.getElementById("overlay").classList.add("active");
}

function hideHint() {
    document.getElementById("hint-window").classList.remove("active");
    document.getElementById("overlay").classList.remove("active");
}

function showHint2() {
    document.getElementById("hint-window2").classList.add("active");
    document.getElementById("overlay").classList.add("active");
}

function hideHint2() {
    document.getElementById("hint-window2").classList.remove("active");
    document.getElementById("overlay").classList.remove("active");
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
                    document.getElementById("finish-proof").click()
                    break;
                case 3:
                    document.getElementById("btn-check").click()
                    break;
                default:
                    break;
            }
            break;
    
        default:
            break;
    }
})