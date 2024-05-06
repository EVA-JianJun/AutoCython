# AutoCython

**自动 Cython, 使用 Cython 批量编译 `.py` 文件为 `.pyd` 文件！**
![py_pyd][1]

## 安装

    pip install AutoCython-jianjun

## 依赖

[Cython](https://github.com/cython/cython) 和 C/C++ 编译器

**如果你都配置完毕了你可以跳过本节.**

### Cython

```
pip install Cython
```

### C/C++ 编译器

推荐 `gcc` 和 `visual studio` 选一个, 其他编译器请查阅 Cython 文档.

* `VS` 安装简便, 占用空间大, 配置简单.
* `gcc` 安装简便, 占用空间小, 配置比较复杂.

不想折腾或者你是 Windows 的话推荐安装 VS, Linux 等系统可以直接使用自带的 gcc。

大部分的编译环境都可以使用, 我在 Win, Linux, Mac, Python3.6 到 Python3.10 都可以使用.

**需要注意的是, 如果你使用的 Python 是64位的, 那么对应的 C、C++ 编译器也必须为64位；**

**win下gcc推荐安装MinGW**：

* 64位：<http://mingw-w64.org/>
* 32位：<http://www.mingw.org/>

## 使用

![命令行][11]

### 命令行

使用命令行进行编译：

`AutoCython -h` 或者 `AutoCython --ch` 查看英文和中文帮助.

    # 编译一个文件
    AutoCython -f test.py

    # 编译一个目录
    AutoCython -C D:/python_code/ProjectPath

![AutoCython][2]

**例子**

编译目录 `D:/python_code/ProjectPath`\
排除所有名为 `tmp.py` 的文件\
排除 `./ProjectPath/print_cy.py` 文件\
排除 `./ProjectPath/data/tmp` 目录下的文件不编译\
使用2个CPU核心\
只删除编译后产生的 `build` 文件夹和中间文件 `setup_file`, 保留自动生成的 `C` 代码.\

    AutoCython -C D:/python_code/ProjectPath -E tmp.py;./ProjectPath/print_cy.py;./ProjectPath/data/tmp -M 2 -D bp

## 特性

* **全自动**：自动编译当前目录下所有.py文件, 支持指定目录编译或单文件编译；
* **个性化**：支持指定排除目录或排除文件跳过编译；
* **高效率**：默认启动进程数为cpu核心数四分之一, 大多数情况下可以把cpu跑满；
* **易纠错**：快速纠错, 在编译失败时能极快的获取错误信息；

### 常见错误

* `print(end='')`\
Cython 不支持 print 函数的 end 参数, 可以在外部定义 `def my_print(*args, **kwargs): print(*args, end='', **kwargs)`, 然后在需要编译的文件中导入这个外部函数.

* `新建文本文档.py`\
文件名需要符合  `C` 命名规范

其他问题请查阅 `Cython` 官方文档.

### 手动指定不编译

在不需要编译的文件 **头两行** 任意一行写上 `# AucoCython No Compile` 则该文件会跳过编译.

## 更新记录
1. 20220613 更新对Linux的支持, Linux下需要配置gcc&g++
2. 20221123 可以通过文件头手动指定不编译的文件
3. 20230306 更新可以指定命令行头如 `Python310` 以此支持非Widnows系统下编译
4. 20230324 更新文档
5. 20240506 修复编译失败时遗漏复原 __init__.py 的问题

  [1]: https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20210824.png
  [2]: https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20200316_2.jpg
  [3]: https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20200316_3.jpg
  [4]: https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20200316_4.jpg
  [5]: https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20200316_5.jpg
  [6]: https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20200316_6.jpg
  [7]: https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20200316_7.jpg
  [8]: https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20200316_8.jpg
  [9]: https://github.com/EVA-JianJun/AutoCython/releases
  [10]: https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20200316_10.jpg
  [11]: https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20200316_11.jpg