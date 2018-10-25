// @flow
import 'unpoly';


/*
 UNPOLY INTERFACE
 *****************************************************************************/
up.compiler('[up-component]', function ($elem) {
    // $elem.forEach((elem) => {
    //     let name = elem.getAttribute('up-component');
    //     let constructor = unpolyComponentRegistry[name];
    //     constructor(elem);
    // });
});


up.compiler('[is-component]', function ($elem) {
    console.log($elem);
    // $elem.forEach((elem) => {
    //     console.log('COMPONENT');
    //     console.log(elem);
    //     let name = elem.getAttribute('up-component');
    //     let constructor = unpolyComponentRegistry[name];
    //     constructor(elem);
    // });
});

console.log('Loaded all unpoly compilers');


/*
 DECORATOR
 *****************************************************************************/

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

component('CollapsibleList', elem => {
    console.log(elem);
});


/*
 LEGACY COMPONENTS
 *****************************************************************************/
up.compiler('.CollapsibleList', $elem => {
    $elem.toggleClass('CollapsibleList--hidden');
    $elem.click(e => {
        $(e).toggleClass('CollapsibleList--hidden')
    });
});
