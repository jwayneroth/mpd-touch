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


/**
 * Radio Page
 */
export default class RadioPage {
	constructor(el) {
		console.log('RadioPage::init');

		this.initDom(el);

	}

	initDom(el) {

		this.archivesLoaded = false;

		this.dom = {
			el,
			streamsTab: el.querySelector('#streams-tab'),
			archivesTab: el.querySelector('#archives-tab'),
			streamsPanel: el.querySelector('#radio__streams'),
			archivesPanel: el.querySelector('#radio__archives'),
		}

		this.dom.archivesTab.addEventListener('shown.bs.tab', this.onArchivesShown.bind(this));

		this.initStreamsStatus();

		this.initStreamsPanelButtons();
	}

	initStreamsStatus() {

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

				this.getStreamStatus(title, url);
			}
		}
	}

	getStreamStatus(title, url) {
		const params = { title, url };
		axios.get(API_URL + '/radio/status', { params }).then(this.onStreamStatus.bind(this));
	}

	onStreamStatus(response) {
		console.log(response.data);

		const { title, status } = response.data;

		const div = this.dom.streamsPanel.querySelector('li[data-title="' + title + '"] .listennow-current-track');

		const track = (typeof status.artist !== 'object') ? status.title + ' by ' + status.artist : status.song;

		div.querySelector('.current-title').innerHTML = `<strong>${track}</strong>`;
		div.querySelector('.show-title').innerHTML = `on <a href="https://www.wfmu.org/playlists/shows/${status.playlist['@attributes'].id}" target="_blank">${status.show}</a>`;
	}

	//
	// panel buttons
	//
	initStreamsPanelButtons() {

		let i;

		const el = this.dom.streamsPanel;

		const streams = el.querySelectorAll('li');

		let anchor, title, url;

		for (i = 0; i < streams.length; i++) {
			title = streams[i].dataset.title;
			anchor = streams[i].querySelector('a.stream');
			url = anchor.dataset.url;
			anchor.addEventListener('click', this.streamClick.bind(this, title, url));
		}
	}

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
		if (this.archivesLoaded) return;
		this.apiCall('archives', {}, this.populateArchivesPanel.bind(this));
	}

	streamClick(title, stream) {
		console.log('radioPage::streamClick', title, stream);
		//evt.preventDefault();
		// const stream = evt.currentTarget.dataset.url;
		this.apiCall('stream', { stream }, () => {
			const streamTitles = FMU_STREAMS.map(s => s.appTitle);
			if (streamTitles.indexOf(title) === -1){
			 this.gotoNowPlaying();
			}
		});
		return false;
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

		let i;

		for (i = 0; i < archives.length; i++) {
			ul.innerHTML += `
				<li>
					<a class="archive" href data-url="${encodeURI(archives[i].url)}">
						<span>${archives[i].title}</span>
					</a>
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