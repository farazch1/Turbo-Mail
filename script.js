function sleep(ms) 
{
    return new Promise(resolve => setTimeout(resolve, ms));
}



// Get the button element
const goToComposebutton = document.querySelector('#composeButton');
const composeBackBtn = document.querySelector('#composeBack-btn');

// Get the element you want to change the display of
const underneth = document.querySelector('#unserneth');

const composeScreen = document.querySelector('#composeScreen');
// Add a click event listener to the button
goToComposebutton.addEventListener('click', () => {
    // Change the display of the element to "block"
    underneth.style.animation =  "hide-out 1.5s ease"
    // underneth.style.visibility = "hidden";

    sleep(1100).then(() => { 
        composeScreen.style.visibility = "visible"
        composeScreen.style.position = "relative"
        composeScreen.style.animation =  "show-up 2s ease"
    });
});

composeBackBtn.addEventListener('click',() => {

    sleep(1100).then(() => { 
        composeScreen.style.visibility = "hidden"
        composeScreen.style.position = "inherit"
        composeScreen.style.animation =  "hide-out 2s ease"
        underneth.style.animation =  "show-up 1.5s ease"
    });
});