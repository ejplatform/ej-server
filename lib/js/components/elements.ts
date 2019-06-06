import {Component, component} from "./base";


@component('collapsible')
class Collapsible extends Component {
    attributes = {'is-collapsed': true};

    register() {
        let $elem = $(this.element),
            self = this;

        if ($elem.attr('start-expanded') !== null) $elem.attr('is-collapsed', null);
        this.on('click keypress', ":nth-child(1)", (ev) => {
            if (!self.isReturnEvent(ev)) return true;
            self.element.toggleAttribute('is-collapsed');
        });
    }
}


@component('tabs')
class Tabs extends Component {
    register() {
        super.register();
        const $anchors = this.$('> a');
        const $pages = $anchors.map((idx, elem) => $($(elem).attr('href'))[0]);
        $pages.hide();
        $pages.filter($anchors.filter('[is-selected]').attr('href')).show();

        // Register click handlers for tab anchor elements
        $anchors.on('click', (ev) => {
            let $elem = $(ev.target),
                href = $elem.attr('href');

            // // Setup tabs bar
            $anchors.attr('is-selected', null);
            $elem.attr('is-selected', '');

            // Show only the correct page
            $pages.hide();
            $pages.filter(href).show();
            ev.preventDefault();
        });

        // Uses the current link to set the current tab
        if (document.location.hash) {
            let href = document.location.hash;
            $anchors.filter(`[href="${href}"]`).trigger('click');
        }
    }
}


@component('categories')
class Categories extends Tabs {
    leftArrow() {
        this.incrementBy(-1);
    }

    rightArrow() {
        this.incrementBy(1);
    }

    incrementBy(idx: number) {
        let $anchors = this.$('> a'),
            anchorMap = {},
            selected = 0,
            size = 0;

        // Store values of each anchor with the corresponding index.
        $anchors.each((i, e) => {
            anchorMap[i] = e;
            size++;
            if ($(e).attr('is-selected') !== null) {
                selected = i;
            }
        });

        // Click on the corresponding element
        anchorMap[(selected + idx) % size].trigger('click');
    }
}

