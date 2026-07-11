(function (window, document) {
    'use strict';

    var exact = {
        '欢迎登录': 'Đăng nhập quản trị',
        '欢迎登陆': 'Chào mừng đăng nhập',
        '管理中心': 'Trung tâm quản trị',
        '后台管理中心': 'Trung tâm quản trị',
        '后台管理系统': 'Hệ thống quản trị',
        '管理平台': 'Hệ thống quản trị',
        '页面管理': 'Quản lý chức năng',
        '管理': 'Quản trị',
        '首页': 'Trang chủ',
        '账号：': 'Tài khoản:',
        '账号': 'Tài khoản',
        '帐号：': 'Tài khoản:',
        '帐号': 'Tài khoản',
        '密码：': 'Mật khẩu:',
        '密码': 'Mật khẩu',
        '登陆': 'Đăng nhập',
        '登录': 'Đăng nhập',
        '退出': 'Đăng xuất',
        'Remember me': 'Ghi nhớ đăng nhập',
        '全服统计': 'Thống kê toàn máy chủ',
        '信息总览': 'Tổng quan',
        '全服列表': 'Danh sách máy chủ',
        '全服状态监控': 'Giám sát máy chủ',
        '全服充值': 'Nạp toàn máy chủ',
        '全服充值详细': 'Chi tiết nạp toàn máy chủ',
        '全服RMB玩家管理': 'Quản lý người chơi nạp tiền',
        '全服内玩管理': 'Quản lý tài khoản nội bộ',
        '全服在线/注册/登陆': 'Online / đăng ký / đăng nhập',
        '全服功能': 'Công cụ toàn máy chủ',
        '全服发送邮件': 'Gửi thư toàn máy chủ',
        '全服审核邮件': 'Duyệt thư toàn máy chủ',
        '活动设置': 'Thiết lập sự kiện',
        '类型添加': 'Thêm loại sự kiện',
        '类型列表': 'Danh sách loại sự kiện',
        '奖励添加': 'Thêm phần thưởng',
        '奖励列表': 'Danh sách phần thưởng',
        '活动添加': 'Thêm sự kiện',
        '活动列表': 'Danh sách sự kiện',
        '监控数据': 'Giám sát dữ liệu',
        '充值数据监控': 'Giám sát dữ liệu nạp',
        '新服数据监控分析': 'Phân tích máy chủ mới',
        '开服30天': 'Theo dõi 30 ngày đầu',
        '刷元宝监控': 'Giám sát bất thường Nguyên Bảo',
        '全服玩家反馈': 'Phản hồi người chơi',
        '收益类数据': 'Dữ liệu doanh thu',
        '商城产出统计': 'Thống kê vật phẩm cửa hàng',
        '道具消耗统计': 'Thống kê tiêu hao vật phẩm',
        '功能消耗统计': 'Thống kê tiêu hao tính năng',
        '全服新增RMB玩家': 'Người chơi nạp mới',
        '元宝库存统计': 'Thống kê tồn Nguyên Bảo',
        '系统设置': 'Thiết lập hệ thống',
        '服务器管理': 'Quản lý máy chủ',
        '用户组管理': 'Quản lý nhóm quyền',
        '后台用户帐号管理': 'Tài khoản quản trị',
        '用户组全服同步': 'Đồng bộ nhóm quyền',
        '用户帐号全服同步': 'Đồng bộ tài khoản quản trị',
        '后台登录日志': 'Nhật ký đăng nhập quản trị',
        '新开服务器管理': 'Quản lý máy chủ mới',
        '合服服务器管理': 'Quản lý gộp máy chủ',
        '运维管理': 'Vận hành máy chủ',
        '服务器配置': 'Cấu hình máy chủ',
        '服务器状态': 'Trạng thái máy chủ',
        '在线与流失': 'Online và rời game',
        '查看在线角色': 'Nhân vật đang online',
        '在线统计': 'Thống kê online',
        '各地图在线分布': 'Online theo bản đồ',
        '创号流失率': 'Tỷ lệ rời sau tạo tài khoản',
        '等级流失率': 'Tỷ lệ rời theo cấp',
        '玩家流失率': 'Tỷ lệ người chơi rời game',
        '任务流失率': 'Tỷ lệ rời theo nhiệm vụ',
        '注册登录统计': 'Thống kê đăng ký / đăng nhập',
        '登录人数统计': 'Thống kê lượt đăng nhập',
        '玩家留存率': 'Tỷ lệ giữ chân',
        '在线时长统计': 'Thống kê thời gian online',
        '充值与消费': 'Nạp và tiêu dùng',
        '充值报表': 'Báo cáo nạp',
        'RMB玩家管理': 'Người chơi nạp tiền',
        '首充统计': 'Thống kê nạp đầu',
        '首充等级统计': 'Nạp đầu theo cấp',
        '充值等级统计': 'Nạp theo cấp',
        '充值区间统计': 'Nạp theo khoảng',
        '元宝铜钱消费统计': 'Tiêu Nguyên Bảo / Đồng',
        '元宝铜钱库存统计': 'Tồn Nguyên Bảo / Đồng',
        '首次消费统计': 'Thống kê tiêu lần đầu',
        '首次消费等级统计': 'Tiêu lần đầu theo cấp',
        '运营数据': 'Dữ liệu vận hành',
        '排行榜': 'Bảng xếp hạng',
        '新手卡': 'Mã quà tân thủ',
        '功能活跃度': 'Mức độ sử dụng tính năng',
        '元宝铜钱获得与使用': 'Nhận và dùng Nguyên Bảo / Đồng',
        '剩余元宝和铜钱排行': 'Xếp hạng tài sản còn lại',
        '商城消费统计': 'Tiêu dùng cửa hàng',
        '玩家管理': 'Quản lý người chơi',
        '玩家列表': 'Danh sách người chơi',
        '登陆玩家账号': 'Đăng nhập tài khoản người chơi',
        '玩家物品列表': 'Vật phẩm người chơi',
        '仙盟列表': 'Danh sách Bang Hội',
        '宠物列表': 'Danh sách thú cưng',
        '坐骑列表': 'Danh sách thú cưỡi',
        '玩家成就': 'Thành tựu người chơi',
        '客服管理': 'Chăm sóc khách hàng',
        '玩家反馈': 'Phản hồi người chơi',
        '系统公告': 'Thông báo hệ thống',
        '管理员发送邮件': 'Gửi thư quản trị',
        '封号禁言管理': 'Khóa tài khoản / cấm chat',
        '同IP监控': 'Giám sát cùng IP',
        '物品信息查询': 'Tra cứu vật phẩm',
        '元宝铜钱扣除': 'Trừ Nguyên Bảo / Đồng',
        '设置玩家身份': 'Thiết lập quyền người chơi',
        '后台充值与查询': 'Nạp và tra cứu',
        '聊天监控': 'Giám sát chat',
        '世界聊天监控': 'Giám sát chat thế giới',
        '后台补单': 'Bổ sung đơn nạp',
        '日志管理': 'Quản lý nhật ký',
        '登录日志': 'Nhật ký đăng nhập',
        '断线日志': 'Nhật ký mất kết nối',
        '坐骑日志': 'Nhật ký thú cưỡi',
        '宠物日志': 'Nhật ký thú cưng',
        '装备日志': 'Nhật ký trang bị',
        '物品合成日志': 'Nhật ký ghép vật phẩm',
        '邮件日志': 'Nhật ký thư',
        '世界BOSS掉落日志': 'Nhật ký rơi đồ Boss thế giới',
        '背包日志': 'Nhật ký túi đồ',
        '战场日志': 'Nhật ký chiến trường',
        '拍卖日志': 'Nhật ký đấu giá',
        '交易日志': 'Nhật ký giao dịch',
        '商城日志': 'Nhật ký cửa hàng',
        '玩家行为日志': 'Nhật ký hành vi',
        '境界提升日志': 'Nhật ký tăng cảnh giới',
        '结婚日志': 'Nhật ký kết hôn',
        '宝箱日志': 'Nhật ký rương báu',
        '配置管理': 'Quản lý cấu hình',
        '活动配置': 'Cấu hình sự kiện',
        '游戏配置': 'Cấu hình game',
        '日常运营工作': 'Vận hành hằng ngày',
        '测试进度': 'Tiến độ kiểm thử',
        '平台相关配置': 'Cấu hình nền tảng',
        '管理员工具': 'Công cụ quản trị viên',
        '所有管理员': 'Danh sách quản trị viên',
        '添加管理员': 'Thêm quản trị viên',
        '管理员分组': 'Nhóm quản trị viên',
        '管理员日志': 'Nhật ký quản trị viên',
        '查询': 'Tra cứu',
        '搜索': 'Tìm kiếm',
        '提交': 'Xác nhận',
        '保存': 'Lưu',
        '添加': 'Thêm',
        '新增': 'Thêm mới',
        '编辑': 'Chỉnh sửa',
        '修改': 'Sửa',
        '删除': 'Xóa',
        '返回': 'Quay lại',
        '发送': 'Gửi',
        '审核': 'Duyệt',
        '导出': 'Xuất dữ liệu',
        '刷新': 'Làm mới',
        '重置': 'Đặt lại',
        '确定': 'Xác nhận',
        '取消': 'Hủy',
        '操作': 'Thao tác',
        '详情': 'Chi tiết',
        '状态': 'Trạng thái',
        '开启': 'Bật',
        '关闭': 'Tắt',
        '正常': 'Bình thường',
        '启用': 'Kích hoạt',
        '禁用': 'Vô hiệu hóa',
        '在线': 'Online',
        '离线': 'Offline',
        '角色名称': 'Tên nhân vật',
        '角色ID': 'ID nhân vật',
        '玩家帐号': 'Tài khoản người chơi',
        '服务器': 'Máy chủ',
        '服务器列表': 'Danh sách máy chủ',
        '等级': 'Cấp',
        '职业': 'Môn phái',
        '注册时间': 'Thời gian đăng ký',
        '最后登录时间': 'Đăng nhập gần nhất',
        '开始时间': 'Thời gian bắt đầu',
        '结束时间': 'Thời gian kết thúc',
        '日期': 'Ngày',
        '时间': 'Thời gian',
        '标题': 'Tiêu đề',
        '内容': 'Nội dung',
        '数量': 'Số lượng',
        '备注': 'Ghi chú',
        '没有数据': 'Không có dữ liệu',
        '暂无数据': 'Chưa có dữ liệu'
    };

    var phrases = [
        ['欢迎登录', 'Chào mừng đăng nhập'],
        ['欢迎登陆', 'Chào mừng đăng nhập'],
        ['欢迎', 'Chào mừng'],
        ['你好', 'Xin chào'],
        ['您好', 'Xin chào'],
        ['总后台', 'trang quản trị tổng'],
        ['管理平台', 'hệ thống quản trị'],
        ['管理中心', 'Trung tâm quản trị'],
        ['点击可进入相应的服务器后台', 'Nhấn để mở trang quản trị của máy chủ tương ứng'],
        ['请选择服务器', 'Vui lòng chọn máy chủ'],
        ['请选择', 'Vui lòng chọn'],
        ['密码错误', 'Mật khẩu không đúng'],
        ['账号或密码错误', 'Tài khoản hoặc mật khẩu không đúng'],
        ['操作成功', 'Thao tác thành công'],
        ['操作失败', 'Thao tác thất bại'],
        ['删除成功', 'Đã xóa thành công'],
        ['保存成功', 'Đã lưu thành công'],
        ['登录成功', 'Đăng nhập thành công'],
        ['退出系统', 'Đăng xuất'],
        ['当前服务器', 'Máy chủ hiện tại'],
        ['切换服务器', 'Chuyển máy chủ'],
        ['当前', 'Hiện tại'],
        ['共', 'Tổng'],
        ['条记录', 'bản ghi']
    ];

    var exactKeys = [];
    for (var exactKey in exact) {
        if (Object.prototype.hasOwnProperty.call(exact, exactKey)) { exactKeys.push(exactKey); }
    }
    exactKeys.sort(function (a, b) { return b.length - a.length; });

    function replaceValue(value) {
        if (!value) { return value; }
        var lead = value.match(/^\s*/)[0];
        var tail = value.match(/\s*$/)[0];
        var core = value.substring(lead.length, value.length - tail.length);
        if (exact[core]) { return lead + exact[core] + tail; }
        if (core.length > 120) { return value; }
        var result = core;
        for (var e = 0; e < exactKeys.length; e++) {
            result = result.split(exactKeys[e]).join(exact[exactKeys[e]]);
        }
        for (var i = 0; i < phrases.length; i++) {
            result = result.split(phrases[i][0]).join(phrases[i][1]);
        }
        return lead + result + tail;
    }

    function translateNode(node) {
        if (!node) { return; }
        if (node.nodeType === 3) {
            var parent = node.parentNode;
            if (!parent || /^(SCRIPT|STYLE|TEXTAREA|PRE|CODE)$/i.test(parent.tagName || '') || /(^|\s)no-vi(\s|$)/.test(parent.className || '')) { return; }
            node.nodeValue = replaceValue(node.nodeValue);
            return;
        }
        if (node.nodeType !== 1) { return; }
        var attrs = ['title', 'placeholder', 'alt'];
        for (var a = 0; a < attrs.length; a++) {
            if (node.getAttribute && node.getAttribute(attrs[a])) {
                node.setAttribute(attrs[a], replaceValue(node.getAttribute(attrs[a])));
            }
        }
        if (node.tagName === 'INPUT' && /^(button|submit|reset)$/i.test(node.type || '')) {
            node.value = replaceValue(node.value);
        }
        for (var child = node.firstChild; child; child = child.nextSibling) { translateNode(child); }
    }

    function run() {
        document.documentElement.lang = 'vi';
        document.title = replaceValue(document.title) || 'Quản trị Âm Hắc Đồ Long OL';
        translateNode(document.body);
        if (window.MutationObserver && document.body) {
            new MutationObserver(function (items) {
                for (var i = 0; i < items.length; i++) {
                    for (var j = 0; j < items[i].addedNodes.length; j++) { translateNode(items[i].addedNodes[j]); }
                }
            }).observe(document.body, { childList: true, subtree: true });
        }
    }

    if (document.readyState === 'loading') {
        if (document.addEventListener) { document.addEventListener('DOMContentLoaded', run, false); }
        else { window.attachEvent('onload', run); }
    } else { run(); }
}(window, document));
