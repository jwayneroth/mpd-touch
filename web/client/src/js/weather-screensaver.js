const FPS = 18;

export default class WeatherScreensaver {
	constructor(app) {
		console.log('WeatherScreensaver::init');

		this.app = app;
		this.el = null;

		this.fps = FPS;
		this.fpsInterval = 1000 / this.fps;
		this.lastRender = null;
		this.active = false;
		this.inited = false;

		const el = document.createElement('div');

		el.setAttribute('id', 'weather-screensaver');
		el.setAttribute('class', 'screensaver');

		el.innerHTML = `
			<div id="weather-screensaver__inner">
				<!--<div id="weather-screensaver__frames" class="weather-anime"></div>-->
				<img id="weather-screensaver__img" src="https://cdn.star.nesdis.noaa.gov/GOES16/ABI/SECTOR/ne/GEOCOLOR/GOES16-NE-GEOCOLOR-600x600.gif">
				<h2 id="weather-screensaver__track"></h2>
			</div>
		`;

		this.dom = {
			el,
			inner: el.querySelector('#weather-screensaver__inner'),
			//frames: el.querySelector('#weather-screensaver__frames'),
			track: el.querySelector('#weather-screensaver__track'),
		}

		this.onMpdStatus(this.app.lastMpdStatus);
	}

	// called by app
	initAnime() {
		this.inited = true;
		// this.lastRender = Date.now();
		// this.active = true;
		// this.animeID = window.requestAnimationFrame(this.animate.bind(this));
		this.active = true;

	}

	stopAnime() {
		this.active = false;
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

	onMpdStatus(status) {

		console.log('Screensaver::onMpdStatus', status);

		if (!status || !status.hasOwnProperty('now_playing')) return;

		this.dom.track.innerHTML = status.now_playing.title;
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
