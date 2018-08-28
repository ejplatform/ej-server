import 'unpoly.js';

let unpolyComponentRegistry = {};

/**
 * Register constructor function for the component. The HTML element is passed
 * as the single argument of the constructor.
 */
function registerComponent(constructor, name, force = false) {
    if (typeof constructor !== 'function') {
        throw "Component constructor must be a function!";
    }
    if (unpolyComponentRegistry.hasOwnProperty(name) && !force) {
        throw "Component already registered: " + name;
    }
    unpolyComponentRegistry[name] = constructor;
}

/**
 * Decorator used to register a new unpoly component in the component system.
 */
function component(name, force) {
    return (func) => {
        registerComponent(func, name, force);
        return func;
    }
}


/*
 COMPONENTS
 *****************************************************************************/

@component('drop-down')
function dropDown(elem) {
    // pass
}


/*
 UNPOLY COMPILER
 *****************************************************************************/
up.compiler('[up-component]', function ($elem) {
    $elem.forEach((elem) => {
        let name = elem.getAttribute('up-component');
        let constructor = unpolyComponentRegistry[name];
        constructor(elem);
    });
});
