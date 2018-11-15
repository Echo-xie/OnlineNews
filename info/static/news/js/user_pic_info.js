$(function () {
    $(".pic_info").submit(function (e) {
        // 阻止表单默认提交行为
        e.preventDefault();

        //TODO 上传头像
        $(this).ajaxSubmit({
            url: "/users/user_pic_info",
            type: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    $(".now_user_pic").attr("src", resp.avatar_url)
                    $(".user_center_pic>img", parent.document).attr("src", resp.avatar_url)
                    $(".user_login>img", parent.document).attr("src", resp.avatar_url)
                } else {
                    alert(resp.errmsg)
                }
            }
        })
    })
});

// 获取cookie
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
