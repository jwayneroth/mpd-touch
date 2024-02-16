export default class Light {
	constructor(x, y, z, brightness) {
		this.x = (x === undefined) ? -100 : x;
		this.y = (y === undefined) ? -100 : y;
		this.z = (z === undefined) ? -100 : z;
		this.brightness = (brightness === undefined) ? 1 : brightness;
	}

	setBrightness(b) {
		this.brightness = Math.min(Math.max(b, 0), 1);
	}
}
