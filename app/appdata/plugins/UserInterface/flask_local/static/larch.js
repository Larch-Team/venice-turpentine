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

function new_proof(e) {
    let ret = sendPOST('API/new_proof', formula.value);
    if (ret["type"] == "success") {
        nextPage();
    } else {
        // pojawianie się dymek z informacją o błędzie - ret["content"]
    }
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

// nextBtns.forEach((btn) => {
//     btn.addEventListener("click", () => );
// });

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