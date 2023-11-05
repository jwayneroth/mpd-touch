import { axios, API_URL } from './api';

/**
 * Settings Page
 */
export default class SettingsPage {
	constructor(el) {
		console.log('SettingsPage::init');

		this.onEnter(el);
	}

	onEnter(el) {

		this.el = el;

		const ssSettings = document.createElement('div');

		ssSettings.setAttribute('id', 'settings__web');
		ssSettings.innerHTML = `
			<h3>Screensaver</h3>
			<div>
				<input type="radio" id="ss_on" name="ss_on_off" value="on">
				<label for="ss_on">On</label><br>
				<input type="radio" id="ss_off" name="ss_on_off" value="off">
				<label for="ss_off">Off</label>
			</div>
			<label for="ss_type">Type: </label>
			<select name="ss_type" id="ss_type">
				<option value="random">Random</option>
				<option value="bouncer">Bouncer</option>
				<option value="weather">Weather</option>
			</select>
		`;

		//this.el.appendChild(ssSettings);

		const links = this.el.querySelectorAll('a');
		let i;
		for (i = 0; i < links.length; i++) {
			links[i].addEventListener('click', this.anchorClick.bind(this));
		}
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