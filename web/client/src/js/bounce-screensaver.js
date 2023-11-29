import { axios, API_URL } from './api';

const FPS = 18;
const BGRGB = [10, 5, 0];

const BOUNCER_IMAGES = [
	'raspberrypi.png',
	'ra.png',
	'ra-demons.png',
	'gd-face.png',
	'gd-bolt.png',
];

export default class BounceScreensaver {
	constructor(app) {
		console.log('BounceScreensaver::init');

		this.app = app;
		this.el = null;
		this.bouncer = null;
		this.cover = null;
		this.fps = FPS;
		this.fpsInterval = 1000 / this.fps;
		this.lastRender = null;
		this.active = false;
		this.inited = false;
		this.eraseMode = true;

		const el = document.createElement('div');

		el.setAttribute('id', 'screensaver');
		el.setAttribute('class', 'screensaver');

		el.innerHTML = `
			<div id="screensaver__inner">
				<div id="screensaver__anime">
					<canvas id="screensaver__cover" width="800" height="425"></canvas>
					<canvas id="screensaver__canvas" width="800" height="425"></canvas>
					<div id="screensaver__bouncer"></div>
				</div>
				<h2 id="screensaver__track"></h2>
			</div>
		`;

		this.dom = {
			el,
			inner: el.querySelector('#screensaver__inner'),
			canvas: el.querySelector('#screensaver__canvas'),
			cover: el.querySelector('#screensaver__cover'),
			track: el.querySelector('#screensaver__track'),
			//bouncer: el.querySelector('#screensaver__bouncer'),
		}

		this.canvasCtx = this.dom.canvas.getContext('2d');
		this.coverCtx = this.dom.cover.getContext('2d');

		this.coverCtx.willReadFrequently = true;

		//this.canvasCtx.fillStyle = `rgb(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255})`;
		this.coverCtx.fillStyle = `rgb(${BGRGB[0]},${BGRGB[1]},${BGRGB[2]})`;

		this.onMpdStatus(this.app.lastMpdStatus);

		console.log('ss dom', this.dom);
	}

	initAnime() {

		if (this.inited) {
			this.active = true;
			this.animeID = window.requestAnimationFrame(this.animate.bind(this));
			return;
		}

		const cover = new Image();
		const bouncer = new Image();

		cover.onload = () => {

			this.cover.left = 400 - cover.width / 2;
			this.cover.top = 240 - cover.height / 2;
			this.cover.right = this.cover.left + cover.width;
			this.cover.bottom = this.cover.top + cover.height;

			console.log('cover props', this.cover);

			this.coverCtx.drawImage(this.cover.img, this.cover.left, this.cover.top);

			this.cover.buffer = this.coverCtx.getImageData(this.cover.left, this.cover.top, cover.width, cover.height).data;

			bouncer.onload = () => {
				console.log('bouncer load', bouncer.width, bouncer.height);

				//this.dom.bouncer.appendChild(bouncer);

				this.bouncer = new Bouncer(bouncer);
				this.bouncer.x = this.bouncer.width / 2 + Math.random() * (800 - this.bouncer.width);
				this.bouncer.y = this.bouncer.height / 2 + Math.random() * (425 - this.bouncer.height);
				console.log('bouncer props', this.bouncer);
				this.lastRender = Date.now();
				this.inited = true;
				this.active = true;
				this.animeID = window.requestAnimationFrame(this.animate.bind(this));
			}

			const src = BOUNCER_IMAGES[Math.floor(Math.random() * BOUNCER_IMAGES.length)];

			bouncer.src = '/assets/images/screensavers/' + src;
		};

		this.cover = {
			img: cover,
			left: null,
			top: null,
			right: null,
			bottom: null,
		};

		cover.setAttribute('src', '/api/cover');
	}

	stopAnime() {
		this.active = false;
		this.canvasCtx.clearRect(0, 0, this.dom.canvas.width, this.dom.canvas.height);
		//this.coverCtx.clearRect(0, 0, this.dom.cover.width, this.dom.cover.height);
		this.coverCtx.drawImage(this.cover.img, this.cover.left, this.cover.top);
		//this.canvasCtx.fillStyle = `rgb(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255})`;
		//this.coverCtx.fillStyle = `rgb(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255})`;
		this.eraseMode = true;
	}

	animate() {
		if (!this.active) return;

		this.animeID = window.requestAnimationFrame(this.animate.bind(this));
		const now = Date.now();
		const elapsed = now - this.lastRender;

		if (elapsed > this.fpsInterval) {
			//console.log('screensaver frame');

			this.lastRender = now - (elapsed % this.fpsInterval);

			// move the bouncing image and do wall check
			const bouncer = this.bouncer;

			bouncer.x += bouncer.vx;
			bouncer.y += bouncer.vy;

			if (bouncer.x > 800 - bouncer.width / 2) {
				bouncer.x = 800 - bouncer.width / 2;
				bouncer.vx *= -1;
			} else if (bouncer.x < bouncer.width / 2) {
				bouncer.x = bouncer.width / 2;
				bouncer.vx *= -1;
			}

			if (bouncer.y > 425 - bouncer.height / 2) {
				bouncer.y = 425 - bouncer.height / 2;
				bouncer.vy *= -1;
			} else if (bouncer.y < bouncer.height / 2) {
				bouncer.y = bouncer.height / 2;
				bouncer.vy *= -1;
			}

			// check intersection btw bouncer and cover
			const cover = this.cover;
			const cl = cover.left;
			const cr = cover.right;
			const ct = cover.top;
			const cb = cover.bottom;
			let x, y, firstHit, lastHit, drawLeft, drawTop, drawWidth, drawHeight, erased;

			for (x = bouncer.left; x < bouncer.right; x++) {
				for (y = bouncer.top; y < bouncer.bottom; y++) {
					if (x >= cl && x <= cr && y >= ct && y <= cb) {
						if (!firstHit) {
							firstHit = { x, y };
						}
						lastHit = { x, y };
					}
				}
			}

			if (firstHit) {
				drawLeft = firstHit.x;// - cl;
				drawTop = firstHit.y;// - ct;
				drawWidth = lastHit.x - firstHit.x;
				drawHeight = lastHit.y - firstHit.y;

				erased = this.isCoverErased();

				// we are erasing the cover image
				if (this.eraseMode) {
					// its fully erased, start redrawing it
					if (erased == 1) {
						this.eraseMode = false;
						this.coverCtx.drawImage(cover.img, drawLeft, drawTop, drawWidth, drawHeight, drawLeft, drawTop, drawWidth, drawHeight);
						// continue erasing
					} else {
						//console.log('erasing');
						this.coverCtx.fillRect(drawLeft, drawTop, drawWidth, drawHeight);
					}
				}
				// we are redrawing the cover image
				else {
					// its fully redrawn, start erasing it
					if (erased == -1) {
						this.eraseMode = true;
						this.coverCtx.fillRect(drawLeft, drawTop, drawWidth, drawHeight);
						// continue redrawing
					} else {
						//console.log('redrawing');
						this.coverCtx.drawImage(cover.img, drawLeft - this.cover.left, drawTop - this.cover.top, drawWidth, drawHeight, drawLeft, drawTop, drawWidth, drawHeight);
					}
				}
			}
			this.canvasCtx.drawImage(bouncer.img, bouncer.x - bouncer.width / 2, bouncer.y - bouncer.height / 2);
		}
	}

	pixelAtCoords(data, x, y, width) {
		const red = y * (width * 4) + x * 4;
		return [data[red], data[red + 1], data[red + 2], data[red + 3]];
	};

	/**
	 * isCoverErased
	 * 
	 * determines if cover image is erased by sampling every <step> pixels
	 * and comparing against original
	 * return 1 for completely erased, 0 for partly erased, -1 for completely original
	 * 
	 * @returns Boolean
	 */
	isCoverErased() {

		const cw = this.cover.right - this.cover.left;
		const ch = this.cover.bottom - this.cover.top;

		const buffer = this.cover.buffer;
		const pixels = this.coverCtx.getImageData(this.cover.left, this.cover.top, cw, ch).data;

		let hasDiff = false;
		let hasOrig = false;
		let step = 20;
		let i, j, pixel, origPixel;
		let x = 0;
		let y = 0;
		let diffs = 0;
		let comps;
		let ct;
		for (i = 0; i < Math.round(cw / step); i++) {
			for (j = 0; j < Math.round(ch / step); j++) {

				x = i * step;
				y = j * step;

				pixel = this.pixelAtCoords(pixels, x, y, cw);
				origPixel = this.pixelAtCoords(buffer, x, y, cw);

				// if (i == 0 && j == 0) {
				// 	console.log(pixel, origPixel);
				// }

				// if any diff in pixels
				comps = [
					pixel[0] - origPixel[0],
					pixel[1] - origPixel[1],
					pixel[2] - origPixel[2],
				];

				ct = comps.reduce((t, comp) => t + Math.abs(comp), 0);

				//console.log('comps', ct);

				//if (pixel[0] != origPixel[0] || pixel[1] != origPixel[1] || pixel[2] != origPixel[2]) {
				if (ct > 3) {
					diffs += 1;
					hasDiff = true;
					// if we have already seen an original pixel, abort and return partly
					if (hasOrig == true) {
						//console.log('diff', pixel, origPixel);
						return 0;
					}
					// no diff
				} else {

					hasOrig = true;
					// if we have seen a diff, abort and return partly
					if (hasDiff == true) {
						return 0;
					}
				}
			}
		}

		// if we only saw differences
		if (hasDiff == true) {
			if (hasOrig == false) {
				return 1;
			}
			return 0
		}
		return -1
	}

	onMpdStatus(status) {

		console.log('Screensaver::onMpdStatus', status);

		if (!status || !status.hasOwnProperty('now_playing')) return;

		this.dom.track.innerHTML = status.now_playing.title;
	}
}

class Bouncer {
	constructor(img) {
		this.img = img;
		this.width = img.width;
		this.height = img.height;

		let pm = Math.random() < 0.5 ? -1 : 1;

		this.vx = (Math.random() * 15 + 3) * pm;

		pm = Math.random() < 0.5 ? -1 : 1;

		this.vy = (Math.random() * 15 + 3) * pm;

		this._x = null;
		this._y = null;
		this.left = null;
		this.right = null;
		this.top = null;
		this.bottom = null;
	}

	get x() {
		return this._x;
	}

	get y() {
		return this._y;
	}

	set x(x) {
		this._x = x;
		this.left = x - this.width / 2;
		this.right = x + this.width / 2;
	}

	set y(y) {
		this._y = y;
		this.top = y - this.height / 2;
		this.bottom = y + this.height / 2;
	}
}