<?php
ob_start();
session_start();
// AHTL_FLASH_DIRECT_ACTIVEX_20260715forcedactivex2
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');
header('Expires: Thu, 01 Jan 1970 00:00:00 GMT');

include('SPDef.php');

$v=$_SESSION['FLVars'];
$sn=$_SESSION['GameServerName'];
$pay_url=$_SESSION['PayURL'];
$gameFrameURL=GAMEAPPURL.(strpos(GAMEAPPURL, '?') === false ? '?' : '&').'ahtlcache=20260714bagui5';
$plainFlashVars=array();
if (!empty($_SESSION['FLVarsPlain']))
{
	$pairs=explode('&', $_SESSION['FLVarsPlain']);
	foreach ($pairs as $pair)
	{
		$pos=strpos($pair, '=');
		if ($pos !== false)
		{
			$key=substr($pair, 0, $pos);
			$value=substr($pair, $pos + 1);
			$plainFlashVars[$key]=$value;
		}
	}
}

// Luôn ưu tiên gói CBP đã Việt hóa và phiên bản mới, kể cả với phiên đăng nhập cũ.
if (count($plainFlashVars) > 0)
{
	$plainFlashVars['cbppack']='1';
	$plainFlashVars['ver']='20260714bagui5';
	$plainFlashVars['nocache']='1';
}

if (!$v || !$sn)
{
	header('location:'.GetLoginUrl());
}

ob_end_flush();
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Truyền Thuyết Đồ Long</title>
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style type="text/css">
*{margin:0; padding:0; overflow:hidden;}
html, body, #GameFrameContainer, #flashContent{width:100%; height:100%;}
body{background:#000;}
a{color:#fff;}
body, div{font-family:Arial, sans-serif; font-size:12px; color:#fff;}
#navBar{text-align:right; padding:2px;}
#down_flash{margin-top:100px;}
</style>
<script type="text/javascript" src="static/common.js?v=20260715launcherbridge2"></script>
<script type="text/javascript" src="static/swfobject.js"></script>
<script type="text/javascript" src="static/rightClick.js"></script>
<script type="text/javascript">
function traceClient(step, data){
	try {
		var img=new Image();
		img.src="/client_trace.php?step="+encodeURIComponent(step)+"&data="+
			encodeURIComponent(data || "")+"&t="+(new Date()).getTime();
	} catch(e) {}
}

function loaded(){
	var flashVer=_uFlash();
	traceClient("djrm_loaded", "flashVer="+flashVer+"|clientH="+document.body.clientHeight);
	resize();
	var flashvars={
<?php
	if (count($plainFlashVars) > 0)
	{
		$i=0;
		$total=count($plainFlashVars);
		foreach ($plainFlashVars as $key => $value)
		{
			++$i;
			echo "\t\t'".addslashes($key)."':'".addslashes($value)."'".($i < $total ? "," : "")."\n";
		}
	}
	else
	{
		echo "\t\tgp:'".addslashes($v)."'\n";
	}
?>
	};
	traceClient("djrm_flashvars_mode", "plain=<?=count($plainFlashVars)?>|gpLen=<?=strlen($v)?>|cbppack=<?=isset($plainFlashVars['cbppack']) ? $plainFlashVars['cbppack'] : 'none'?>|ver=<?=isset($plainFlashVars['ver']) ? $plainFlashVars['ver'] : 'none'?>");
	var params={
		allowScriptAccess:"always",
		allowFullScreen:"true",
		wmode:"opaque"
	};
	var attributes={
		id:"gameSwf",
		name:"gameSwf",
		menu:"false"
	};
	var parsedFlashVer=parseFloat(flashVer);
	var hasDetectedFlash=!isNaN(parsedFlashVer) && parsedFlashVer >= 10;
	var isIeActiveXHost=(typeof swfobject !== "undefined" && swfobject.ua &&
		swfobject.ua.win && (/MSIE|Trident/i.test(navigator.userAgent) ||
		navigator.appName.indexOf("Microsoft") !== -1));

	// WebBrowser/IE của launcher có thể chặn `new ActiveXObject(...)` trong
	// JavaScript dù CLSID Flash vẫn khởi tạo được qua thẻ <object>. Vì vậy với
	// host này phải thử tạo control bằng CLSID trước khi hiện thông báo cài Flash.
	if (!hasDetectedFlash && isIeActiveXHost && typeof swfobject.createSWF === "function") {
		var directFlashVars=[];
		var key;
		for (key in flashvars) {
			if (Object.prototype.hasOwnProperty.call(flashvars, key)) {
				directFlashVars.push(key+"="+flashvars[key]);
			}
		}
		var directAttributes={
			data:"<?=$gameFrameURL?>",
			width:"100%",
			height:"100%",
			id:"gameSwf",
			name:"gameSwf",
			menu:"false"
		};
		var directParams={
			movie:"<?=$gameFrameURL?>",
			allowScriptAccess:params.allowScriptAccess,
			allowFullScreen:params.allowFullScreen,
			wmode:params.wmode,
			flashvars:directFlashVars.join("&")
		};
		traceClient("djrm_direct_activex_try", "flashVer="+flashVer+"|hasCreateSWF=1");
		var directRef=swfobject.createSWF(directAttributes, directParams, "flashContent");
		if (directRef) {
			traceClient("djrm_direct_activex_created", "ref=yes");
			RightClick.init();
			// Host WebBrowser này không hỗ trợ GetVariable trên phần tử <object>.
			// Control đã tạo thành công thì để Flash tiếp tục khởi tạo, không gọi COM chẩn đoán.
			traceClient("djrm_direct_activex_started", "ref=yes");
			return;
		}
		traceClient("djrm_direct_activex_failed", "ref=no");
	}

	if (!hasDetectedFlash) {
		traceClient("djrm_low_flash", "flashVer="+flashVer+"|directTried="+(isIeActiveXHost ? "1" : "0"));
		$('down_flash').style.display='block';
		document.getElementById('flash_down_a').setAttribute('href', flashDown());
		return;
	}

	traceClient("djrm_before_embed", "hasSwfobject="+(typeof swfobject));
	swfobject.embedSWF("<?=$gameFrameURL?>", "flashContent", "100%", "100%", "10.0.0", false, flashvars, params, attributes, function(e){
		traceClient("djrm_embed_callback", "success="+e.success+"|id="+e.id+"|ref="+(e.ref ? "yes" : "no"));
	});
	RightClick.init();
}

function resize(){
	var clientH=document.body.clientHeight;
	var navH=$("navBar").offsetHeight;
	$('GameFrameContainer').style.height=(clientH-navH)+"px";
}

function addBookmark_game(){
	addBookmark("<?=GAMENAME.' - '.$sn?>", "<?=GetFavUrl()?>");
}
</script>
</head>
<body onload="loaded();" onresize="resize();">
<div id="navBar" <? if($_SESSION['client']): ?>style="display:none"<? endif;?>>
	<?=gameTopLinks()?>
</div>
<div style="display:none" id="down_flash">
<center>
<a id="flash_down_a" target="_blank" href="">
<img style="border:0" src="/download/warning.jpg" alt="Vui lòng cài Flash ActiveX để chạy game" /><br />
Vui lòng cài Flash ActiveX để chạy game
</a>
</center>
</div>
<div id="GameFrameContainer"><div id="flashContent"></div></div>
</body>
</html>
