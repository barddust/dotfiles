// ==UserScript==
// @name        wikipedia custom CSS
// @description Custom CSS for Wikipedia
// @include     https://*.wikipedia.org/wiki/*
// @run-at      document-end
// ==/UserScript==

(function () {
	'use strict';

	const style = document.createElement('style');
	document.body.appendChild(style);
	style.innerHTML = `
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,100..900;1,100..900&display=swap');

body > div.vector-header-container > header > div.vector-header-end,
#content > div.vector-page-toolbar,
#bodyContent > div.vector-body-before-content,
body > div.vector-header-container > header > div.vector-header-start > nav,
#mw-content-text span.mw-editsection{
    display: none;
}

body > div.vector-header-container > header > div.vector-header-start > a {
    margin: 0;
}

body {
    font-family: "Noto Serif", serif;
    font-weight: normal;
}

div.mw-content-container {
    max-width: 860px;
    margin: 0 auto;
    margin-left: max(2em, auto);
}

#mw-content-text {
    font-size: 1.2em;
    text-align: justify;
}
#mw-content-text p {
    line-height: 1.6;
}
a {
    color:inherit;
    text-decoration: underline;
}
.nounderlines a, .IPA a:link, .IPA a:visited {
    font-style: italic;
}
#mw-panel-toc-list > li a.vector-toc-link {
    color: inherit;
    text-decoration: none;
    font-weight: bold;
}

#mw-panel-toc-list > li > ul a.vector-toc-link {
    font-weight: normal;
}`;

})();
