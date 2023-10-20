import { axios, API_URL } from './api';

const FPS = 18;

const BOUNCER_IMAGES = [
	'raspberrypi.png',
	'ra.png',
	'ra-demons.png',
	'gd-face.png',
	'gd-bolt.png',
];

export default class BounceScreensaver {
	constructor() {
		console.log('BounceScreensaver::init');

		this.el = null;
		this.bouncer = null;
		this.cover = null;
		this.bufferCover = null;
		this.fps = FPS;
		this.fpsInterval = 1000 / this.fps;
		this.lastRender = null;
		this.active = false;
		this.eraseMode = true;

		const el = document.createElement('div');

		el.setAttribute('id', 'screensaver');

		el.innerHTML = `
			<div id="screensaver__inner">
				<canvas id="screensaver__canvas" width="800" height="425"></canvas>
				<h2 id="screensaver__track"></h2>
				<div id="screensaver__bouncer"></div>
			</div>
		`;

		this.dom = {
			el,
			inner: el.querySelector('#screensaver__inner'),
			canvas: el.querySelector('#screensaver__canvas'),
			track: el.querySelector('#screensaver__track'),
			//bouncer: el.querySelector('#screensaver__bouncer'),
		}

		this.ctx = this.dom.canvas.getContext('2d');
		this.ctx.fillStyle = 'yellow'; //'rgb(10,5,0)';

		console.log('ss dom', this.dom);
	}

	initAnime() {
		const cover = new Image();
		const bouncer = new Image();

		cover.onload = () => {

			this.cover.left = 400 - cover.width / 2;
			this.cover.top = 240 - cover.height / 2;
			this.cover.right = this.cover.left + cover.width;
			this.cover.bottom = this.cover.top + cover.height;

			console.log('cover props', this.cover);

			this.ctx.drawImage(cover, this.cover.left, this.cover.top);

			bouncer.onload = () => {
				console.log('bouncer load', bouncer.width, bouncer.height);

				//this.dom.bouncer.appendChild(bouncer);

				this.bouncer = new Bouncer(bouncer);
				this.bouncer.x = this.bouncer.width / 2 + Math.random() * (800 - this.bouncer.width);
				this.bouncer.y = this.bouncer.height / 2 + Math.random() * (425 - this.bouncer.height);
				console.log('bouncer props', this.bouncer);
				this.lastRender = Date.now();
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
						this.ctx.drawImage(cover.img, drawLeft, drawTop, drawWidth, drawHeight);
						// continue erasing
					} else {
						this.ctx.fillRect(drawLeft, drawTop, drawWidth, drawHeight);
					}
				}
				// we are redrawing the cover image
				else {
					// its fully redrawn, start erasing it
					if (erased == -1) {
						this.eraseMode = true;
						this.ctx.fillRect(drawLeft, drawTop, drawWidth, drawHeight);
						// continue redrawing
					} else {
						this.ctx.drawImage(cover.img, drawLeft, drawTop, drawWidth, drawHeight);
					}
				}
			}
			this.ctx.drawImage(bouncer.img, bouncer.x - bouncer.width / 2, bouncer.y - bouncer.height / 2);
		}
	}

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
		const cover = this.cover;
		const cw = cover.width;
		const ch = cover.height;

		let hasDiff = false;
		let hasOrig = false;
		let step = 20;
		let i, j, pixel, origPixel;
		let x = 0;
		let y = 0;
		let diffs = 0;

		for (i = 0; i < Math.round(cw / step); i++) {
			for (j = 0; j < Math.round(ch / step); j++) {

				x = i * step;
				y = j * step;

				pixel = cover.getImageData(x, y, 1, 1).data;
				origPixel = this.bufferCover.getImageData(x, y, 1, 1).data;

				if (pixel[0] != origPixel[0] || pixel[1] != origPixel[1] || pixel[2] != origPixel[2]) {
					diffs += 1;
					hasDiff = true;
					if (hasOrig == true) {
						return 0;
					}
				} else {
					hasOrig = true;
					if (hasDiff == true) {
						return 0;
					}
				}
			}
		}

		if (hasDiff == true) {
			if (hasOrig == false) {
				return 1;
			}
			return 0
		}
		return -1
	}

	onMpdStatus(evt) {
		const status = evt.detail;

		console.log('Screensaver::onMpdStatus', status);

		this.dom.track.innerHTML = status.now_playing.title;
	}
}

class Bouncer {
	constructor(img) {
		this.img = img;
		this.width = img.width;
		this.height = img.height;
		this.vx = Math.random() * 30 - 15;
		this.vy = Math.random() * 30 - 15;
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