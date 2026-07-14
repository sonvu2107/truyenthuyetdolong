<?php
ob_start();
session_start();
// AHTL_GLOBAL_CBP_CACHE_20260714bagui2
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');
header('Expires: Thu, 01 Jan 1970 00:00:00 GMT');

include('SPDef.php');

$v=$_SESSION['FLVars'];
$sn=$_SESSION['GameServerName'];
$pay_url=$_SESSION['PayURL'];
$gameFrameURL=GAMEAPPURL.(strpos(GAMEAPPURL, '?') === false ? '?' : '&').'ahtlcache=20260714bagui2gf';
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
	$plainFlashVars['ver']='20260714bagui2';
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
<script type="text/javascript" src="static/common.js?v=20260713flashdetect1"></script>
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
	if (isNaN(parseFloat(flashVer)) || parseFloat(flashVer) < 10) {
		traceClient("djrm_low_flash", "flashVer="+flashVer);
		$('down_flash').style.display='block';
		document.getElementById('flash_down_a').setAttribute('href', flashDown());
		return;
	}
	resize();
	traceClient("djrm_before_embed", "hasSwfobject="+(typeof swfobject));
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
