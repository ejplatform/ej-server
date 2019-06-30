"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DEBUG = true;
exports.DEVELOPMENT = exports.DEBUG;
/**
 * Prints a warning in production via console.log() and throws an error in
 * development;
 */
function warn() {
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    if (exports.DEVELOPMENT) {
        var msg = args.join(', ');
        throw "[error] " + msg;
    }
    else {
        console.log.apply(console, ['[warning]'].concat(args));
    }
}
exports.warn = warn;
/**
 * Prints a message when in debug mode;
 */
function debug() {
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    exports.DEBUG ? console.log.apply(console, ['[debug] '].concat(args)) : null;
}
exports.debug = debug;
//==============================================================================
// STRING FUNCTIONS
//==============================================================================
/**
 * Convert camelCase to dash-case.
 */
function camelCaseToDash(myStr) {
    return myStr.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
}
exports.camelCaseToDash = camelCaseToDash;
