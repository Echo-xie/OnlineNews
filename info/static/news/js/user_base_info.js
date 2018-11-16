$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault();

        var signature = $("#signature").val();
        var nick_name = $("#nick_name").val();
        var gender = $(".gender:checked").val();

        if (!nick_name) {
            alert('请输入昵称');
            return
        }
        if (!gender) {
            alert('请选择性别');
            return
        }

        // 组织参数
        var params = {
            "signature": signature,
            "nick_name": nick_name,
            "gender": gender
        };

        // TODO 请求修改用户基本信息
        init_ajax("/users/user_base_info", params, function (resp) {
            if (resp.errno == "0") {
                // 更新父窗口内容 parent.document
                $('.user_center_name', parent.document).html(params['nick_name'])
                $('#nick_name', parent.document).html(params['nick_name'])
                alert("更新成功!")
            } else {
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