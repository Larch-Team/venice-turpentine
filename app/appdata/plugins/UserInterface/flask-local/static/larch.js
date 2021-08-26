const nextBtns = document.querySelectorAll(".btn");
const larchSteps = document.querySelectorAll(".larch-container");
const progress = document.getElementById("progress");
const progressSteps = document.querySelectorAll(".circle");

let larchStepsNum = 0;

nextBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
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
    });
});

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