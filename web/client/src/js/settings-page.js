import { axios, API_URL } from './api';

/**
 * Settings Page
 */
export default class SettingsPage {
	constructor(el, app) {
		console.log('SettingsPage::init');

		this.app = app;

		this.onEnter(el);
	}

	onEnter(el) {

		this.dom = {
			el,
			links: el.querySelectorAll('a'),
			webTypeRadio: el.querySelectorAll('input[name="ss_web_type"]'),
			webTimeoutInput: el.querySelector('#ss_web_timeout'),
			hostTypeRadio: el.querySelectorAll('input[name="ss_host_type"]'),
		};

		this.dom.el.querySelector('#ss_web_' + this.app.storedSettings.screensaverType).setAttribute('checked', true);

		this.dom.webTypeRadio.forEach(radio => radio.addEventListener('change', this.webTypeRadioChange.bind(this)));
		this.dom.hostTypeRadio.forEach(radio => radio.addEventListener('change', this.hostTypeRadioChange.bind(this)));

		this.dom.webTimeoutInput.value = this.app.storedSettings.screensaverTimeout / 1000;
		this.dom.webTimeoutInput.addEventListener('change', this.timeoutInputChange.bind(this));

		let i;
		for (i = 0; i < this.dom.links.length; i++) {
			this.dom.links[i].addEventListener('click', this.anchorClick.bind(this));
		}
	}

	webTypeRadioChange(evt) {
		console.log('webTypeRadioChange', evt.target.value);
		this.app.updateSetting('screensaverType', evt.target.value);
	}

	hostTypeRadioChange(evt) {
		console.log('hostTypeRadioChange', evt.target.value);
		axios.post(API_URL + '/settings/screensaver', { type: evt.target.value }, {
			headers: {
				'Content-Type': 'multipart/form-data'
			}
		})
			.then(this.hostTypeUpdate.bind(this));
	}

	hostTypeUpdate(response) {
		console.log('hostTypeUpdate', response.data);
	}

	timeoutInputChange(evt) {
		console.log('timeoutInputChange', evt.target.value);
		this.app.updateSetting('screensaverTimeout', evt.target.value * 1000);
	}

	anchorClick(evt) {
		evt.preventDefault();

		console.log('settings link click', evt.currentTarget.dataset.name);

		const btnName = evt.currentTarget.dataset.name;

		if (btnName == 'settings') {
			return false;
		}

		axios.get(API_URL + '/settings/' + evt.currentTarget.dataset.name)
			.then(response => console.log(response.data))

		return false;
	}
}