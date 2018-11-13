function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    // 新闻ID
    var news_id = $("#news_id").val();
    // 登陆用户ID
    var user_id = $("#user_id").val();
    // 作者ID
    var author_id = $("#author_id").val();
    // 是否已收藏
    var is_collected = $("#is_collected").val();
    // 是否已关注
    var is_followed = $("#is_followed").val();
    // 如果已收藏
    if (is_collected == "True") {
        // 隐藏收藏按钮
        $(".collection").hide();
        // 显示取消收藏按钮
        $(".collected").show();
    }
    // 如果已收藏
    if (is_followed == "True") {
        // 隐藏关注按钮
        $(".focus").hide();
        // 显示取消关注按钮
        $(".focused").show();
    }

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    });

    // 收藏
    $(".collection").click(function () {
        // 如果用户ID不存在, 需要先登陆
        if ($.isEmptyObject(user_id)) {
            // 打开用户等窗口
            $('.login_form_con').show();
            return;
        }
        // 获取收藏的`新闻id`
        var action = "collect";

        // 组织参数
        var params = {
            "news_id": news_id,
            "action": action
        };

        // TODO 请求收藏新闻
        init_ajax("/news/news_collect", params, function (response) {
            let errno = response.errno;
            let errmsg = response.errmsg;
            if (errno == 0) {
                // 收藏成功
                // 隐藏收藏按钮
                $(".collection").hide();
                // 显示取消收藏按钮
                $(".collected").show();
            } else {
                alert(resp.errmsg);
            }
        })
        // $.ajax({
        //     url: "/news/news_collect",
        //     type: "POST",
        //     contentType: "application/json",
        //     headers: {
        //         "X-CSRFToken": getCookie("csrf_token")
        //     },
        //     data: JSON.stringify(params),
        //     dataType:"json",
        //     success: function (response) {
        //         let errno = response.errno;
        //         let errmsg = response.errmsg;
        //         if (errno == 0) {
        //             // 收藏成功
        //             // 隐藏收藏按钮
        //             $(".collection").hide();
        //             // 显示取消收藏按钮
        //             $(".collected").show();
        //         } else {
        //             alert(resp.errmsg);
        //         }
        //     }
        // });

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
        init_ajax("/news/news_collect", params, function (response) {
            let errno = response.errno;
            let errmsg = response.errmsg;
            if (errno == 0) {
                // 收藏成功
                // 隐藏收藏按钮
                $(".collection").show();
                // 显示取消收藏按钮
                $(".collected").hide();
            } else {
                alert(resp.errmsg);
            }
        })
        // $.ajax({
        //     url: "/news/news_collect",
        //     type: "POST",
        //     contentType: "application/json",
        //     headers: {
        //         "X-CSRFToken": getCookie("csrf_token")
        //     },
        //     data: JSON.stringify(params),
        //     dataType: "json",
        //     success: function (response) {
        //         let errno = response.errno;
        //         let errmsg = response.errmsg;
        //         if (errno == 0) {
        //             // 收藏成功
        //             // 隐藏收藏按钮
        //             $(".collection").show();
        //             // 显示取消收藏按钮
        //             $(".collected").hide();
        //         } else {
        //             alert(resp.errmsg);
        //         }
        //     }
        // });
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
        // 如果用户ID不存在, 需要先登陆
        if ($.isEmptyObject(user_id)) {
            // 打开用户等窗口
            $('.login_form_con').show();
            return;
        }
        // 组织参数
        var params = {
            "followed_id": author_id,
            "action": "follow",
        };
        init_ajax("/users/follow", params, function (response) {
            location.reload();
        })
    });

    // 取消关注当前新闻作者
    $(".focused").click(function () {
        // 组织参数
        var params = {
            "followed_id": author_id,
            "action": "un_follow",
        };
        init_ajax("/users/follow", params, function (response) {
            location.reload();
        })
    });
});