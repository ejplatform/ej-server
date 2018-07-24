// Cluster data
var clusters = {
    shapes: [
        {
            pos: [70, 120],
            rotation: 0,
            intersections: [1.0, 0.0, 0.0, 0.0],
            personCount: 25
        },
        {
            pos: [200, 220],
            rotation: 0,
            intersections: [0.0, 1.0, 0.0, 0.0],
            personCount: 50,
        },
        {
            pos: [300, 100],
            rotation: 0,
            intersections: [0.0, 0.0, 1.0, 0.1],
            personCount: 40,
        },
        {
            pos: [100, 200],
            rotation: 0,
            intersections: [0.0, 0.0, 0.1, 1.0],
            personCount: 25,
        }
    ],
}


/**
 * Simulates a force layout for a given set of elements.
 */
function ForceLayout(data) {
    this.intersections = data.intersections;
    this.time = 0;
    this.dt = 1 / 24;
    this.color = "black";
    this.dumping = 3;
    this.velocityScale = 200;
    this.repulsionForce = 50;
    this.layoutTolerance = 3;
    this.springConstant = 10;
    this.breakAcc = 1000;
    this.shapes = this.makeShapes(data.shapes);
    return this;
}

ForceLayout.prototype = {
    /**
     * Create shapes from input JSON data.
     */
    makeShapes: function (data) {
        var layout = this;

        return data.map(function (item) {
            var element = layout.newElement(item.pos, item.personCount * 2);
            element.vel = randomPoint(layout.velocityScale);
            element.acc = new Point(0, 0);
            element.impulse = new Point(0, 0);
            element.radius = item.personCount * 2 //item.radius;
            element.equilibrium = pt(item.pos);
            element.mass = element.radius * element.radius / 1000;
            element.invmass = 1 / element.mass;
            element.shadows = item.intersections;
            element.omega = 0;
            element.angle = 0;
            element.position = pt(item.pos);
            element.position = new Point(0, 0);
            return element;
        });
    },

    /**
     * Creates a new path element.
     */
    newElement: function (pos, r) {
        // Useful constants
        var dt = 0.03 * Math.PI;
        var theta = Math.PI * 0.5;
        var cos = Math.cos, sin = Math.sin;
        var x = pos[0], y = pos[1];

        // Arc
        var from = [r * cos(theta + dt), r * sin(theta + dt)];
        var to = [r * cos(theta - dt), r * sin(theta - dt)];
        var up = [0, -r];
        var down = [0, r * 1.25];


        // Creates group
        var group = new Group({
            children: [
                new Path.Arc({ from: from, through: up, to: to }),
                new Path.Line({ from: down, to: to }),
                new Path.Line({ from: from, to: down }),
            ],
            strokeColor: 'black',
            strokeWidth: 5,
            strokeCap: 'round',
            fillColor: 'yellow',
        });
        group.fillColor.alpha = 0.25;

        return group;
    },

    /**
     * Force that moves each element to its desired equilibrium position.
     * It includes both a drag term and a spring-like force redirecting it
     * to the equilibrium position.
     */
    layoutAcc: function (obj) {
        // Drag acc
        var speed = obj.vel.length;
        if (speed > 0.5 && false) {
            var acc = obj.vel * (-this.breakAcc / speed);
        }
        else {
            var acc = obj.vel * (-this.dumping);
        }

        //Spring-like forces for adjusting layout target positions
        var deltaPos = obj.position - obj.equilibrium;
        var distance = deltaPos.length;
        if (distance > this.layoutTolerance) {
            acc = acc - deltaPos * this.springConstant;
        }
        return acc
    },


    /**
     * Compute contact force between two objects a and b.
     * 
     * Returns the force applied to a
     */
    contactImpulse: function (i, j, dt) {
        var a = this.shapes[i];
        var b = this.shapes[j];
        var diff = shape.position - other.position;
        var distance = a.radius * (1 - a.shadows[j]) + b.radius * (1 - b.shadows[i]);

        if (diff.length < (distance - this.layoutTolerance)) {
            return diff * (layout.repulsionForce / diff.length);
        }
        else {
            return new Point(0, 0);
        }
    },

    /**
     * Reset force and impulse accumulators
     */
    cleanFrame: function () {
        this.shapes.map(function (shape) {
            shape.acc = new Point(0, 0);
            shape.impulse = new Point(0, 0);
        });
    },

    /**
     * Apply all impulses and forces accumulated in the acc and impulse 
     * accumulators.
     */
    applyForces: function (dt) {
        this.shapes.map(function (shape) {
            var acc = shape.acc + shape.impulse * shape.invmass;

            // Implicit Euler
            shape.vel = shape.vel + acc * dt;
            shape.position = shape.position + shape.vel * dt;

            // Newton
            // shape.position = shape.position + shape.vel * dt + acc * (dt*dt / 2);
            // shape.vel = shape.vel + acc * dt;

        })
    },

    /**
     * Return the angle of rotation that points the balloon far from the other
     * balloons.
     */
    getBestRotation: function (obj) {
        // Compute center of mass
        var mass = 0;
        var cumPos = new Point(0, 0);

        this.shapes.map(function (other) {
            if (obj !== other) {
                mass += other.mass;
                cumPos = cumPos + other.position * other.mass;
            }
        })
        cumPos = cumPos / mass;

        // Unity vector pointing to the center of mass
        var dir = cumPos - obj.position;
        dir = dir / dir.length;

        // Rotation angle
        return Math.atan2(dir.x, -dir.y);
    },

    computeRotations: function () {
        var layout = this;
        var scale = 180 / Math.PI;
        this.shapes.map(function (obj) {
            var angle = layout.getBestRotation(obj);
            obj.rotation = scale * (angle - obj.angle);
            obj.angle = angle;
        })
    },

    /**
     * Update simulation by the given time delta.
     */
    update: function (dt) {
        var shapes = this.shapes;
        this.cleanFrame();

        for (var i = 0; i < shapes.length; i++) {
            // Simple forces
            shape = shapes[i];
            shape.acc = shape.acc + this.layoutAcc(shape);

            // Contact forces
            for (var j = i + 1; j < shapes.length; j++) {
                other = shapes[j];
                var impulse = this.contactImpulse(i, j, dt);

                shape.impulse = shape.impulse + impulse;
                other.impulse = other.impulse - impulse;
            }
        }

        // Evolve simulation with accumulated forces and impulses
        this.applyForces(dt);

        // Recompute orientation
        this.computeRotations();
    }
};


/**
 * Return a random point element with x and y coordinates selected within the
 * range of [-scale, +scale].
 */
function randomPoint(scale) {
    return new Point(2 * scale * (Math.random() - 0.5),
        2 * scale * (Math.random() - 0.5))
}


/**
 * Creates and initializes a new Force layout object.
 */
function startLayout(data) {
    var layout = new ForceLayout(data);
    return layout;
}


/**
 * Convert an [x, y] array to point.
 */
function pt(data) {
    return new Point(data[0], data[1]);
}


/**
 * Executed on every frame.
 */
function onFrame(event) {
    layout.update(Math.min(event.delta, 0.032));
}

var layout = startLayout(clusters);
