// add to end of slack.app/Contents/Resources/app.asar.unpacked/src/static/ssb-interop.js

document.addEventListener('DOMContentLoaded', function() {
 $.ajax({
   // url: 'https://cdn.rawgit.com/laCour/slack-night-mode/master/css/raw/black.css',
   url: 'https://gist.githubusercontent.com/danhcole/9d10a4ce4a630446c87cded327e82409/raw/85b41f47ccd97ed0ebe32d1a1aa68734dfb6bd66/black.css',
   success: function(css) {
     let overrides = `
     code { background-color: #535353; color: #85c5ff; } /* Change color: to whatever font color you want */
     .c-mrkdwn__pre, .c-mrkdwn__quote { background: #535353 !important; background-color: #535353 !important; }
     `
     $("<style></style>").appendTo('head').html(css + overrides);
   }
 });
});
