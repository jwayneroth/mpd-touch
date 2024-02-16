// import math
// 	from random import randint
// //import pyglet
// from.point3d import Point3D
// 	from .triangle import Triangle
// 	from .light import Light

import { RGBToHex } from './utils';
import Light from './light';
import Triangle from './triangle-light';
import Point3D from './point3d';

const randint = (min, max) => {
	min = Math.ceil(min);
	max = Math.floor(max);
	return Math.floor(Math.random() * (max - min + 1)) + min;
};

const WAVE_COLOR = RGBToHex(randint(0, 255), randint(0, 255), randint(0, 255)); //RGBToHex(150, 200, 252);
const BASE_COLOR = RGBToHex(randint(0, 255), randint(0, 255), randint(0, 255)); //RGBToHex(88, 99, 252);
//BASE_HIGHLIGHT_COLOR = (50, 196, 232)
//BG_COLOR = (50, 10, 41)

const WAVE_RES = 33; // odd number please

const BASE_HEIGHT = 80;
const BASE_WIDTH = 550;
const BASE_DEPTH = 150;

const WAVE_HEIGHT_MIN = 2;
const WAVE_HEIGHT_MAX = 85;

const SIN_FREQ = 1;
const SIN256_NUM_CELLS = 256;
const SIN256_DATA = [-1, 3, 6, 9, 12, 15, 18, 21, 24, 28, 31, 34, 37, 40, 43, 46, 48, 51, 54, 57, 60, 63, 65, 68, 71, 73, 76, 78, 81, 83, 85, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 109, 111, 112, 114, 115, 117, 118, 119, 120, 121, 122, 123, 124, 124, 125, 126, 126, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 126, 126, 125, 124, 124, 123, 122, 121, 120, 119, 118, 117, 115, 114, 112, 111, 109, 108, 106, 104, 102, 100, 98, 96, 94, 92, 90, 88, 85, 83, 81, 78, 76, 73, 71, 68, 65, 63, 60, 57, 54, 51, 48, 46, 43, 40, 37, 34, 31, 28, 24, 21, 18, 15, 12, 9, 6, 3, 0, -4, -7, -10, -13, -16, -19, -22, -25, -29, -32, -35, -38, -41, -44, -47, -49, -52, -55, -58, -61, -64, -66, -69, -72, -74, -77, -79, -82, -84, -86, -89, -91, -93, -95, -97, -99, -101, -103, -105, -107, -109, -110, -112, -113, -115, -116, -118, -119, -120, -121, -122, -123, -124, -125, -125, -126, -127, -127, -128, -128, -128, -128, -128, -128, -128, -128, -128, -128, -128, -127, -127, -126, -125, -125, -124, -123, -122, -121, -120, -119, -118, -116, -115, -113, -112, -110, -109, -107, -105, -103, -101, -99, -97, -95, -93, -91, -89, -86, -84, -82, -79, -77, -74, -72, -69, -66, -64, -61, -58, -55, -52, -49, -47, -44, -41, -38, -35, -32, -29, -25, -22, -19, -16, -13, -10, -7, -4];
//const SAW256_DATA = [-128, -127, -126, -125, -124, -123, -122, -121, -120, -119, -118, -117, -116, -115, -114, -113, -112, -111, -110, -109, -108, -107, -106, -105, -104, -103, -102, -101, -100, -99, -98, -97, -96, -95, -94, -93, -92, -91, -90, -89, -88, -87, -86, -85, -84, -83, -82, -81, -80, -79, -78, -77, -76, -75, -74, -73, -72, -71, -70, -69, -68, -67, -66, -65, -64, -63, -62, -61, -60, -59, -58, -57, -56, -55, -54, -53, -52, -51, -50, -49, -48, -47, -46, -45, -44, -43, -42, -41, -40, -39, -38, -37, -36, -35, -34, -33, -32, -31, -30, -29, -28, -27, -26, -25, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 53, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127];
const WAVE_WIDTH_MIN = 55;
const WAVE_WIDTH_MAX = 105;

const WIRE_FRAME = true;

let sinCount = Math.ceil(SIN256_NUM_CELLS - SIN256_NUM_CELLS / 4, 10);

const BASE_TOP = 135;
const BASE_BOTTOM = BASE_TOP + BASE_HEIGHT;
const BASE_LEFT = 0 - BASE_WIDTH / 2;
const BASE_RIGHT = BASE_WIDTH / 2;
const BASE_FRONT = -50 - BASE_DEPTH / 2;
const BASE_BACK = BASE_DEPTH / 2;

const COLOR_CHANGE_INTERVAL_FRAMES = 1000; //3600;

export default class Wave {
	constructor(window, batch) {

		const self = this;

		self.window = window;
		self.batch = batch;

		self.base_points = [];
		self.base_triangles = [];
		self.wave_points = [];
		self.wave_triangles = [];
		self.face_triangles = [];

		self.fl = 500;
		self.vpX = 400;
		self.vpY = 100;

		self.view_angle_x = 0;
		self.view_angle_y = 0; // - Math.pi / 8
		self.view_angle_z = 0;

		self.curve_alpha = 2; //randint(2, 5);
		self.wave_width = WAVE_WIDTH_MAX;
		self.wave_height = null;
		self.wave_x = null;
		self.wave_vx = null;

		self.cos_y = Math.cos(self.view_angle_y);
		self.sin_y = Math.sin(self.view_angle_y);

		self.base_left_slope = null;
		self.base_left_intercept = null;
		self.base_back_slope = null;
		self.base_back_intercept = null;

		self.light = new Light(-20, -130, -60, 1);

		self.frame_count = 0;

		self.initBase();

		const baseOrigin = {
			x: self.base_points[0].getScreenX(),
			y: self.base_points[0].getScreenY(),
		};

		self.bgRect = {
			x: baseOrigin.x,
			y: baseOrigin.y,
			width: self.base_points[1].getScreenX() - baseOrigin.x,
			height: baseOrigin.y
		};

		self.setWaveHeightAndX(SIN256_DATA[sinCount]);

		self.initWave();

		self.renderBase()

		self.computeWave()

		// console.log(self.base_points);
		// console.log(self.base_triangles);
		// console.log(self.wave_points);

		self.renderWave()
	}

	/**
	 loopDisplay
	 */
	loopDisplay() {

		const self = this;

		// self.vpX++;
		// self.vpY++;

		if (self.computeWave()) {

			// console.log('loopDisplay::computed');

			self.frame_count = self.frame_count + 1;

			if (self.frame_count >= COLOR_CHANGE_INTERVAL_FRAMES) {
				self.frame_count = 0;
				self.doColorChange();
			}
			//tft.fillScreen(BG_COLOR)
			//checkTestUI()

			self.eraseWave();

			self.renderBase();

			self.renderWave();

		}
	}

	/**
	 * initBase
	 */
	initBase() {
		const self = this;

		self.base_points[0] = new Point3D(BASE_LEFT, BASE_TOP, BASE_FRONT, self.fl);
		self.base_points[1] = new Point3D(BASE_RIGHT, BASE_TOP, BASE_FRONT, self.fl);
		self.base_points[2] = new Point3D(BASE_RIGHT, BASE_BOTTOM, BASE_FRONT, self.fl);
		self.base_points[3] = new Point3D(BASE_LEFT, BASE_BOTTOM, BASE_FRONT, self.fl);
		self.base_points[4] = new Point3D(BASE_LEFT, BASE_TOP, BASE_BACK, self.fl);
		self.base_points[5] = new Point3D(BASE_RIGHT, BASE_TOP, BASE_BACK, self.fl);
		self.base_points[6] = new Point3D(BASE_RIGHT, BASE_BOTTOM, BASE_BACK, self.fl);
		self.base_points[7] = new Point3D(BASE_LEFT, BASE_BOTTOM, BASE_BACK, self.fl);

		let i, point;
		for (i = 0; i < self.base_points.length; i++) {
			point = self.base_points[i];

			point.setVanishingPoint(self.vpX, self.vpY);
			point.setCenter(0, 0, BASE_DEPTH / 2);
			point.rotateX(self.view_angle_x);
			point.rotateY(self.view_angle_y);
			point.rotateZ(self.view_angle_z);

			self.base_triangles[0] = new Triangle(self.base_points[0], self.base_points[1], self.base_points[3], BASE_COLOR, self.light);
			self.base_triangles[1] = new Triangle(self.base_points[1], self.base_points[2], self.base_points[3], BASE_COLOR, self.light);
			self.base_triangles[2] = new Triangle(self.base_points[4], self.base_points[5], self.base_points[0], WAVE_COLOR, self.light);
			self.base_triangles[3] = new Triangle(self.base_points[5], self.base_points[1], self.base_points[0], WAVE_COLOR, self.light);
			self.base_triangles[4] = new Triangle(self.base_points[1], self.base_points[5], self.base_points[2], BASE_COLOR, self.light);
			self.base_triangles[5] = new Triangle(self.base_points[5], self.base_points[6], self.base_points[2], BASE_COLOR, self.light);

			//self.base_left_slope = (self.base_points[0].screenY - self.base_points[4].screenY) / (self.base_points[0].screenX - self.base_points[4].screenX) //(base_lines[13] - base_lines[1]) / (base_lines[12] - base_lines[0])
			//self.base_left_intercept = self.base_left_slope * self.base_points[0].screenX - self.base_points[0].screenY //(base_left_slope * base_lines[0]) + base_lines[1]
			//self.base_back_slope = (self.base_points[5].screenY - self.base_points[4].screenY) / (self.base_points[5].screenX - self.base_points[4].screenX)
			//self.base_back_intercept = self.base_back_slope * self.base_points[5].screenX - self.base_points[5].screenY
		}
	}

	/**
	 renderBase
	 */
	renderBase() {
		const self = this;

		let i, tri;
		for (i = 0; i < self.base_triangles.length; i++) {
			tri = self.base_triangles[i];
			tri.draw(self.window)
		}
	}

	/**
	 initWave
	 */
	initWave() {
		const self = this;

		let i, point, tri;

		for (i = 0; i < WAVE_RES * 2 + 3; i++) {
			self.wave_points.push(new Point3D(0, 0, 0, self.fl));
		}

		// front center bottom point
		self.wave_points[0].x = self.wave_vx;
		self.wave_points[0].y = BASE_BOTTOM;
		self.wave_points[0].z = BASE_FRONT;

		// back center bottom point
		self.wave_points[1].x = self.wave_vx;
		self.wave_points[1].y = BASE_BOTTOM;
		self.wave_points[1].z = BASE_BACK;

		self.setWaveEdge(self.wave_vx);

		// base top left of wave
		//self.wave_points.push();

		for (i = 0; i < self.wave_points.length; i++) {
			point = self.wave_points[i];
			point.setVanishingPoint(self.vpX, self.vpY)
			point.setCenter(0, 0, BASE_DEPTH / 2)
			point.rotateX(self.view_angle_x)
			point.rotateY(self.view_angle_y)
			point.rotateZ(self.view_angle_z)
		}

		// front triangles
		for (i = 0; i < WAVE_RES - 1; i++) {
			tri = new Triangle(
				self.wave_points[0],
				self.wave_points[2 + i],
				self.wave_points[3 + i],
				BASE_COLOR,
				self.light
			);
			//tri.debug = true
			self.face_triangles.push(tri);
		}

		// back triangles
		for (i = 0; i < WAVE_RES - 1; i++) {
			tri = new Triangle(
				self.wave_points[1],
				self.wave_points[WAVE_RES * 2 + 1 - i],
				self.wave_points[WAVE_RES * 2 - i],
				BASE_COLOR,
				self.light
			);
			//tri.debug = true
			self.face_triangles.push(tri);
		}

		// edge triangles
		for (i = 0; i < WAVE_RES; i++) {
			self.wave_triangles.push(new Triangle(
				self.wave_points[2 + i],
				self.wave_points[2 + WAVE_RES + i],
				self.wave_points[3 + i],
				WAVE_COLOR,
				self.light
			));
			self.wave_triangles.push(new Triangle(
				self.wave_points[3 + i],
				self.wave_points[2 + WAVE_RES + i],
				self.wave_points[3 + WAVE_RES + i],
				WAVE_COLOR,
				self.light
			));
		}
		// top
		//self.wave_triangles.push(Triangle(self.wave_points[2 + WAVE_RES - 1], self.wave_points[2 + WAVE_RES * 2 - 1], self.base_points[1], WAVE_COLOR, self.batch))
		//self.wave_triangles.push(Triangle(self.base_points[1], self.wave_points[2 + WAVE_RES * 2 - 1], self.base_points[5], WAVE_COLOR, self.batch))
	}

	/**
	 computeWave
	 */
	computeWave() {
		const self = this;

		const sinVal = self.incrementCounter()

		self.setWaveHeightAndX(sinVal)

		self.wave_points[0].x = self.wave_vx
		self.wave_points[0].y = BASE_BOTTOM - 3
		self.wave_points[0].z = BASE_FRONT

		self.wave_points[1].x = self.wave_vx
		self.wave_points[1].y = BASE_BOTTOM - 3
		self.wave_points[1].z = BASE_BACK

		self.setWaveEdge(self.wave_vx)

		let i, point;
		for (i = 0; i < self.wave_points.length; i++) {
			point = self.wave_points[i];
			point.setVanishingPoint(self.vpX, self.vpY)
			point.setCenter(0, 0, BASE_DEPTH / 2)
			point.rotateX(self.view_angle_x)
			point.rotateY(self.view_angle_y)
			point.rotateZ(self.view_angle_z)
		}

		// for (i = 0; i < self.base_points.length; i++) {
		// 	point = self.base_points[i];
		// 	point.setVanishingPoint(self.vpX, self.vpY)
		// 	point.setCenter(0, 0, BASE_DEPTH / 2)
		// 	point.rotateX(self.view_angle_x)
		// 	point.rotateY(self.view_angle_y)
		// 	point.rotateZ(self.view_angle_z)
		// }

		return 1
	}

	incrementCounter() {
		sinCount = sinCount + SIN_FREQ
		if (sinCount >= SIN256_NUM_CELLS) {
			sinCount = 0;
		}
		return SIN256_DATA[sinCount];
	}

	setWaveHeightAndX(sinVal) {
		const self = this;

		// console.log(`setWaveHeightAndX sin count: ${sinCount} val: ${sinVal}`);

		self.wave_height = rangeMap(sinVal, -127, 127, WAVE_HEIGHT_MAX, WAVE_HEIGHT_MIN)
		self.wave_x = rangeMap(sinVal, 127, -127, BASE_RIGHT - self.wave_width, BASE_LEFT + 2)
		self.wave_vx = self.wave_x + Math.ceil(((self.wave_width / WAVE_RES) * (WAVE_RES / 2)))

		// console.log(`wave height: ${self.wave_height} x: ${self.wave_x} vx: ${self.wave_vx}`);
	}

	setWaveEdge(wave_vx) {
		const self = this;

		let i, inc, px, py, curve_pct;

		for (i = 0; i < WAVE_RES; i++) {

			if (i <= WAVE_RES / 2) {
				inc = (wave_vx - self.wave_x) / ((WAVE_RES - 1) / 2)
				px = Math.ceil(self.wave_x + inc * i)
			} else {
				inc = (self.wave_width - (wave_vx - self.wave_x)) / ((WAVE_RES - 1) / 2)
				px = Math.ceil(wave_vx + inc * (i - ((WAVE_RES - 1) / 2)))
			}
			if (i >= 1 && i <= WAVE_RES - 2) {
				curve_pct = (self.wave_x - px) / (self.wave_x - (self.wave_x + self.wave_width))
				py = Math.ceil(BASE_TOP - Math.pow(4, self.curve_alpha) * Math.pow((curve_pct * (1.00 - curve_pct)), self.curve_alpha) * self.wave_height)
			} else {
				py = BASE_TOP //int(BASE_TOP - (Math.sin((i / (WAVE_RES - 1)) * Math.pi) * self.wave_height))
			}

			// front edge points
			self.wave_points[2 + i].x = px
			self.wave_points[2 + i].y = py
			self.wave_points[2 + i].z = BASE_FRONT
			//back edge points
			self.wave_points[2 + WAVE_RES + i].x = px
			self.wave_points[2 + WAVE_RES + i].y = py
			self.wave_points[2 + WAVE_RES + i].z = BASE_BACK
		}
	}

	eraseWave() {
		const self = this;

		// for (let tri in self.wave_triangles) {
		// 	self.window.fill(0, tri.render)
		// }

		//self.window.clearRect(self.bgRect.x, 0, self.bgRect.width, self.bgRect.height);
	}

	/**
	 renderWave
	 */
	renderWave(firstRun = false) {
		const self = this;

		let i, tri;
		for (i = 0; i < self.wave_triangles.length; i++) {
			tri = self.wave_triangles[i];
			tri.draw(self.window)
		}
		self.renderFace()
	}

	/**
	 renderFace
	 */
	renderFace() {
		const self = this;

		let i, tri;
		for (i = 0; i < self.face_triangles.length; i++) {
			tri = self.face_triangles[i];
			tri.draw(self.window)
		}
	}

	/**
	 doColorChange
	 */
	doColorChange() {
		const self = this;

		const base_color = RGBToHex(randint(0, 255), randint(0, 255), randint(0, 255));
		const wave_color = RGBToHex(randint(0, 255), randint(0, 255), randint(0, 255));

		//console.log(`random base color: ${base_color}`);

		let i, tri;

		for (i = 0; i < self.base_triangles.length; i++) {
			tri = self.base_triangles[i];
			tri.color = base_color
		}
		for (i = 0; i < self.wave_triangles.length; i++) {
			tri = self.wave_triangles[i];
			tri.color = wave_color
		}
		for (i = 0; i < self.face_triangles.length; i++) {
			tri = self.face_triangles[i];
			tri.color = base_color
		}
		self.base_triangles[2].color = wave_color
		self.base_triangles[3].color = wave_color
	}
}
/**
 isBackFace
 */
const isBackFace = function (asx, asy, bsx, bsy, csx, csy) {
	// see http://www.jurjans.lv/flash/shape.html

	cax = csx - asx
	cay = csy - asy

	bcx = bsx - csx
	bcy = bsy - csy

	return cax * bcy > cay * bcx
}

const RGB565CONVERT = function (r, g, b) {
	//long RGB565
	RGB565 = (((r & 0xF8) << 8) | ((g & 0xFC) << 3) | ((b & 0xF8) >> 3))
	return RGB565
}

const RGB888_to_RGB565 = function (rgb) {
	//long RGB565
	RGB565 = (((rgb >> 19) & 0x1f) << 11) | (((rgb >> 10) & 0x3f) << 5) | (((rgb >> 3) & 0x1f))
	return RGB565
}

const getHighlight = function (base_color) {

	r = base_color >> 16
	g = base_color >> 8
	b = base_color
	//wr, wg, wb

	wr = (r * 210) >> 8
	wg = (g * 210) >> 8
	wb = (b * 210) >> 8

	return (wr, wg, wb) //return RGB565CONVERT(wr, wg, wb)
}

const populateWaveColors = function (wave_color) {

	r = wave_color[0] //(wave_color >> 16)
	g = wave_color[1] //(wave_color >> 8)
	b = wave_color[2] //wave_color
	//wr, wg, wb
	//uint16_t wc
	//int i

	for (let i in range(int(WAVE_TRIANGLES_TOTAL / 9))) {

		wr = (r * (255 - i * 15)) >> 8
		wg = (g * (255 - i * 15)) >> 8
		wb = (b * (255 - i * 15)) >> 8

		wc = (abs(wr), abs(wg), abs(wb)) //RGB565CONVERT(wr, wg, wb)

		//print('populateWaveColors %d of %d: %s' % (i, int(WAVE_TRIANGLES_TOTAL / 9), wc))

		wave_colors[i] = wc
	}
}

const rangeMap = function (val, min1, max1, min2, max2) {
	const range1 = max1 - min1
	const range2 = max2 - min2
	const scale = (val - min1) / (range1)
	return min2 + (scale * range2)
}
