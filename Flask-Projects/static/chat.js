
const socket = io();

function sendMessage() {
    const input = document.getElementById("message");
    const msg = input.value.trim();
    if (msg !== "") {
        socket.emit("message", {
            username: USERNAME,
            room: ROOM,
            msg: msg
        });
        input.value = "";
        socket.emit("stop_typing", { username: USERNAME, room: ROOM });
    }
}

let typingTimer;
function handleTyping() {
    socket.emit("typing", { username: USERNAME, room: ROOM });
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
        socket.emit("stop_typing", { username: USERNAME, room: ROOM });
    }, 1000);
}

socket.on("message", function(data) {
    const box = document.getElementById("chat-box");
    const p = document.createElement("p");
    p.textContent = data.msg;
    box.appendChild(p);
    box.scrollTop = box.scrollHeight;
});

socket.on("typing", function(data) {
    document.getElementById("typing-status").innerText = `${data.username} is typing...`;
});

socket.on("stop_typing", function() {
    document.getElementById("typing-status").innerText = "";
});

function leaveRoom() {
    socket.emit("leave", { username: USERNAME, room: ROOM });
    window.location.href = "join.html";
}

window.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    if (typeof CHAT_HISTORY !== 'undefined') {
        CHAT_HISTORY.forEach(entry => {
            const p = document.createElement("p");
            p.textContent = entry;
            chatBox.appendChild(p);
        });
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
