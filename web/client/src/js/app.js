import 'bootstrap/js/dist/tab';
import 'bootstrap/js/dist/modal';

import WebSocketHandler from './websocket-handler';
import SettingsPage from './settings-page';
import LibraryPage from './library-page';
import RadioPage from './radio-page';
import ControlsDialog from './controls-dialog';

const socketHandler = new WebSocketHandler();

window.addEventListener('load', function () {

	socketHandler.checkInitSocket();

	const library = document.querySelector('#library');
	if (library) {
		new LibraryPage(library);
	}

	const settings = document.querySelector('#settings');
	if (settings) {
		new SettingsPage(settings);
	}

	const radio = document.querySelector('#radio');
	if (radio) {
		new RadioPage(radio);
	}

	const controls = document.querySelector('#controls');
	if (controls) {
		new ControlsDialog(controls);
	}
});