import os
import sys
import locale
import argparse

def find_python_files(path):
    """
    查找指定路径下的所有子孙py文件，不包括 __init__.py, 排除头两行包含"# AucoCython No Compile"的文件

    :param path: 要搜索的根目录路径
    :return: 符合条件的py文件路径列表
    """
    valid_py_files = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if file == "__init__.py":
                continue
            if file.endswith('.py'):
                filepath = os.path.join(root, file)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        # 读取头两行
                        line1 = f.readline()
                        line2 = f.readline()

                        # 检查是否包含排除标记
                        if "# AucoCython No Compile" not in line1 and "# AucoCython No Compile" not in line2:
                            valid_py_files.append(filepath)
                except UnicodeDecodeError:
                    # 如果utf-8解码失败，尝试其他编码
                    try:
                        with open(filepath, 'r', encoding='latin-1') as f:
                            line1 = f.readline()
                            line2 = f.readline()

                            if "# AucoCython No Compile" not in line1 and "# AucoCython No Compile" not in line2:
                                valid_py_files.append(filepath)
                    except Exception as e:
                        print(f"无法读取文件 {filepath}: {e}")
                except Exception as e:
                    print(f"处理文件 {filepath} 时出错: {e}")

    return valid_py_files

def parse_arguments():
    # 获取系统语言
    try:
        sys_language, _ = locale.getdefaultlocale()
        lang = 'zh' if sys_language and sys_language.startswith('zh') else 'en'
    except Exception:
        lang = 'en'  # 异常时默认英文

    # 中英文帮助信息配置
    help_messages = {
        'en': {
            'description': 'AutoCython',
            'file_help': 'Compile File Path',
            'path_help': 'Compile directory path',
            'conc_help': 'Compile concurrency count (default: 2)',
            'del_help': 'Remove source code after compilation (default: False)',
            'help_help': 'Show help message',
            'version_help': 'Show program version',
            'version_text': 'v2.0.0',
            'required_error': 'The following arguments are required: {}',
            'epilog': 'Example:\n   AutoCython -f demo.py\n   AutoCython -p path'
        },
        'zh': {
            'description': 'AutoCython',
            'file_help': '编译文件路径',
            'path_help': '编译目录路径',
            'conc_help': '编译并发数（默认：2）',
            'del_help': '编译后删除源代码（默认：False）',
            'help_help': '显示帮助信息',
            'version_help': '显示程序版本',
            'version_text': 'v2.0.0',
            'required_error': '缺少必要参数: {}',
            'epilog': '示例:\n   AutoCython -f demo.py\n   AutoCython -p path'
        }
    }
    msg = help_messages[lang]

    # 创建带自定义错误处理的解析器
    class CustomParser(argparse.ArgumentParser):
        def error(self, message):
            self.print_usage(sys.stderr)
            required_args = [f'--{a.dest}' for a in self._actions if a.required]
            err_msg = msg['required_error'].format(', '.join(required_args))
            sys.stderr.write(f'error: {err_msg}\n')
            sys.exit(2)

    # 配置参数解析器
    parser = CustomParser(
        description=msg['description'],
        epilog=msg['epilog'],
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter
    )

    # 添加参数定义
    required_group = parser.add_argument_group('required arguments')
    required_group.add_argument('-f', '--file', type=str, help=msg['file_help'])
    required_group.add_argument('-p', '--path', type=str, help=msg['path_help'])

    optional_group = parser.add_argument_group('optional arguments')
    optional_group.add_argument('-c', '--conc', type=int, default=2, help=msg['conc_help'])
    optional_group.add_argument('-d', '--del', dest='del_source', type=bool, default=False, help=msg['del_help'])
    optional_group.add_argument('-h', '--help', action='store_true', help=msg['help_help'])
    optional_group.add_argument('-v', '--version', action='store_true', help=msg['version_help'])

    # 解析参数
    args = parser.parse_args()

    # 处理帮助和版本请求
    if args.help:
        parser.print_help()
        sys.exit(0)

    if args.version:
        print(msg['version_text'])
        sys.exit(0)

    if not args.file and not args.path:
        parser.print_help()
        sys.exit(0)

    return args

def show_not_find_file():
    # 获取系统语言
    try:
        sys_language, _ = locale.getdefaultlocale()
        lang = 'zh' if sys_language and sys_language.startswith('zh') else 'en'
    except Exception:
        lang = 'en'  # 异常时默认英文

    if lang == 'zh':
        print("没有找到任何需要编译的文件!")
    else:
        print("No files found that need to be compiled!")

if __name__ == "__main__":
    args = parse_arguments()
    print(f"文件: {args.file}")
    print(f"路径: {args.path}")
    print(f"并发数: {args.conc}")
