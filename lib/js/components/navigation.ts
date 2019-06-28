import {component, Component} from "./base";
import {cookie} from "../utils";


@component('main-header')
class MainHeader extends Component {
    isOpen: boolean;

    constructor(element) {
        super(element);
        this.isOpen = false;
    }

    back() {
        window.history.back();
    }

    toggleMenu() {
        this.isOpen ? this.closeMenu() : this.openMenu();
    }

    openMenu() {
        let yCoord = $('.main-header').innerHeight();
        $('.page-menu')
            .css('top', `${yCoord - 4}px`)
            .attr('is-open', '');
        this.createOverlay();
        this.isOpen = true;
    }

    closeMenu() {
        $('.page-menu').attr('is-open', null);
        this.removeOverlay();
        this.isOpen = false;
    }

    removeOverlay() {
        $('#page-menu-overlay').remove();
    }

    createOverlay() {
        let self = this;
        let overlay = document.createElement('div');
        $(overlay)
            .toggleClass('overlay')
            .attr('id', 'page-menu-overlay')
            .on('click', () => {
                self.removeOverlay();
                self.toggleMenu();
            });
        document.body.appendChild(overlay);
        return overlay;
    }
}


@component('page-menu')
class PageMenu extends Component {
    attributes = {'is-open': true};
    isFontLarge: boolean;
    hasContrast: boolean;
    scaleFactor: number;

    init() {
        this.$().attr('is-menu', '');
        this.isFontLarge = false;
        this.hasContrast = cookie('hicontrast') == 'true';
        this.scaleFactor = 1.5;
        this.setContrast();
    }

    // TOGGLE MENU
    toggleMenu() {
        $('.main-header')[0]['ej-component'].toggleMenu();
        return false;
    }

    // TOGGLE CONTRASTS
    toggleContrast() {
        this.hasContrast = !this.hasContrast;
        this.setContrast();
        this.toggleMenu();
        return false;
    }

    // TOGGLE FONT SIZES
    toggleFontSize() {
        this.isFontLarge ? this.makeFontsRegular() : this.makeFontsLarge();
        this.toggleMenu();
        return false;
    }

    makeFontsRegular() {
        $('*').each((_, elem) => this.restoreFontSize($(elem)));
        this.isFontLarge = false;
    }

    makeFontsLarge() {
        this.isFontLarge = true;
        let $main = $('html');
        $('body *')
            .map((_, elem) => this.storeFontSize($(elem)))
            .map((_, $elem) => this.scaleFont($elem, this.scaleFactor));
        this.storeFontSize($main);
        this.scaleFont($main, (2 * this.scaleFactor + 1) / 3);
    }

    // noinspection JSMethodCanBeStatic
    storeFontSize($elem) {
        $elem.data('original-font-size', {
            size: $elem.css('font-size'),
            hasOwnStyle: $elem[0].style.fontStyle != '',
        });
        return $elem;
    }

    // noinspection JSMethodCanBeStatic
    restoreFontSize($elem) {
        let data = $elem.data('original-font-size');
        if (data === undefined) {
            return;
        } else if (data.hasOwnStyle) {
            $elem.css('font-size', data.size);
        } else {
            $elem[0].style.fontSize = "";
        }
    }

    // noinspection JSMethodCanBeStatic
    scaleFont($elem, by) {
        let size = parseInt($elem.data('original-font-size').size),
            newSize = (by * size) | 0;
        if (size) {
            $elem.css('font-size', `${newSize}px`)
        }
        return $elem;
    }

    setContrast() {
        let $link = $('#main-css-link'),
            href = $link.attr('href');

        if (this.hasContrast) {
            $link.attr({href: href.replace('main.css', 'hicontrast.css')});
            $link.data({style: 'hicontrast'});
            document.cookie = "hicontrast = true";
        }
        else {
            $link.attr({href: href.replace('hicontrast.css', 'main.css')});
            $link.data({style: 'main'});
            document.cookie = "hicontrast = false";
        }
    }
}
