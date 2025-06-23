import time
import locale
import platform
import threading
import concurrent.futures
from rich.live import Live
from rich.text import Text
from rich.table import Table
from rich.console import Console
from rich.spinner import Spinner
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TimeElapsedColumn

def run_tasks(task_list, max_workers=2, language=None):
    """
    并发执行任务列表并实时显示状态

    :param task_list: 任务列表，每个元素是 (函数, 位置参数元组, 关键字参数字典)
    :param max_workers: 最大并发线程数
    :param language: 显示语言 ('en' 或 'zh', 默认根据系统语言自动判断)
    """
    print("""\n █████╗ ██╗   ██╗████████╗ ██████╗  ██████╗██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔════╝╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║
███████║██║   ██║   ██║   ██║   ██║██║      ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║
██╔══██║██║   ██║   ██║   ██║   ██║██║       ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝╚██████╗   ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝""")

    bit_architecture = platform.architecture()[0]  # 获取位数信息，例如 '64bit' 或 '32bit'
    print(f"{platform.system()} {platform.version()} {platform.machine()} | {platform.python_implementation()} {platform.python_version()} {platform.python_compiler()} | {bit_architecture}")

    # 获取系统默认区域设置
    try:
        sys_language, _ = locale.getdefaultlocale()
        language = 'zh' if sys_language and sys_language.startswith('zh') else 'en'
    except Exception:
        language = 'en'  # 异常时默认英文

    # 中英文文本映射
    TEXT_MAP = {
        'en': {
            'overall_progress': "[cyan]Overall Progress",
            'total_tasks': "\n📊 Total Tasks: ",
            'completed': " ✅ Completed: ",
            'elapsed': " ⏱️ Elapsed Time: ",
            'remaining': " ⏳ Estimated Remaining: ",
            'id': "ID",
            'status': "Status",
            'function': "Names",
            'time': "Time (s)",
            'result': "Result",
            'status_pending': "⏱️ Pending",
            'status_running': " Compiling",
            'status_success': "✅ Success",
            'status_failed': "❌ Failed",
            'succeeded': "\n[bold green]✅ Tasks succeeded: {0}[/bold green] |",
            'failed': " [bold red]❌ Tasks failed: {0}[/bold red] |",
            'total_time': " [bold]⏱️ Total time: [bold green]{0:.2f}s[/bold green][/bold] |",
            'all_completed': " [bold green]🎉 All compilation tasks completed![/bold green]",
            'wait_test': "Waiting for the test...",
        },
        'zh': {
            'overall_progress': "[cyan]总进度",
            'total_tasks': "\n📊 总任务数: ",
            'completed': " ✅ 已完成: ",
            'elapsed': " ⏱️ 已用时间: ",
            'remaining': " ⏳ 预计剩余: ",
            'id': "ID",
            'status': "状态",
            'function': "名称",
            'time': "时间 (秒)",
            'result': "结果",
            'status_pending': "⏱️ 等待编译",
            'status_running': " 编译中",
            'status_success': "✅ 编译成功",
            'status_failed': "❌ 编译失败",
            'succeeded': "\n[bold green]✅ 成功任务数: {0}[/bold green] |",
            'failed': " [bold red]❌ 失败任务数: {0}[/bold red] |",
            'total_time': " [bold]⏱️ 总耗时: [bold green]{0:.2f}s[/bold green][/bold] |",
            'all_completed': " [bold green]🎉 所有编译任务已完成![/bold green]",
            'wait_test': "等待测试..",
        }
    }
    # 获取当前语言文本
    t = TEXT_MAP.get(language, TEXT_MAP['en'])

    console = Console()
    start_time = time.time()
    completed = 0
    total_tasks = len(task_list)

    # 创建任务状态数据
    task_status = [
        {
            "id": idx,
            "func": func,
            "name": name,
            "args": args,
            "kwargs": kwargs,
            "status": "pending",
            "start": None,
            "end": None,
            "result": None,
            "error": None,
            "lock": threading.Lock()  # 添加锁保证线程安全
        }
        for idx, (func, name, args, kwargs) in enumerate(task_list, 1)
    ]

    # 创建进度条
    progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(bar_width=60),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        console=console
    )
    overall_task = progress.add_task(t['overall_progress'], total=total_tasks)

    # 用于控制实时更新的标志
    refresh_event = threading.Event()

    def execute_task(task):
        """执行单个任务并记录结果"""
        with task["lock"]:
            task["status"] = "running"
            task["start"] = time.time()
            refresh_event.set()  # 触发刷新

        try:
            result = task["func"](*task["args"], **task["kwargs"])
            with task["lock"]:
                task["status"] = "success"
                task["result"] = result
        except Exception as e:
            with task["lock"]:
                task["status"] = "failed"
                task["error"] = str(e)
        finally:
            with task["lock"]:
                task["end"] = time.time()
                refresh_event.set()  # 触发刷新

        nonlocal completed
        completed += 1
        progress.update(overall_task, advance=1)
        refresh_event.set()  # 触发刷新
        return task

    def generate_display():
        """生成实时显示内容"""
        # 创建总状态面板
        total_panel = Table.grid(padding=1)
        elapsed_time = time.time() - start_time
        if completed > 0:
            remaining_time = (elapsed_time / (completed + 0.001)) * (total_tasks - completed) if completed < total_tasks else 0
            total_panel.add_row(
                Text(t['total_tasks'], style="bold") + Text(f"{total_tasks}", style="bold cyan") + Text(" |") +
                Text(t['completed'], style="bold") + Text(f"{completed}/{total_tasks}", style="bold cyan") + Text(" |") +
                Text(t['elapsed'], style="bold") + Text(f"{elapsed_time:.2f}s", style="bold green") + Text(" |") +
                Text(t['remaining'], style="bold") + Text(f"{remaining_time:.2f}s\n", style="bold yellow")
            )
        else:
            total_panel.add_row(
                Text(t['total_tasks'], style="bold") + Text(f"{total_tasks}", style="bold cyan") + Text(" |") +
                Text(t['completed'], style="bold") + Text(f"{completed}/{total_tasks}", style="bold cyan") + Text(" |") +
                Text(t['elapsed'], style="bold") + Text(f"{elapsed_time:.2f}s", style="bold green") + Text(" |") +
                Text(t['remaining'], style="bold") + Text(f"{t['wait_test']}\n", style="bold yellow")
            )

        # 创建任务表格
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column(t['id'], width=5, justify="center")
        table.add_column(t['status'], width=15)
        table.add_column(t['function'], width=30)
        table.add_column(t['time'], width=10, justify="right")
        table.add_column(t['result'], width=80)

        # 添加任务行
        for task in task_status:
            with task["lock"]:  # 使用锁保证状态一致性
                # 计算运行时间
                run_time = (
                    (task["end"] or time.time()) - task["start"]
                    if task["start"] else 0
                )

                # 状态显示
                if task["status"] == "pending":
                    status = Text(t['status_pending'], style="yellow")
                    result_text = Text("-")
                elif task["status"] == "running":
                    # 使用Columns组合Spinner和Text
                    spinner = Spinner("dots", style="blue")
                    status = Columns([spinner, Text(t['status_running'], style="blue")])
                    result_text = Text("-")
                elif task["status"] == "success":
                    status = Text(t['status_success'], style="green bold")
                    result_text = Text(str(task["result"]), style="green")
                else:  # failed
                    status = Text(t['status_failed'], style="red bold")
                    result_text = Text(task["error"], style="red")

                table.add_row(
                    str(task["id"]),
                    status,
                    task["name"],
                    f"{run_time:.3f}",
                    result_text
                )

        # 组合所有元素
        group = Table.grid()
        group.add_row(table)
        group.add_row(total_panel)
        group.add_row(progress)

        return group

    # 使用Live上下文管理器实现实时刷新
    with Live(console=console, refresh_per_second=20, vertical_overflow="visible") as live:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = {executor.submit(execute_task, task): task for task in task_status}

            # 初始显示
            live.update(generate_display())

            # 实时更新显示（使用事件驱动刷新）
            last_refresh_time = time.time()
            while completed < total_tasks:
                # 定期刷新或状态变化时刷新
                if refresh_event.is_set() or (time.time() - last_refresh_time) > 0.05:
                    live.update(generate_display())
                    refresh_event.clear()
                    last_refresh_time = time.time()
                time.sleep(0.01)

            # 等待所有任务完成
            concurrent.futures.wait(futures)

            # 最终显示
            live.update(generate_display())

    # 最终汇总信息
    total_elapsed = time.time() - start_time
    success_count = sum(1 for t in task_status if t["status"] == "success")
    failure_count = sum(1 for t in task_status if t["status"] == "failed")

    console.print(t['succeeded'].format(success_count) + t['failed'].format(failure_count) + t['total_time'].format(total_elapsed) + t['all_completed'])

# 示例使用方式
if __name__ == "__main__":
    # 示例任务函数
    def task_success(seconds):
        time.sleep(seconds)
        return f"Slept for {seconds}s"

    def task_failure():
        time.sleep(0.5)
        raise ValueError("Intentional error")

    def long_task(seconds):
        time.sleep(seconds)
        return f"Long task {seconds}s"

    # 创建任务列表 (函数, 位置参数, 关键字参数)
    tasks = [
        (task_success, task_success.__name__, (0.5,), {}),
        (task_failure, task_failure.__name__, (), {}),
        (long_task, long_task.__name__, (2.5,), {}),
        (task_success, task_success.__name__, (1.2,), {}),
        (long_task, long_task.__name__, (1.8,), {}),
        (task_failure, task_failure.__name__, (), {}),
    ]

    # 执行任务 (最大并发4个)
    run_tasks(tasks, max_workers=2, language='en')
