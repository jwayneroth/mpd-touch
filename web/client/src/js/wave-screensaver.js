import Wave from './lib/wave.js';

const FPS = 18;

export default class WaveScreensaver {
	constructor(app) {
		console.log('WaveScreensaver::init');

		this.app = app;
		this.el = null;
		this.fps = FPS;
		this.fpsInterval = 1000 / this.fps;
		this.lastRender = null;
		this.active = false;
		this.inited = false;

		const el = document.createElement('div');

		el.setAttribute('id', 'screensaver');
		el.setAttribute('class', 'screensaver');

		el.innerHTML = `
			<div id="screensaver__inner">
				<div id="screensaver__anime">
					<canvas id="screensaver__canvas" width="800" height="425"></canvas>
				</div>
				<h2 id="screensaver__track"></h2>
			</div>
		`;

		this.dom = {
			el,
			inner: el.querySelector('#screensaver__inner'),
			canvas: el.querySelector('#screensaver__canvas'),
			track: el.querySelector('#screensaver__track'),
		}

		this.canvasCtx = this.dom.canvas.getContext('2d');

		this.onMpdStatus(this.app.lastMpdStatus);

		this.wave = null;

		console.log('ss dom', this.dom);
	}

	initAnime() {

		if (this.inited) {
			this.active = true;
			this.animeID = window.requestAnimationFrame(this.animate.bind(this));
			return;
		}

		this.lastRender = Date.now();
		this.inited = true;
		this.active = true;

		this.wave = new Wave(this.canvasCtx, null);

		this.animeID = window.requestAnimationFrame(this.animate.bind(this));
	}

	stopAnime() {
		this.active = false;
		this.canvasCtx.clearRect(0, 0, this.dom.canvas.width, this.dom.canvas.height);
	}

	animate() {
		if (!this.active) return;

		this.animeID = window.requestAnimationFrame(this.animate.bind(this));
		const now = Date.now();
		const elapsed = now - this.lastRender;

		if (elapsed > this.fpsInterval) {
			this.lastRender = now - (elapsed % this.fpsInterval);

			this.canvasCtx.clearRect(0, 0, this.dom.canvas.width, this.dom.canvas.height);

			this.wave.loopDisplay();
		}
	}

	onMpdStatus(status) {

		console.log('Screensaver::onMpdStatus', status);

		if (!status || !status.hasOwnProperty('now_playing')) return;

		this.dom.track.innerHTML = status.now_playing.title;
	}
}