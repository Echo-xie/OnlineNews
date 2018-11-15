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
        if (!check_login()) {
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
        // 如果用户ID不存在, 需要先登陆
        if (!check_login()) {
            return;
        }
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
        // 如果用户ID不存在, 需要先登陆
        if (!check_login()) {
            return;
        }
        var sHandler = $(this).prop('class');

        if (sHandler.indexOf('comment_reply') >= 0) {
            $(this).next().toggle();
        }

        if (sHandler.indexOf('reply_cancel') >= 0) {
            $(this).parent().toggle();
        }

        if (sHandler.indexOf('comment_up') >= 0) {
            var $this = $(this);

            // 获取`评论id`
            var comment_id = $this.attr('data-commentid');

            // 组织参数
            var params = {
                "comment_id": comment_id,
            };

            // TODO 请求`点赞`或`取消点赞`
            init_ajax("/news/comment_like", params, function (resp) {
                // 请求成功
                if (resp.errno == "0") {
                    // 获取点赞数量
                    var like_count = $this.attr('data-likecount')
                    // 如果找不到
                    if (like_count == undefined) {
                        // 默认为0
                        like_count = 0
                    }
                    // 如果已点赞
                    if (sHandler.indexOf('has_comment_up') >= 0) {
                        // 点赞次数-1
                        like_count = parseInt(like_count) - 1
                        // 修改点赞样式 -- 没有点赞
                        $this.removeClass('has_comment_up');
                        // 否则 没有点赞
                    } else {
                        // 点赞次数+1
                        like_count = parseInt(like_count) + 1
                        // 修改点赞样式 -- 已点赞
                        $this.addClass('has_comment_up')
                    }
                    // 更新点赞数据
                    $this.attr('data-likecount', like_count)
                    // 如果点赞次数为0
                    if (like_count == 0) {
                        //
                        $this.html("赞")
                    } else {
                        // 点赞次数
                        $this.html(like_count)
                    }
                    // location.reload();
                } else {
                    alert(resp.errmsg)
                }
            })
        }

        if (sHandler.indexOf('reply_sub') >= 0) {
            // 获取参数
            var $this = $(this);
            var parent_id = $this.parent().attr('data-commentid');
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
            init_ajax("/news/news_comment", params, function (resp) {
                if (resp.errno == "0") {
                    var comment = resp.data
                    // 拼接内容
                    var comment_html = ""
                    comment_html += '<div class="comment_list">'
                    comment_html += '<div class="person_pic fl">'
                    if (comment.user.avatar_url) {
                        comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">'
                    } else {
                        comment_html += '<img src="../../static/news/images/person01.png" alt="用户图标">'
                    }
                    comment_html += '</div>'
                    comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>'
                    comment_html += '<div class="comment_text fl">'
                    comment_html += comment.content
                    comment_html += '</div>'
                    comment_html += '<div class="reply_text_con fl">'
                    comment_html += '<div class="user_name2">' + comment.parent.user.nick_name + '</div>'
                    comment_html += '<div class="reply_text">'
                    comment_html += comment.parent.content
                    comment_html += '</div>'
                    comment_html += '</div>'
                    comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>'

                    comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-newsid="' + comment.news_id + '">赞</a>'
                    comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>'
                    comment_html += '<form class="reply_form fl" data-commentid="' + comment.id + '">'
                    comment_html += '<textarea class="reply_input"></textarea>'
                    comment_html += '<input type="button" value="回复" class="reply_sub fr">'
                    comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">'
                    comment_html += '</form>'

                    comment_html += '</div>'
                    $(".comment_list_con").prepend(comment_html)
                    // 请空输入框
                    $this.prev().val('')
                    // 关闭
                    $this.parent().hide()
                } else {
                    alert(resp.errmsg)
                }
            })

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

// 提交评论
function submit_comment() {
    var $this = $(this)
    // 评论信息
    var content = $(".comment_input").val()
    // 评论信息ID
    var parent_id = $this.parent().attr('data-commentid')
    if (!content) {
        alert('请输入评论内容');
        return
    }
    // 请求体
    params = {
        "news_id": $("#news_id").val(),
        "content": content,
        "parent_id": parent_id
    }
    // ajax请求
    init_ajax("/news/news_comment", params, function (resp) {
        if (resp.errno == '0') {
            var comment = resp.data
            // 拼接内容
            var comment_html = ''
            comment_html += '<div class="comment_list">'
            comment_html += '<div class="person_pic fl">'
            if (comment.user.avatar_url) {
                comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">'
            } else {
                comment_html += '<img src="../../static/news/images/person01.png" alt="用户图标">'
            }
            comment_html += '</div>'
            comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>'
            comment_html += '<div class="comment_text fl">'
            comment_html += comment.content
            comment_html += '</div>'
            comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>'

            comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-newsid="' + comment.news_id + '">赞</a>'
            comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>'
            comment_html += '<form class="reply_form fl" data-commentid="' + comment.id + '" data-newsid="' + news_id + '">'
            comment_html += '<textarea class="reply_input"></textarea>'
            comment_html += '<input type="button" value="回复" class="reply_sub fr">'
            comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">'
            comment_html += '</form>'

            comment_html += '</div>'
            // 拼接到内容的前面
            $(".comment_list_con").prepend(comment_html)
            // 让comment_sub 失去焦点
            $('.comment_sub').blur();
            // 清空输入框内容
            $(".comment_input").val("")
        } else {
            alert(resp.errmsg)
        }
    })
}

// 查询是否登陆用户 -- true: 已登陆, false: 没有登陆
function check_login() {
    var user_id = $("#user_id").val();
    // 如果用户ID不存在, 需要先登陆
    if ($.isEmptyObject(user_id)) {
        // 打开用户等窗口
        $('.login_form_con').show();
        return false;
    }
    return true;
}