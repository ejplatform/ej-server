import {JSONShape, Shape} from "./shape";
import {Color, Group, Item, Path, PlacedSymbol, Point, PointText, Raster, setup, view} from "paper"


type JSONMessage = {
    shapes: Array<JSONShape>,
}

/**
 * Simulates a force layout for a given set of elements.
 */
export class ForceLayout {
    time: number = 0;
    dt: number = 1 / 24;
    shapes: Array<Shape>;
    color: string;

    constructor(shapes: Array<Shape>) {
        this.shapes = shapes;
    }

    get isStatic() {
        for (let shape of this.shapes) {
            if (!shape.isStatic) return false;
        }
        return true;
    }

    /**
     * Initialize Layout from JSON data.
     */
    static fromJSON(data: JSONMessage) {
        let reg = 5,
            nShapes = data.shapes.length,
            unity = new Point(Math.min(view.size.width, view.size.height) * 0.4, 0),
            rotation = Math.random() * 360,
            index = 0,
            totalSize = sum(data.shapes.map(({size}) => size + reg)),
            shapes = data.shapes.map(({size, intersections, name, highlight}) => {
                let radius = Math.sqrt((size + reg) / totalSize) * view.size.width / 4,
                    pos = unity.rotate(rotation + 360 * index / nShapes, new Point(0, 0));
                pos = pos.add(new Point(view.size.width / 2, view.size.height / 2));
                index++;

                return new Shape({
                    size: size,
                    intersections: intersections.map(x => x / size),
                    radius: radius,
                    pos: pos,
                    name: name,
                    isUserGroup: highlight,
                });
            });
        return new ForceLayout(shapes)
    }


    /**
     * Return the angle of angle that points the balloon far from the other
     * balloons.
     */
    getBestRotation(obj: Shape): number {
        // Compute center of mass of remaining objects
        let mass = 0,
            cumPos = new Point(0, 0);

        this.shapes.map(other => {
            if (obj !== other) {
                mass += other.mass;
                cumPos = cumPos.add(other.pos.multiply(other.mass));
            }
        });
        cumPos = cumPos.divide(mass);

        // Unity vector pointing to the center of mass
        let dir = cumPos.subtract(obj.pos);
        dir = dir.divide(dir.length);

        // Rotation angle
        return Math.atan2(dir.x, -dir.y);
    }

    /**
     * Update simulation by the given time delta.
     */
    update(dt) {
        if (this.isStatic) {
            return;
        }

        let layout = this;
        for (let i = 0; i < this.shapes.length; i++) {
            let a = this.shapes[i];
            for (let j = 0; j < this.shapes.length; j++) {
                if (i !== j) {
                    let b = this.shapes[j],
                        impulse = a.interactionImpulse(b, i, j);
                    a.impulse = a.impulse.add(impulse);
                    b.impulse = b.impulse.add(origin.subtract(impulse));
                }
            }
            a.applyForces(dt);
            a.rotate(layout.getBestRotation(a) - a.angle);
        }
    }
}


function sum(lst: Array<number>): number {
    let sum = 0.0;
    lst.forEach(x => {
        sum += x;
    });
    return sum;
}

let origin = new Point(0, 0);
