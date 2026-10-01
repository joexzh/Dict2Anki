# 用户文件

插件更新会忽略 user_files 文件夹的内容，具体请查看 https://addon-docs.ankiweb.net/addon-config.html#user-files

## 第三方模块

任何项目源文件之外的查询/字典模块可放在 user_files/{queryAPI,dictionary} 内，要求单个 module 文件或带 `__init__.py` 的 package，对外提供对应接口。import 请用相对路径，因为整个 addon 本身是 package。

### 第三方查询 API

要求对外提供 API 类，此类继承自 ..._typing.AbstractQueryAPI (addon._typing.AbstractQueryAPI)。

### 第三方词典

要求对外提供 Dict 类，此类继承自 ..._typing.AbstractDictionary (addon._typing.AbstractDictionary)。
