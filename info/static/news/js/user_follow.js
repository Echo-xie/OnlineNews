$(function () {

    $(".focused").click(function () {
        // TODO 取消关注当前新闻作者
        // 组织参数
        var params = {
            "followed_id": $(this).attr('data-user-id'),
            "action": "un_follow",
        };
        init_ajax("/users/follow", params, function (response) {
            location.reload();
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