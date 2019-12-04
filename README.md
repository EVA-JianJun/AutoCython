# AutoCython

==================
**使用Cython批量编译.py文件为.pyd文件！**
![py_pyd][1]

这是一个轮子，让你更加快速的把.py调教为.pyd！
大多数情况下，你只需要这样就可以很快的调教！

    from AutoCython import AutoCython
    AutoCython().compile()

![AutoCython][2]

* **全自动**：自动编译当前目录下所有.py文件，支持指定目录编译或单文件编译；
* **个性化**：支持指定排除目录或排除文件跳过编译；
* **高效率**：默认利用全部CPU核心，也可指定使用核心数量；
* **易纠错**：快速纠错，在编译失败时能极快的获取错误信息；

## 前置

Cython : <https://github.com/cython/cython>

### Cython前置

如果你已经正确安装配置好Cython，那么你可以不用看这；

推荐C、C++编译器gcc和VS选一个，其他编译器能否使用未知，具体的安装请查阅Cython的安装教程；

目前测试了64位Python3.6与gcc 64位，与VS2017下都可以通过编译；
**需要注意的是，如果你使用的Python是64位的，那么对应的C、C++编译器也必须为64位；**

vs安装简便，占用空间大，配置简单；gcc安装简便，占用空间小，配置比较复杂；
不想折腾的话安装vs，想精简一点的话安装gcc。

**win下gcc推荐安装MinGW**：

* 64位：<http://mingw-w64.org/>
* 32位：<http://www.mingw.org/>

具体安装Cython过程请查阅相关资料

## 使用方式

编译当前目录下能找到的所有py文件：

    from AutoCython import AutoCython
    ac = AutoCython()
    ac.compile()

### 自定义

AutoCython类接受4个参数，默认为：compile_path='.', exclude=[], mode='f', delete=['b', 'p', 'c']

    compile_path ： str ，需要编译的目录；

    exclude      ： list，需要排除的目录或者文件：
                        eg ：['./abc', './a_path/test.py', 'test2.py']
                        这么写会排除目录./abc下的所有.py文件，排除./a_path/test.py文件，排除所有名为test2.py的文件不进行编译

    mode         ： str， 指定使用CPU核心数：
                        'f' : 使用全部CPU核心
                        'n' : 只使用一个,相当于单进程
                        '4' : 使用4个CPU核心，输入指定使用的数目

    delete       :  list, 指定编译后需要清理的临时文件，一般默认就好：
                         b  ： build文件夹
                         p  ： 中间文件setup_file py文件
                         c  ： 产生的c文件
                         s  ： 源代码文件，慎用
                         all： 全部清理

**例子：**

编译目录 D:/python_code/ProjectPath 下的所有.py文件；

排除所有名为 tmp.py 的文件，排除 ./ProjectPath/print_cy.py 文件，排除 ./ProjectPath/data/tmp 目录下的文件不编译；

使用8个CPU核心；

只删除编译后产生的build文件夹和中间文件setup_file，保留C代码。

    from AutoCython import AutoCython
    ac = AutoCython(compile_path='D:/python_code/ProjectPath', exclude=['tmp.py','./ProjectPath/print_cy.py','./ProjectPath/data/tmp'], mode='8', delete=['b', 'p'])
    ac.compile()

AutoCython类里compile和compile_file函数的使用和函数参数请参考源代码，参数功能为控制阻塞，并发处理等。

### 错误处理

在这个目录下：
![文件目录][3]

运行如下代码只编译目录 build_test\ 下的.py文件;

    from AutoCython import AutoCython
    ac = AutoCython('./build_test/')
    ac.compile()

**程序默认会打印出错误文件的错误日志**
![错误编译][4]

可以看到 .\build_test\新建文本文档.py 和 .\build_test\test1\test2.py 发生错误，如何手动查看错误信息？
在ipython下直接打.ac按TAB，选择 **compile_result**：
![compile_result][5]

再按TAB，好了，这时候所有的编译任务都调出来了，错误的任务名称以 **ERR_** 开头，正确的以 **OK_** 开头：
![错误任务][6]

选择编号为**2**，错误文件名为test2的任务：

![任务属性][7]

其下的属性中其中 **err** 为错误输出；**out** 为正常输出；**base** 为任务Popen对象；**ExitCode** 为编译退出时错误代码，与系统保持一致；**PyPath** 为源文件目录；**PydPath** 为编译生成的pyd文件目录。

**查看错误信息：**
![错误信息][8]

可以看到**test2.py**为使用了Cython不支持的函数功能print(end='')，**新建文本文档.py**为文件命名不符合规范，导致编译失败。

* 对于print(end='')使用end参数不能编译通过，可以外部导入一个print_no_end.py文件，其中自定义end=''的函数，然后不编译这个print_no_end.py这个文件就好。
* 解决的方法一是重新命名 新建文本文档.py ，让其文件名符合C命名规范;

至于其他遇到的问题怎么改，请查阅Cython的文档，这只是个轮子。重新编译错误文件可以使用compile_file函数单独编译。

**在编译时系统会为每一个文件分配一个ID，如果有同名文件，其中一个错误，可以通过ID很好的找到对应的文件进行错误处理。**

所以错误处理你只需要按几个TAB就可以查看了，我觉得我这里已经写的够懒了！

## 命令行

除了把AutoCython作为包导入外，AutoCython也支持直接命令行进行编译：

与上面功能一样的命令行写法:

    python AutoCython.py -C D:/python_code/ProjectPath -E tmp.py;./ProjectPath/print_cy.py;./ProjectPath/data/tmp -M 8 -D bp

除了AutoCython.py外我在 **[releases][9]** 中也提供了exe程序 ![exe图标][10]可以直接在win下使用：

    AutoCython build_test

![命令行][11]

  [1]: https://ws3.sinaimg.cn/large/8253c4ddly1fzj3wzhaeaj20xc0njav8.jpg
  [2]: https://ws2.sinaimg.cn/large/8253c4ddly1fziy5tgpw2j21740pr7wh.jpg
  [3]: https://ws4.sinaimg.cn/large/8253c4ddly1fzgmw57xpuj21740prkjl.jpg
  [4]: https://ws2.sinaimg.cn/large/8253c4ddly1fzixse4vw9j21740prb29.jpg
  [5]: https://ws4.sinaimg.cn/large/8253c4ddly1fziyae76u4j20jy02iq4d.jpg
  [6]: https://ws2.sinaimg.cn/large/8253c4ddly1fziybwsx9oj20je02iq4f.jpg
  [7]: https://ws2.sinaimg.cn/large/8253c4ddly1fziyeaaqosj20e002imy5.jpg
  [8]: https://ws2.sinaimg.cn/large/8253c4ddly1fziygp52y3j21740prb29.jpg
  [9]: https://github.com/EVA-JianJun/AutoCython/releases
  [10]: https://ws2.sinaimg.cn/large/8253c4ddly1fziyi8nmofj203c03cq32.jpg
  [11]: https://ws2.sinaimg.cn/large/8253c4ddly1fzhe4nnwwgj21740pr7wh.jpg