from .run_tasks import run_tasks
from .compile import compile_to_binary
from .tools import parse_arguments, find_python_files, show_not_find_file

def compile():
    args = parse_arguments()

    if args.file:
        compile_file = args.file
        del_source = args.del_source
        tasks = [
            # 函数, 位置参数, 关键字参数
            (compile_to_binary, compile_file, (compile_file, del_source), {}),
        ]
        run_tasks(tasks, max_workers=1) # 执行编译
    elif args.path:
        compile_file_list = find_python_files(args.path)
        del_source = args.del_source
        if compile_file_list:
            tasks = []
            for compile_file in compile_file_list:
                tasks.append(
                    # 函数, 位置参数, 关键字参数
                    (compile_to_binary, compile_file, (compile_file, del_source), {}),
                )
            run_tasks(tasks, max_workers=args.conc) # 执行编译
        else:
            show_not_find_file()
