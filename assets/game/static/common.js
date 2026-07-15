// JavaScript Document
var $ = function(id) {
	return document.getElementById(id);
}

function getQueryParamValue(p) {
	var url = document.URL.toString();
	var tmpStr = p + "=";
	var tmp_reg = eval("/[\?&]" + tmpStr + "/i");
	if (url.search(tmp_reg) == -1)
		return null;
	else {
		var a = url.split(/[\?&]/);
		for ( var i = 0; i < a.length; i++)
			if (a[i].search(eval("/^" + tmpStr + "/i")) != -1)
				return a[i].substring(tmpStr.length);
	}
}

function getParams() {
	var params = new Object();
	var query = document.location.search.substr(1);
	var pairs = query.split("&");
	for ( var i = 0; i < pairs.length; i++) {
		var index = pairs[i].indexOf("=");
		if (index <= 0) {
			continue;
		}
		var paramName = pairs[i].substr(0, index);
		var paramValue = pairs[i].substr(index + 1);
		params[paramName] = paramValue;
	}
	return params;
}

function ClientCallJs(code, x, y) {
	swf = document.getElementById("gameSwf");
	if (swf == undefined) {
		alert("no swf found");
		return;
	}
	swf.ClientCallJs(code);
	// window.external.JsCallClient(1,2)

	// alert(code + " " + x + " " + y);
	// getFlashMovieObject("wushuang").systemRightClick(x,y);//js����flash�еķ���
}

function JsCallClient(code, a, b) {
	try {
		(new Image()).src = "/client_trace.php?step=js_call_client_before&data=" +
			encodeURIComponent("id=" + code + "|aLen=" + String(a || "").length +
			"|bLen=" + String(b || "").length) + "&t=" + (new Date()).getTime();
	} catch (ignoreTraceBefore) {}
	// Một số launcher WebBrowser cũ không công bố JsCallClient qua window.external.
	// Không để callback phụ này làm ExternalInterface dừng toàn bộ quá trình khởi tạo game.
	var result = true;
	try {
		result = window.external.JsCallClient(code, a, b);
		if (result === undefined || result === null) {
			result = true;
		}
	} catch (bridgeError) {
		result = true;
		try {
			(new Image()).src = "/client_trace.php?step=js_call_client_fallback&data=" +
				encodeURIComponent("id=" + code + "|error=" +
					(bridgeError.number || bridgeError.message || "unknown")) +
				"&t=" + (new Date()).getTime();
		} catch (ignoreTraceFallback) {}
	}
	try {
		(new Image()).src = "/client_trace.php?step=js_call_client_after&data=" +
			encodeURIComponent("id=" + code) + "&t=" + (new Date()).getTime();
	} catch (ignoreTraceAfter) {}
	return result;
}

function addBookmark(title, url) {
	if (window.sidebar) {
		window.sidebar.addPanel(title, url, "");
	} else if (document.all) {
		top.external.AddFavorite(url, title);
	} else if (window.opera && window.print) {
		return true;
	}
}

function setValue(o) {

	swf = document.getElementById("gameSwf");
	if (swf == undefined) {
		alert("no swf found");
		return;
	}
	return swf;
}

function thisMovie(movieName) {
	if (navigator.appName.indexOf("Microsoft") != -1) {

		return window[movieName];
	} else {

		return document[movieName];
	}
}

function getFlashMovieObject(movieName) {
	if (window.document[movieName]) {
		return window.document[movieName];
	}
	if (navigator.appName.indexOf("Microsoft") == -1) {
		if (document.embeds && document.embeds[movieName])
			return document.embeds[movieName];
	} else {
		return document.getElementById(movieName);
	}
}

/**
 * 获取flash版本号
 * @returns {String}
 */
function _uFlash() {
	var f = "-", n = navigator, ii, fl, version, parts;
	if (n.plugins && n.plugins.length) {
		for (ii = 0; ii < n.plugins.length; ii++) {
			if (n.plugins[ii].name.indexOf('Shockwave Flash') != -1) {
				// alert(n.plugins[ii].name);
				// alert(n.plugins[ii].description);
				f = n.plugins[ii].description.split('Shockwave Flash ')[1];
				break;
			}
		}
	}
	// Một số máy có navigator.plugins nhưng không liệt kê Flash ActiveX.
	// Khi đó vẫn phải thử COM thay vì kết luận nhầm là chưa cài Flash.
	if (f == "-" && window.ActiveXObject) {
		var progIds = [
			'ShockwaveFlash.ShockwaveFlash',
			'ShockwaveFlash.ShockwaveFlash.11'
		];
		for (ii = 10; ii >= 2; ii--) {
			progIds.push('ShockwaveFlash.ShockwaveFlash.' + ii);
		}
		for (ii = 0; ii < progIds.length; ii++) {
			try {
				fl = new ActiveXObject(progIds[ii]);
				if (fl) {
					try {
						version = fl.GetVariable('$version');
						if (version) {
							parts = version.split(' ')[1].split(',');
							f = parts[0] + '.' + parts[1] + ' r' + parts[2];
						} else {
							f = '10.0';
						}
					} catch (ignoreVersion) {
						f = '10.0';
					}
					break;
				}
			} catch (e) {
			}
		}
	}
	return f;
}

/**
 * 返回flash下载地址
 * @returns {String}
 */
function flashDown() {
	if (window.ActiveXObject) {
		return '/download/lhzs_activx.exe';
	} else {
		return '/download/lhzs_plugin.exe';
	}

}
