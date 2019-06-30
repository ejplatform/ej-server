import $ = require('jquery');
import unpoly = require('unpoly');
import jsCookies = require('js-cookie');

window['jQuery'] = $;
window['$'] = $;
window['Cookies'] = jsCookies;
export let up = unpoly.version == '0.60.0' ? unpoly : window['up'];
export let Cookies = jsCookies;
up.log.disable();
