(function () {
    var elements = $('[up-target][page-role=main]');

    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        element.href = element.href + '?render=main';
    }
}());

