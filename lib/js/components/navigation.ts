import {component, Component} from "./base";


@component
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


@component
class PageMenu extends Component {
    attributes = {'is-open': true};
    isFontLarge: boolean;
    hasContrast: boolean;
    scaleFactor: number;

    init() {
        this.$().attr('is-menu', '');
        this.isFontLarge = false;
        this.hasContrast = false;
        this.scaleFactor = 1.5;
    }

    // TOGGLE CONTRASTS
    toggleContrast() {
        $('body').toggleClass('hicontrast');
        return false;
    }

    // TOGGLE FONT SIZES
    toggleFontSize() {
        this.isFontLarge ? this.makeFontsRegular() : this.makeFontsLarge();
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

    storeFontSize($elem) {
        $elem.data('original-font-size', {
            size: $elem.css('font-size'),
            hasOwnStyle: $elem[0].style.fontStyle != '',
        });
        return $elem;
    }

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

    scaleFont($elem, by) {
        let size = parseInt($elem.data('original-font-size').size),
            newSize = (by * size) | 0;
        if (size) {
            $elem.css('font-size', `${newSize}px`)
        }
        return $elem;
    }
}
