#include "HtmlThread.h"

HtmlThread::HtmlThread(QObject *parent) :
    QThread(parent)
{
}

void HtmlThread::run()
{
    Helper::Download(this->url);
    QWebElement root;
    QString flag("False");
    emit this->ParseHtml(this->getUrl(),root,flag);
    while("True"==flag){break;}
    QWebElementCollection items;
    items = root.findAll("table");
    qDebug()<<items.count();
}

QString HtmlThread::getUrl() const
{
    return url;
}

void HtmlThread::setUrl(const QString &value)
{
    url = value;
}
