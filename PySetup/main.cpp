#include <iostream>
#include <Windows.h>
#include <stdlib.h>
#include <stdio.h>
#include <Python.h>
#define _WIN32_WINNT 0x0500
#pragma comment(linker,   "/subsystem:\"windows\"  /entry:\"wmainCRTStartup\" ")
using namespace std;

int wmain(int argc, wchar_t** argv)
{
    Py_Initialize();
    PySys_SetArgv(argc, argv);
    // 得到当前可执行文件所在的目录
    char szPath[10240];
    char szCmd[10240];
    GetModuleFileName(NULL, szPath, sizeof(szPath));

    char* p = strrchr(szPath, '\\');
    if (p == NULL)
    {
         printf("Get module file name error!\n");
         return -1;
    }

    *p = 0;

    // 设定运行时的PATH
    sprintf(szCmd, "PATH=%s", szPath);
    _putenv(szCmd);

    // 把sys.path设定为['.', '自己的源代码zip文件', '标准库zip文件', 'dll目录']
    // 然后调用main模块
    sprintf(szCmd,
                 "import sys\n"
                "sys.path.insert(0,'.')\n"
                "sys.path.insert(1,r'%s\\library.zip')\n"
                "from PyQt5 import QtWidgets\n"
                "from WaterPress import Workbench\n"
                 "app = QtWidgets.QApplication(sys.argv)\n"
                  "window = Workbench()\n"
                  "window.show()\n"
                  "sys.exit(app.exec_())\n",
                    szPath);
    Py_OptimizeFlag = 2;
    Py_NoSiteFlag = 1;
    Py_Initialize();
    PyRun_SimpleString(szCmd);
    Py_Finalize();
    return 0;
}

