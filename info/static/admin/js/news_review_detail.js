$(function () {
    $(".news_review").submit(function (e) {
        e.preventDefault();

        // TODO 新闻审核提交

        var params = {
            "news_id": $("#news_id").val(),
            "action": $("input[name=action]:checked").val(),
            "reason": $("textarea[name=reason]").val()
        }
        $.ajax({
            url: "/admin/news_review_detail",
            type: "POST",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            dataType: "json",
            success: function (resp) {
                if (resp.errno == "0") {
                    // 返回上一页，刷新数据
                    location.href = document.referrer;
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    })
});

// 点击取消，返回上一页
function cancel() {
    history.go(-1);
}

// 获取cookie
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}