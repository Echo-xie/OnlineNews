function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    var news_id = $("#news_id").val();
    var user_id = $("#user_id").val();

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    });

    // 收藏
    $(".collection").click(function () {
        if ($.isEmptyObject(user_id)) {
            $('.login_form_con').show();
        }
        // 获取收藏的`新闻id`
        var action = "collect";

        // 组织参数
        var params = {
            "news_id": news_id,
            "action": action
        };

        // TODO 请求收藏新闻
        $.ajax({
            url: "/news/news_collect",
            type: "POST",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            dataType:"json",
            success: function (response) {
                let errno = response.errno;
                let errmsg = response.errmsg;
                if (errno == "0") {
                    // 收藏成功
                    // 隐藏收藏按钮
                    $(".collection").hide();
                    // 显示取消收藏按钮
                    $(".collected").show();
                } else {
                    alert(resp.errmsg);
                }
            }
        });

    });

    // 取消收藏
    $(".collected").click(function () {
        // 获取收藏的`新闻id`
        var action = "cancel_collect";

        // 组织参数
        var params = {
            "news_id": news_id,
            "action": action
        };

        // TODO 请求取消收藏新闻
        $.ajax({
            url: "/news/news_collect",
            type: "POST",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            dataType:"json",
            success: function (response) {
                let errno = response.errno;
                let errmsg = response.errmsg;
                if (errno == "0") {
                    // 收藏成功
                    // 隐藏收藏按钮
                    $(".collection").show();
                    // 显示取消收藏按钮
                    $(".collected").hide();
                } else {
                    alert(resp.errmsg);
                }
            }
        });
    });

    // 更新评论条数
    function updateCommentCount() {
        var length = $(".comment_list").length;
        $(".comment_count").html(length + "条评论");
    }

    // 评论提交
    $(".comment_form").submit(function (e) {
        // 组织表单默认提交行为
        e.preventDefault();

        // 获取参数
        var comment = $(".comment_input").val();

        // 组织参数
        var params = {
            "news_id": news_id,
            "content": comment
        };

        // TODO 请求对新闻`进行评论`


    });

    $('.comment_list_con').delegate('a,input', 'click', function () {

        var sHandler = $(this).prop('class');

        if (sHandler.indexOf('comment_reply') >= 0) {
            $(this).next().toggle();
        }

        if (sHandler.indexOf('reply_cancel') >= 0) {
            $(this).parent().toggle();
        }

        if (sHandler.indexOf('comment_up') >= 0) {
            var $this = $(this);
            // 默认点击时代表`点赞`
            var action = 'do';
            if (sHandler.indexOf('has_comment_up') >= 0) {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                $this.removeClass('has_comment_up');
                // 如果已经点赞，设置为`取消点赞`
                action = 'undo';
            } else {
                $this.addClass('has_comment_up')
            }

            // 获取`评论id`
            var comment_id = $this.attr('data-comment-id');

            // 组织参数
            var params = {
                "comment_id": comment_id,
                "action": action
            };

            // TODO 请求`点赞`或`取消点赞`

        }

        if (sHandler.indexOf('reply_sub') >= 0) {
            // 获取参数
            var $this = $(this);
            var parent_id = $this.parent().attr('data-comment-id');
            var comment = $this.prev().val();

            if (!comment) {
                alert("请输入评论内容");
                return;
            }

            // 组织参数
            var params = {
                "news_id": news_id,
                "content": comment,
                "parent_id": parent_id
            };

            // TODO 请求`回复评论`

        }
    });

    // 关注当前新闻作者
    $(".focus").click(function () {

    });

    // 取消关注当前新闻作者
    $(".focused").click(function () {

    });
});