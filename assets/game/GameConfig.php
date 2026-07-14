<?php
ob_start(); //打开缓冲区
session_start();

$LoginUser=$_SESSION['LoginUser'];
$LoginVerify=$_SESSION['LoginVerify'];
$ServerId=$_SESSION['ServerId'];
$SPID=$_SESSION['SPID'];
$PayURL=$_SESSION['PayURL'];
$RepUS=$_SESSION['RepUS'];

if (!$LoginUser || !$ServerId) {
    die('login error session timedout');
}

include('SPDef.php');

$configDoc = simplexml_load_file('GameConfig.xml');
if ( !$configDoc ) die('error load GameConfig');
$nodes = $configDoc->xpath('//Server[@id='.$ServerId.']');
if ( !$nodes )
{
	die('未配置指定的服务器数据');
}
$serverNode = $nodes[0];

//循环取得合并的最终服务器
while ($serverNode['mergedto'] != 0)
{
	$nodes = $configDoc->xpath('//Server[@id='.$serverNode['mergedto'].']');
	if ( !$nodes )
	{
		die('未配置指定的服务器数据');
		break;
	}
	$serverNode = $nodes[0];
}

$_srvAddr=(string)$serverNode['serveraddr'];
$_srvPort=(string)$serverNode['serverport'];
$_srvName=(string)$serverNode['name'];
$_srvId=(string)$serverNode['id'];
$_resSite=(string)$serverNode['ressite'];
$_rankServer=(string)$serverNode['rankserver'];
$_payUrl=str_replace('&', ';', $PayURL);

$gameName = GAMENAME;
$key='differofzjcqha';
$flash_vars="srvaddr=".$_srvAddr."&srvport=".$_srvPort."&srvid=".$_srvId."&spid=".$SPID."&ressite=".$_resSite."&rankurl=".$_rankServer."&payurl=".$_payUrl."&user=".$LoginUser."&spverify=".$LoginVerify."&gameName=".$gameName."&lang=".LANGUAGE."&repus=".$RepUS."&frameRate=48&cbppack=1&ver=20260714bagui1&nocache=1&homeURL=".HOMEURL."&forumURL=".BBSURL.'&client='.$_SESSION['client'].'&clienURL='.CLIENT_DOWN_URL;
$_SESSION['FLVarsPlain']=$flash_vars;
//针对参数进行xor简单加密,FLASH中需要做对应的解密,这样避免查看源文件得到这些敏感信息,如不需要加密则屏蔽下面这行
//解密时,先base64_decode再与 $key 做异或运算

function sampleEncodeParam($s)
{
	$hexchars = '0123456789ABCDEF';
	if ( !$s || strlen($s) <= 0 )
	{
		echo "null string.";
		return "";
	}
	$len = strlen($s);
	$ret = '';
	$curc = 0;
	$nextc = ord(substr($s, 0, 1));
	for ($i=1; $i<$len; $i++ )
	{
		$curc = $nextc;
		$nextc = ord(substr($s, $i, 1));
		$curc ^= $nextc;
		//echo '<br> 0x'. substr($hexchars, ($curc & 0xF0) >> 4, 1) . substr($hexchars, $curc & 0x0F, 1);
		$ret .= substr($hexchars, ($curc & 0xF0) >> 4, 1);
		$ret .= substr($hexchars, $curc & 0x0F, 1);
	}
	$curc = $nextc ^ 0x7C;
	$ret .= substr($hexchars, ($curc & 0xF0) >> 4, 1);
	$ret .= substr($hexchars, $curc & 0x0F, 1);
	return $ret;
}

//echo $flash_vars;
$flash_vars=base64_encode(sampleEncodeParam($flash_vars));
//echo '<br>';
//echo $flash_vars;

$_SESSION['FLVars']=$flash_vars;
$_SESSION['GameServerName']=$_srvName;



header('location:djrm.php');
ob_end_flush();//输出全部内容到浏览器
?>
