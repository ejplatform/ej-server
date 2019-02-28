import {component, Component} from "./base";

@component
class PageMenu extends Component {
    attributes = {'is-open': true};

    register() {
        this.on('click', ".collapsible__title", () => {
            this.element.toggleAttribute('is-collapsed');
        });
        console.log('registered!')
    }
}

@component
class MainHeader extends Component {
}
