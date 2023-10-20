const FPS = 18;

export default class WeatherScreensaver {
	constructor() {
		console.log('WeatherScreensaver::init');

		this.el = null;

		this.fps = FPS;
		this.fpsInterval = 1000 / this.fps;
		this.lastRender = null;
		this.active = false;

		const el = document.createElement('div');

		el.setAttribute('id', 'weather-screensaver');

		el.innerHTML = `
			<div id="weather-screensaver__inner">
				<div id="weather-screensaver__frames" class="weather-anime"></div>
				<h2 id="weather-screensaver__track"></h2>
			</div>
		`;

		this.dom = {
			el,
			inner: el.querySelector('#weather-screensaver__inner'),
			frames: el.querySelector('#weather-screensaver__frames'),
			track: el.querySelector('#weather-screensaver__track'),
		}
	}

	// called by app
	initAnime() {


		this.lastRender = Date.now();
		this.active = true;
		this.animeID = window.requestAnimationFrame(this.animate.bind(this));
	}

	animate() {
		if (!this.active) return;

		this.animeID = window.requestAnimationFrame(this.animate.bind(this));
		const now = Date.now();
		const elapsed = now - this.lastRender;

		if (elapsed > this.fpsInterval) {
			this.lastRender = now - (elapsed % this.fpsInterval);


		}
	}
}

class ScreensaverBase {
	constructor() {
		console.log('ScreensaverBase::init');

		this.el = null;

		this.fps = FPS;
		this.fpsInterval = 1000 / this.fps;
		this.lastRender = null;
		this.active = false;

		const el = document.createElement('div');

		el.setAttribute('id', 'screensaver');

		el.innerHTML = `
			<div id="screensaver__inner">
				<h2 id="screensaver__track"></h2>
			</div>
		`;

		this.dom = {
			el,
			inner: el.querySelector('#screensaver__inner'),
			track: el.querySelector('#screensaver__track'),
		}

		console.log('ss dom', this.dom);
	}

	// called by app
	initAnime() {
		this.lastRender = Date.now();
		this.active = true;
		this.animeID = window.requestAnimationFrame(this.animate.bind(this));
	}

	animate() {
		if (!this.active) return;

		this.animeID = window.requestAnimationFrame(this.animate.bind(this));
		const now = Date.now();
		const elapsed = now - this.lastRender;

		if (elapsed > this.fpsInterval) {
			this.lastRender = now - (elapsed % this.fpsInterval);


		}
	}
}
