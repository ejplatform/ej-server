import {up} from '../dependencies';
import {camelCaseToDash, debug, warn} from '../utils';

//==============================================================================
// UNPOLY INTERFACE
//------------------------------------------------------------------------------

let componentRegistry = {};
let hooksRegistry = {};

/**
 * Components derive from the Component class and are objects that define hooks
 * to many sub-elements using the is-element hook or some other type of
 * method.
 */
up.compiler('[is-component]', function (elem) {
    let name = elem.getAttribute('is-component');
    name = name ? name : elem.classList[0];
    let componentClass = componentRegistry[name];

    if (componentClass === undefined) {
        return warn(`Component not found: ${name}`);
    }
    let component = elem.component = new componentClass(elem);
    component.register();
    debug(`Component initialized: ${name}`);
});

/**
 * Hooks are very simple functional components that simply bind themselves to
 * some Javascript function.
 *
 * This compiler looks for the function in the hooks registry and then calls
 * it with the component element.
 */
up.compiler('[is-hook]', function (elem: Element) {
    let name = elem.getAttribute('is-hook'),
        hook = hooksRegistry[name];

    if (hook === undefined) {
        return warn(`Hook not found: ${name}`);
    }
    hook(elem);
    debug(`Hook initialized: ${name}`);
});


//==============================================================================
// DECORATORS
//------------------------------------------------------------------------------

/**
 * Decorator that register hook on registry.
 * @param {string} name - Unique name for hook.
 */
function hook(name: string) {
    return (func: Function) => {
        if (hooksRegistry.hasOwnProperty(name)) {
            warn(`Hook already exists: ${name}. Overloading.`)
        }
        debug(`Registering hook: ${name}`);
        hooksRegistry[name] = func;
    };
}

/**
 * Register hook to execute function when object is clicked.
 */
hook.on = (event, name) => {
    return func => {
        return hook(name)(
            function eventHook(elem: Element) {
                elem.addEventListener(event, func.bind(elem));
            });
    }
};

/**
 * Register hook to execute function when object is clicked.
 */
hook.click = (name) => hook.on('click', name);
hook.load = (name) => hook.on('load', name);

/**
 * Register a component class.
 */
export function component(cls) {
    if (componentRegistry.hasOwnProperty(cls.name)) {
        warn(`Component already registered: ${cls.name}`);
    }
    debug(`Registering component: ${cls.name}`);
    componentRegistry[cls.name] = cls;
    componentRegistry[camelCaseToDash(cls.name)] = cls;
    return cls;
}


//==============================================================================
// COMPONENT CLASS
//------------------------------------------------------------------------------

/**
 * Base class for all components.
 */
export class Component {
    attributes: Object = {};
    element: Element;

    constructor(elem: Element) {
        this.element = elem;

        // Set attributes to default values
        for (let attr in this.attributes) {
            console.log('attr', attr);
            if (!elem.hasAttribute(attr)) {
                elem.setAttribute(attr, this.attributes[attr]);
            }
        }
    }

    register() {
        this.element.querySelectorAll('[is-element]').forEach(elem => {
            let name = elem.getAttribute('is-element');
            console.log("Elem:" + elem + name);
        });
    }

    // jQuery-like selectors and API
    /** Call .querySelector() on element */
    $(selector?: string) {
        if (selector === undefined) {
            return $(this.element);
        }
        return $(selector, this.element);
    }


    /** Register event listener on sub-elements */
    on(event: string, ...args) {
        switch (args.length) {
            case 2: {
                let [selector, callback] = args;
                this.$(selector).on(event, callback);
                break;
            }
            case 1: {
                let [callback] = args;
                this.$().on(event, callback);
                break;
            }
            default: {
                throw "Expect have 2 or 3 arguments";
            }
        }
    }
}

