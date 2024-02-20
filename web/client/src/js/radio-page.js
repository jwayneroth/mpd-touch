import { axios, API_URL } from './api';

const FMU_STREAMS = [
	{
		'appTitle': "WFMU",
		'statusURL': 'https://wfmu.org/wp-content/themes/wfmu-theme/status/main.json',
	},
	{
		'appTitle': "GtDR",
		'statusURL': 'https://wfmu.org/wp-content/themes/wfmu-theme/status/drummer.json',
	},
	{
		'appTitle': "Rock 'n Soul",
		'statusURL': 'https://wfmu.org/wp-content/themes/wfmu-theme/status/rockSoul.json',
	},
	{
		'appTitle': "Sheena",
		'statusURL': 'https://wfmu.org/wp-content/themes/wfmu-theme/status/sheena.json',
	}
];

const STATUS_TIMEOUT = 40000;

/**
 * Radio Page
 */
export default class RadioPage {
	constructor(el) {
		console.log('RadioPage::init');

		this.statusTimeoutID = null;
		this.archivesLoaded = false;

		// this.streamStatuses = FMU_STREAMS.map(s => {
		// 	const status = {};
		// 	status[s.appTitle] = null;
		// 	return status;
		// });

		this.onEnter(el);
	}

	onEnter(el) {

		this.dom = {
			el,
			streamsTab: el.querySelector('#streams-tab'),
			archivesTab: el.querySelector('#archives-tab'),
			streamsPanel: el.querySelector('#radio__streams'),
			archivesPanel: el.querySelector('#radio__archives'),
		}

		this.dom.archivesTab.addEventListener('shown.bs.tab', this.onArchivesShown.bind(this));

		this.initStatusStreamsDom();

		this.initStreamPanelButtons();

		this.getAllStatuses();
	}

	onExit() {
		console.log('RadioPage::onExit');

		if (this.statusTimeoutID) {
			window.clearTimeout(this.statusTimeoutID);
		}
	}

	initStatusStreamsDom() {

		const streamTitles = FMU_STREAMS.map(s => s.appTitle);
		const streams = this.dom.streamsPanel.querySelectorAll('li');

		let stream, div, idx, title, url, ico, i;

		for (i = 0; i < streams.length; i++) {

			stream = streams[i];

			idx = streamTitles.indexOf(stream.dataset.title);

			if (idx > -1) {

				title = FMU_STREAMS[idx].appTitle;
				url = FMU_STREAMS[idx].statusURL;

				div = document.createElement('div');
				div.classList.add('listennow-current-track');
				div.innerHTML += `
					<p class="current-title"></p>
					<p class="show-title"></p>
				`;
				ico = document.createElement('a');
				ico.classList.add('refresh');
				ico.dataset.title = title;
				ico.innerHTML = `<span class="icon repeat"></span>`;
				ico.addEventListener('click', this.getStreamStatus.bind(this, title, url));

				stream.appendChild(div);
				stream.appendChild(ico);

				//this.getStreamStatus(title, url);
			}
		}
	}

	getAllStatuses() {
		console.log('RadioPage::getAllStatuses');

		let i, title, url;

		for (i = 0; i < FMU_STREAMS.length; i++) {
			title = FMU_STREAMS[i].appTitle;
			url = FMU_STREAMS[i].statusURL;
			this.getStreamStatus(title, url);
		}

		if (this.statusTimeoutID) {
			window.clearTimeout(this.statusTimeoutID);
		}

		this.statusTimeoutID = window.setTimeout(() => this.getAllStatuses(), STATUS_TIMEOUT);
	}

	getStreamStatus(title, url) {
		const params = { title, url };
		axios.get(API_URL + '/radio/status', { params }).then(this.onStreamStatus.bind(this));
	}

	onStreamStatus(response) {

		const appTitle = response.data.title;
		const { status } = response.data;
		const { artist, title, song, show, playlist } = status;

		//const track = (typeof artist !== 'object') ? title + ' by ' + artist : song;
		let track = '';

		if (
			typeof artist !== 'object' && artist !== '' &&
			typeof title !== 'object' && title !== ''
		) {
			track = title + ' by ' + artist;
		} else if (typeof song !== 'object') {
			track = song;
		}

		const div = this.dom.streamsPanel.querySelector('li[data-title="' + appTitle + '"] .listennow-current-track');

		console.log('RadioPage::onStreamStatus ' + appTitle);

		//this.streamStatuses[appTitle] = status;

		div.querySelector('.current-title').innerHTML = `<strong>${track}</strong>`;
		if (playlist['@attributes'].id && playlist['@attributes'].id !== '') {
			div.querySelector('.show-title').innerHTML = `on <a href="https://www.wfmu.org/playlists/shows/${playlist['@attributes'].id}" target="_blank">${status.show}</a>`;
		} else {
			div.querySelector('.show-title').innerHTML = `on <span>${show}</span>`;
		}
	}

	/**
	 * stream panel buttons
	 */
	initStreamPanelButtons() {

		let i;

		const el = this.dom.streamsPanel;

		const streams = el.querySelectorAll('li');

		let anchor, title, url;

		for (i = 0; i < streams.length; i++) {

			title = streams[i].dataset.title;
			anchor = streams[i].querySelector('a.stream');
			url = anchor.dataset.url;

			((_title, _anchor, _url) => {
				_anchor.addEventListener('click', evt => {
					evt.preventDefault();
					this.streamClick(_title, _url);
					return false;
				});
			})(title, anchor, url);
		}
	}

	/**
	* archive panel buttons
	*/
	initArchivesPanelButtons() {

		let i;

		const el = this.dom.archivesPanel;

		const archive = el.querySelectorAll('a.archive');

		for (i = 0; i < archive.length; i++) {
			archive[i].addEventListener('click', this.archiveClick.bind(this));
		}

		const refreshButton = el.querySelectorAll('a.refresh-archives');

		for (i = 0; i < refreshButton.length; i++) {
			refreshButton[i].addEventListener('click', evt => {
				evt.preventDefault();
				this.apiCall('archives', {}, this.populateArchivesPanel.bind(this));
				return false;
			});
		}
	}

	//
	// api helper
	//
	apiCall(endpoint, params, callback) {
		axios.get(API_URL + '/radio/' + endpoint, { params }).then(callback);
	}

	gotoNowPlaying() {
		window.location.hash = '';
	}

	//
	// button handlers
	//
	onArchivesShown() {
		//if (this.archivesLoaded) return;
		this.apiCall('archives', {}, this.populateArchivesPanel.bind(this));
	}

	/**
	 * stream button click
	 * tell app to play stream
	 * switch to now playing page unless a stream with status info was chosen
	 * 
	 * @param {String} title 
	 * @param {String} stream 
	 */
	streamClick(title, stream) {
		console.log('radioPage::streamClick', title);

		this.apiCall('stream', { stream }, () => {

			const streamTitles = FMU_STREAMS.map(s => s.appTitle);
			const is_status_stream = streamTitles.indexOf(title);

			if (is_status_stream == -1) {
				this.gotoNowPlaying();
			}
		});
	}

	archiveClick(evt) {
		console.log('archive link click', evt.currentTarget.dataset.url);
		evt.preventDefault();
		const archive = evt.currentTarget.dataset.url;
		this.apiCall('archive', { archive }, () => this.gotoNowPlaying());
		return false;
	}

	//
	// panel contents
	//
	populateArchivesPanel(response) {

		const archives = response.data.archives;
		const ul = document.createElement('ul');

		let i, playlist;

		for (i = 0; i < archives.length; i++) {

			if (archives[i].show) {
				playlist = `
					<a class="plist small" target="_blank" href="https://www.wfmu.org/playlists/shows/${archives[i].show}">
						<span class="icon list-alt"></span>
					</a>`;
			} else {
				playlist = '';
			}

			ul.innerHTML += `
				<li>
					<a class="archive" href data-url="${encodeURI(archives[i].url)}">
						<span>${archives[i].title}</span>
					</a>
					${playlist}
				</li>`;
		}

		this.dom.archivesPanel.innerHTML = '';

		this.dom.archivesPanel.innerHTML = `
			<div class= "button-row">
				<a href class="refresh-archives icon-button">
					<span class="icon refresh"></span>
					<span class="txt">refresh</span>
				</a>
			</div>`;

		this.dom.archivesPanel.appendChild(ul);

		this.initArchivesPanelButtons();

		this.archivesLoaded = true;
	}
}