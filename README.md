
## Dict2Anki-ng

**Dict2Anki-ng** is a fork from [Dict2Anki](https://github.com/megachweng/Dict2Anki)（原作者：[@megachweng](https://github.com/megachweng)），迁移到 Qt 6 和新版 anki，主要功能与原版一致。

**Dict2Anki** 是一款方便[有道词典](http://cidian.youdao.com/multi.html)、[欧路词典](https://www.eudic.net/)用户同步生成单词本卡片至[Anki](https://apps.ankiweb.net/#download)的插件

> **Note:**  
> 无论导入有道还是欧路词典的生词本，都推荐使用【查询 - 有道 API】。欧路词典API容易触发限流。

### Change log
___
* v7.2.3
  * 支持登录窗口最大化
* v7.2.2
  * 【待删除】增加批量复选框
* v7.2.1
  * 修复单元测试
* v7.2.0
  * 【默认配置】新增【每分钟查询次数】
* v7.1.0
  * 增加字段修复功能
* v7.0.0
  * **Breaking Changes:**
    * 迁移到 Qt 6，不兼容 Qt 5
    * 模板的 sentence, phrase 字段有调整，不再使用 `<table>` 格式。
    * 模板的 image 字段有调整，`v7` 前的版本保存 `src=xxx`，现在保存完整的 `<img src="xxx">`，手动添加图片不会打乱排版了。
  * 修复欧路词典单词信息不完整、不正确的问题。有道词典的部分未作修改。
* v6.1.6
  * 修复ARM Mac启动日志出错的问题 THX to <a href="https://github.com/megachweng/Dict2Anki/pull/108">@xbot</a>  
* v6.1.5  
  * 更新有道词典API，解决首次登录无法唤出登陆页的问题  
* v6.1.4
  * 修复Anki 2.1.4版本同步失败的问题 THX to <a href="https://github.com/megachweng/Dict2Anki/pull/92">@YLongo</a>
  * 修复Anki 2.1.4版本首次同步默认到Default Deck的问题
* v6.1.3
    修复欧路字典无法登录的问题 THX to <a href="https://github.com/megachweng/Dict2Anki/pull/84" rel="nofollow">@cythb</a>  
* v6.1.2
    修复有道单词本分组获取失败的问题  
* v6.1.1
    添加欧路词典查询API THX to <a href="https://github.com/megachweng/Dict2Anki/pull/75" rel="nofollow">@wd</a>  
* v6.1.0
    * 支持第三方登陆
    * 加入模版字段检查
* v6.0.2
    添加英英注释 THX to deluser8
* v6.0.1
    修复菜单栏不雅词汇
* v6.0.0
    * 导入指定单词分组
    * 添加必应（bing）词典查询API
    * 添加待删除单词列表，可选择需要删除的 Anki 卡片
    * 恢复卡片 *短语字段*
    * 一些UI优化
    * 重构代码，解决上版本奔溃问题
    * 添加单元测试

### Features

* 导入有道词典、欧路词典生词本
* 检测词典软件的生词变化,并在Anki中相应的添加或删除删除卡片
* 获取图片、发音、注解、音标、短语、例句

### How to install

Anki --> 工具 --> 附加组件 --> 获取插件  
插件代码：107281012

### How to use

同步  
![同步](https://raw.githubusercontent.com/joexzh/Dict2Anki/master/screenshots/sync.gif)

同步删除  
![同步删除](https://raw.githubusercontent.com/joexzh/Dict2Anki/master/screenshots/del.gif)

字段修复  
![字段修复](https://raw.githubusercontent.com/joexzh/Dict2Anki/master/screenshots/repair.png)

### Contribute Guide

非常欢迎你的贡献，请PR前确保通过了全部单元测试 `pytest test`

### Development Guide

Python 3.9

在 `venv` 环境中，运行：

```bash
pip install -r requirements.txt
```

单独运行 UI：

```bash
(cd .. && python -m Dict2Anki)
```

生成 UI 文件：

```bash
pyuic6 -o ./addon/UIForm/xxx.py ./addon/UIForm/xxx.ui
```