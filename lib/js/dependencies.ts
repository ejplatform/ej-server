import $ = require('jquery');
import unpoly = require('unpoly');

window['jQuery'] = $;
window['$'] = $;
export let up = unpoly.version == '0.60.0' ? unpoly : window['up'];
up.log.disable();
