import { axios, API_URL } from './api';

/**
 * Settings Page
 */
export default class SettingsPage {
	constructor(el) {
		this.el = el;
		const links = this.el.querySelectorAll('a');
		let i;
		for (i = 0; i < links.length; i++) {
			links[i].addEventListener('click', this.anchorClick.bind(this));
		}
	}

	anchorClick(evt) {
		evt.preventDefault();

		console.log('settings link click', evt.currentTarget.dataset.name);

		axios.get(API_URL + '/settings/' + evt.currentTarget.dataset.name)
			.then(response => console.log(response.data))

		return false;
	}
}