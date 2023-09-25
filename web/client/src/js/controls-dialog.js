import { axios, API_URL } from './api';

/**
 * Controls Modal
 */
export default class ControlsDialog {
	constructor(el) {
		let i;

		const controls = el.querySelectorAll('.btn-group .btn[data-tag-name]');

		this.dom = {
			el,
			navButton: document.querySelector('#main-nav a[data-bs-target="#controls"]'),
			playPause: el.querySelector("button[data-tag-name='play_pause']"),
			playMode: el.querySelector("button[data-tag-name='play_mode']"),
			volumeSlider: el.querySelector('#controls__volume'),
		};

		console.log('ControlsDialog dom', this.dom);

		for (i = 0; i < controls.length; i++) {
			controls[i].addEventListener('click', this.controlClick.bind(this));
		}

		this.dom.volumeSlider.addEventListener('change', this.onVolumeChange.bind(this));

		el.addEventListener('shown.bs.modal', this.onModalShown.bind(this));

		window.addEventListener('mpdstatus', this.onMpdStatus.bind(this));
	}

	onMpdStatus(evt) {
		console.log('ControlsDialog::onMpdStatus', evt.detail);
	}

	controlClick(evt) {
		evt.preventDefault();

		const tag_name = evt.currentTarget.dataset.tagName;
		console.log('control link click', tag_name);

		if (tag_name == 'volume-off') {
			this.dom.volumeSlider.value = 0;
			this.onVolumeChange();
		} else if (tag_name == 'volume-down') {
			this.dom.volumeSlider.value = parseInt(this.dom.volumeSlider.value, 10) - 10;
			this.onVolumeChange();
		} else if (tag_name == 'volume-up') {
			this.dom.volumeSlider.value = parseInt(this.dom.volumeSlider.value, 10) + 10;
			this.onVolumeChange();
		} else {
			axios.get(API_URL + '/controls/' + tag_name)
				.then(this.updateControlButtons.bind(this))
		}

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
			.then(function (response) {
				console.log(response);
			})
			.catch(function (error) {
				console.log(error);
			});
	}

	onModalShown() {
		console.log('onModalShown');

		axios.get(API_URL + '/controls/volume')
			.then(response => {
				console.log('volume ' + response.data.volume);
				this.dom.volumeSlider.value = parseInt(response.data.volume, 10);
				this.dom.volumeSlider.removeAttribute('disabled');
			})
	}
}