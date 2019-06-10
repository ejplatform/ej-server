function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i)
    }
    return outputArray;
}

function loadVersionBrowser(userAgent) {
    const ua = userAgent;
    let tem, M = userAgent.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
    if (/trident/i.test(M[1])) {
        tem = /\brv[ :]+(\d+)/g.exec(ua) || [];
        return {name: 'IE', version: (tem[1] || '')};
    }
    if (M[1] === 'Chrome') {
        tem = ua.match(/\bOPR\/(\d+)/);
        if (tem != null) {
            return {name: 'Opera', version: tem[1]};
        }
    }
    M = M[2] ? [M[1], M[2]] : [navigator.appName, navigator.appVersion, '-?'];
    if ((tem = ua.match(/version\/(\d+)/i)) != null) {
        M.splice(1, 1, tem[1]);
    }
    return {
        name: M[0],
        version: M[1]
    };
};
const applicationServerKey = "AIzaSyDf2GEdXj1Kn5krFrRYjU_LMfTKVSOafjc";


document.addEventListener('DOMContentLoaded', function () {
    if ('serviceWorker' in navigator) {
        // The service worker has to store in the root of the app
        // http://stackoverflow.com/questions/29874068/navigator-serviceworker-is-never-ready
        const browser = loadVersionBrowser(navigator.userAgent);
        navigator.serviceWorker.register('navigatorPush.service.js?version=1.0.0').then(function (reg) {
            reg.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(applicationServerKey)
            }).then(function (sub) {
                const endpointParts = sub.endpoint.split('/');
                const registration_id = endpointParts[endpointParts.length - 1];
                const data = {
                    'browser': browser.name.toUpperCase(),
                    'p256dh': btoa(String.fromCharCode.apply(null, new Uint8Array(sub.getKey('p256dh')))),
                    'auth': btoa(String.fromCharCode.apply(null, new Uint8Array(sub.getKey('auth')))),
                    'name': 'XXXXX',
                    'registration_id': registration_id
                };
                requestPOSTToServer(data);
            })
        }).catch(function (err) {
            console.log(':^(', err);
        });
    }
});
