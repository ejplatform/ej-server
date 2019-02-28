import {Component, component} from "./base";

@component
class Collapsible extends Component {
    attributes = {'is-collapsed': true};

    register() {
        this.on('click', ".collapsible__title", () => {
            this.element.toggleAttribute('is-collapsed');
        });
    }
}


@component
class Tabs extends Component {
    constructor(element) {
        super(element);
    }

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

            // Setup tabs bar
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
