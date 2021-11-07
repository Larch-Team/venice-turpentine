const nextBtns = document.querySelectorAll(".btn");
const larchSteps = document.querySelectorAll(".larch-container");
const progress = document.getElementById("progress");
const progressSteps = document.querySelectorAll(".circle");
const formula = document.getElementById("formula");

var branchName;

let larchStepsNum = 0;

var COLORS;
function colors() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", '/API/colors', true);
    xhr.responseType = 'json';
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            COLORS = xhr.response;
        }
    };
    xhr.send(null);
}
colors();

function getColor(color) {
    return COLORS[color] ? COLORS[color]['rgb'] : "Black";
}

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

function disableBtn() {
    if(document.getElementById("formula").value==="") { 
           document.getElementById("new_proof").disabled = true; 
       } 
    else { 
       document.getElementById("new_proof").disabled = false;
    }
}

function new_proof(e) {
    let ret = sendPOST('API/new_proof', formula.value);
    if (ret["type"] == "success") {
        getProof('/API/worktree', function(text) {
            document.getElementById('clickable-container').innerHTML = text;
        });
        nextPage();
        toggleBtns();
    } else {
        showHintModal();
        document.getElementById("hints-p").innerHTML = ret["content"];
    }
}

function getRules(tokenID, sentenceID, branch) {
    var xhr = new XMLHttpRequest();
    if (branchNumber > 1) {
        var currentLeaf = document.getElementById("btn"+sentenceID+tokenID+branch);
        var classNames = currentLeaf.getAttribute("class").match(/[\w-]*leaf[\w-]*/g);
        if (typeof classNames != "undefined" && classNames != null && classNames.length != null && classNames.length > 0) {
            var leafName = currentLeaf.classList[0];
            jump(leafName);
        }
    }
    xhr.open("GET", 'API/rules?tokenID='+tokenID+'&sentenceID='+sentenceID);
    xhr.responseType = 'text';
    xhr.send();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            rules = xhr.response;
            document.getElementById('rules-container').innerHTML = rules;   
        }
    }
}

function use_rule(rule_name, tokenID, sentenceID) {
    var xhr = new XMLHttpRequest();
    var jsonData= {
        "rule":rule_name,
        "context": {
            "tokenID":tokenID,
            "sentenceID":sentenceID
            }
        };
    xhr.open('POST', 'API/use_rule', true);
    xhr.responseType = 'json';
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.send(JSON.stringify(jsonData));
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.response['type']=='success') {
                getProof('/API/worktree', function(text) {
                    document.getElementById('clickable-container').innerHTML = text;
                    toggleBtns();
                });
            } else {
                showHintModal();
                document.getElementById("hints-p").innerHTML = xhr.response["content"];
            }
        }
    };
    getBranchesNumber();
}

var branchNumber;
var branchNumberCounter = 0;

function getBranchesNumber() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', '/API/allbranch');
    xhr.send();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            branchNumber = parseInt(xhr.responseText);
            if (branchNumber == 2 && branchNumberCounter == 0) {
                showHint2();
                branchNumberCounter++;
            };
        };
    };
}

function getCurrentBranch() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', '/API/branchname');
    xhr.send();
    xhr.onreadystatechange = function() {
        branchName = xhr.responseText;
        document.getElementById("current-branch").innerHTML = branchName;
        document.getElementById("current-branch").style.color = getColor(branchName);
    }
}

function toggleBtns() {
    var treeBtns = document.querySelectorAll('.tree-btn');
    xhr = new XMLHttpRequest();
    xhr.open('GET', '/API/branchname');
    xhr.send();
    xhr.onreadystatechange = function() {
        branchName = xhr.responseText;
        document.getElementById("current-branch").innerHTML = branchName;
        document.getElementById("current-branch").style.color = getColor(branchName);
        if (document.getElementById("switch-check").checked == true) {
            for (var i = 0; i < treeBtns.length; i++) {
                if (treeBtns[i].classList.contains(branchName.toLowerCase()) || treeBtns[i].classList.contains(branchName)) {
                    treeBtns[i].style.color = getColor(branchName);
                    if (treeBtns[i].classList.contains(`used-${branchName.toLowerCase()}`)) {
                        treeBtns[i].style.opacity = 0.3;
                    }
                    else {
                        treeBtns[i].style.opacity = 1;
                    }
                }
                else {
                    treeBtns[i].style.color = 'black';
                }
            }
        }
        else if (document.getElementById("switch-check").checked == false) {
            for (var i = 0; i < treeBtns.length; i++) {
                treeBtns[i].style.color = "black";
                if (treeBtns[i].classList.contains(`used-${branchName.toLowerCase()}`)) {
                    treeBtns[i].style.opacity = 0.3;
                }
                else {
                    treeBtns[i].style.opacity = 1;
                }
            }
        }
    }
}

function jump(leafName) {
    var xhr = new XMLHttpRequest();
    var jsonData= {
        "branch":leafName
        };
    xhr.open('POST', 'API/jump', true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.send(JSON.stringify(jsonData));
    document.getElementById('current-branch').innerHTML = leafName;
    document.getElementById("current-branch").style.color = getColor(leafName);
    toggleBtns();
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
            document.getElementById("close-window-btn").addEventListener("click", function _f() {  
                closeBranch(branch_name);
                this.removeEventListener('click', _f);
            })
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
    xhr.responseType = 'json';
    xhr.send(JSON.stringify(jsonData));
    xhr.onreadystatechange = function() {
        if (xhr.response['type']=='success') {
            getProof('API/contratree', function(text) {
                document.getElementById('checking-container').innerHTML = text;
            });
        }
        else {
            showHintModal();
            document.getElementById("hints-p").innerHTML = xhr.response["content"];
        }
    }
}

function closeBranch(branch) {
    closeWindow();
    var xhr = new XMLHttpRequest();
    var jsonData= {
        "branch":branch,
        };
    xhr.open('POST', 'API/no_contra', true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.responseType = 'json';
    xhr.send(JSON.stringify(jsonData));
    xhr.onreadystatechange = function() {
        if (xhr.response['type']=='success') {
            getProof('API/contratree', function(text) {
                document.getElementById('checking-container').innerHTML = text;
            });
        }
        else {
            showHintModal();
            document.getElementById("hints-p").innerHTML = xhr.response["content"];
        }
    }
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
        showHintModal();
        document.getElementById("hints-p").innerHTML = "Podejmij decyzję czy dana formuła jest tautologią.";
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
            if (lastPage["type"] == "success") {
                document.getElementById("decision").appendChild(document.getElementById("right"));
                if (document.getElementById("is-tautology").checked) {
                    document.getElementById("tautology-end1").innerHTML = "Twoje rozstrzygnięcie: Formuła jest tautologią.";
                }
                else {
                    document.getElementById("tautology-end1").innerHTML = "Twoje rozstrzygnięcie: Formuła nie jest tautologią."
                }
                getProof('API/contratree', function(text) {
                    document.getElementById('tree-end1').innerHTML = text;
                });
                nextPage();
            }
            else {
                document.getElementById("decision").appendChild(document.getElementById("wrong"));
                document.getElementById("feedback-wrong").innerHTML = lastPage["content"]
                if (document.getElementById("is-tautology").checked) {
                    document.getElementById("tautology-end2").innerHTML = "Twoje rozstrzygnięcie: Formuła jest tautologią.";
                } 
                else {
                    document.getElementById("tautology-end2").innerHTML = "Twoje rozstrzygnięcie: Formuła nie jest tautologią."
                }
                getProof('API/contratree', function(text) {
                    document.getElementById('tree-end2').innerHTML = text;
                });
                nextPage();
            }
        }
    }
}

function generate_formula() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', '/API/randform');
    xhr.responseType = 'json';
    xhr.send();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.response['type']=='success') {
                document.getElementById("formula").value = xhr.response['content'];
                disableBtn();
            }
            else {
                showHintModal();
                document.getElementById("hints-p").innerHTML = xhr.response["content"];
            }
        }
    }
}

document.getElementById("back-to-1").addEventListener('click', function () {
    prevPage();
})
document.getElementById("back-to-2").addEventListener('click', function () {
    getProof('/API/worktree', function(text) {
        document.getElementById('clickable-container').innerHTML = text;
    });
    toggleBtns();
    prevPage();
})

document.getElementById("ok2").addEventListener('click', hideHintModal)
document.getElementById("stay").addEventListener('click', hideLeave)
document.getElementById("leave").addEventListener('click', showLeave)
document.getElementById("generate").addEventListener('click', generate_formula)
document.getElementById("switch").addEventListener('click', toggleBtns)
document.getElementById("ok").addEventListener('click', hideHint2)
document.getElementById("hint-x2").addEventListener('click', hideHintRules)
document.getElementById("rules-hint").addEventListener('click', showHintRules)
document.getElementById("hint-x").addEventListener('click', hideHint)
document.getElementById("qm").addEventListener('click', showHint)
document.getElementById("new_proof").addEventListener("click", new_proof)
document.getElementById("start").addEventListener("click", nextPage)
document.getElementById("finish-proof").addEventListener("click", finishProofPage)
document.getElementById("check").addEventListener("click", branchCheckPage)
document.getElementById("check-branch-btn").addEventListener("click", checkBranch)
document.getElementById("btn-check").addEventListener("click", tautologyCheck)
document.getElementById("rules-report").addEventListener("click", function () {
    window.open('https://szymanski.notion.site/4a180f6826464e9dac60dd9c18c5ac0b?v=56fec8f735024f94ab421aa97cab3dc8','_blank')
})

document.getElementById("rules-undo").addEventListener("click", function (){
    ret = sendPOST('API/undo', null);
    if (ret["type"] == "success") {
        getProof('/API/worktree', function(text) {
            document.getElementById('clickable-container').innerHTML = text;
            toggleBtns();
        });
    } else {
        showHintModal();
        document.getElementById("hints-p").innerHTML = ret["content"];
    }
})

document.getElementById("new_end1").addEventListener("click", function () {
    window.location.reload(true)
})
document.getElementById("new_end2").addEventListener("click", function () {
    window.location.reload(true)
})

// document.getElementById("save_end").addEventListener("click", function () {
//     hide = [
//         "save_end",
//         "new_end",
//         "tex",
//         "leave"
//     ];
//     hide.forEach(element => {
//         document.getElementById(element).hidden = true;
//     });
//     window.print();
//     hide.forEach(element => {
//         document.getElementById(element).hidden = false;
//     });
// })

function tex_export() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', '/API/print');
    xhr.send();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            navigator.clipboard.writeText(xhr.response)
            showHintModal();
            document.getElementById("hints-p").innerHTML = "Skopiowano dowód do schowka";
        }
    }  
};
document.getElementById("tex1").addEventListener("click", tex_export);
document.getElementById("tex2").addEventListener("click", tex_export);

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

function prevPage() {
    larchStepsNum--;
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
    document.getElementById("hint-window3").classList.add("active");
    document.getElementById("overlay").classList.add("active");
}

function hideHint2() {
    document.getElementById("hint-window3").classList.remove("active");
    document.getElementById("overlay").classList.remove("active");
}

function showLeave() {
    document.getElementById("leave-window").classList.add("active");
    document.getElementById("overlay").classList.add("active");
}

function hideLeave() {
    document.getElementById("leave-window").classList.remove("active");
    document.getElementById("overlay").classList.remove("active");
}

function showHintModal() {
    document.getElementById("general-modal").classList.add("active");
    document.getElementById("overlay").classList.add("active");
}

function hideHintModal() {
    document.getElementById("general-modal").classList.remove("active");
    document.getElementById("overlay").classList.remove("active");
}
function showHintRules() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'API/hint', true);
    xhr.responseType = 'json';
    xhr.send();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.response['type']=='success') {
                ret = xhr.response['content']
            } else {
                ret = `</h2>Wystąpił błąd:</h2>${xhr.response['content']}`
            }
            document.getElementById("hint-textbox").innerHTML = ret;
            document.getElementById("hint-window2").classList.add("active");
            document.getElementById("overlay").classList.add("active");
        }
    };
}

function hideHintRules() {
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
                    document.getElementById("check").click()
                    break;
                case 3:
                    document.getElementById("finish-proof").click()
                    break;
                case 4:
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