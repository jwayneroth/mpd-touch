
window.webSocket = null;

export default class WebSocketHandler {
	constructor() {
		this.retries = 0;
	}

	checkInitSocket() {
		if (window.webSocket == null) {
			this.openWebSocket();
		} else {
			console.log('ws exists');
			wsOpened();
		}
	}

	openWebSocket() {
		try {
			webSocket = new WebSocket(`ws://${location.host}/ws`);
		} catch (e) {
			webSocket = new WebSocket(`wss://${location.host}/ws`);
		}

		if (webSocket == null) {
			return;
		}

		webSocket.onopen = this.onSocketOpen.bind(this);
		webSocket.onclose = this.onSocketClose.bind(this);
		webSocket.onmessage = this.onSocketMessage.bind(this);
	}

	onSocketOpen() {
		console.log("webSocket opened");
	}

	onSocketClose() {
		console.log("webSocket closed in server");
		// close socket in client
		if (webSocket !== null) {
			webSocket.close();
			webSocket = null;
			console.log("webSocket closed in client");

			// try to reopen once ?
			if (this.retries == 0) {
				this.retries++;
				this.openWebSocket();
			}
		}
	}

	/**
	 * Dispatch the message from web server to corresponding handler
	 *
	 * @param msg - the message received from web server
	 */
	onSocketMessage(msg) {
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
		console.log('status', s);

		if (s) {
			this.dispatchStatus(s);
		}

		var c = d["command"];
		console.log("command", c);

		if (c) {
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
	}

	dispatchStatus(status) {
		console.log('dispatchStatus', status)

		const event = new CustomEvent("mpdstatus", { detail: status });

		// Dispatch the event.
		window.dispatchEvent(event);
	}

	/**
	 * Send data to web server via WebSocket
	 *
	 * @param data - command in Json format
	 */
	// sendDataToServer(data) {
	// 	if (webSocket == null) {
	// 		console.log("webSocket closed");
	// 		return;
	// 	}
	// 	d = JSON.stringify(data);
	// 	console.log("sending to server: " + d);
	// 	webSocket.send(d);
	// 	console.log("sent");
	// }
}

