import { parseColor } from './utils';

export default class Triangle {
	constructor(a, b, c, color, light) {
		this.pointA = a;
		this.pointB = b;
		this.pointC = c;
		this.color = (color === undefined) ? "#ff0000" : parseColor(color);
		this.lineWidth = 1;
		this.alpha = 1;
		this.light = light;
	}

	draw(context, light) {
		if (this.isBackface()) {
			return;
		}
		context.save();
		context.lineWidth = this.lineWidth;
		context.fillStyle = context.strokeStyle = this.getAdjustedColor(light);
		context.beginPath();
		context.moveTo(this.pointA.getScreenX(), this.pointA.getScreenY());
		context.lineTo(this.pointB.getScreenX(), this.pointB.getScreenY());
		context.lineTo(this.pointC.getScreenX(), this.pointC.getScreenY());
		context.closePath();
		context.fill();
		if (this.lineWidth > 0) {
			context.stroke();
		}
		context.restore();
	}

	getDepth() {
		return Math.min(this.pointA.z, this.pointB.z, this.pointC.z);
	}

	isBackface() {
		var cax = this.pointC.getScreenX() - this.pointA.getScreenX(),
			cay = this.pointC.getScreenY() - this.pointA.getScreenY(),
			bcx = this.pointB.getScreenX() - this.pointC.getScreenX(),
			bcy = this.pointB.getScreenY() - this.pointC.getScreenY();
		return cax * bcy > cay * bcx;
	}

	getAdjustedColor(light) {
		var color = parseColor(this.color, true),
			red = color >> 16,
			green = color >> 8 & 0xff,
			blue = color & 0xff,
			lightFactor = this.getLightFactor(light);
		red *= lightFactor;
		green *= lightFactor;
		blue *= lightFactor;
		return parseColor(red << 16 | green << 8 | blue);
	}

	getLightFactor(light) {
		var ab = {
			x: this.pointA.x - this.pointB.x,
			y: this.pointA.y - this.pointB.y,
			z: this.pointA.z - this.pointB.z
		};
		var bc = {
			x: this.pointB.x - this.pointC.x,
			y: this.pointB.y - this.pointC.y,
			z: this.pointB.z - this.pointC.z
		};
		var norm = {
			x: (ab.y * bc.z) - (ab.z * bc.y),
			y: -((ab.x * bc.z) - (ab.z * bc.x)),
			z: (ab.x * bc.y) - (ab.y * bc.x)
		};
		var dotProd = norm.x * light.x +
			norm.y * light.y +
			norm.z * light.z,
			normMag = Math.sqrt(norm.x * norm.x +
				norm.y * norm.y +
				norm.z * norm.z),
			lightMag = Math.sqrt(light.x * light.x +
				light.y * light.y +
				light.z * light.z);

		return (Math.acos(dotProd / (normMag * lightMag)) / Math.PI) * light.brightness;
	}
}
