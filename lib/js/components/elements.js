"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
var base_1 = require("./base");
var Collapsible = /** @class */ (function (_super) {
    __extends(Collapsible, _super);
    function Collapsible() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.attributes = { 'is-collapsed': true };
        return _this;
    }
    Collapsible.prototype.register = function () {
        var _this = this;
        this.on('click', ".collapsible__title", function () {
            _this.element.toggleAttribute('is-collapsed');
        });
    };
    Collapsible = __decorate([
        base_1.component
    ], Collapsible);
    return Collapsible;
}(base_1.Component));
var Tabs = /** @class */ (function (_super) {
    __extends(Tabs, _super);
    function Tabs(element) {
        return _super.call(this, element) || this;
    }
    Tabs.prototype.register = function () {
        _super.prototype.register.call(this);
        var $anchors = this.$('> a');
        var $pages = $anchors.map(function (idx, elem) { return $($(elem).attr('href'))[0]; });
        $pages.hide();
        $pages.filter($anchors.filter('[is-selected]').attr('href')).show();
        // Register click handlers for tab anchor elements
        $anchors.on('click', function (ev) {
            var $elem = $(ev.target), href = $elem.attr('href');
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
            var href = document.location.hash;
            $anchors.filter("[href=\"" + href + "\"]").trigger('click');
        }
    };
    Tabs = __decorate([
        base_1.component
    ], Tabs);
    return Tabs;
}(base_1.Component));
