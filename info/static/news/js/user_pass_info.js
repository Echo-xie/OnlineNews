$(function () {
    $(".pass_info").submit(function (e) {
        // 阻止表单的默认提交行为
        e.preventDefault();
        var error_tip = $(".error_tip");
        var old_password = $('#old_password').val();
        var new_password = $('#new_password').val();
        var new_password2 = $('#new_password2').val();

        error_tip.hide()
        if (!old_password) {
            error_tip.html("原密码不能为空!")
            error_tip.show()
            return;
        }

        if (!new_password) {
            error_tip.html("新密码不能为空!")
            error_tip.show()
            return;
        }

        if (!new_password2) {
            error_tip.html("重复新密码不能为空!")
            error_tip.show()
            return;
        }

        if (new_password != new_password2) {
            error_tip.html("两次密码不一致!")
            error_tip.show()
            return;
        }

        // 组织参数
        var params = {
            "old_password": old_password,
            "new_password": new_password
        };

        // TODO: 请求修改用户密码
        init_ajax("/users/user_pass_info", params, function (resp) {
            if (resp.errno == "0") {
                alert("更新成功!")
                window.location.reload()
            } else {
                error_tip.html(resp.errmsg)
                error_tip.show()
                alert(resp.errmsg)
            }
        })
    })
});

// 获取cookie
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
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
                $('.login_form_con', parent.document).show();
                return false;
            }
            callback_success(resp)
        }
    });
}