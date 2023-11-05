import { axios, API_URL } from './api';

/**
 * Library Page
 */
export default class LibraryPage {
	constructor(el) {
		console.log('LibraryPage::init');

		this.onEnter(el);
	}

	onEnter(el) {
		this.currentArtist = null;
		this.currentAlbum = null;
		this.dom = {
			el,
			//tabList: el.querySelector('#library__tabs'),
			artistsTab: el.querySelector('#artists-tab'),
			albumsTab: el.querySelector('#albums-tab'),
			tracksTab: el.querySelector('#tracks-tab'),
			artistsPanel: el.querySelector('#library__artists'),
			albumsPanel: el.querySelector('#library__albums'),
			tracksPanel: el.querySelector('#library__tracks'),
		}

		const newPlaylist = el.querySelector('.new-playlist');

		if (newPlaylist) {
			newPlaylist.addEventListener('click', this.newPlaylistClick.bind(this));
		}

		this.initArtistsPanelButtons();
	}

	//
	// panel buttons
	//
	initArtistsPanelButtons() {

		let i;

		const el = this.dom.artistsPanel;

		const artists = el.querySelectorAll('a.artist');

		for (i = 0; i < artists.length; i++) {
			artists[i].addEventListener('click', this.artistClick.bind(this));
		}

		const addArtists = el.querySelectorAll('a.add-artist');

		for (i = 0; i < addArtists.length; i++) {
			addArtists[i].addEventListener('click', this.addArtistClick.bind(this));
		}
	}

	initAlbumsPanelButtons() {

		let i;

		const el = this.dom.albumsPanel;

		const album = el.querySelectorAll('a.album');

		for (i = 0; i < album.length; i++) {
			album[i].addEventListener('click', this.albumClick.bind(this));
		}

		const addAlbum = el.querySelectorAll('a.add-album');

		for (i = 0; i < addAlbum.length; i++) {
			addAlbum[i].addEventListener('click', this.addAlbumClick.bind(this));
		}

		const addArtistAlbums = el.querySelectorAll('a.add-artist-albums');

		for (i = 0; i < addArtistAlbums.length; i++) {
			addArtistAlbums[i].addEventListener('click', this.addArtistAlbumsClick.bind(this));
		}

		const backButton = el.querySelectorAll('a.back-button');

		console.log('backButtons', backButton);
		for (i = 0; i < backButton.length; i++) {
			backButton[i].addEventListener('click', evt => {
				evt.preventDefault();
				this.dom.artistsTab.click();
				return false;
			});
		}
	}

	initTracksPanelButtons() {

		let i;

		const el = this.dom.tracksPanel;

		const addTrack = el.querySelectorAll('a.add-track');

		for (i = 0; i < addTrack.length; i++) {
			addTrack[i].addEventListener('click', this.addTrackClick.bind(this));
		}

		const addAlbum = el.querySelectorAll('a.add-album');

		for (i = 0; i < addAlbum.length; i++) {
			addAlbum[i].addEventListener('click', this.addAlbumClick.bind(this));
		}

		const backButton = el.querySelectorAll('a.back-button');

		for (i = 0; i < backButton.length; i++) {
			backButton[i].addEventListener('click', evt => {
				evt.preventDefault();
				this.dom.albumsTab.click();
				return false;
			});
		}
	}

	//
	// api helper
	//
	apiCall(endpoint, params, callback) {
		axios.get(API_URL + '/library/' + endpoint, { params }).then(callback);
	}

	// gotoNowPlaying() {
	// 	window.location.hash = '';
	// }

	//
	// button handlers
	//
	newPlaylistClick(evt) {
		evt.preventDefault();
		this.apiCall('new-playlist', {}, () => { });
		return false;
	}

	artistClick(evt) {
		console.log('artist link click', evt.currentTarget.dataset.name);
		evt.preventDefault();
		const artist = evt.currentTarget.dataset.name;
		this.currentArtist = artist
		this.apiCall('artist', { artist }, this.populateAlbumsPanel.bind(this));
		return false;
	}

	addArtistClick(evt) {
		console.log('add artist link click', evt.currentTarget.dataset.name);
		evt.preventDefault();
		const artist = evt.currentTarget.dataset.name;
		this.apiCall('add-artist', { artist }, () => { });
		return false;
	}

	albumClick(evt) {
		console.log('album link click', evt.currentTarget.dataset.name);
		evt.preventDefault();
		const album = evt.currentTarget.dataset.name;
		this.currentAlbum = album;
		this.apiCall('album', { album }, this.populateTracksPanel.bind(this));
		return false;
	}

	addAlbumClick(evt) {
		console.log('add album link click', evt.currentTarget.dataset.name);
		evt.preventDefault();
		const album = evt.currentTarget.dataset.name;
		this.apiCall('add-album', { album }, () => { });
		return false;
	}

	addArtistAlbumsClick(evt) {
		console.log('add artist albums link click', evt.currentTarget.dataset.name);
		evt.preventDefault();
		this.apiCall(
			'add-artist-albums',
			{ artist: evt.currentTarget.dataset.name },
			() => { });
		return false;
	}

	addTrackClick(evt) {
		console.log('add track link click', evt.currentTarget.dataset.name);
		evt.preventDefault();
		const track = evt.currentTarget.dataset.name;
		this.apiCall('add-track', { track }, () => { });
		return false;
	}

	//
	// panel contents
	//
	populateAlbumsPanel(response) {

		const albums = response.data.albums;
		const ul = document.createElement('ul');

		let i;

		for (i = 0; i < albums.length; i++) {
			ul.innerHTML += `
			<li>
				<a class="album" href data-name="${encodeURI(albums[i])}">
					<span>${albums[i]}</span>
				</a>
				<a href class="add-album icon plus" data-name="${encodeURI(albums[i])}"></a>
			</li>
			`;
		}

		this.dom.albumsPanel.innerHTML = '';

		this.dom.albumsPanel.innerHTML = `
		<div class="button-row">
			<a href class="add-artist-albums icon-button" data-name="${this.currentArtist}">
				<span class="icon plus"></span>
				<span class="txt">All</span>
			</a>
			<a href class="back-button icon-button">
				<span class="icon arrow-left"></span>
				<span class="txt">Back</span>
			</a>
		</div>
		`;

		this.dom.albumsPanel.appendChild(ul);

		this.initAlbumsPanelButtons();

		this.dom.albumsTab.click();
	}

	populateTracksPanel(response) {

		const tracks = response.data.tracks;

		const ul = document.createElement('ul');

		let i;

		for (i = 0; i < tracks.length; i++) {
			ul.innerHTML += `
			<li>
				<a class="add-track" href data-name="${encodeURI(tracks[i])}">
					<span>${tracks[i]}</span>
				</a>
			</li>`;
		}

		this.dom.tracksPanel.innerHTML = '';

		this.dom.tracksPanel.innerHTML = `
		<div class="button-row">
			<a href class="add-album icon-button" data-name="${this.currentAlbum}">
				<span class="icon plus"></span>
				<span class="txt">All</span>
			</a>
			<a href class="back-button icon-button">
				<span class="icon arrow-left"></span>
				<span class="txt">Back</span>
			</a>
		</div>
		`;

		this.dom.tracksPanel.appendChild(ul);

		this.initTracksPanelButtons();

		this.dom.tracksTab.click();
	}
}