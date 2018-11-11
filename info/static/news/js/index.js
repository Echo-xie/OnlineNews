var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据


$(function () {
    // 获取首页新闻信息
    updateNewsData();

    // 首页分类切换
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid');
        $('.menu li').each(function () {
            $(this).removeClass('active');
        });
        $(this).addClass('active');

        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = clickCid;

            // 重置分页参数
            cur_page = 1;
            total_page = 1;
            updateNewsData();
        }
    });

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
        // 获取右侧标签控件
        var rank_con = $(".rank_con")
        // 如果屏幕滚动遮住头部标签, 设置标签的margin-top
        if (nowScroll > header_height) {
            // 设置外边界-top
            rank_con.css("marginTop", nowScroll - header_height)
        } else {
            // 取消外边距, 恢复原本布局
            rank_con.css("marginTop", 0)
        }

        if ((canScrollHeight - nowScroll) < 100) {
            // TODO 判断页数，去更新新闻数据
            // 判断`是否正在向服务器请求获取数据`
            if (!data_querying) {
                // 设置`是否正在向服务器请求获取数据`data_querying为true
                // 防止页面滚动时多次向服务器请求数据
                data_querying = true;

                // 判断是否还有`下一页`，如果有则获取`下一页`内容
                if (cur_page < total_page) {
                    updateNewsData();
                }
                else {
                    data_querying = false;
                }
            }
        }
    })
});

// 获取指定页码的`分类新闻信息`
function updateNewsData() {
    // 组织参数
    var params = {
        "cid": currentCid,
        "page": cur_page,
        "per_page": 10
    };

    // TODO 更新新闻数据
    // ajax get请求
    $.get("/newslist", params, function (resp) {
        // 设置 `数据正在查询数据` 变量为 false，以便下次上拉加载
        data_querying = false
        if (resp) {
            // 记录总页数
            total_page = resp.totalPage
            // 如果当前页数为1，则清空原有数据
            if (cur_page == 1) {
                $(".list_con").html('')
            }
            // 当前页数递增
            cur_page += 1
            // 显示数据
            for (var i = 0; i < resp.newsList.length; i++) {
                var news = resp.newsList[i]
                var content = '<li>'
                content += '<a href="#" class="news_pic fl"><img src="' + news.index_image_url + '?imageView2/1/w/170/h/170"></a>'
                content += '<a href="/news/' + news.id + '" class="news_title fl">' + news.title + '</a>'
                content += '<a href="#" class="news_detail fl">' + news.digest + '</a>'
                content += '<div class="author_info fl">'
                content += '<div class="source fl">来源：' + news.source + '</div>'
                content += '<div class="time fl">' + news.create_time + '</div>'
                content += '</div>'
                content += '</li>'
                $(".list_con").append(content)
            }
        }
    })

}
