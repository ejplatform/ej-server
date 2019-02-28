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
var PageMenu = /** @class */ (function (_super) {
    __extends(PageMenu, _super);
    function PageMenu() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.attributes = { 'is-open': true };
        return _this;
    }
    PageMenu.prototype.register = function () {
        var _this = this;
        this.on('click', ".collapsible__title", function () {
            _this.element.toggleAttribute('is-collapsed');
        });
        console.log('registered!');
    };
    PageMenu = __decorate([
        base_1.component
    ], PageMenu);
    return PageMenu;
}(base_1.Component));
var MainHeader = /** @class */ (function (_super) {
    __extends(MainHeader, _super);
    function MainHeader() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    MainHeader = __decorate([
        base_1.component
    ], MainHeader);
    return MainHeader;
}(base_1.Component));
