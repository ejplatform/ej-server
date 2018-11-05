// Cluster data
var clusters = {
    shapes: [
        {
            id: 1,
            // pos: [450, 280],
            distance: [0, 0, 0],
            // rotation: 0,
            // intersections: [1.0, 0.0, 0.0, 0.0],
            personCount: 80,
            label: 'Grupo 1',
            svg: new Raster('./img/person.svg').scale(0.04)
        },
        {
            id: 2,
            // pos: [200, 280],
            distance: [1, 0, 0.5],
            // rotation: 0,
            // intersections: [0.0, 1.0, 0.0, 0.0],
            personCount: 40,
            label: 'Grupo 2',
            svg: new Raster('./img/person.svg').scale(0.04)
        },
        {
            id: 3,
            pos: [300, 100],
            distance: [1, 0.5, 0],
            // rotation: 0,
            // intersections: [0.0, 0.0, 1.0, 0.1],
            personCount: 20,
            label: 'Grupo 3',
            svg: new Raster('./img/person.svg').scale(0.04)
        },
        // {
        //     pos: [100, 200],
        //     // distance: [],
        //     // rotation: 0,
        //     // intersections: [0.0, 0.0, 0.1, 1.0],
        //     personCount: 35,
        //     label: 'Grupo 4',
        //     svg: new Raster('./img/person.svg').scale(0.04)
        // }
    ],
}


/**
 * Simulates a force layout for a given set of elements.
 */
function ForceLayout(data) {
    // this.intersections = data.intersections;
    // this.time = 0;
    // this.dt = 1 / 24;
    this.color = "black";
    this.dumping = 3;
    this.velocityScale = 20;
    // this.repulsionForce = 50;
    this.layoutTolerance = 3;
    this.springConstant = 10;
    this.breakAcc = 1000;
    shapes = initialShapesPosition(data.shapes);
    console.log('INICIAL', shapes);
    this.shapes = this.makeShapes(shapes);
    return this;
}


initialShapesPosition = function (shapes) {
    newShapes = [];
    initial_y = 280;
    initial_x = 350;
    var dt = 0.3 ;

    shapes.map(function (item, index) {
        newShapes[index] = item;
        if (index == 0) {
            // Define the position of the first group
            newShapes[index].pos = [initial_x, initial_y];
            console.log('INDICE 0:');

        } else if (index == 1) {
            console.log('INDICE 1:', dt   );
            shape_size = 0;
            
            
            distance = newShapes[index].distance[0];

            if( distance > 0.5 ){
                shape_size = newShapes[index].personCount * (2 ) * newShapes[index].distance[0];
                
            } else if(distance < 0.5){
                shape_size = newShapes[index].personCount * (2)  * (newShapes[index].distance[0] - 1);
            } 
            console.log(shape_size);
            console.log(newShapes[0].pos[0] + newShapes[0].personCount * ( 2 + dt ))
            newShapes[index].pos = [newShapes[0].pos[0] + newShapes[0].personCount * ( 2 + dt ) + shape_size, initial_y];
            
        } else {
            console.log('INDICE X:', index   );
        }
    });
    return newShapes;
},

    ForceLayout.prototype = {
        /**
         * Create shapes from input JSON data.
         */
        makeShapes: function (data) {
            var layout = this;

            return data.map(function (item, index) {
                var personCountText = new PointText();
                personCountText.justification = 'center';
                personCountText.content = item.personCount.toString();

                var groupLabel = new PointText();
                groupLabel.justification = 'center';
                groupLabel.content = item.label.toString();

                item.svg.position = new Point(0, 0);
                personCountText.position = new Point(30, 10);
                groupLabel.position = new Point(10, 30);
                var element = layout.newElement(
                    item.personCount * 2);

                element.internalGroup = new Group({
                    children: [
                        personCountText,
                        groupLabel,
                        item.svg
                    ]
                });

                element.groupLabel = groupLabel;
                // console.log('INDICE', index);
                // layout.getElementPosition(index);

                element.vel = randomPoint(layout.velocityScale);
                element.acc = new Point(0, 0);
                // element.impulse = new Point(0, 0);
                element.radius = item.personCount * 2 //item.radius;
                element.equilibrium = pt(item.pos);
                // element.equilibrium = pt(layout.getElementPosition(index));
                element.mass = 1;
                // element.invmass = 1 / element.mass;
                // element.shadows = item.intersections;
                // element.shadows = 0;
                // element.omega = 0;
                element.angle = 0;
                // element.position = view.center;
                // element.position = pt(item.pos);
                // element.position = new Point(0, 0);
                return element;
            });
        },


        /**
         * Creates a new path element.
         */
        newElement: function (radius) {
            // Useful constants
            var dt = 0.03 * Math.PI;
            var theta = Math.PI * 0.5;
            var cos = Math.cos, sin = Math.sin;
            // var x = pos[0], y = pos[1];

            console.log('BLI', radius);

            // Arc
            var from = [radius * cos(theta + dt), radius * sin(theta + dt)];
            var to = [radius * cos(theta - dt), radius * sin(theta - dt)];
            var up = [0, -radius];
            var down = [0, radius * 1.25];


            // Creates group
            var group = new Group({
                children: [
                    new Path.Arc({ from: from, through: up, to: to }),
                    new Path.Line({ from: down, to: to }),
                    new Path.Line({ from: from, to: down }),
                ],
                strokeColor: '#00C2D4',
                strokeWidth: 5,
                strokeCap: 'round',
                fillColor: '#F0FBFC',
                // position: view.center,
            });
            group.fillColor.alpha = 0.5;

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
                console.log('AAAAAAAAAAAAAAAAAAAAAAAA');
                var acc = obj.vel * (-this.breakAcc / speed);
            }
            else {
                // console.log('BBBBBBBBBBBBBBBBBBB');
                var acc = obj.vel * (-this.dumping);
                
            }

            //Spring-like forces for adjusting layout target positions
            var deltaPos = obj.position - obj.equilibrium;
            // console.log(deltaPos);
            // console.log(deltaPos * this.springConstant);
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
        // contactImpulse: function (i, j, dt) {
        //     var a = this.shapes[i];
        //     var b = this.shapes[j];
        //     var diff = shape.position - other.position;
        //     var distance = a.radius * (1 - a.shadows[j]) + b.radius * (1 - b.shadows[i]);

        //     if (diff.length < (distance - this.layoutTolerance)) {
        //         return diff * (layout.repulsionForce / diff.length);
        //     }
        //     else {
        //         return new Point(0, 0);
        //     }
        // },

        /**
         * Reset force and impulse accumulators
         */
        cleanFrame: function () {
            this.shapes.map(function (shape) {
                shape.acc = new Point(0, 0);
                // shape.impulse = new Point(0, 0);
            });
        },

        /**
         * Apply all impulses and forces accumulated in the acc and impulse 
         * accumulators.
         */
        applyForces: function (dt) {
            this.shapes.map(function (shape) {
                // var acc = shape.acc;

                // Implicit Euler
                shape.vel = shape.vel + shape.acc * dt;
                shape.position = shape.position + shape.vel * dt;

                // shape.vel = shape.vel + acc;
                // shape.position = shape.position + shape.vel;

                // Newton
                // shape.position = shape.position + shape.vel * dt + acc * (dt*dt / 2);
                // shape.vel = shape.vel + acc * dt;
                // console.log('Posicao', shape.position);
                // console.log('velocidade:', shape.vel);

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

                //internal elements
                // obj.svg.rotation = -(scale * (angle - obj.angle))
                // obj.personCountText.rotation = -(scale * (angle - obj.angle))
                obj.internalGroup.rotation = -(scale * (angle - obj.angle));
            })
        },

        positionLabels: function () {
            this.shapes.map(function (shape) {
                shape.internalGroup.position = shape.position;
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
                // for (var j = i + 1; j < shapes.length; j++) {
                //     other = shapes[j];
                //     var impulse = this.contactImpulse(i, j, dt);

                //     shape.impulse = shape.impulse + impulse;
                //     other.impulse = other.impulse - impulse;
                // }
            }

            // Evolve simulation with accumulated forces and impulses
            this.applyForces(dt);

            // Recompute orientation
            this.computeRotations();

            this.positionLabels();
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
    console.log(layout.shapes);
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
    // console.log('BLI', event.delta)
    // console.log('BLI', Math.min(event.delta, 0.032))
    // layout.update(Math.min(event.delta, 0.032));
    layout.update(0.017);
}

var layout = startLayout(clusters);

