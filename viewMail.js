function sleep_1(ms) 
{
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Get references to elements
const messageList = document.querySelector('.table');
const messageModal = document.getElementById('message-modal');
const messageContent = document.getElementById('message-content');



const inboxItemHandler = document.querySelector('#inboxItemHandler');

// Function to handle opening the modal
function openModal(messageId) {
//   fetch(`/get_message/${messageId}`)
//     .then(response => response.text())
//     .then(messageText => {
//       messageContent.innerHTML = messageText;
//       messageModal.style.display = 'block';
//     });
    
    inboxItemHandler.style.display = 'none';
    messageModal.style.display = 'block';
    messageModal.style.animation =  "swipe-in 1.5s ease"
    messageContent.innerHTML = messageId;
}

// Function to close the modal
function closeModal() {
  messageModal.style.animation =  "swipe-out 1.5s ease"
  sleep_1(900).then(() => { 
    inboxItemHandler.style.animation =  "show-up 0.9s ease"
    messageModal.style.display = 'none';
    inboxItemHandler.style.display = 'block';
});
  
}

// (Later) Add event listeners to message anchors
const messageAnchors = messageList.querySelectorAll('a');
messageAnchors.forEach(anchor => {
    anchor.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent default navigation
        // const messageId = anchor.dataset.messageId; 
        
        //testing purpose
        const messageId = 'x';

        openModal(messageId);
    });
});
