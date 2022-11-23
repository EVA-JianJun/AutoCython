#!/use/bin/dev python
# -*- coding: utf-8 -*-
import os
import sys
import time
import getopt
import shutil
import platform
import traceback
from threading import Thread, Lock
from subprocess import Popen, PIPE
from concurrent.futures import as_completed, ThreadPoolExecutor
from typing import Union

sysstr = platform.system()
if (sysstr == "Windows"):
    DLL_TYPE = "pyd"
elif (sysstr == "Linux"):
    DLL_TYPE = "so"
else:
    DLL_TYPE = "pyd"

class Container(object):
    def __setitem__(self, key, value):
        self.__setattr__(key, value)

class Popen_out():

    def __init__(self, po : Popen, py_path : str, pyd_path=None) -> None:

        self._system = platform.system()

        self.base = po
        self.ExitCode = po.wait()
        self.PyPath = py_path
        self.PydPath = pyd_path
        if self._system == 'Windows':

            self.out = po.stdout.read().decode('utf-8', errors='ignore')
            self.err = po.stderr.read().decode('utf-8', errors='ignore')
        else:
            # utf-8
            self.out = po.stdout.read().decode()
            self.err = po.stderr.read().decode()

class AutoCython():

    def __init__(self, compile_path='.', exclude=[], mode='f', delete=['b','p','c']):
        """[summary]

        [description]
            初始化编译参数
        Parameters
        ----------
        compile_path : {str}, optional
            [description] (the default is '.', which [default_description])
                需要编译的文件夹,默认为当前工作目录下的所有能找到的.py文件
        exclude : {list}, optional
            [description] (the default is [], which [default_description])
                需要排除的目录或者文件
        mode : {str}, optional
            [description] (the default is 'f', which [default_description])
                运行模式
        delete : {list}, optional
            [description] (the default is ['b','p','c'], which [default_description])
                编译后需要清理的文件种类
        """

        # 锁
        self._compile_lock = Lock()
        # 根据系统的不同获取不同路径分隔符
        self._sp = os.path.join('a','a')[1:-1]

        # 需要编译的目录
        self.compile_path = self._fitter_path(compile_path)
        self.exclude = exclude
        # 需要排除的文件,写全路径就是绝对指定文件,只写文件名就同名文件全部不编译
        self._exclude_file_list = list(map(self._fitter_path, [ex for ex in exclude if ex[-3:] == '.py']))
        # 需要排除的目录
        self._exclude_path_list = list(map(self._fitter_path, [ex for ex in exclude if ex[-3:] != '.py']))

        # 接收结果的字典
        self.compile_result = Container()

        self.mode = mode
        # 编译时使用的cpu核数
        if mode in ('f', 'fast'):
            # cpu核数
            self._cpu_core_count = int(os.cpu_count() / 4)
            if not self._cpu_core_count:
                self._cpu_core_count = 1
        elif mode in ('n', 'normal'):
            # 使用1核
            self._cpu_core_count = 1
        else:
            # 用户指定
            try:
                self._cpu_core_count = int(mode)
            except Exception:
                self._cpu_core_count = 1

        # 编译后需要删除的目录
        self.delete = delete

        # 注意源代码里不要有build文件夹
        self._setup_file_str = '#!/use/bin/dev python\n# -*- coding: utf-8 -*-\nfrom distutils.core import setup\nfrom Cython.Build import cythonize\nsetup(ext_modules = cythonize("{0}"))'
        self._Popen_cmd = 'python {0} build_ext --inplace'

    def _fitter_path(self, path : str) -> str:
        """ 让一个路径的分隔符统一为当前系统下的 """
        return path.replace('/', self._sp).replace('\\', self._sp).rstrip(self._sp)

    def _get_all_file_list(self, path='.', file_type=[], file_name=[]) -> list:
        """ 获取某个目录下的某类文件或某文件名路径列表 """
        all_file = list()
        try:
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    if file_type or file_name:
                        _, filename = os.path.split(file_path)
                        if filename.split('.')[-1] in file_type and file.find('AutoCython') == -1:
                            all_file.append(file_path)
                        if filename in file_name:
                            all_file.append(file_path)
                    else:
                        all_file.append(file_path)
                elif os.path.isdir(file_path):
                    all_file.extend(self._get_all_file_list(file_path, file_type, file_name))
        except FileNotFoundError:
            pass
        finally:
            return all_file

    def _get_all_path_list(self, path='.', file_type=[]) -> list:
        """ 获取某个目录下的某文件路径列表 """
        all_path = list()
        try:
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isdir(file_path):
                    if file_type:
                        _, filename = os.path.split(file_path)
                        if filename in file_type:
                            all_path.append(file_path)
                    else:
                        all_path.append(file_path)
                    all_path.extend(self._get_all_path_list(file_path, file_type))
        except FileNotFoundError:
            pass
        finally:
            return all_path

    def compile_file(self, file_path : str, wait=False, delete=[], complicating=False) -> Popen:
        """ 编译一个文件 """
        # complicating : 本函数是否是并发运行,如果是的话要特殊处理build文件夹
        def delete_tmp_file(cython_popen, dirname, filename, setup_file, delete, complicating) -> None:
            """ 清理编译后残留的文件 """
            def rmtree(path, name):
                try:
                    shutil.rmtree(os.path.join(path, name))
                except (FileNotFoundError,PermissionError):
                    pass

            def remove(path, name):
                try:
                    os.remove(os.path.join(path, name))
                except (FileNotFoundError,PermissionError):
                    pass

            exit_code = cython_popen.wait()
            for file_code in delete:
                try:
                    if file_code in ('build', 'b'):
                        if not complicating:
                            # 不是并发式,直接删除build编译临时文件夹
                            # 是并发的情况下会在所有任务完成后统一删除build文件夹
                            rmtree(dirname, 'build')
                    elif file_code in ('py','.py','p'):
                        # 删除编译产生的setup_file
                        remove(dirname, setup_file)
                    elif file_code in ('c',):
                        # 删除编译产生的C代码
                        remove(dirname, filename[:-3] + '.c')
                    elif file_code in ('s',):
                        # 删除源source py源文件
                        if exit_code == 0:
                            # 正常退出的情况下才删除
                            remove(dirname, filename)
                    elif file_code in ('all', 'ALL', 'A'):
                        # 删除除编译好的pyd文件外的所有文件
                        if complicating:
                            filename_name = filename[:-3]
                            for file in self._get_all_file_list(os.path.join(dirname, 'build')):
                                if filename_name in file:
                                    try:
                                        os.remove(file)
                                    except PermissionError:
                                        pass
                        else:
                            rmtree(dirname, 'build')

                        remove(dirname, setup_file)
                        remove(dirname, filename[:-3] + '.c')

                        if exit_code == 0:
                            remove(dirname, filename)

                        break
                except FileNotFoundError:
                    pass

        try:
            dirname, filename = os.path.split(file_path)
            setup_file = 'AutoCython_' + filename
            if not dirname:
                dirname ='.'
            with open(os.path.join(dirname, setup_file), 'w', encoding='utf-8') as f:
                f.write(self._setup_file_str.format(filename))

            if not complicating and os.path.isfile(os.path.join(dirname, "__init__.py")):
                os.rename(os.path.join(dirname, "__init__.py"), os.path.join(dirname, "___init__.py"))

            # Popen('python AutoCython_DataServerClient_Alice.py build_ext --inplace', stdout=PIPE, stderr=PIPE, cwd='build_test/test1\\')
            cython_popen = Popen(self._Popen_cmd.format(setup_file).split(" "), stdout=PIPE, stderr=PIPE, cwd=dirname)

            if delete:
                delete_tmp_file_th = Thread(target=delete_tmp_file, args=(cython_popen, dirname, filename, setup_file, delete, complicating))
                delete_tmp_file_th.start()

            if wait:
                cython_popen.wait()
                if not complicating and os.path.isfile(os.path.join(dirname, "___init__.py")):
                    os.rename(os.path.join(dirname, "___init__.py"), os.path.join(dirname, "__init__.py"))

            if not complicating and cython_popen.wait() != 0:
                # 错误是输出
                err_po = Popen_out(cython_popen, file_path)
                print('\033[0;37;41m' + file_path, ':\033[0m')
                print(err_po.out)
                print(err_po.err)
                print()

            return cython_popen, file_path

        except Exception as err:
            print('\033[0;37;41m', file_path, "编译运行失败!\033[0m")
            traceback.print_exc()
            print(err)
            return None

    def compile(self, wait=True, delete=[], log=True) -> None:
        """ 编译所有文件 """
        def compile_th(delete):
            if self._compile_lock.locked():
                print("Waiting for the end of the previous task")

            self._compile_lock.acquire()
            try:
                st = time.time()
                if not delete:
                    delete = self.delete

                # 重命名所有__init__.py文件,这个文件存在生成的pyd会跑到二级目录
                self._re_init_file_dict = dict()
                for init_file_path in self._get_all_file_list(file_name=['__init__.py']):
                    # 重命名为___init__.py
                    path, name = os.path.split(init_file_path)
                    new_name = '_' + name
                    new_file_path = os.path.join(path, new_name)
                    self._re_init_file_dict[init_file_path] = new_file_path
                    os.rename(init_file_path, new_file_path)

                # 获取所有的py文件
                py_file_path_iter = map(self._fitter_path, self._get_all_file_list(self.compile_path, ['py']))
                self._exclude_file_list.extend(['__init__.py','___init__.py'])
                # 剔除不需要编译的文件
                py_file_path_iter = filter(lambda file_path : file_path not in self._exclude_file_list, py_file_path_iter)
                # 剔除全部只标注了文件名的文件
                # exclude_file_absolute_set = set(filter(lambda file_path : file_path.find(self._sp) == -1 and file_path.split('.')[-1] == 'py', self._exclude_file_list))
                py_file_path_iter = filter(lambda py_file_path : not bool(set(filter(lambda file_path : file_path.find(self._sp) == -1 and file_path.split('.')[-1] == 'py', self._exclude_file_list)) & set(py_file_path.split(self._sp))), py_file_path_iter)
                # 剔除不需要编译的路径
                py_file_path_list = list(filter(lambda py_file_path : not any([exclude_path in py_file_path for exclude_path in self._exclude_path_list]), py_file_path_iter))

                # 检查不编译的文件
                tmp_py_file_path_list = []
                for file_path in py_file_path_list:
                    with open(file_path, "r", encoding="utf-8") as fr:
                        line1 = fr.readline().strip()
                        line2 = fr.readline().strip()

                    if line1 == "# AucoCython No Compile" or line2 == "# AucoCython No Compile":
                        pass
                    else:
                        tmp_py_file_path_list.append(file_path)
                py_file_path_list = tmp_py_file_path_list

                self.compile_result = Container()
                err_task_dict = dict()
                task_index_dict = dict()
                print("Initialize compilation information")
                for i in range(len(py_file_path_list)):
                    print('{0:<4} path : {1}'.format(i, py_file_path_list[i]))
                    task_index_dict[py_file_path_list[i]] = str(i)
                print("Compiling...")
                # 创建线程池
                pool = ThreadPoolExecutor(self._cpu_core_count)
                # 添加任务
                task_list = list()
                for py_file_path in py_file_path_list:
                    task_list.append(pool.submit(self.compile_file, py_file_path, True, delete, True))
                # 接收结果
                for task in as_completed(task_list):
                    cython_popen, file_path = task.result()
                    if cython_popen.wait():
                        # 编译错误
                        try:
                            _, file_name = os.path.split(file_path)
                            po = Popen_out(cython_popen, file_path)
                            self.compile_result['ERR_' + task_index_dict[file_path] + '_' +file_name[:-3]] = po
                            err_task_dict['ERR_' + task_index_dict[file_path] + '_' +file_name[:-3]] = po
                        except Exception as err:
                            print("\033[0;37;41m任务信息记录失败!\033[0m")
                            traceback.print_exc()
                            print(err)
                        else:
                            print('{0:<4} Info : \033[0;37;41mERR\033[0m  path : {1}'.format(task_index_dict[file_path], file_path))
                    else:
                        # 编译正确
                        try:
                            path, file_name = os.path.split(file_path)
                            pyd_name = list(filter(lambda name : name.split('.')[-1] == DLL_TYPE and name.split('.')[0] == file_name[:-3], os.listdir(path)))[0]
                            pyd_path = os.path.join(path, pyd_name)
                            self.compile_result['OK_' + task_index_dict[file_path] + '_' + file_name[:-3]] = Popen_out(cython_popen, file_path, pyd_path)
                        except Exception as err:
                            print("\033[0;37;41m任务信息记录失败!\033[0m")
                            print(file_path)
                            traceback.print_exc()
                            print(err)
                        else:
                            print('{0:<4} Info : \033[0;37;44m OK\033[0m  path : {1} -> {2}'.format(task_index_dict[file_path], file_path, pyd_path))
                # 全部结束后清理build文件夹
                for rm_path in self._get_all_path_list(self.compile_path, file_type=['build', '__pycache__']):
                    shutil.rmtree(rm_path)
                # 逆向重命名
                for old_file, new_file in self._re_init_file_dict.items():
                    os.rename(new_file, old_file)
                print("time cost : ", time.time() - st)
                print("complete!\n")
                if log:
                    for err_file_name, err_po in err_task_dict.items():
                        print('\033[0;37;41m' + err_file_name, ':\033[0m')
                        print("path : ", err_po.PyPath)
                        print(err_po.out)
                        print(err_po.err)
                        print()
            finally:
                self._compile_lock.release()

        compile_thread = Thread(target=compile_th, args=(delete,))
        compile_thread.start()
        if wait:
            compile_thread.join()

class AC_getopt_argv():

    def __init__(self):
        """ 初始化默认参数 """
        self.compile_path = '.'
        self.exclude = []
        self.mode = 'f'
        self.delete = ['b','p','c']

        # a file
        self.file_path = ''
        self.a_file_flag = False

        self.version = 'AutoCython V1.2.8'
        # 像这样写格式好看一点
        self.help_info =(
                        "Usage: AutoCython [options] ...\n"+
                        "Options:\n"+
                        "  -f -F --file                Compile only a .py file.\n"+
                        "  -c -C --compile             Compile and assemble all .py files under the path.\n"+
                        "  -e -E --exclude             Excluded .py files or all .py files in a path, Used ';' split file or path.\n"+
                        "  -m -M --mode                Compile mode of 'f'(fast) used a quarter of all CPU core, 'n'(normal) only used one CPU core,\n"+
                        "                                    or used a number eg '4' of used CPU core what you want.\n"+
                        "  -d -D --delete              Select to delete the file generated after compilation\n"+
                        "                                    b : The build path\n"+
                        "                                    p : The setup_file\n"+
                        "                                    c : The .c file\n"+
                        "                                    s : The .py source code\n"+
                        "                                format:\n"+
                        "                                    eg : 'bp' or 'bps'\n"+
                        "                                    default: 'bpc'\n"+
                        "  -h -H --help                Display command line options of sub-processes.\n"+
                        "        --ch                  Display Chinese command line options of sub-processes.\n"+
                        "  -v -V --version             Display compiler version information.\n"
                        )

        self.help_info_ch =(
                        "命令行: AutoCython [选项] ...\n"+
                        "选项:\n"+
                        "  -f -F --file                编译一个.py文件.\n"+
                        "  -c -C --compile             编译目录下的所有.py文件.\n"+
                        "  -e -E --exclude             编译时忽略的.py文件和忽略编译的目录, 使用';'字符分割参数.\n"+
                        "  -m -M --mode                编译使用的CPU核心数量.\n"+
                        "                                    fast模式: 使用 Autocython -m f 表示使用所有CPU核心数的四分之一\n"+
                        "                                    normal模式: 使用 Autocython -m n 使用1核心进行编译\n"+
                        "                                    number模式: 使用 Autocython -m 2 指定使用2核心进行编译\n"+
                        "  -d -D --delete              选择删除编译后生成的临时文件.\n"+
                        "                                    b : build 目录\n"+
                        "                                    p : setup.py 文件\n"+
                        "                                    c : .c 中间代码\n"+
                        "                                    s : .py 源代码\n"+
                        "                                格式:\n"+
                        "                                    例 : 'bp' 或者 'bps'\n"+
                        "                                    默认: 'bpc'\n"+
                        "  -h -H --help                显示命令行帮助文档.\n"+
                        "        --ch                  显示中文命令行帮助文档.\n"+
                        "  -v -V --version             显示编译器版本信息.\n"
                        )

    def geto(self) -> Union[str, list, str, list]:
        """ 获取命令行参数 """
        try:
            opts, args = getopt.getopt(sys.argv[1:],"hHvVF:f:C:c:E:e:M:m:D:d:",["help","version","ch","file=","compile=","exclude=","mode=","delete="])
            if not opts and not args:
                print(self.help_info + '\n' + self.version)
                sys.exit()
        except getopt.GetoptError:
            print("\033[1;34;41mErr : Get err Command Line!\033[0m")
            print(self.help_info)
            sys.exit(1)

        if args:
            if os.path.isfile(args[0]):
                self.file_path = args[0]
                self.a_file_flag = True
            else:
                self.compile_path = args[0]

        for opt, arg in opts:
            if opt in ('-h', '-H','--help'):
                print(self.help_info + '\n' + self.version)
                sys.exit()
            elif opt in ('--ch', ):
                print(self.help_info_ch + '\n' + self.version)
                sys.exit()
            elif opt in ('-v', '-V','--version'):
                print(self.version)
                sys.exit()
            elif opt in ('-F', '-f','--file'):
                self.file_path = arg
                self.a_file_flag = True
            elif opt in ('-C', '-c','--compile'):
                self.compile_path = arg
            elif opt in ('-E', '-e','--exclude'):
                self.exclude = arg.split(';')
            elif opt in ('-M', '-m','--mode'):
                self.mode = arg
            elif opt in ('-D', '-d','--delete'):
                self.delete = list(arg)

        if self.a_file_flag:
            ac = AutoCython()
            ac.compile_file(self.file_path, wait=True, delete=self.delete, complicating=False)
            sys.exit()

        return self.compile_path, self.exclude, self.mode, self.delete

if __name__ == '__main__':
    """ CMD """
    ac = AutoCython(*AC_getopt_argv().geto())

    ac.compile()
