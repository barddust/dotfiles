// ==UserScript==
// @name        Duckduckgo custom CSS
// @description Custom CSS for duckduckgo
// @match       https://duckduckgo.com/?*
// @run-at      document-end
// ==/UserScript==

(function () {
	'use strict';

	const style = document.createElement('style');
	document.body.appendChild(style);
	style.innerHTML = `
/* REF: https://github.com/sumadoratyper/userstyles/blob/master/multicol-ddg.css*/

    #react-layout > div > div > div {
        margin: 0 auto;
        max-width: 900px;
    }

    #react-layout > div > div > div > div {
        display: block;
    }

    #react-layout > div > div > div > div > section:nth-child(2) {
        display: none;
    }

    #react-layout > div > div > div > div > section:nth-child(1) {
        max-width: 1920px;
    }

    #react-layout ol.react-results--main {
        display: flex;
        flex-wrap: wrap;
        column-gap: 1em;
    }

    #react-layout ol.react-results--main > li {
        flex-basis: 50%; 
        max-width: 45%;
        margin: 0 auto;
        margin-bottom: 2em;
        border: 1pt solid;
        border-color: #ff79c6;
        padding: 1em;
    }

    #react-layout ol.react-results--main > li > article > div:nth-child(4) {
        display: none;
    };
`;

})();
