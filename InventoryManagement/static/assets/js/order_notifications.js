// static/js/order_notifications.js

// Initialize WebSocket connection (only once)
const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const orderSocket = new WebSocket(protocol + '://' + window.location.host + '/ws/orders/');


// Handle incoming messages from the WebSocket server
orderSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const message = data.message;

    // Check if the message includes 'New order' and show the red dot if it does
    if (message.includes('New order')) {
        document.getElementById("circle").style.display = "inline-block";
    }

    // Optionally log the message to the console for debugging
    console.log("Received message: " + message);
};

// Close the WebSocket connection when leaving the page
window.onbeforeunload = function() {
    orderSocket.close();
};

// Handle the click event to hide the red dot (when the orders page is clicked)
document.getElementById('orders-page').addEventListener('click', () => {
    document.getElementById("circle").style.display = "none";
});

// Optionally, you can log WebSocket events (open and close)
orderSocket.onopen = function(event) {
    console.log("WebSocket is open now.");
};

orderSocket.onclose = function(event) {
    console.log("WebSocket is closed now.");
};
