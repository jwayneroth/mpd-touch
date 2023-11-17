import TesselationAutomata from './lib/tesselation-automata.js';

export default class AutomataScreensaver {
	constructor(app) {
		console.log('AutomataScreensaver::init');

		this.app = app;
		this.ta = null;
		this.restartID = null;

		this.active = false;
		this.inited = false;

		const el = document.createElement('div');

		el.setAttribute('id', 'automata-screensaver');
		el.setAttribute('class', 'screensaver');

		el.innerHTML = `
			<div id="automata-screensaver__inner">
				<canvas id="automata-screensaver__canvas" width="400" height="400"></canvas>
				<h2 id="automata-screensaver__track"></h2>
			</div>
		`;

		this.dom = {
			el,
			inner: el.querySelector('#automata-screensaver___inner'),
			canvas: el.querySelector('#automata-screensaver__canvas'),
			track: el.querySelector('#automata-screensaver__track'),
		}

		this.onMpdStatus(this.app.lastMpdStatus);
	}

	// called by app
	initAnime() {

		this.inited = true;

		this.ta = new TesselationAutomata(this.dom.canvas, {
			type: '4ARGBA',
			fps: 3,
			scale: 50,
			seeds: 5,
			color_one: { r: 255, g: 255, b: 255, a: 255 },
			color_two: { r: 33, g: 33, b: 33, a: 100 },
		});

		if (this.restartID) {
			clearInterval(this.restartID);
		}

		this.restartID = setInterval(() => {
			console.log('restart ta');
			this.ta.restart();
		}, 20000);

		this.active = true;
	}

	stopAnime() {
		if (this.restartID) {
			clearInterval(this.restartID);
			this.restartID = null;
		}
		this.ta.stop();
		this.active = false;
	}

	onMpdStatus(status) {

		console.log('Screensaver::onMpdStatus', status);

		if (!status || !status.hasOwnProperty('now_playing')) return;

		this.dom.track.innerHTML = status.now_playing.title;
	}
}