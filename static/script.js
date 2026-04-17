// Wartelisten-Kontaktverwaltung – Minimales JavaScript

// Flash-Nachrichten nach 4 Sekunden automatisch ausblenden
document.addEventListener('DOMContentLoaded', function () {
    var flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            msg.style.transition = 'opacity 0.5s';
            msg.style.opacity = '0';
            setTimeout(function () { msg.remove(); }, 500);
        }, 4000);
    });
});
