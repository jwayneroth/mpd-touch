import Point3d from './point3d';

export default class Light {
	constructor(x, y, z, brightness) {
		this.x = (x === undefined) ? -100 : x;
		this.y = (y === undefined) ? -100 : y;
		this.z = (z === undefined) ? -100 : z;
		this.brightness = (brightness === undefined) ? 1 : brightness;
		this.color = "#ff0000";
		this.lineWidth = 1;
		this.alpha = 1;

		const point = new Point3d(x, y, z);

		point.setVanishingPoint(400, 50);
		point.setCenter(0, 0, 75);
		point.rotateX(0);
		point.rotateY(0);
		point.rotateZ(0);

		this.point = point;
	}

	setBrightness(b) {
		this.brightness = Math.min(Math.max(b, 0), 1);
	}

	draw(context) {
		context.save();
		// context.lineWidth = this.lineWidth;
		context.fillStyle = this.color;
		context.beginPath();
		context.arc(this.point.getScreenX(), this.point.getScreenY(), 20, 0, 2 * Math.PI);
		// context.moveTo(this.pointA.getScreenX(), this.pointA.getScreenY());
		context.closePath();
		context.fill();
		// if (this.lineWidth > 0) {
		// 	context.stroke();
		// }
		context.restore();
	}
}
