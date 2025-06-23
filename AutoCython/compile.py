import os
import sys
import glob
import shutil
import tempfile
import subprocess

def get_platform_extension() -> str:
    """返回当前平台的扩展名"""
    if sys.platform.startswith('win'):
        return '.pyd'
    return '.so'

def compile_to_binary(file_path: str, del_source=False):
    """
    将指定的 Python 文件（.py）通过 Cython 编译为二进制扩展文件

    :param file_path: Python 文件路径（可以是相对路径或绝对路径）
    :param del_source: 是否删除源代码
    :return: 生成的二进制文件路径（与输入保持相同的路径类型）
    """
    # 保存原始路径类型（相对/绝对）
    is_absolute = os.path.isabs(file_path)

    # 获取绝对路径用于内部操作
    abs_file_path = os.path.abspath(file_path)

    if not os.path.isfile(abs_file_path):
        raise FileNotFoundError(f"FileNotFoundError: {file_path}.")

    # 获取文件名和目录
    file_name = os.path.basename(abs_file_path)
    module_name, ext = os.path.splitext(file_name)
    source_dir = os.path.dirname(abs_file_path)  # 源文件所在目录（绝对路径）

    if ext != ".py":
        raise ValueError(f"ValueError: The file {file_path} is not a valid Python file (.py)!")

    # 获取平台特定扩展名
    target_ext = get_platform_extension()

    # 创建临时工作目录
    temp_dir = tempfile.mkdtemp()

    try:
        # 将目标文件复制到临时目录
        temp_file_path = os.path.join(temp_dir, file_name)
        shutil.copy2(abs_file_path, temp_file_path)

        # 创建临时的 setup.py 文件
        setup_code = f"""
from setuptools import setup
from Cython.Build import cythonize

# 编译器指令
compiler_directives = {{
    'language_level': '3',
}}

setup(
    ext_modules=cythonize(
        "{file_name}",
        compiler_directives=compiler_directives,
        force=True
    )
)
"""
        setup_path = os.path.join(temp_dir, "setup.py")
        with open(setup_path, "w", encoding='utf-8') as f:
            f.write(setup_code)

        # 执行编译命令
        command = [sys.executable, "setup.py", "build_ext", "--inplace"]
        result = subprocess.run(
            command,
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='replace')
            raise RuntimeError(f"RuntimeError: {error_msg}")

        # 查找生成的二进制文件
        pattern = os.path.join(temp_dir, f"{module_name}*{target_ext}")
        matches = glob.glob(pattern)

        if not matches:
            pattern = os.path.join(temp_dir, f"*{module_name}*{target_ext}")
            matches = glob.glob(pattern)

        if not matches:
            raise FileNotFoundError(f"FileNotFoundError: The file {file_path} is not a valid Python file (.py)! Generated file {target_ext} not found, in {temp_dir} possible file: {os.listdir(temp_dir)}")

        # 取最新生成的文件
        generated_file = max(matches, key=os.path.getctime)

        # 获取源文件的目录（使用原始路径类型）
        if is_absolute:
            output_dir = source_dir
        else:
            # 如果输入是相对路径，保持相对路径
            output_dir = os.path.dirname(file_path) or '.'

        # 创建目标目录（如果不存在）
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # 目标文件路径（保持原始路径类型）
        output_file_name = os.path.basename(generated_file)
        output_path = os.path.join(output_dir, output_file_name)

        # 移动文件
        shutil.move(generated_file, output_path)

        if del_source:
            os.remove(file_path)

        # 返回与输入相同类型的路径
        return output_path
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)

# 测试函数
if __name__ == "__main__":
    # 替换为你的 Python 文件路径
    target_file = "test/example.py"  # 请确保文件路径正确

    try:
        output_file = compile_to_binary(target_file)
        print(output_file)
    except Exception as e:
        print(e)