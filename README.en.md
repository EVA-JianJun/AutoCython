# AutoCython
[中文](https://github.com/EVA-JianJun/AutoCython/blob/master/README.md) | English

**AutoCython: Batch Compile Python Files to PYD Files with One Click**
![py_pyd](https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20210824.png)

## ✨ Key Features
- Single-file/Multi-file batch compilation
- Cross-platform support (Windows/Linux/MacOS)
- Clean command-line interface

## 📦 Installation
```bash
pip install AutoCython-jianjun
```

## ⚙️ Dependencies
### C/C++ Compiler Requirements
- **Windows**: Visual Studio
- **Linux**: gcc & g++

**Important**: Compiler architecture must match Python interpreter (64-bit Python requires 64-bit compiler)

> For other compiler configurations, refer to [Cython](https://github.com/cython/cython) project

## 🚀 Usage Guide
### Command Line Operations
![CLI Demo](https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20250609_3.png)

```bash
# Compile single file
AutoCython -f test.py

# Compile entire directory
AutoCython -p D:/python_code/ProjectPath

# Delete source after compilation (disabled by default)
AutoCython -d True -f test.py
AutoCython -d True -p D:/python_code/ProjectPath
```

### Compilation Interface
![AutoCython GUI](https://raw.githubusercontent.com/EVA-JianJun/GitPigBed/master/blog_files/img/AutoCython_20250609_4.png)

### Manually Exclude Files from Compilation
Add declaration in the **first two lines** of file header:
```python
# AutoCython No Compile
# This file will be skipped during compilation
```

## ⚠️ Troubleshooting

Typically caused by Cython-unsupported statements or invalid filenames.
Consult [Cython Wiki](https://github.com/cython/cython/wiki) official documentation or submit an Issue.

## 📅 Changelog
### V2 Releases
1. 20250609 release V2.0.0: Codebase refactored with new UI

### V1 Releases
1. 20220613: Added Linux support (requires gcc & g++ configuration)
2. 20221123: Added manual file exclusion via file header comments
3. 20230306: Added CLI header specification (e.g., `Python310`) for non-Windows compilation
4. 20230324: Documentation updates
5. 20240506: Fixed issue with `__init__.py` restoration after failed compilation
