"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var $ = require("jquery");
var unpoly = require("unpoly");
window['jQuery'] = $;
window['$'] = $;
exports.up = unpoly.version == '0.60.0' ? unpoly : window['up'];
exports.up.log.disable();
