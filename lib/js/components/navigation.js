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
var MainHeader = /** @class */ (function (_super) {
    __extends(MainHeader, _super);
    function MainHeader(element) {
        var _this = _super.call(this, element) || this;
        _this.isOpen = false;
        return _this;
    }
    MainHeader.prototype.back = function () {
        window.history.back();
    };
    MainHeader.prototype.toggleMenu = function () {
        this.isOpen ? this.closeMenu() : this.openMenu();
    };
    MainHeader.prototype.openMenu = function () {
        var yCoord = $('.main-header').innerHeight();
        $('.page-menu')
            .css('top', yCoord - 4 + "px")
            .attr('is-open', '');
        this.createOverlay();
        this.isOpen = true;
    };
    MainHeader.prototype.closeMenu = function () {
        $('.page-menu').attr('is-open', null);
        this.removeOverlay();
        this.isOpen = false;
    };
    MainHeader.prototype.removeOverlay = function () {
        $('#page-menu-overlay').remove();
    };
    MainHeader.prototype.createOverlay = function () {
        var self = this;
        var overlay = document.createElement('div');
        $(overlay)
            .toggleClass('overlay')
            .attr('id', 'page-menu-overlay')
            .on('click', function () {
            self.removeOverlay();
            self.toggleMenu();
        });
        document.body.appendChild(overlay);
        return overlay;
    };
    MainHeader = __decorate([
        base_1.component
    ], MainHeader);
    return MainHeader;
}(base_1.Component));
var PageMenu = /** @class */ (function (_super) {
    __extends(PageMenu, _super);
    function PageMenu() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.attributes = { 'is-open': true };
        return _this;
    }
    PageMenu.prototype.init = function () {
        this.$().attr('is-menu', '');
        this.isFontLarge = false;
        this.hasContrast = false;
        this.scaleFactor = 1.5;
    };
    // TOGGLE CONTRASTS
    PageMenu.prototype.toggleContrast = function () {
        $('body').toggleClass('hicontrast');
        return false;
    };
    // TOGGLE FONT SIZES
    PageMenu.prototype.toggleFontSize = function () {
        this.isFontLarge ? this.makeFontsRegular() : this.makeFontsLarge();
        return false;
    };
    PageMenu.prototype.makeFontsRegular = function () {
        var _this = this;
        $('*').each(function (_, elem) { return _this.restoreFontSize($(elem)); });
        this.isFontLarge = false;
    };
    PageMenu.prototype.makeFontsLarge = function () {
        var _this = this;
        this.isFontLarge = true;
        var $main = $('html');
        $('body *')
            .map(function (_, elem) { return _this.storeFontSize($(elem)); })
            .map(function (_, $elem) { return _this.scaleFont($elem, _this.scaleFactor); });
        this.storeFontSize($main);
        this.scaleFont($main, (2 * this.scaleFactor + 1) / 3);
    };
    PageMenu.prototype.storeFontSize = function ($elem) {
        $elem.data('original-font-size', {
            size: $elem.css('font-size'),
            hasOwnStyle: $elem[0].style.fontStyle != '',
        });
        return $elem;
    };
    PageMenu.prototype.restoreFontSize = function ($elem) {
        var data = $elem.data('original-font-size');
        if (data === undefined) {
            return;
        }
        else if (data.hasOwnStyle) {
            $elem.css('font-size', data.size);
        }
        else {
            $elem[0].style.fontSize = "";
        }
    };
    PageMenu.prototype.scaleFont = function ($elem, by) {
        var size = parseInt($elem.data('original-font-size').size), newSize = (by * size) | 0;
        if (size) {
            $elem.css('font-size', newSize + "px");
        }
        return $elem;
    };
    PageMenu = __decorate([
        base_1.component
    ], PageMenu);
    return PageMenu;
}(base_1.Component));
