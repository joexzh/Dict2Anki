
## Dict2Anki-ng

**Dict2Anki-ng** is a fork from [Dict2Anki](https://github.com/megachweng/Dict2Anki)，目的是兼容 PyQt6 和新版 anki，主要与功能原版一致。

**Dict2Anki** 是一款方便[有道词典](http://cidian.youdao.com/multi.html)、[欧陆词典](https://www.eudic.net/)用户同步生成单词本卡片至[Anki](https://apps.ankiweb.net/#download)的插件


### Change log
___

* v7.0.0
  * **Breaking Change:**
    * 迁移到 pyqt6，现在不兼容 pyqt5
    * 模板的 image 字段有调整，`v7` 前的版本保存 `src=xxx`，现在保存完整的 `<img src="xxx">`，手动添加图片不会打乱排版了。
  * 修复欧路词典单词信息不完整、不正确的问题
* v6.1.6
  * 修复ARM Mac启动日志出错的问题 THX to <a href="https://github.com/megachweng/Dict2Anki/pull/108">@xbot</a>  
* v6.1.5  
  * 更新有道词典API，解决首次登录无法唤出登陆页的问题  
* v6.1.4
  * 修复Anki 2.1.4版本同步失败的问题 THX to <a href="https://github.com/megachweng/Dict2Anki/pull/92">@YLongo</a>
  * 修复Anki 2.1.4版本首次同步默认到Default Deck的问题
* v6.1.3
    修复欧陆字典无法登录的问题 THX to <a href="https://github.com/megachweng/Dict2Anki/pull/84" rel="nofollow">@cythb</a>  
* v6.1.2
    修复有道单词本分组获取失败的问题  
* v6.1.1
    添加欧陆词典查询API THX to <a href="https://github.com/megachweng/Dict2Anki/pull/75" rel="nofollow">@wd</a>  
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

 
### How to install
Anki --> 工具 --> 附加组件 --> 获取插件  
插件代码：1284759083
### How to use
同步
<img src = "https://raw.githubusercontent.com/megachweng/Dict2Anki/master/screenshots/sync.gif"></span>

同步删除
<img src = "https://raw.githubusercontent.com/megachweng/Dict2Anki/master/screenshots/del.gif"></span>

### Contribute Guide
非常欢迎你的贡献，<del>请PR前确保通过了全部单元测试 `pytest test`。</del>暂时没有 unit test。

### Development Guide
Python > 3.8 
```
export PYTHONPATH='xxx/Dict2Anki'  
export DEVDICT2ANKI=1  
pip install -r requirements.txt  
python __init__.py
```
