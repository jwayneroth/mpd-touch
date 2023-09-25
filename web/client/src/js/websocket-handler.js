
window.webSocket = null; // global

export default class WebSocketHandler {
	constructor() {

	}

	checkInitSocket() {
		if (webSocket == null) {
			openWebSocket(wsOpened, dispatchMessageFromServer, webSocketClosedInServer);
		} else {
			console.log('ws exists');
			wsOpened();
		}
	}
}

/**
* Creates new WebSocket channel
*
* @param openCallback - callback method which will be called upon successful WebSocket channel
* @param messageCallback - callback method which will be called upon new message from server
* @param closeCallback = callback method which will be called when WebSocket channel closed
*/
function openWebSocket(openCallback, messageCallback, closeCallback) {
	console.log('openWebSocket');

	webSocket = null;

	try {
		webSocket = new WebSocket(`ws://${location.host}/ws`);
	} catch (e) {
		webSocket = new WebSocket(`wss://${location.host}/ws`);
	}

	if (webSocket == null) {
		return;
	}

	if (openCallback) {
		webSocket.onopen = openCallback;
	}
	if (messageCallback) {
		webSocket.onmessage = messageCallback;
	}
	if (closeCallback) {
		webSocket.onclose = closeCallback;
	}
}

/**
* Closes and nullifies WebSocket object
*/
function closeWebSocketInClient() {
	if (webSocket !== null) {
		webSocket.close();
		webSocket = null;
	}
}

/**
* Send data to web server via WebSocket
*
* @param data - command in Json format
*/
function sendDataToServer(data) {
	if (webSocket == null) {
		console.log("webSocket closed");
		return;
	}
	d = JSON.stringify(data);
	console.log("sending to server: " + d);
	webSocket.send(d);
	console.log("sent");
}

/**
* Dispatch the message from web server to corresponding handler
*
* @param msg - the message received from web server
*/
function dispatchMessageFromServer(msg) {
	console.log("received message from server");

	var d = {}
	try {
		d = JSON.parse(msg.data);
	} catch (e) {
		console.log("error parsing message from server");
		console.log(msg.data);
		return;
	}

	var s = d["status"];

	if (s) {
		dispatchStatus(s);
	}

	console.log('status', s);

	var c = d["command"];
	console.log("command", c);

	if (c == "refresh") {
		if (document.body.classList.contains('home')) {
			if (document.body.classList.contains('modal-open')) {
				document.querySelector('#controls').addEventListener('hidden.bs.modal', function () {
					window.location.reload();
				})
				return;
			}
			window.location.reload();
		}
	}
}


/**
* Handler for initial WebSocket event. Called upon WebSocket opened.
*/
function wsOpened() {
	console.log("webSocket opened");
	const app = document.querySelector('#app');
	if (!app) return;
}

/**
* Handler for WebSocket close event
*/
function webSocketClosedInServer() {
	console.log("webSocket closed in server");
	closeWebSocketInClient();
	console.log("webSocket closed in client");
}

function dispatchStatus(status) {
	console.log('dispatchStatus', status)

	const event = new CustomEvent("mpdstatus", { detail: status });

	// Dispatch the event.
	window.dispatchEvent(event);
}