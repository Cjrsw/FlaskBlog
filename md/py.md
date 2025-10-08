## Python中以下值被认为是假值（false）：
None
False
数字 0（包括 0.0, 0j）
空序列（如 '', [], ()）
空映射（如 {}）
其他定义了 __bool__() 返回 False 或 __len__() 返回 0 的对象
除了上述情况，其他值都被认为是真值（truthy）。
## pip是一个包管理工具，用于安装、更新和卸载Python包。
### 安装最新版

```
pip install <package_name>
```
### 安装指定版本
```
pip install <package_name>==1.0.4
```
### 从需求文件安装 (项目依赖管理)
```
pip install -r requirements.txt
```
### 列出已安装的包
```
pip list
```
### 生成需求文件
```
pip freeze > requirements.txt
```
### 卸载包
```
pip uninstall <package_name>
```
## python项目文件夹如果移动，需要重新导入依赖虚拟环境
虚拟环境并不是完整的python解释器，只是有指向的功能，并且独立存放python依赖



