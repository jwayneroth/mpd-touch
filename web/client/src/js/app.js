import 'bootstrap/js/dist/tab';
import 'bootstrap/js/dist/modal';

import { axios, API_URL } from './api';

import WebSocketHandler from './websocket-handler';
import NowPlayingPage from './nowplaying-page';
import SettingsPage from './settings-page';
import LibraryPage from './library-page';
import RadioPage from './radio-page';
import BounceScreensaver from './bounce-screensaver';
import WeatherScreensaver from './weather-screensaver';
import ControlsDialog from './controls-dialog';

const SS_ON = true;
const SS_DELAY = 480000;

// class DynamicSS {
// 	constructor(className, opts) {
// 		return new classes[className](opts);
// 	}
// }

class FmuLcd {
	constructor(el) {

		this.currentPageName = null;

		this.lastMpdStatus = (window.initialMpdStatus || null);

		console.log('initialMpdStatus', window.initialMpdStatus);

		this.dom = {
			el,
			inner: el.querySelector('#app__inner'),
			main: el.querySelector('#main'),
			main_nav: el.querySelector('#main-nav'),
			nav_links: el.querySelectorAll('#main-nav a:not([data-bs-toggle="modal"])')
		};

		this.pages = {};

		this.screensaverKeys = ['bounce', 'weather'];
		this.screensavers = {
			'bounce': {
				'class': BounceScreensaver,
				'instance': null,
			},
			'weather': {
				'class': WeatherScreensaver,
				'instance': null,
			}
		};

		this.onHashChange();

		window.addEventListener('mpdstatus', this.onMpdStatus.bind(this));
		window.addEventListener('hashchange', this.onHashChange.bind(this));

		this.lastPage = null;
		this.ssActivityListener = this.activityCheck.bind(this);
		this.removeScreensaverDelegate = this.removeScreensaver.bind(this);

		this.ssTimerOn = false;
		this.ssTimeoutID = null;
		this.ss = null;

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

			let ss;

			const ssKey = this.screensaverKeys[Math.floor(Math.random() * this.screensaverKeys.length)];

			if (!this.screensavers[ssKey].instance) {
				ss = new this.screensavers[ssKey].class(this);
				this.screensavers[ssKey].instance = ss;
			} else {
				ss = this.screensavers[ssKey].instance;
			}

			//this.dom.el.appendChild(ss.dom.el);
			//this.dom.el.innerHTML = ss.dom.el.outerHTML;
			this.lastPage = this.dom.el.replaceChild(ss.dom.el, this.dom.inner);

			ss.initAnime();

			this.ss = ss;

			window.addEventListener('click', this.removeScreensaverDelegate);
		}
	}

	removeScreensaver() {
		console.log('removeScreensaver', this.ss);

		if (this.ss) {

			//this.ss.dom.el.remove();
			this.dom.el.replaceChild(this.lastPage, this.ss.dom.el);

			this.ss.stopAnime();

			this.ss = null;

			window.removeEventListener('click', this.removeScreensaverDelegate);

			this.turnOnScreensaverTimer();
		}
	}

	onMpdStatus(evt) {

		const status = evt.detail;

		this.lastMpdStatus = status;

		console.log('app::onMpdStatus', evt, status);

		if (!this.pages.hasOwnProperty(this.currentPageName)) return;

		const page = this.pages[this.currentPageName];

		if (typeof page.onMpdStatus === 'function') {
			page.onMpdStatus(status);
		}

		if (this.ss && typeof this.ss.onMpdStatus === 'function') {
			this.ss.onMpdStatus(status);
		}
	}

	initPage() {

		const pageName = this.currentPageName;

		const pageEl = document.querySelector('#' + pageName);

		if (pageEl) {

			// page has been created before
			if (this.pages.hasOwnProperty(pageName)) {

				this.pages[pageName].onEnter(pageEl);

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

		const lastPageName = this.currentPageName;

		const pageName = this.pageFromHash();

		this.currentPageName = pageName;

		axios.get(API_URL + '/' + pageName)
			.then(response => {

				// tell old page its leaving
				if (lastPageName && this.pages.hasOwnProperty(lastPageName)) {
					if (typeof this.pages[lastPageName].onExit === 'function') {
						this.pages[lastPageName].onExit();
					}
				}

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
