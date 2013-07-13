#ifndef HELPER_H
#define HELPER_H
#include <QtCore>
#include <QWebFrame>
#include <QWebView>
#include <QWebElement>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QThreadPool>
#include <QStringList>
#include <QList>
#include <QRegularExpression>
#include <QDir>
#include <QDate>
#include <QFile>

class HtmlDownladTask: public QRunnable{
private:
    QString url;
public:
    HtmlDownladTask();
    void run();
    QString getUrl() const;
    void setUrl(const QString &value);
};
class Helper
{
public:
    Helper();
public:
    static void Download(QStringList& urls);
    static void Download(QString& url);
    static QWebElement Soup(QString url,QWebView* view);
    static QString HttpGet(QString url,bool isUnicode);
    static QString MD5(QString str);
    static QString GetCacheFileFullName(QString fileName);
    static QString MakeDirs(QString path);
    static QList<int> ParseInt(QString str);
    static QList<float> ParseFloat(QString str);
    static QString ParseDate(QString str);
    static QString TextReader(QString fileName);
    static void TextWriter(QString fileName,QString text);
    static QString ApplicationPath();
private:
    static void EvtFinished(QNetworkReply *);
};

#endif // HELPER_H
