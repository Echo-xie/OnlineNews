$(function () {
    // ES6 模板字符串
    Vue.config.delimiters = ['{[', ']}']

    // 修改原生 HTML 插值的定界符。
    // 实例化vue
    vm = new Vue({
        // 指定标签
        el: "#app",
        // 设置语法模板
        // delimiters: ["{[", "]}"],
        // 属性字典
        data: {
            // 获取cookie中csrf_token -- CSRF防范
            csrf_token: getCookie("csrf_token"),
            get_code_str: "60秒",
            user: $("#user").val(),
        },
        // 方法字典
        methods: {
            // 定义一个json请求函数, 后面补充 -- 发送短信验证码
            send_sms() {
            },
            // 定义一个json请求函数, 后面补充 -- 新用户注册
            register() {
            },
            // 定义一个json请求函数, 后面补充 -- 用户登陆
            login() {
            },
            // 定义一个json请求函数, 后面补充 -- 用户登出
            logout() {
            },

        },
        // 自定义过滤器
        filters: {},
        // 计算器
        computed: {
            is_login: function () {
                return true ? (this.user && this.user != "None") : false
            }
        },
    });

    // 打开登录框
    $('.login_btn').click(function () {
        $('.login_form_con').show();
    });

    // 点击关闭按钮关闭登录框或者注册框
    $('.shutoff').click(function () {
        $(this).closest('form').hide();
        $(this).closest('form')[0].reset();
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
        // 打开注册框架时调用`获取图形验证码`函数
        generateImageCode();
    });


    // 登录框和注册框切换
    $('.to_register').click(function () {
        $('.login_form_con').hide();
        $('.register_form_con').show();
        // 打开注册框架时调用`获取图形验证码`函数
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

        $("#login-mobile-err").hide();
        if (!mobile) {
            $("#login-mobile-err").show();
            return;
        }

        $("#login-password-err").hide();
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
        vm.login()
        {   // ajax post请求,
            axios.post("/passport/login", params, {headers: {'X-CSRFToken': vm.csrf_token, "Content-Type": "application/json"}})
            // 请求访问成功
                .then(function (response) {
                    // 响应状态码
                    let errno = response.data.errno;
                    // 响应信息
                    let errmsg = response.data.errmsg;
                    //  状态码 -- 成功
                    if (errno == 0) {
                        // 刷新页面
                        location.reload();
                    } else {
                        // 显示错误信息
                        $("#login-password-err").html(errmsg);
                        $("#login-password-err").show();
                    }
                })
                // 请求访问失败
                .catch(function (error) {
                    // 错误信息
                    console.log(error);
                });
        }
    });


    // TODO 注册按钮点击
    $(".register_form_con").submit(function (e) {
        // 阻止默认提交操作
        e.preventDefault();

        // 取到用户输入的内容
        var mobile = $("#register_mobile").val();
        var smscode = $("#smscode").val();
        var password = $("#register_password").val();
        var agree_input = $(".agree_input").is(":checked")

        $("#register-mobile-err").hide();
        if (!mobile) {
            $("#register-mobile-err").html("请填写正确的手机号！");
            $("#register-mobile-err").show();
            return;
        }
        $("#register-sms-code-err").hide();
        if (!smscode) {
            $("#register-sms-code-err").html("请填写短信验证码");
            $("#register-sms-code-err").show();
            return;
        }
        $("#register-password-err").hide();
        if (!password) {
            $("#register-password-err").html("请填写密码!");
            $("#register-password-err").show();
            return;
        }
        $("#register-password-err").hide();
        if (password.length < 6) {
            $("#register-password-err").html("密码长度不能少于6位");
            $("#register-password-err").show();
            return;
        }
        $("#register-agree-input-err").hide();
        if (!agree_input) {
            $("#register-agree-input-err").show();
            return;
        }

        // 注册参数
        var params = {
            "mobile": mobile,
            "sms_code": smscode,
            "password": password
        };

        // TODO 发起注册请求
        vm.register()
        {   // ajax post请求,
            axios.post("/passport/register", params, {headers: {'X-CSRFToken': vm.csrf_token, "Content-Type": "application/json"}})
            // 请求访问成功
                .then(function (response) {
                    // 响应状态码
                    let errno = response.data.errno;
                    // 响应信息
                    let errmsg = response.data.errmsg;
                    //  状态码 -- 成功
                    if (errno == 0) {
                        // 刷新页面
                        location.reload();
                    } else {
                        // 显示错误信息
                        $("#register-password-err").html(errmsg);
                        $("#register-password-err").show();
                    }
                })
                // 请求访问失败
                .catch(function (error) {
                    // 错误信息
                    console.log(error);
                });
        }
    });

    // TODO 用户退出功能
    $('#logout').click(function () {
        vm.logout()
        {
            axios.post("/passport/logout", "", {headers: {'X-CSRFToken': vm.csrf_token}})
                .then(function (response) {
                    //
                    // alert("成功退出系统");
                    // 刷新页面
                    location.reload();
                })
        }
    })
    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();
        // 网页头部标签高度
        var header_height = $(".header").height()
        // 右侧标签控件
        var rank_con = $(".rank_con")
        // 滚动不可超过 页面可以滚动的距离
        if (nowScroll < canScrollHeight - 40) {
            // 如果屏幕滚动遮住头部标签, 设置标签的margin-top
            if (nowScroll > header_height) {
                // 设置外边界-top
                rank_con.css("marginTop", nowScroll - header_height)
            } else {
                // 取消外边距, 恢复原本布局
                rank_con.css("marginTop", 0)
            }
        }
        // 如果滚动条下滑到一定位置, 出现返回顶部
        if (nowScroll > 600) {
            $("#to_top").show()
        } else {
            $("#to_top").hide()
        }
    });

});
// 图片uuid
var imageCodeId = "";

// TODO 生成一个图形验证码的编号，并设置页面中图形验证码img标签的src属性
function generateImageCode() {
    // 生成uuid
    imageCodeId = generateUUID();
    // json请求地址
    var imageCodeUrl = "/passport/image_code?code_id=" + imageCodeId;
    // 设置 图形验证码 url
    $(".get_pic_code").attr("src", imageCodeUrl);

}

// 发送短信验证码
function sendSMSCode() {
    // 点击获取短信验证码标签
    var get_code = $(".get_code")
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
    // TODO 发送短信验证码
    // 组织参数
    var params = {
        "mobile": mobile,
        "image_code": imageCode,
        "image_code_id": imageCodeId
    };
    // TODO 发送ajax请求，请求发送短信验证码
    // 隐藏短信验证码错误信息框
    $("#register-sms-code-err").hide();

    // 调用vm的方法
    vm.send_sms()
    {   // ajax post请求 -- 设置请求头信息
        axios.post("/passport/send_sms", params, {headers: {'X-CSRFToken': vm.csrf_token, "Content-Type": "application/json"}})
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
                } else {
                    // 设置不可点击, 并且倒计时开始
                    get_code.removeAttr("onclick")
                    sendSMSCode
                    // 定时器 -- 1分钟只能请求一次短信验证码
                    var num = 60;
                    // 设置定时器
                    var t = setInterval(function () {
                        // 下一秒就会取消倒计时
                        if (num == 1) {
                            // 取消计时器
                            clearInterval(t)
                            // 显示可点击
                            get_code.attr("onclick", "sendSMSCode();");
                            // 初始化
                            vget_code.html("点击获取验证码")
                        } else {
                            // 倒计时
                            num -= 1;
                            // 显示倒计时
                            get_code.html(num + "秒");
                        }
                    }, 1000);
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

// 获取cookie
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

// 封装ajax请求
function init_ajax(out_url, params, callback_success) {
    $.ajax({
        url: out_url,
        type: "POST",
        contentType: "application/json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        data: JSON.stringify(params),
        dataType: "json",
        success: function (resp) {
            if (resp.errno == 4101) {
                $('.login_form_con').show();
                return false;
            }
            callback_success(resp)
        }
    });
}