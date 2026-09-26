# Qt designer UI

生成命令：

```shell
pyuic6 -o ./addon/UIForm/{xxx.py,xxx.ui}
```

## mainUI.py

每次生成后需手动将文件末尾的

```python
from ClickableLineEdit import ClickableLineEdit
```

改成

```python
from .ClickableLineEdit import ClickableLineEdit
```

注意，从绝对改成了相对。
