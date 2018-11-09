$(function () {

    vm = new Vue({
        el: "#app",
        delimiters: ["{[", "]}"],
        data: {
            image_src: "../../static/news/images/pic_code.png",
            get_code_str: "60秒",
            get_code_cli: true,
        },
        methods: {
            // 定义一个json请求函数, 后面补充
            send_sms() {
            },
        },
    });

    // 打开登录框
    $('.login_btn').click(function () {
        $('.login_form_con').show();
    });

    // 点击关闭按钮关闭登录框或者注册框
    $('.shutoff').click(function () {
        $(this).closest('form').hide();
    });

    // 隐藏错误
    $(".login_form #mobile").focus(function () {
        $("#login-mobile-err").hide();
    });
    $(".login_form #password").focus(function () {
        $("#login-password-err").hide();
    });

    $(".register_form #mobile").focus(function () {
        $("#register-mobile-err").hide();
    });
    $(".register_form #imagecode").focus(function () {
        $("#register-image-code-err").hide();
    });
    $(".register_form #smscode").focus(function () {
        $("#register-sms-code-err").hide();
    });
    $(".register_form #password").focus(function () {
        $("#register-password-err").hide();
    });


    // 点击输入框，提示文字上移
    $('.form_group').on('click focusin', function () {
        $(this).children('.input_tip').animate({'top': -5, 'font-size': 12}, 'fast');
    });

    // 输入框失去焦点，如果输入框为空，则提示文字下移
    $('.form_group input').on('blur focusout', function () {
        $(this).parent().removeClass('hotline');
        var val = $(this).val();
        if (val == '') {
            $(this).siblings('.input_tip').animate({'top': 22, 'font-size': 14}, 'fast');
        }
    });


    // 打开注册框
    $('.register_btn').click(function () {
        $('.register_form_con').show();
        // 打开注册框架时调用`获取图片验证码`函数
        generateImageCode();
    });


    // 登录框和注册框切换
    $('.to_register').click(function () {
        $('.login_form_con').hide();
        $('.register_form_con').show();
        // 打开注册框架时调用`获取图片验证码`函数
        generateImageCode();
    });

    // 登录框和注册框切换
    $('.to_login').click(function () {
        $('.login_form_con').show();
        $('.register_form_con').hide();
    });

    // 根据地址栏的hash值来显示用户中心对应的菜单
    var sHash = window.location.hash;
    if (sHash != '') {
        var sId = sHash.substring(1);
        var oNow = $('.' + sId);
        var iNowIndex = oNow.index();
        $('.option_list li').eq(iNowIndex).addClass('active').siblings().removeClass('active');
        oNow.show().siblings().hide();
    }

    // 用户中心菜单切换
    var $li = $('.option_list li');
    var $frame = $('#main_frame');

    $li.click(function () {
        if ($(this).index() == 5) {
            $('#main_frame').css({'height': 900});
        }
        else {
            $('#main_frame').css({'height': 660});
        }
        $(this).addClass('active').siblings().removeClass('active');
        $(this).find('a')[0].click();
    });

    // TODO 登录表单提交
    $(".login_form_con").submit(function (e) {
        e.preventDefault();
        var mobile = $(".login_form #mobile").val();
        var password = $(".login_form #password").val();

        if (!mobile) {
            $("#login-mobile-err").show();
            return;
        }

        if (!password) {
            $("#login-password-err").show();
            return;
        }

        // 组织参数
        var params = {
            "mobile": mobile,
            "password": password
        };

        // TODO 发起登录请求

    });


    // TODO 注册按钮点击
    $(".register_form_con").submit(function (e) {
        // 阻止默认提交操作
        e.preventDefault();

        // 取到用户输入的内容
        var mobile = $("#register_mobile").val();
        var smscode = $("#smscode").val();
        var password = $("#register_password").val();

        if (!mobile) {
            $("#register-mobile-err").show();
            return;
        }
        if (!smscode) {
            $("#register-sms-code-err").show();
            return;
        }
        if (!password) {
            $("#register-password-err").html("请填写密码!");
            $("#register-password-err").show();
            return;
        }

        if (password.length < 6) {
            $("#register-password-err").html("密码长度不能少于6位");
            $("#register-password-err").show();
            return;
        }

        // 注册参数
        var params = {
            "mobile": mobile,
            "sms_code": smscode,
            "password": password
        };

        // TODO 发起注册请求
    });

    // TODO 用户退出功能
    $('#logout').click(function () {

    })

});
// 图片uuid
var imageCodeId = "";

// TODO 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    // 生成uuid
    imageCodeId = generateUUID();
    // json请求地址
    var imageCodeUrl = "/passport/image_code?code_id=" + imageCodeId;
    // 设置 图片验证码 url
    vm.image_src = imageCodeUrl

}

// 发送短信验证码
function sendSMSCode() {
    // 前端校验参数，保证输入框有数据填写
    var mobile = $("#register_mobile").val();
    $("#register-mobile-err").hide();
    if (!mobile) {
        $("#register-mobile-err").html("请填写正确的手机号！");
        $("#register-mobile-err").show();
        return;
    }
    var imageCode = $("#imagecode").val();
    $("#register-image-code-err").hide();
    if (!imageCode) {
        $("#register-image-code-err").html("请填写验证码！");
        $("#register-image-code-err").show();
        return;
    }
    // 获取csrf_token -- CSRF防范
    csrf_token = $("#csrf_token").val()
    // TODO 发送短信验证码
    // 组织参数
    var params = {
        "mobile": mobile,
        "image_code": imageCode,
        "image_code_id": imageCodeId
    };
    // 设置不可点击, 并且倒计时开始
    vm.get_code_cli = false
    // 定时器 -- 1分钟只能请求一次短信验证码
    var num = 60;
    // 设置定时器
    var t = setInterval(function () {
        // 下一秒就会取消倒计时
        if (num == 1) {
            // 取消计时器
            clearInterval(t)
            // 显示可点击
            vm.get_code_cli = true;
            // 初始化
            vm.get_code_str = "60秒";
        } else {
            // 倒计时
            num -= 1;
            // 显示倒计时
            vm.get_code_str = num + "秒";
        }
    }, 1000);
    // TODO 发送ajax请求，请求发送短信验证码
    // 隐藏短信验证码错误信息框
    $("#register-sms-code-err").hide();
    vm.send_sms()
    {   // ajax post请求
        axios.post("/passport/send_sms", params, {headers: {'X-CSRFToken': csrf_token}})
        // 成功访问
            .then(function (response) {
                // 返回状态码
                errno = response.data.errno;
                // 返回信息
                errmsg = response.data.errmsg;
                // 手机相关的返回信息
                if (errmsg.indexOf("手机") != -1) {
                    $("#register-mobile-err").html(errmsg);
                    $("#register-mobile-err").show();
                }
                // 图形验证码的返回信息
                else if (errmsg.indexOf("图形验证码") != -1) {
                    $("#register-image-code-err").html(errmsg);
                    $("#register-image-code-err").show();
                }
                // 其他返回信息
                else {
                    $("#register-sms-code-err").html(response.data.errmsg);
                    $("#register-sms-code-err").show();
                }
                // 如果返回码 != 0 发送短信验证码失败
                if (errno != 0) {
                    // 重新生成验证码
                    generateImageCode()
                }
            })
            // 访问失败
            .catch(function (error) {
                // 错误信息
                console.log(error);
            });
    }

}

// 调用该函数模拟点击左侧按钮
function fnChangeMenu(n) {
    var $li = $('.option_list li');
    if (n >= 0) {
        $li.eq(n).addClass('active').siblings().removeClass('active');
        // 执行 a 标签的点击事件
        $li.eq(n).find('a')[0].click()
    }
}

// 一般页面的iframe的高度是660
// 新闻发布页面iframe的高度是900
function fnSetIframeHeight(num) {
    var $frame = $('#main_frame');
    $frame.css({'height': num});
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
}
