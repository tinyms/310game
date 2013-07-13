#include "Workbench.h"
#include <QApplication>
#include <QWebElement>

int main(int argc, char *argv[])
{
    qRegisterMetaType<QWebElement>("QWebElement");
    qRegisterMetaType<QWebElement>("QWebElement&");
    qRegisterMetaType<QString>("QString&");

    QApplication a(argc, argv);
    Workbench w;
    w.show();
    
    return a.exec();
}
