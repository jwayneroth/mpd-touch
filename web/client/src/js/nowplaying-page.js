import { axios, API_URL } from './api';

/**
 * NowPlaying
 */
export default class NowPlayingPage {
	constructor(el) {
		console.log('NowPlayingPage::init');

		this.initDom(el);

		//window.addEventListener('mpdstatus', this.onMpdStatus.bind(this));
	}

	initDom(el) {
		this.dom = {
			el,
			artist: el.querySelector('#nowplaying__artist'),
			album: el.querySelector('#nowplaying__album'),
			cover: el.querySelector('#nowplaying__cover'),
			track: el.querySelector('#nowplaying__track'),
		};

		console.log('NowPlayingPage dom', this.dom);
	}

	onMpdStatus(status) {

		console.log('NowPlayingPage::onMpdStatus', status);

		if (status.now_playing.artist && status.now_playing.artist != '') {
			this.dom.artist.innerHTML = status.now_playing.artist;
			this.dom.artist.setAttribute('style', 'display: block;');
		} else {
			this.dom.artist.setAttribute('style', 'display: none;');
		}

		if (status.now_playing.album && status.now_playing.album != '') {
			this.dom.album.innerHTML = status.now_playing.album;
			this.dom.album.setAttribute('style', 'display: block;');
		} else {
			this.dom.album.setAttribute('style', 'display: none;');
		}

		this.dom.track.innerHTML = status.now_playing.title;

		this.dom.cover.setAttribute('src', '/api/cover');
	}
}