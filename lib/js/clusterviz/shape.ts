import {Color, Group, Item, Path, PlacedSymbol, Point, PointText, Raster, setup, Symbol, view} from "paper"


export type JSONShape = {
    size: number,
    name: string,
    intersections: Array<number>,
    highlight?: boolean,
}

/**
 * A shape that represents a dialog balloon with Physical dynamics.
 */
export class Shape {
    // Physics
    angle: number = 0;
    pos: Point = new Point(0, 0);
    vel: Point = new Point(0, 0);
    acc: Point = new Point(0, 0);
    impulse: Point = new Point(0, 0);
    springConstant: number = 15;
    dragConstant: number = 6;
    impulseForce: number = 5000;
    maxVel: number = 700;
    decay: number = 1;
    initialVelocity: number = 200;

    // Superpositions
    size: number;
    radius: number = 50;
    invmass: number;
    mass: number;
    intersections: Array<number>;

    // Rendering
    shape: Group;
    text: PointText;
    counterText: Group;
    strokeColor: Color = color('#00C2D4');
    fillColor: Color = color('#F0FBFC', 0.33);
    fillColorUser: Color = color('#82ebf0', 0.33);
    textColor: Color = color('#052B47', 1);
    highlight: boolean = false;
    name: string = "Group";
    fontSize: number = 12 + view.size.height / 80;
    fontFamily: string = "Raleway";


    constructor({size, intersections, radius = 50, pos = null, vel = null, isUserGroup = false, name = "Group"}) {
        this.size = size;
        this.intersections = intersections.slice();
        this.radius = radius;
        this.mass = (this.radius / 100) ** 2;
        this.invmass = 1 / this.mass;
        this.pos = pos || new Point(
            Math.random() * view.size.width,
            Math.random() * view.size.height);
        this.vel = vel || new Point(
            Math.random() * this.initialVelocity,
            Math.random() * this.initialVelocity);

        // Creates path element
        let dt = 0.03 * Math.PI,
            theta = Math.PI * 0.5,
            cos = Math.cos, sin = Math.sin,
            r = this.radius,
            from = new Point(r * cos(theta + dt), r * sin(theta + dt)),
            to = new Point(r * cos(theta - dt), r * sin(theta - dt)),
            up = new Point(0, -r),
            down = new Point(0, r * 1.25);

        // Creates group
        this.highlight = isUserGroup;
        this.name = name;
        this.shape = new Group({
            children: [
                new Path.Arc({from: from, through: up, to: to}),
                new Path.Line({from: down, to: to}),
                new Path.Line({from: from, to: down}),
            ],
            strokeColor: this.strokeColor,
            strokeWidth: 5,
            strokeCap: 'round',
            fillColor: this.highlight ? this.fillColorUser : this.fillColor,
        });

        // Creates text
        this.text = new PointText(this.pos);
        this.text.justification = 'center';
        this.text.content = name;
        this.text.fontSize = this.fontSize;
        this.text.fontFamily = this.fontFamily;
        this.text.fillColor = this.textColor;

        let counterText = new PointText(origin);
        counterText.justification = 'center';
        counterText.content = this.size.toString();
        counterText.fontSize = this.fontSize;
        counterText.fontFamily = this.fontFamily;
        if (this.highlight) {
            counterText.fontWeight = 'bold';
            this.text.fontWeight = 'bold';
        }

        let personImg = personSvgSymbol.place(origin);
        personImg.scale(this.text.bounds.height / 106);
        personImg.position = new Point(-personImg.bounds.width - 3, -personImg.bounds.width * 0.25);

        this.counterText = new Group({
            children: [counterText, personImg]
        });
    }

    get pointPos() {
        let tol = 1e-10,
            dx = this.text.bounds.width / 2,
            dy = this.text.bounds.height / 2,
            delta = new Point(0, this.radius * 1.25);

        delta = delta.rotate(180 / Math.PI * this.angle, new Point(0, 0));
        let norm = (Math.abs(delta.x) + Math.abs(delta.y) + tol);

        dx *= Math.abs(delta.x) / norm;
        dy *= Math.abs(delta.y) / norm;
        delta = delta.add(new Point(delta.x > 0 ? dx : -dx, delta.y > 0 ? dy : -dy));

        return this.pos.add(delta);
    }

    // Properties
    get isStatic() {
        let tol = 1e-3;
        return (Math.abs(this.vel.x) < tol) && (Math.abs(this.vel.y) < tol);
    }

    /**
     * Apply all impulses and forces accumulated in the acc and impulse
     * accumulators.
     */
    applyForces(dt) {
        // Create force towards the center
        let k = this.springConstant,
            a = this.dragConstant,
            Ix = this.impulse.x,
            Iy = this.impulse.y,
            vx = this.vel.x,
            vy = this.vel.y,
            ax = -k * (this.pos.x - view.size.width / 2) + Ix * this.invmass - a * vx,
            ay = -k * (this.pos.y - view.size.height / 2) + Iy * this.invmass - a * vy;


        // Implicit Euler
        this.acc = this.acc.add(new Point(ax, ay));
        this.vel = this.vel.add(this.acc.multiply(dt));
        if (this.vel.length >= this.maxVel) {
            this.vel = this.vel.multiply(this.maxVel / this.vel.length);
        }
        this.pos = this.pos.add(this.vel.multiply(dt));

        // Reset accelerations and impulses
        this.acc = this.impulse = new Point(0, 0);

        // Update positions
        this.shape.position = this.pos;
        this.text.position = this.pointPos;
        this.counterText.position = this.pos;

        // Force decay
        let decay = 0.99;
        if (this.decay > 0.75) {
            this.decay = 1 - decay * (1 - this.decay);
            this.springConstant *= decay;
            this.impulseForce *= decay;
        }
    }


    /**
     * Compute contact force between two objects a and b.
     *
     * Returns the force applied to a
     */
    interactionImpulse(other: Shape, i: number, j: number) {
        let tol = 2,
            force = this.impulseForce,
            diff = this.pos.subtract(other.pos),
            distance = diff.length,
            maxDistance = this.radius * (1 - this.intersections[j]) + other.radius * (1 - other.intersections[i]) + tol;

        if (distance < maxDistance) {
            force = force * (maxDistance - distance) / maxDistance;
            return diff.multiply(force / distance);
        }
        else {
            return new Point(0, 0);
        }
    }

    rotate(angle) {
        this.angle += angle;
        this.shape.rotate(180 / Math.PI * angle);
    }
}


//
// UTILITY FUNCTIONS AND CONSTANTS
export function initSvg(raster) {
    personSvgSymbol = new Symbol(raster.importSVG(personSvg, {insert: false}));
}

//
function color(hex, alpha = 1.0): Color {
    let color = new Color(hex);
    color.alpha = alpha;
    return color;
}

let origin = new Point(0, 0);
let personSvgSymbol: Symbol = null;
let personSvg: SVGElement = document.createElementNS("http://www.w3.org/2000/svg", "svg");
personSvg.innerHTML = "<defs><style>.cls-1{fill:#052B47;}</style></defs><g><path class=\"cls-1\" d=\"M81.05,53.1H71a29.65,29.65,0,1,0-36.17,0H25.37c-14,0-25.37,8-25.37,38.05V101a81.66,81.66,0,0,0,106.46.29c0-4.09-.07-7.84,0-10.18C106.79,63.14,95.06,53.1,81.05,53.1Z\"/></g>";
personSvg.setAttribute('width', '106');
personSvg.setAttribute('height', '120');
personSvg.setAttribute('viewBox', '0 0 106 120');
