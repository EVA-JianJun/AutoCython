# AutoCython V2
中文 | [English](https://github.com/EVA-JianJun/AutoCython/blob/master/README.en.md)

**自动 Cython：一键将 Python 文件批量编译为 `PYD / SO` 文件**
![py_pyd](https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20250623.png)

## ✨ 特性
- 单文件/多文件批量编译
- 跨平台支持 (Windows/Linux/MacOS)
- 简洁命令行界面

## 📦 安装
```bash
pip install -U AutoCython-jianjun
```

## ⚙️ 依赖环境
### C/C++ 编译器
- **Windows**: Visual Studio
- **Linux**: gcc & g++

**重要提示**：编译器架构必须与Python解释器一致（64位Python需64位编译器）

> 其他编译器配置请参考 [Cython](https://github.com/cython/cython) 项目

## 🚀 使用指南
### 命令行操作
![命令行演示](https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20250609_1.png)

```bash
# 编译单个文件
AutoCython -f test.py

# 编译整个目录
AutoCython -p D:/python_code/ProjectPath

# 编译后删除源代码 (默认不删除)
AutoCython -d True -f test.py
AutoCython -d True -p D:/python_code/ProjectPath
```

### 编译界面
![AutoCython GUI](https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20250609_2.png)

### 手动排除文件不编译
在文件头部 **前两行** 添加声明：
```python
# AutoCython No Compile
# 此文件将跳过编译处理
```

## ⚠️ 常见问题解决

一般是源代码中有 Cython 不支持的语句, 或者文件名不支持等.
 可以查阅 [Cython Wiki](https://github.com/cython/cython/wiki) 项目 官方文档, 或者提 Issue.

## 📅 更新记录
### V2 版本
1. 20250623 release V2.1.0 禁用激进的性能优化选项. 显示系统信息.
2. 20250609 release V2.0.0 重构了代码, 使用新的界面 (不安全版本)

### V1 版本
1. 20220613 更新对Linux的支持, Linux下需要配置gcc&g++
2. 20221123 可以通过文件头手动指定不编译的文件
3. 20230306 更新可以指定命令行头如 `Python310` 以此支持非Widnows系统下编译
4. 20230324 更新文档
5. 20240506 修复编译失败时遗漏复原 \_\_init\_\_.py 的问题