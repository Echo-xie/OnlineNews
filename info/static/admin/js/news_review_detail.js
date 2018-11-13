$(function(){
    $(".news_review").submit(function (e) {
        e.preventDefault();

        // TODO 新闻审核提交

    })
});

// 点击取消，返回上一页
function cancel() {
    history.go(-1);
}