#ifndef HTMLTHREAD_H
#define HTMLTHREAD_H

#include "Helper.h"
#include <QThread>
#include <QWebElement>


class HtmlThread : public QThread
{
    Q_OBJECT
private:
    QString url;
public:
    explicit HtmlThread(QObject *parent = 0);
    void run() Q_DECL_OVERRIDE;
    QString getUrl() const;
    void setUrl(const QString &value);

signals:
    void ParseHtml(QString targetUrl,QWebElement& document,QString& flag);
public slots:
    
};

#endif // HTMLTHREAD_H
