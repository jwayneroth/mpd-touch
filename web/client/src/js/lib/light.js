import Point3d from './point3d';

export default class Light {
	constructor(x, y, z, brightness) {
		this.x = (x === undefined) ? -100 : x;
		this.y = (y === undefined) ? -100 : y;
		this.z = (z === undefined) ? -100 : z;
		this.brightness = (brightness === undefined) ? 1 : brightness;
		this.color = "#ffffff";
		this.lineWidth = 1;
		this.alpha = 1;

		this.point = new Point3d(x, y, z);
	}

	setPoint(x,y,z) {

		this.x = x;
		this.y = y;
		this.z = z;

		this.point.x = x;
		this.point.y = y;
		this.point.z = z;
	}

	setBrightness(b) {
		this.brightness = Math.min(Math.max(b, 0), 1);
	}

	draw(context) {
		context.save();
		// context.lineWidth = this.lineWidth;
		context.fillStyle = this.color;
		context.beginPath();
		context.arc(this.point.getScreenX(), this.point.getScreenY(), 10, 0, 2 * Math.PI);
		// context.moveTo(this.pointA.getScreenX(), this.pointA.getScreenY());
		context.closePath();
		context.fill();
		// if (this.lineWidth > 0) {
		// 	context.stroke();
		// }
		context.restore();
	}
}
