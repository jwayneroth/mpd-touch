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

		this.el = el;

		const ssSettings = document.createElement('div');

		ssSettings.setAttribute('id', 'settings__web');
		ssSettings.innerHTML = `
			<div>
				<h3>Screensaver</h3>
				<div>
					<input type="radio" id="ss_random" name="ss_type" value="random">
					<label for="ss_random">Random</label><br>
				</div>
				<div>
					<input type="radio" id="ss_bounce" name="ss_type" value="bounce">
					<label for="ss_bounce">Bounce</label>
				</div>
				<div>
					<input type="radio" id="ss_wave" name="ss_type" value="wave">
					<label for="ss_wave">Wave</label>
				</div>
				<div>
					<label for=""ss_timeout>Timeout (seconds)</label>
					<input type="number" id="ss_timeout" name="ss_timeout" value="${this.app.storedSettings.screensaverTimeout / 1000}" min="">
				</div>
			</div>
		`;

		this.el.appendChild(ssSettings);

		this.el.querySelector('#ss_' + this.app.storedSettings.screensaverType).setAttribute('checked', true);
		this.el.querySelectorAll('input[name="ss_type"]').forEach(radio => radio.addEventListener('change', this.typeRadioChange.bind(this)));
		this.el.querySelector('#ss_timeout').addEventListener('change', this.timeoutInputChange.bind(this));

		const links = this.el.querySelectorAll('a');

		let i;
		for (i = 0; i < links.length; i++) {
			links[i].addEventListener('click', this.anchorClick.bind(this));
		}
	}

	typeRadioChange(evt) {
		console.log('onRadioChange', evt.target.value);
		this.app.updateSetting('screensaverType', evt.target.value);
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