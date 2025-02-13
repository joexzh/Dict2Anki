<strong>Dict2Anki-ng</strong> is a fork from <a href="https://github.com/megachweng/Dict2Anki" rel="nofollow">Dict2Anki</a>，目的是兼容 PyQt6 和新版 anki，主要功能与原版一致。

<strong>Dict2Anki</strong> 是一款方便<a href="http://cidian.youdao.com/multi.html" rel="nofollow">有道词典</a>、<a href="https://www.eudic.net/" rel="nofollow">欧陆词典</a>用户同步生成单词本卡片至<a href="https://apps.ankiweb.net/#download" rel="nofollow">Anki</a>的插件

<strong>Change Logs</strong>:
<strong>v7.0.0</strong>:
    <strong>Breaking Change:</strong>
        迁移到 pyqt6，现在不兼容 pyqt5
        模板的 image 字段有调整，`v7` 前的版本保存 `src=xxx`，现在保存完整的 `<img src="xxx">`，手动添加图片不会打乱排版了。
    修复欧路词典单词信息不完整、不正确的问题
<strong>v6.1.5</strong>:
    更新有道词典API，解决首次登录无法唤出登陆页的问题
<strong>v6.1.4</strong>:
    修复Anki 2.1.4版本同步失败的问题 THX to <a href="https://github.com/megachweng/Dict2Anki/pull/92">@YLongo</a>
    修复Anki 2.1.4版本首次同步默认到Default Deck的问题
<strong>v6.1.3</strong>:
    修复欧陆字典无法登录的问题 THX to <a href="https://github.com/megachweng/Dict2Anki/pull/84" rel="nofollow">@cythb</a>
<strong>v6.1.2</strong>
    修复有道单词本分组获取失败的问题
<strong>v6.1.1</strong>:
    添加欧陆词典查询API THX to <a href="https://github.com/megachweng/Dict2Anki/pull/73" rel="nofollow">wd</a>
<strong>v6.1.0</strong>:
    支持第三方登陆
    加入模版字段检查
<strong>v6.0.2</strong>:
    添加英英注释 THX to deluser8
<strong>v6.0.1</strong>:
    修复菜单栏不雅词汇
<strong>v6.0.0</strong>:
    导入指定单词分组
    添加必应（bing）词典查询API
    添加待删除单词列表，可选择需要删除的 Anki 卡片
    恢复卡片 <em>短语字段</em>
    一些UI优化
    重构代码，解决上版本奔溃问题
    添加单元测试
<strong>v5.0.2:</strong> 添加单词发音下载功能
<strong>v5.0.1</strong> 解决欧陆词典单词数过大时产生的异常

<strong>Features</strong>:
    导入有道词典、欧陆词典生词本
    检测词典软件的生词变化,并在Anki中相应的添加或删除删除卡片
    获取图片、发音、注解、音标、短语、例句

<strong>How to use</strong>:
同步
<img src = "https://raw.githubusercontent.com/megachweng/Dict2Anki/master/screenshots/sync.gif">

同步删除
<img src = "https://raw.githubusercontent.com/megachweng/Dict2Anki/master/screenshots/del.gif">