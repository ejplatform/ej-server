"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var dependencies_1 = require("../dependencies");
var utils_1 = require("../utils");
//==============================================================================
// UNPOLY INTERFACE
//------------------------------------------------------------------------------
var componentRegistry = {};
var hooksRegistry = {};
/**
 * Components derive from the Component class and are objects that define hooks
 * to many sub-elements using the is-element hook or some other type of
 * method.
 */
dependencies_1.up.compiler('[is-component]', function (elem) {
    var name = elem.getAttribute('is-component');
    name = name ? name : elem.classList[0];
    var componentClass = componentRegistry[name];
    if (componentClass === undefined) {
        return utils_1.warn("Component not found: " + name);
    }
    var component = elem.component = new componentClass(elem);
    component.register();
    utils_1.debug("Component initialized: " + name);
});
/**
 * Hooks are very simple functional components that simply bind themselves to
 * some Javascript function.
 *
 * This compiler looks for the function in the hooks registry and then calls
 * it with the component element.
 */
dependencies_1.up.compiler('[is-hook]', function (elem) {
    var name = elem.getAttribute('is-hook'), hook = hooksRegistry[name];
    if (hook === undefined) {
        return utils_1.warn("Hook not found: " + name);
    }
    hook(elem);
    utils_1.debug("Hook initialized: " + name);
});
//==============================================================================
// DECORATORS
//------------------------------------------------------------------------------
/**
 * Decorator that register hook on registry.
 * @param {string} name - Unique name for hook.
 */
function hook(name) {
    return function (func) {
        if (hooksRegistry.hasOwnProperty(name)) {
            utils_1.warn("Hook already exists: " + name + ". Overloading.");
        }
        utils_1.debug("Registering hook: " + name);
        hooksRegistry[name] = func;
    };
}
/**
 * Register hook to execute function when object is clicked.
 */
hook.on = function (event, name) {
    return function (func) {
        return hook(name)(function eventHook(elem) {
            elem.addEventListener(event, func.bind(elem));
        });
    };
};
/**
 * Register hook to execute function when object is clicked.
 */
hook.click = function (name) { return hook.on('click', name); };
hook.load = function (name) { return hook.on('load', name); };
/**
 * Register a component class.
 */
function component(cls) {
    if (componentRegistry.hasOwnProperty(cls.name)) {
        utils_1.warn("Component already registered: " + cls.name);
    }
    utils_1.debug("Registering component: " + cls.name);
    componentRegistry[cls.name] = cls;
    componentRegistry[utils_1.camelCaseToDash(cls.name)] = cls;
    return cls;
}
exports.component = component;
//==============================================================================
// COMPONENT CLASS
//------------------------------------------------------------------------------
/**
 * Base class for all components.
 */
var Component = /** @class */ (function () {
    function Component(elem) {
        this.attributes = {};
        this.element = elem;
        // Set attributes to default values
        for (var attr in this.attributes) {
            console.log('attr', attr);
            if (!elem.hasAttribute(attr)) {
                elem.setAttribute(attr, this.attributes[attr]);
            }
        }
    }
    Component.prototype.register = function () {
        this.element.querySelectorAll('[is-element]').forEach(function (elem) {
            var name = elem.getAttribute('is-element');
            console.log("Elem:" + elem + name);
        });
    };
    // jQuery-like selectors and API
    /** Call .querySelector() on element */
    Component.prototype.$ = function (selector) {
        if (selector === undefined) {
            return $(this.element);
        }
        return $(selector, this.element);
    };
    /** Register event listener on sub-elements */
    Component.prototype.on = function (event) {
        var args = [];
        for (var _i = 1; _i < arguments.length; _i++) {
            args[_i - 1] = arguments[_i];
        }
        switch (args.length) {
            case 2: {
                var selector = args[0], callback = args[1];
                this.$(selector).on(event, callback);
                break;
            }
            case 1: {
                var callback = args[0];
                this.$().on(event, callback);
                break;
            }
            default: {
                throw "Expect have 2 or 3 arguments";
            }
        }
    };
    return Component;
}());
exports.Component = Component;
