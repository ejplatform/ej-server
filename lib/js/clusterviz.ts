import {Raster, setup, view} from "paper"
import {ForceLayout} from "./clusterviz/force";
import {initSvg} from "./clusterviz/shape";


//
// INITIALIZATION
//
export function initializeForceLayout(elem = "#canvas", data = null) {
    // Setup canvas
    const canvas: HTMLCanvasElement = document.querySelector(elem) as HTMLCanvasElement;
    setup(canvas);

    // Svg symbol
    initSvg(new Raster());

    // Init simulation
    let layout = ForceLayout.fromJSON(data);
    view.onFrame = (ev) => layout.update(Math.min(ev.delta, 0.032));
}


window['initializeForceLayout'] = initializeForceLayout;
