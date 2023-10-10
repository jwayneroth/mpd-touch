import { axios, API_URL } from './api';

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

		this.initStreamsPanelButtons();
	}

	//
	// panel buttons
	//
	initStreamsPanelButtons() {

		let i;

		const el = this.dom.streamsPanel;

		const streams = el.querySelectorAll('a.stream');

		for (i = 0; i < streams.length; i++) {
			streams[i].addEventListener('click', this.streamClick.bind(this));
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

	streamClick(evt) {
		console.log('stream link click', evt.currentTarget.dataset.url);
		evt.preventDefault();
		const stream = evt.currentTarget.dataset.url;
		this.apiCall('stream', { stream }, () => this.gotoNowPlaying());
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
			</li>
			`;
		}

		this.dom.archivesPanel.innerHTML = '';

		this.dom.archivesPanel.innerHTML = `
		<div class="button-row">
			<a href class="refresh-archives icon-button">
				<span class="icon refresh"></span>
				<span class="txt">refresh</span>
			</a>
		</div>
		`;

		this.dom.archivesPanel.appendChild(ul);

		this.initArchivesPanelButtons();

		this.archivesLoaded = true;
	}
}