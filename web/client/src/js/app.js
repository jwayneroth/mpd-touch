import 'bootstrap/js/dist/tab';
import 'bootstrap/js/dist/modal';

import { axios, API_URL } from './api';

import WebSocketHandler from './websocket-handler';
import NowPlayingPage from './nowplaying-page';
import SettingsPage from './settings-page';
import LibraryPage from './library-page';
import RadioPage from './radio-page';
import ScreensaverPage from './screensaver-page';
import ControlsDialog from './controls-dialog';

const SS_ON = false;
const SS_DELAY = 1500;

class FmuLcd {
	constructor(el) {

		this.currentPageName = null;

		this.dom = {
			el,
			main: el.querySelector('#main'),
			main_nav: el.querySelector('#main-nav'),
			nav_links: el.querySelectorAll('#main-nav a:not([data-bs-toggle="modal"])')
		};

		this.pages = {};

		this.onHashChange();

		window.addEventListener('mpdstatus', this.onMpdStatus.bind(this));
		window.addEventListener('hashchange', this.onHashChange.bind(this));

		this.ssActivityListener = this.activityCheck.bind(this);
		this.ssTimerOn = false;
		this.ssTimeoutID = null;

		if (SS_ON) {
			this.turnOnScreensaverTimer();
		}
	}

	turnOnScreensaverTimer() {
		this.ssTimerOn = true;
		this.ssTimeoutID = window.setTimeout(this.screensaverFire.bind(this), SS_DELAY);
		window.addEventListener('click', this.ssActivityListener);
	}

	screensaverFire() {
		this.turnOffScreensaverTimer();
		this.addScreensaver();
		this.ssTimeoutID = null;
	}

	turnOffScreensaverTimer() {
		this.ssTimerOn = false;
		window.removeEventListener('click', this.ssActivityListener);
	}

	// reset ss timeout
	activityCheck() {
		if (this.ssTimeoutID) {
			window.clearTimeout(this.ssTimeoutID);
			this.ssTimeoutID = window.setTimeout(this.screensaverFire.bind(this), SS_DELAY);
		}
	}

	addScreensaver() {
		console.log('addScreensaver');
		if (!this.ss) {
			console.log('app dom', this.dom);
			const ss = new ScreensaverPage();
			this.dom.el.appendChild(ss.dom.el);
			//ss.initDom();
			ss.initAnime();
		}
	}

	onMpdStatus(evt) {

		if (!this.pages.hasOwnProperty(this.currentPageName)) return;

		const page = this.pages[this.currentPageName];

		if (typeof page.onMpdStatus === 'function') {
			page.onMpdStatus(evt);
		}
	}

	initPage() {

		const pageName = this.currentPageName;

		const pageEl = document.querySelector('#' + pageName);

		if (pageEl) {

			// page has been created before
			if (this.pages.hasOwnProperty(pageName)) {

				this.pages[pageName].initDom(pageEl);

				// create page
			} else {

				let page;

				switch (pageName) {
					case 'nowplaying':
						page = new NowPlayingPage(pageEl);
						break;
					case 'library':
						page = new LibraryPage(pageEl);
						break;
					case 'settings':
						page = new SettingsPage(pageEl);
						break;
					case 'radio':
						page = new RadioPage(pageEl);
						break;
					default:
						page = null;
				}

				if (page) {
					this.pages[pageName] = page;
				}
			}
		}
	}

	onHashChange() {
		console.log('onHashChange', window.location.hash);

		const pageName = this.pageFromHash();

		this.currentPageName = pageName;

		axios.get(API_URL + '/' + pageName)
			.then(response => {

				// load new page dom
				this.dom.main.innerHTML = response.data;

				// update nav active class
				this.updateMainNav();

				// init page js
				this.initPage();
			});
	}

	updateMainNav() {

		const hash = (window.location.hash == '') ? '#' : window.location.hash;

		let i, link, href;

		for (i = 0; i < this.dom.nav_links.length; i++) {
			link = this.dom.nav_links[i];
			href = link.href.substring(link.href.indexOf('#'));
			if (href == hash) {
				link.classList.add('active');
				continue;
			}
			link.classList.remove('active');
		}
	}

	pageFromHash() {
		return (window.location.hash == '') ? 'nowplaying' : window.location.hash.substring(1);
	}
}

const socketHandler = new WebSocketHandler();

window.addEventListener('load', function () {

	socketHandler.checkInitSocket();

	const app = document.querySelector('#app');
	if (app) {
		new FmuLcd(app);
	}

	const controls = document.querySelector('#controls');
	if (controls) {
		new ControlsDialog(controls);
	}
});