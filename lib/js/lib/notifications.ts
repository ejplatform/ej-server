import $ = require('jquery');


/**
 * Notify user with message.
 *
 * Must provide the title and the message body.
 */
export function notify(title, message, options = {}) {
    options = {icon: '/static/img/logo/logo.svg', body: message, ...options};
    return new Notification(title, options);
}


/**
 * Display a standard toast.
 */
export function toast(title, message, icon, callback?) {
    let html, $toast = $('#toast');
    title = `<h1>${title}</h1>`;
    message = message ? '' : `<p>${message}`;
    html = `<i class="toast"><i class="toast__icon ${icon}"></i><div class="toast__content">${title + message}</div></div>`
    $toast[0] ? $toast.html(html) : $('body').append(html);
    callback ? callback() : null;
}

/**
 * Initializes the notification sub-system.
 */
export function initializeNotifications(callback?) {
    Notification.requestPermission().then(status => {
        window.localStorage.setItem('notification', status);
        callback ? callback(status) : null;
    })
}
