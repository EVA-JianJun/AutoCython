import os
from .run_tasks import run_tasks
from .compile import compile_to_binary
from .tools import parse_arguments, find_python_files
from .tools import show_path_not_find_file, show_file_find_file, show_path_find_file

def compile():
    args = parse_arguments()

    if args.file:
        if os.path.isfile(args.file):
            compile_file = args.file
            del_source = args.del_source
            tasks = [
                # 函数, 位置参数, 关键字参数
                (compile_to_binary, compile_file, (compile_file, del_source), {}),
            ]
            run_tasks(tasks, max_workers=1) # 执行编译
        else:
            show_file_find_file(args.file)
    elif args.path:
        if os.path.exists(args.path) and not os.path.isfile(args.path):
            compile_file_list = find_python_files(args.path)
            if compile_file_list:
                del_source = args.del_source
                tasks = []
                for compile_file in compile_file_list:
                    tasks.append(
                        # 函数, 位置参数, 关键字参数
                        (compile_to_binary, compile_file, (compile_file, del_source), {}),
                    )
                run_tasks(tasks, max_workers=args.conc) # 执行编译
            else:
                show_path_not_find_file(args.path)
        else:
            show_path_find_file(args.path)