export default class TesselationAutomata {
	constructor(canvas, config) {

		if (!canvas) {
			console.log('missing or invalid ta canvas!');
			return false;
		}

		//console.log('TesselationAutomata::canvas ' + canvas.width + ' ' + canvas.height);

		this.canvas = canvas;

		const overrides = config || {};

		const defaults = {
			type: '4ARGBA',
			lattice: 'centered',
			scale: 25,
			seeds: 10,
			fps: 18,
			color_one: { r: 255, g: 255, b: 255, a: 255 },
			color_two: { r: 33, g: 33, b: 33, a: 100 },
			animeID: null
		};

		this.opts = Object.assign({}, defaults, overrides);

		this.scale = this.opts.scale;
		this.seeds = this.opts.seeds;
		this.color_one = this.opts.color_one;
		this.color_two = this.opts.color_two;
		this.type = this.opts.type;
		this.lattice = this.opts.lattice;
		this.rate = 1000 / this.opts.fps;
		this.ctx = this.canvas.getContext('2d');
		this.width = this.canvas.width;
		this.height = this.canvas.height;
		this.imageData = this.ctx.getImageData(0, 0, this.width, this.height);
		this.animeID = this.opts.animeId;

		this.initLattice();

		this.startLoop();
	}

	initLattice() {
		if (this.type == '4A' || this.type == '4ARGBA') {
			if (this.lattice == 'centered') {
				this.centeredLattice();
			} else if (this.lattice == 'rectangular') {
				this.rectangularLattice();
			} else if (this.lattice == 'mixed') {
				this.mixedLattice();
			}
		} else {
			this.solidLattice();
		}
	}

	solidLattice() {

		const { scale, color_one, color_two } = this;

		let i = 0;
		let row = 0;
		let col = 0;
		let offset;
		let sizew;

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			offset = col * 4 + row * 4 * width;

			sizew = (col + scale <= width) ? scale : width - col;

			this.fillSquare(offset, sizew, scale, color_two);

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
			} else {
				col += scale;
			}

			i++;
		}

		this.ctx.putImageData(imageData, 0, 0);
		this.seedLattice((this.type.indexOf('RGBA') !== -1));
	}

	centeredLattice() {

		const { scale, color_one, color_two, width, height } = this;

		let i = 0;
		let row = 0;
		let col = 0;
		let offset;
		let sizew;
		let square_rgb;

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			if (((row / scale % 2 == 0) && (col / scale % 2 == 0)) ||
				((row / scale % 2 != 0) && (col / scale % 2 != 0))
			) {
				square_rgb = color_one;
			} else {
				square_rgb = color_two;
			}

			offset = col * 4 + row * 4 * width;

			//console.log('i: ' + i + '\t\t row: ' + row + '\t\t col: ' + col + '\t\t offset: ' + offset);

			sizew = (col + scale <= width) ? scale : width - col;

			this.fillSquare(offset, sizew, scale, square_rgb);

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
			} else {
				col += scale;
			}

			i++;
		}

		this.ctx.putImageData(this.imageData, 0, 0);

		this.seedLattice((this.type.indexOf('RGBA') !== -1));
	}

	rectangularLattice() {

		const { scale, color_one, color_two } = this;

		let i = 0;
		let row = 0;
		let col = 0;
		let square_rgb;
		let offset;
		let sizew;

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			if (col / scale % 2 == 0) {
				square_rgb = color_one;
			} else {
				square_rgb = color_two;
			}

			offset = col * 4 + row * 4 * width;

			sizew = (col + scale <= width) ? scale : width - col;

			this.fillSquare(offset, sizew, scale, square_rgb);

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
			} else {
				col += scale;
			}

			i++;
		}

		this.ctx.putImageData(imageData, 0, 0);

		this.seedLattice((this.type.indexOf('RGBA') !== -1));
	}

	mixedLattice() {

		const { scale, color_one, color_two } = this;
		const lattice = Math.round(Math.random());

		let i = 0;
		let row = 0;
		let col = 0;
		let square_rgb;
		let offset;
		let sizew;

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			if (lattice) {
				if (((row / scale % 2 == 0) && (col / scale % 2 == 0)) ||
					((row / scale % 2 != 0) && (col / scale % 2 != 0))
				) {
					square_rgb = color_one;
				} else {
					square_rgb = color_two;
				}
			} else {
				if (col / scale % 2 == 0) {
					square_rgb = color_one;
				} else {
					square_rgb = color_two;
				}
			}

			offset = col * 4 + row * 4 * width;

			sizew = (col + scale <= width) ? scale : width - col;

			this.fillSquare(offset, sizew, scale, square_rgb);

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
				if (row % 15 == 0) lattice = Math.round(Math.random());
			} else {
				col += scale;
			}

			i++;
		}

		this.ctx.putImageData(imageData, 0, 0);

		this.seedLattice((this.type.indexOf('RGBA') !== -1));
	}

	implementColors(c1, c2) {

		const { scale, color_one } = this;

		const id = {
			data: this.cloneArray(this.imageData.data),
			width: this.width,
			height: this.height
		};

		let i = 0;
		let row = 0;
		let col = 0;
		let square_rgb;
		let offset;
		let sizew;

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			offset = col * 4 + row * 4 * width;

			sizew = (col + scale <= width) ? scale : width - col;

			pixel = this.getPixel(id, col, row, width);

			pixel.r = (pixel.r == color_one.r) ? c1.r : c2.r;
			pixel.g = (pixel.g == color_one.g) ? c1.g : c2.g;
			pixel.b = (pixel.b == color_one.b) ? c1.b : c2.b;
			pixel.a = (pixel.a == color_one.a) ? c1.a : c2.a;

			this.fillSquare(offset, sizew, scale, pixel);

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
			} else {
				col += scale;
			}

			i++;
		}

		this.ctx.putImageData(this.imageData, 0, 0);
	}

	seedLattice(rgba) {

		const { scale, color_one, color_two, seeds, width, height } = this;

		let i = 0;
		let sizew;
		let seed_r, seed_c, seed_rgba;
		let offset;

		for (i = 0; i < seeds; i++) {

			seed_r = scale * Math.floor(Math.random() * (height / scale));
			seed_c = scale * Math.floor(Math.random() * (width / scale));
			seed_rgba = { r: color_one.r, g: color_one.g, b: color_one.b, a: color_one.a };

			if (rgba) {
				if (Math.round(Math.random())) seed_rgba.r = color_two.r;
				if (Math.round(Math.random())) seed_rgba.g = color_two.g;
				if (Math.round(Math.random())) seed_rgba.b = color_two.b;
				if (Math.round(Math.random())) seed_rgba.a = color_two.a;
			}

			offset = seed_c * 4 + seed_r * 4 * width;

			sizew = (seed_c + scale <= width) ? scale : width - seed_c;

			this.fillSquare(offset, sizew, scale, seed_rgba);
		}

		this.ctx.putImageData(this.imageData, 0, 0);
	}

	iterate1() {

		var id = { data: this.cloneArray(this.imageData.data), width: this.width, height: this.height },
			scale = this.scale,
			sizew,
			i = 0, row = 0, col = 0, draw = 0,
			rsum, gsum, bsum, asum,
			tp, bp, lp, rp,
			last_col = (Math.ceil(width / scale) * scale - scale),
			last_row = (Math.ceil(height / scale) * scale - scale),
			l, t, r, b,
			color_one = this.color_one,
			color_two = this.color_two,
			rmatch = color_one.r * 1 + color_two.r * 3,
			gmatch = color_one.g * 1 + color_two.g * 3,
			bmatch = color_one.b * 1 + color_two.b * 3,
			amatch = color_one.a * 1 + color_two.a * 3;

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			draw = 0;

			tp = (row > 0) ? row - scale : last_row;
			bp = (row < last_row) ? row + scale : 0;
			lp = (col > 0) ? col - scale : last_col;
			rp = (col < last_col) ? col + scale : 0;

			t = this.getPixel(id, col, tp, width);
			b = this.getPixel(id, col, bp, width);
			l = this.getPixel(id, lp, row, width);
			r = this.getPixel(id, rp, row, width);

			rsum = t.r + b.r + l.r + r.r;
			gsum = t.g + b.g + l.g + r.g;
			bsum = t.b + b.b + l.b + r.b;
			asum = t.a + b.a + l.a + r.a;

			pixel = this.getPixel(id, col, row, width);

			if (rsum == rmatch && pixel.r != color_one.r) {
				draw = 1;
				pixel.r = (pixel.r == color_one.r) ? color_two.r : color_one.r;
			}
			if (gsum == gmatch && pixel.g != color_one.g) {
				draw = 1;
				pixel.g = (pixel.g == color_one.g) ? color_two.g : color_one.g;
			}
			if (bsum == bmatch && pixel.b != color_one.b) {
				draw = 1;
				pixel.b = (pixel.b == color_one.b) ? color_two.b : color_one.b;
			}
			if (asum == amatch && pixel.a != color_one.a) {
				draw = 1;
				pixel.a = (pixel.a == color_one.a) ? color_two.a : color_one.a;
			}

			if (draw) {
				offset = col * 4 + row * 4 * width;
				sizew = (col + scale <= width) ? scale : width - col;
				this.fillSquare(offset, sizew, scale, pixel);
			}

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
			} else {
				col += scale;
			}
			i++;
		}
		this.ctx.putImageData(imageData, 0, 0);
	};

	iterate4A() {

		const { width, height, scale, color_one, color_two } = this;

		const id = {
			data: this.cloneArray(this.imageData.data),
			width,
			height,
		};

		let sizew,
			i = 0, row = 0, col = 0, draw = 0,
			rsum, gsum, bsum, asum,
			last_col = (Math.ceil(width / scale) * scale - scale),
			last_row = (Math.ceil(height / scale) * scale - scale),
			tp, bp, lp, rp,
			l, t, r, b, br, tl,
			rmatch = color_one.r * 3 + color_two.r * 3,
			gmatch = color_one.g * 3 + color_two.g * 3,
			bmatch = color_one.b * 3 + color_two.b * 3,
			amatch = color_one.a * 3 + color_two.a * 3,
			pixel,
			offset;

		//console.log(width, height, scale, color_one, color_two);
		//console.log('iterate4A: imageData.data ' + this.imageData.data.slice().length);

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			draw = 0;

			tp = (row > 0) ? row - scale : last_row;
			bp = (row < last_row) ? row + scale : 0;
			lp = (col > 0) ? col - scale : last_col;
			rp = (col < last_col) ? col + scale : 0;

			t = this.getPixel(id, col, tp, width);
			b = this.getPixel(id, col, bp, width);
			l = this.getPixel(id, lp, row, width);
			r = this.getPixel(id, rp, row, width);
			br = this.getPixel(id, rp, bp, width);
			tl = this.getPixel(id, lp, tp, width);

			rsum = t.r + b.r + l.r + r.r + br.r + tl.r;
			gsum = t.g + b.g + l.g + r.g + br.g + tl.g;
			bsum = t.b + b.b + l.b + r.b + br.b + tl.b;
			asum = t.a + b.a + l.a + r.a + br.a + tl.a;

			pixel = this.getPixel(id, col, row, width);

			if (rsum == rmatch) {
				draw = 1;
				pixel.r = (pixel.r == color_one.r) ? color_two.r : color_one.r;
			}
			if (gsum == gmatch) {
				draw = 1;
				pixel.g = (pixel.g == color_one.g) ? color_two.g : color_one.g;
			}
			if (bsum == bmatch) {
				draw = 1;
				pixel.b = (pixel.b == color_one.b) ? color_two.b : color_one.b;
			}
			if (asum == amatch) {
				draw = 1;
				pixel.a = (pixel.a == color_one.a) ? color_two.a : color_one.a;
			}

			if (draw) {
				offset = col * 4 + row * 4 * width;
				sizew = (col + scale <= width) ? scale : width - col;
				this.fillSquare(offset, sizew, scale, pixel);
			}

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
			} else {
				col += scale;
			}
			i++;
		}

		this.ctx.putImageData(this.imageData, 0, 0);
	}

	iterateLife() {

		var id = { data: this.cloneArray(this.imageData.data), width: this.width, height: this.height },
			scale = this.scale,
			sizew,
			i = 0, row = 0, col = 0, draw = 0,
			rsum, gsum, bsum, asum,
			tp, bp, lp, rp,
			last_col = (Math.ceil(width / scale) * scale - scale),
			last_row = (Math.ceil(height / scale) * scale - scale),
			l, t, r, b, br, tl, bl, tr,
			color_one = this.color_one,
			color_two = this.color_two,
			rmatch2 = color_one.r * 2 + color_two.r * 6,
			gmatch2 = color_one.g * 2 + color_two.g * 6,
			bmatch2 = color_one.b * 2 + color_two.b * 6,
			amatch2 = color_one.a * 2 + color_two.a * 6;
		rmatch3 = color_one.r * 3 + color_two.r * 5,
			gmatch3 = color_one.g * 3 + color_two.g * 5,
			bmatch3 = color_one.b * 3 + color_two.b * 5,
			amatch3 = color_one.a * 3 + color_two.a * 5;

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			draw = 0;

			tp = (row > 0) ? row - scale : last_row;
			bp = (row < last_row) ? row + scale : 0;
			lp = (col > 0) ? col - scale : last_col;
			rp = (col < last_col) ? col + scale : 0;

			t = this.getPixel(id, col, tp, width);
			b = this.getPixel(id, col, bp, width);
			l = this.getPixel(id, lp, row, width);
			r = this.getPixel(id, rp, row, width);
			br = this.getPixel(id, rp, bp, width);
			tl = this.getPixel(id, lp, tp, width);
			bl = this.getPixel(id, lp, bp, width);
			tr = this.getPixel(id, rp, tp, width);

			rsum = t.r + b.r + l.r + r.r + br.r + tl.r + bl.r + tr.r;
			gsum = t.g + b.g + l.g + r.g + br.g + tl.g + bl.g + tr.g;
			bsum = t.b + b.b + l.b + r.b + br.b + tl.b + bl.b + tr.b;
			asum = t.a + b.a + l.a + r.a + br.a + tl.a + bl.a + tr.a;

			pixel = this.getPixel(id, col, row, width);

			// if live cell
			if (pixel.r == color_one.r) {
				// if no match, dies
				if (rsum != rmatch2 && rsum != rmatch3) {
					draw = 1;
					pixel.r = color_two.r;
				}
				// dead cell born if match
			} else if (rsum == rmatch3) {
				draw = 1;
				pixel.r = color_one.r;
			}
			if (pixel.g == color_one.g) {
				if (gsum != gmatch2 && gsum != gmatch3) {
					draw = 1;
					pixel.g = color_two.g;
				}
			} else if (gsum == gmatch3) {
				draw = 1;
				pixel.g = color_one.g;
			}
			if (pixel.b == color_one.b) {
				if (bsum != bmatch2 && bsum != bmatch3) {
					draw = 1;
					pixel.b = color_two.b;
				}
			} else if (bsum == bmatch3) {
				draw = 1;
				pixel.b = color_one.b;
			}
			if (pixel.a == color_one.a) {
				if (asum != amatch2 && asum != amatch3) {
					draw = 1;
					pixel.a = color_two.a;
				}
			} else if (asum == amatch3) {
				draw = 1;
				pixel.a = color_one.a;
			}

			if (draw) {
				offset = col * 4 + row * 4 * width;
				sizew = (col + scale <= width) ? scale : width - col;
				this.fillSquare(offset, sizew, scale, pixel);
			}

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
			} else {
				col += scale;
			}
			i++;
		}
		this.ctx.putImageData(imageData, 0, 0);
	}

	iterate30() {

		var id = { data: this.cloneArray(this.imageData.data), width: this.width, height: this.height },
			scale = this.scale,
			sizew,
			i = 0, row = 0, col = 0, draw = 0,
			rsum, gsum, bsum, asum,
			lp, rp, tp,
			last_col = (Math.ceil(width / scale) * scale - scale),
			last_row = (Math.ceil(height / scale) * scale - scale),
			tl, t, tr,
			color_one = this.color_one,
			color_two = this.color_two,
			rmatch1 = color_one.r + color_two.r * 2,
			gmatch1 = color_one.g + color_two.g * 2,
			bmatch1 = color_one.b + color_two.b * 2,
			amatch1 = color_one.a + color_two.a * 2;
		rmatch2 = color_one.r * 2 + color_two.r;
		gmatch2 = color_one.g * 2 + color_two.g;
		bmatch2 = color_one.b * 2 + color_two.b;
		amatch2 = color_one.a * 2 + color_two.a;

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			draw = 0;

			tp = (row > 0) ? row - scale : last_row;
			lp = (col > 0) ? col - scale : last_col;
			rp = (col < last_col) ? col + scale : 0;

			t = this.getPixel(id, col, tp, width);
			tl = this.getPixel(id, lp, tp, width);
			tr = this.getPixel(id, rp, tp, width);

			rsum = t.r + tl.r + tr.r;
			gsum = t.g + tl.g + tr.g;
			bsum = t.b + tl.b + tr.b;
			asum = t.a + tl.a + tr.a;

			pixel = { r: color_two.r, g: color_two.g, b: color_two.b, a: color_two.a };
			//pixel = this.getPixel(id,col,row,width);

			//console.log(i + ') row:' + row/100 + ' col:' + col/100 +
			//			' prev:' + pp/100 + ' next:' + np/100 +
			//			' l:' + l.r + ' r:' + r.r +
			//			' rsum:' + rsum);

			if (rsum == rmatch1 || (rsum == rmatch2 && tl.r == color_two.r)) {
				draw = 1;
				pixel.r = color_one.r;
			}

			if (gsum == gmatch1 || (gsum == gmatch2 && tl.g == color_two.g)) {
				draw = 1;
				pixel.g = color_one.g;
			}

			if (bsum == bmatch1 || (bsum == bmatch2 && tl.b == color_two.b)) {
				draw = 1;
				pixel.b = color_one.b;
			}

			if (asum == amatch1 || (asum == amatch2 && tl.a == color_two.a)) {
				draw = 1;
				pixel.a = color_one.a;
			}

			if (draw) {
				offset = col * 4 + row * 4 * width;
				sizew = (col + scale <= width) ? scale : width - col;
				this.fillSquare(offset, sizew, scale, pixel);
			}

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
			} else {
				col += scale;
			}
			i++;
		}
		this.ctx.putImageData(imageData, 0, 0);
	}

	iterate90() {

		var id = { data: this.cloneArray(this.imageData.data), width: this.width, height: this.height },
			scale = this.scale,
			sizew,
			i = 0, row = 0, col = 0, draw = 0,
			rsum, gsum, bsum, asum,
			lp, rp, tp,
			last_col = (Math.ceil(width / scale) * scale - scale),
			last_row = (Math.ceil(height / scale) * scale - scale),
			tl, t, tr,
			color_one = this.color_one,
			color_two = this.color_two,
			rmatch1 = color_one.r + color_two.r * 2,
			gmatch1 = color_one.g + color_two.g * 2,
			bmatch1 = color_one.b + color_two.b * 2,
			amatch1 = color_one.a + color_two.a * 2;
		rmatch2 = color_one.r * 2 + color_two.r;
		gmatch2 = color_one.g * 2 + color_two.g;
		bmatch2 = color_one.b * 2 + color_two.b;
		amatch2 = color_one.a * 2 + color_two.a;

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			draw = 0;

			tp = (row > 0) ? row - scale : last_row;
			lp = (col > 0) ? col - scale : last_col;
			rp = (col < last_col) ? col + scale : 0;

			t = this.getPixel(id, col, tp, width);
			tl = this.getPixel(id, lp, tp, width);
			tr = this.getPixel(id, rp, tp, width);

			rsum = t.r + tl.r + tr.r;
			gsum = t.g + tl.g + tr.g;
			bsum = t.b + tl.b + tr.b;
			asum = t.a + tl.a + tr.a;

			pixel = { r: color_two.r, g: color_two.g, b: color_two.b, a: color_two.a };

			if ((rsum == rmatch1 && t.r != color_one.r) || (rsum == rmatch2 && t.r == color_one.r)) {
				draw = 1;
				pixel.r = color_one.r;
			}

			if ((gsum == gmatch1 && t.g != color_one.g) || (gsum == gmatch2 && t.g == color_one.g)) {
				draw = 1;
				pixel.g = color_one.g;
			}

			if ((bsum == bmatch1 && t.b != color_one.b) || (bsum == bmatch2 && t.b == color_one.b)) {
				draw = 1;
				pixel.b = color_one.b;
			}

			if ((asum == amatch1 && t.a != color_one.a) || (asum == amatch2 && t.a == color_one.a)) {
				draw = 1;
				pixel.a = color_one.a;
			}

			if (draw) {
				offset = col * 4 + row * 4 * width;
				sizew = (col + scale <= width) ? scale : width - col;
				this.fillSquare(offset, sizew, scale, pixel);
			}

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
			} else {
				col += scale;
			}
			i++;
		}
		this.ctx.putImageData(imageData, 0, 0);
	}

	iterate110() {

		var id = { data: this.cloneArray(this.imageData.data), width: this.width, height: this.height },
			scale = this.scale,
			sizew,
			i = 0, row = 0, col = 0, draw = 0,
			rsum, gsum, bsum, asum,
			lp, rp, tp,
			last_col = (Math.ceil(width / scale) * scale - scale),
			last_row = (Math.ceil(height / scale) * scale - scale),
			tl, t, tr,
			color_one = this.color_one,
			color_two = this.color_two,
			rmatch1 = color_one.r + color_two.r * 2,
			gmatch1 = color_one.g + color_two.g * 2,
			bmatch1 = color_one.b + color_two.b * 2,
			amatch1 = color_one.a + color_two.a * 2;
		rmatch2 = color_one.r * 2 + color_two.r;
		gmatch2 = color_one.g * 2 + color_two.g;
		bmatch2 = color_one.b * 2 + color_two.b;
		amatch2 = color_one.a * 2 + color_two.a;

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			draw = 0;

			tp = (row > 0) ? row - scale : last_row;
			lp = (col > 0) ? col - scale : last_col;
			rp = (col < last_col) ? col + scale : 0;

			t = this.getPixel(id, col, tp, width);
			tl = this.getPixel(id, lp, tp, width);
			tr = this.getPixel(id, rp, tp, width);

			rsum = t.r + tl.r + tr.r;
			gsum = t.g + tl.g + tr.g;
			bsum = t.b + tl.b + tr.b;
			asum = t.a + tl.a + tr.a;

			pixel = { r: color_two.r, g: color_two.g, b: color_two.b, a: color_two.a };

			if (rsum == rmatch2 || (rsum == rmatch1 && tl.r == color_two.r)) {
				draw = 1;
				pixel.r = color_one.r;
			}

			if (gsum == gmatch2 || (gsum == gmatch1 && tl.g == color_two.g)) {
				draw = 1;
				pixel.g = color_one.g;
			}

			if (bsum == bmatch2 || (bsum == bmatch1 && tl.b == color_two.b)) {
				draw = 1;
				pixel.b = color_one.b;
			}

			if (asum == amatch2 || (asum == amatch1 && tl.a == color_two.a)) {
				draw = 1;
				pixel.a = color_one.a;
			}

			if (draw) {
				offset = col * 4 + row * 4 * width;
				sizew = (col + scale <= width) ? scale : width - col;
				this.fillSquare(offset, sizew, scale, pixel);
			}

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
			} else {
				col += scale;
			}
			i++;
		}
		this.ctx.putImageData(imageData, 0, 0);
	}

	dither() {

		console.log('TA::dither');

		var id = { data: this.cloneArray(this.imageData.data), width: this.width, height: this.height },
			scale = this.scale,
			sizew,
			i = 0, row = 0, col = 0,
			rsum, gsum, bsum, asum,
			last_col = (Math.ceil(width / scale) * scale - scale),
			last_row = (Math.ceil(height / scale) * scale - scale),
			bp, lp, rp,
			r, b, bl, br,
			pixel, pixel_new,
			dither;

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			bp = (row < last_row) ? row + scale : 0;
			lp = (col > 0) ? col - scale : last_col;
			rp = (col < last_col) ? col + scale : 0;

			r = this.getPixel(id, rp, row, width);
			bl = this.getPixel(id, lp, bp, width);
			b = this.getPixel(id, col, bp, width);
			br = this.getPixel(id, rp, bp, width);

			pixel = this.getPixel(id, col, row, width);
			dither = this.getDithered(pixel);

			console.log('dither', pixel, dither[0]);//, dither[1]);

			pixel_new = dither[0];

			r = this.distributeDither(r, dither[1], 7 / 16);
			bl = this.distributeDither(bl, dither[1], 3 / 16);
			b = this.distributeDither(b, dither[1], 5 / 16);
			br = this.distributeDither(br, dither[1], 1 / 16);

			offset = col * 4 + row * 4 * width;
			sizew = (col + scale <= width) ? scale : width - col;
			this.fillSquare(offset, sizew, scale, pixel_new);

			offset = rp * 4 + row * 4 * width;
			sizew = (rp + scale <= width) ? scale : width - rp;
			this.fillSquare(offset, sizew, scale, r);

			offset = lp * 4 + bp * 4 * width;
			sizew = (lp + scale <= width) ? scale : width - lp;
			this.fillSquare(offset, sizew, scale, bl);

			offset = col * 4 + bp * 4 * width;
			sizew = (col + scale <= width) ? scale : width - col;
			this.fillSquare(offset, sizew, scale, b);

			offset = rp * 4 + bp * 4 * width;
			sizew = (rp + scale <= width) ? scale : width - rp;
			this.fillSquare(offset, sizew, scale, br);

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
			} else {
				col += scale;
			}
			i++;
		}
		this.color_one = this.getDithered(this.color_one);
		this.color_two = this.getDithered(this.color_two);
		this.ctx.putImageData(imageData, 0, 0);

	}

	antialias() {

		console.log('TA::antialias');

		var id = { data: this.cloneArray(this.imageData.data), width: this.width, height: this.height },
			scale = this.scale,
			sizew,
			i = 0, row = 0, col = 0,
			rsum, gsum, bsum, asum,
			last_col = (Math.ceil(width / scale) * scale - scale),
			last_row = (Math.ceil(height / scale) * scale - scale),
			lp, rp, tp, bp,
			l, r, t, b,
			sqr = Math.ceil(scale / 3),
			avgtl, avgt, avgtr, avgl, avgr, avgbl, avgbr,
			pixel, pixel_new,
			dither;

		if (scale < 3) return;

		while (i < Math.ceil(width / scale) * Math.ceil(height / scale)) {

			lp = (col > 0) ? col - scale : last_col;
			rp = (col < last_col) ? col + scale : 0;
			tp = (row > 0) ? row - scale : last_row;
			bp = (row < last_row) ? row + scale : 0;

			l = this.getPixel(id, lp, row, width);
			r = this.getPixel(id, rp, row, width);
			t = this.getPixel(id, col, tp, width);
			b = this.getPixel(id, col, bp, width);

			pixel = this.getPixel(id, col + sqr, row + sqr, width);

			// top left
			avgtl = this.getAverage([l, t, pixel]);
			offset = col * 4 + row * 4 * width;
			sizew = (col + sqr <= width) ? sqr : width - (col + sqr);
			this.fillSquare(offset, sizew, sqr, avgtl);

			// top
			avgt = this.getAverage([t, pixel]);
			offset = (col + sqr) * 4 + row * 4 * width;
			sizew = ((col + scale - sqr - sqr) <= width) ? (scale - sqr - sqr) : width - (col + scale - sqr - sqr);
			this.fillSquare(offset, sizew, sqr, avgt);

			// top right
			avgtr = this.getAverage([r, t, pixel]);
			offset = (col + scale - sqr) * 4 + row * 4 * width;
			sizew = (col + scale <= width) ? sqr : width - (col + scale);
			this.fillSquare(offset, sizew, sqr, avgtr);

			// left
			avgl = this.getAverage([l, pixel]);
			offset = col * 4 + (row + sqr) * 4 * width;
			sizew = (col + sqr <= width) ? sqr : width - (col + sqr);
			this.fillSquare(offset, sizew, scale - sqr - sqr, avgl);

			// right
			avgr = this.getAverage([r, pixel]);
			offset = (col + scale - sqr) * 4 + (row + sqr) * 4 * width;
			sizew = (col + sqr <= width) ? sqr : width - (col + scale);
			this.fillSquare(offset, sizew, scale - sqr - sqr, avgr);

			// bottom left
			avgbl = this.getAverage([l, b, pixel]);
			offset = col * 4 + (row + scale - sqr) * 4 * width;
			sizew = (col + sqr <= width) ? sqr : width - (col + sqr);
			this.fillSquare(offset, sizew, sqr, avgbl);

			// bottom
			avgb = this.getAverage([b, pixel]);
			offset = (col + sqr) * 4 + (row + scale - sqr) * 4 * width;
			sizew = ((col + scale - sqr - sqr) <= width) ? (scale - sqr - sqr) : width - (col + scale - sqr - sqr);
			this.fillSquare(offset, sizew, sqr, avgb);

			// bottom right
			avgbr = this.getAverage([r, b, pixel]);
			offset = (col + scale - sqr) * 4 + (row + scale - sqr) * 4 * width;
			sizew = (col + sqr <= width) ? sqr : width - (col + scale);
			this.fillSquare(offset, sizew, sqr, avgbr);

			if (col > width - 1 - scale) {
				col = 0;
				row += scale;
			} else {
				col += scale;
			}
			i++;
		}
		this.ctx.putImageData(imageData, 0, 0);

	}

	getAverage(pixels) {
		var i = 0,
			count = pixels.length,
			sumr = 0, sumg = 0, sumb = 0, suma = 0;
		for (i = 0; i < count; i++) {
			sumr += pixels[i].r;
			sumg += pixels[i].g;
			sumb += pixels[i].b;
			suma += pixels[i].a;
		}
		return {
			r: Math.round(sumr / count),
			g: Math.round(sumg / count),
			b: Math.round(sumb / count),
			a: Math.round(suma / count)
		}
	}

	getDithered(p) {
		var div = 10,
			palette = Array.apply(null, Array(div)).map(function (_, i) { return Math.round(((i + 1) / div) * 255); }),
			r = palette[Math.floor((p.r / 255) * (div - 1))],
			g = palette[Math.floor((p.g / 255) * (div - 1))],
			b = palette[Math.floor((p.b / 255) * (div - 1))],
			a = palette[Math.floor((p.a / 255) * (div - 1))];
		return [
			{ r: r, g: g, b: b, a: a },
			{ r: p.r - r, g: p.g - g, b: p.b - b, a: p.a - a }
		];
	}

	distributeDither(p, dither, mult) {
		return {
			r: p.r + dither.r * mult,
			g: p.g + dither.g * mult,
			b: p.b + dither.b * mult,
			a: p.a + dither.a * mult
		}
	}

	countInArray(arr, needle) {
		var i = 0, count = 0;
		for (i = 0; i < arr.length; i++) {
			if (arr[i] == needle) count++;
		}
		return count;
	}

	cloneArray(arr) {
		var clone = new Array(), i;
		for (i = 0; i < arr.length; i++) {
			clone.push(arr[i]);
		}
		return clone;
	}

	getPixelTotal(imageData, x, y) {
		var r, g, b, a, offset = x * 4 + y * 4 * imageData.width;
		r = imageData.data[offset];
		g = imageData.data[offset + 1];
		b = imageData.data[offset + 2];
		a = imageData.data[offset + 3];
		return r + g + b;
	}

	getPixel(imageData, x, y) {
		var r, g, b, a, offset = x * 4 + y * 4 * imageData.width;
		r = imageData.data[offset];
		g = imageData.data[offset + 1];
		b = imageData.data[offset + 2];
		a = imageData.data[offset + 3];
		return { r: r, g: g, b: b, a: a };
	}

	fillSquare(orig, sizew, sizeh, rgba) {
		const { width, imageData } = this;
		var i, j, offset;
		for (i = 0; i < sizeh; i++) {
			for (j = 0; j < sizew; j++) {
				offset = orig + width * 4 * i + 4 * j;
				imageData.data[offset + 0] = rgba.r;
				imageData.data[offset + 1] = rgba.g;
				imageData.data[offset + 2] = rgba.b;
				imageData.data[offset + 3] = rgba.a;
			}
		}

	}

	startLoop() {

		const _self = this;

		let lastRender = Date.now();
		let iteration;

		if (this.type == '1' || this.type == '1RGBA') {
			iteration = this.iterate1;
		} else if (this.type == '4A' || this.type == '4ARGBA') {
			iteration = this.iterate4A;
		} else if (this.type == 'B3S23' || this.type == 'B3S23RGBA') {
			iteration = this.iterateLife;
		} else if (this.type == '30' || this.type == '30RGBA') {
			iteration = this.iterate30;
		} else if (this.type == '90' || this.type == '90RGBA') {
			iteration = this.iterate90;
		} else if (this.type == '110' || this.type == '110RGBA') {
			iteration = this.iterate110;
		}

		function drawFrame() {
			_self.animeID = window.requestAnimationFrame(drawFrame, _self.canvas);
			const now = Date.now();
			const elapsed = now - lastRender;
			if (elapsed >= _self.rate) {
				lastRender = now - (elapsed % _self.rate);
				iteration.apply(_self);
			}
		};

		this.animeID = window.requestAnimationFrame(drawFrame, this.canvas);

		//$(window).trigger('loopStarted');
	}

	stopLoop() {
		window.cancelAnimationFrame(this.animeID);
		this.animeID = null;
		//$(window).trigger('loopStopped');
	}

	///////////////////////////////////////////////////////
	// public methods
	///////////////////////////////////////////////////////

	setTAType(type) {
		this.type = type;
		this.stopLoop();
		this.initLattice();
	}

	restart() {
		if (this.animeID) {
			this.stopLoop();
			this.initLattice();
			this.startLoop();
		} else {
			this.initLattice();
		}
	}

	stop() {
		if (this.animeID) {
			this.stopLoop();
		}
	}

	play() {
		if (this.animeID) {
			this.stopLoop();
		}
		this.initLattice();
		this.startLoop();
	}

	toggleLoop() {
		if (this.animeID) {
			this.stopLoop();
		} else {
			this.startLoop();
		}
	}

	setScale(scale) {
		//console.log('TA::setScale \t: ' + scale);
		//if (scale < this.scale || !this.animeID) {
		this.stopLoop();
		this.scale = scale;
		this.initLattice();
		//} else {
		//	this.scale = scale;
		//}
	}

	setSeeds(seeds) {
		this.seeds = seeds;
		this.stopLoop();
		this.initLattice();
	}

	setColors(c1, c2) {

		//console.log('setColors', c1, c2);

		if (this.animeID) {
			this.stopLoop();
			this.implementColors(c1, c2);
			this.startLoop();
		} else {
			this.implementColors(c1, c2);
		}
		this.color_one = c1;
		this.color_two = c2;
	}

	setFPS(fps) {
		this.fps = fps;
		this.rate = 1000 / fps;
	}

	setLattice(lattice) {
		this.stopLoop();
		this.lattice = lattice;
		this.initLattice();
	}
}