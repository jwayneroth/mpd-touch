import { axios, API_URL } from './api';

/**
 * Controls Modal
 */

const MODAL_TIMEOUT = 60000;

export default class ControlsDialog {
	constructor(el) {
		console.log('ControlsDialog::init');

		let i;

		const controls = el.querySelectorAll('.btn-group .btn[data-tag-name]');

		this.modalShown = false;
		this.modalTimeoutID = null;

		this.dom = {
			el,
			navButton: document.querySelector('#main-nav a[data-bs-target="#controls"]'),
			playPause: el.querySelector("button[data-tag-name='play_pause']"),
			playMode: el.querySelector("button[data-tag-name='play_mode']"),
			volumeDisplay: el.querySelector('#controls__volume-display'),
			volumeSlider: el.querySelector('#controls__volume'),
			close: el.querySelector('#controls__close'),
		};

		for (i = 0; i < controls.length; i++) {
			controls[i].addEventListener('click', this.controlClick.bind(this));
		}

		this.dom.volumeSlider.addEventListener('change', this.onVolumeChange.bind(this));

		el.addEventListener('shown.bs.modal', this.onModalShown.bind(this));
		el.addEventListener('hidden.bs.modal', this.onModalHidden.bind(this));

		window.addEventListener('mpdstatus', this.onMpdStatus.bind(this));
	}

	onMpdStatus(evt) {

		const status = evt.detail;

		console.log('ControlsDialog::onMpdStatus', status);

		//const play_mode = response.data.play_mode;
		const play_state = status.play_state;

		//console.log('updateControlButtons', play_mode, play_state);

		//this.dom.playMode.querySelector('span').setAttribute('class', 'icon ' + play_mode[1]);
		this.dom.playPause.querySelector('span').setAttribute('class', 'icon ' + play_state);
	}

	controlClick(evt) {
		evt.preventDefault();

		const tag_name = evt.currentTarget.dataset.tagName;
		console.log('control link click', tag_name);

		if (tag_name == 'volume-off') {
			this.setVolume(0);
			this.onVolumeChange();
		} else if (tag_name == 'volume-down') {
			this.setVolume(parseInt(this.dom.volumeSlider.value, 10) - 5);
			this.onVolumeChange();
		} else if (tag_name == 'volume-up') {
			this.setVolume(parseInt(this.dom.volumeSlider.value, 10) + 5);
			this.onVolumeChange();
		} else {
			axios.get(API_URL + '/controls/' + tag_name)
				.then(this.updateControlButtons.bind(this))
		}

		this.setModalTimeout();

		return false;
	}

	updateControlButtons(response) {
		const play_mode = response.data.play_mode;
		const play_state = response.data.play_state;

		console.log('updateControlButtons', play_mode, play_state);

		this.dom.playMode.querySelector('span').setAttribute('class', 'icon ' + play_mode[1]);
		this.dom.playPause.querySelector('span').setAttribute('class', 'icon ' + play_state);
	}

	onVolumeChange() {
		const volume = this.dom.volumeSlider.value;
		console.log('volumeChange: ' + volume);
		axios.post(API_URL + '/controls/volume', { volume }, {
			headers: {
				'Content-Type': 'multipart/form-data'
			}
		})
			.then(response => {
				console.log(response);
				this.setVolume(parseInt(response.data.volume, 10));
			})
			// .catch(function (error) {
			// 	console.log(error);
			// })
			;

		this.setModalTimeout();
	}

	setVolume(vol) {
		this.dom.volumeSlider.value = vol;
		this.dom.volumeDisplay.innerHTML = ' : ' + vol;
	}

	onModalShown() {
		console.log('onModalShown');

		axios.get(API_URL + '/controls/volume')
			.then(response => {
				console.log('volume ' + response.data.volume);
				this.setVolume(parseInt(response.data.volume, 10));
				this.dom.volumeSlider.removeAttribute('disabled');
			})

		this.modalShown = true;

		this.setModalTimeout();
	}

	onModalHidden() {
		console.log('onModalHidden');

		this.modalShown = false;

		if (this.modalTimeoutID) {
			window.clearTimeout(this.modalTimeoutID);
			this.modalTimeoutID = null;
		}
	}

	setModalTimeout() {

		if (!this.modalShown) return;

		if (this.modalTimeoutID) {
			window.clearTimeout(this.modalTimeoutID);
			this.modalTimeoutID = null;
		}

		this.modalTimeoutID = window.setTimeout(this.timeoutFire.bind(this), MODAL_TIMEOUT);
	}

	timeoutFire() {
		console.log('timeoutFire');

		this.modalTimeoutID = null;
		// click close
		this.dom.close.click();
	}
}