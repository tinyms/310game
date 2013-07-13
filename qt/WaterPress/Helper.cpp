#include "Helper.h"

Helper::Helper()
{
}

void Helper::Download(QStringList &urls)
{
    if(!urls.empty()){
        int len = urls.length();
        QThreadPool* pool = QThreadPool::globalInstance();
        pool->setMaxThreadCount(15);
        for(int k=0;k<len;k++){
            HtmlDownladTask* task = new HtmlDownladTask();
            task->setUrl(urls.at(k));
            pool->start(task);
        }
        qDebug()<< "Download Finished.";
        pool->waitForDone();
    }
}

void Helper::Download(QString &url)
{
    QStringList urls;
    urls.append(url);
    Download(urls);
}

QWebElement Helper::Soup(QString url, QWebView *view)
{
    QString path = "file:///"+GetCacheFileFullName(MD5(url)+".html");
    QWebFrame* frame = view->page()->mainFrame();
    QEventLoop eventLoop;
    QObject::connect(frame,SIGNAL(loadFinished(bool)),&eventLoop,SLOT(quit()));
    QString html;
    html = TextReader(GetCacheFileFullName(MD5(url)+".html"));
    qDebug()<<html;
    frame->setHtml(html);
    //frame->load(QUrl(path));
    eventLoop.exec();
    view->stop();
    return frame->documentElement();
}

QString Helper::HttpGet(QString url, bool isUnicode=false)
{
    QNetworkAccessManager *manager = new QNetworkAccessManager();
    QNetworkReply *reply = manager->get(QNetworkRequest(QUrl(url)));
    QByteArray responseData;
    QEventLoop eventLoop;
    QObject::connect(manager, SIGNAL(finished(QNetworkReply *)), &eventLoop, SLOT(quit()));
    eventLoop.exec();//block until finish
    responseData = reply->readAll();
    if(!isUnicode){
        return QString::fromLocal8Bit(responseData);
    }
    return QString(responseData);
}

QString Helper::MD5(QString str)
{
    QString md5;
    QByteArray bb;
    bb = QCryptographicHash::hash (str.toUtf8(),QCryptographicHash::Md5);
    md5.append(bb.toHex());
    return md5;
}

QString Helper::GetCacheFileFullName(QString fileName)
{
    QString folder = Helper::ApplicationPath()+"/Cache/"+QDate::currentDate().toString("yyyy-MM-dd/");
    Helper::MakeDirs(folder);
    return folder + fileName;
}

QString Helper::MakeDirs(QString path)
{
    QDir dirs;
    if(dirs.exists(path)){
        return path;
    }
    dirs.mkpath(path);
    return path;
}

QList<int> Helper::ParseInt(QString str)
{
    QList<int> items;
    QRegularExpression re("\\d+",QRegularExpression::MultilineOption);
    QRegularExpressionMatch match = re.match(str);
    while(match.hasMatch()){
        QString item = match.captured();
        items.append(item.toInt());
    }
    return items;
}

QList<float> Helper::ParseFloat(QString str)
{
    QList<float> items;
    QRegularExpression re("\\d+.\\d+",QRegularExpression::MultilineOption);
    QRegularExpressionMatch match = re.match(str);
    while(match.hasMatch()){
        QString item = match.captured();
        items.append(item.toFloat());
    }
    return items;
}

QString Helper::ParseDate(QString str)
{
    QRegularExpression re("\\d{4}-\\d{2}-\\d{2}");
    QRegularExpressionMatch match = re.match(str);
    if(match.hasMatch()){
        return match.captured();
    }
    return "";
}

QString Helper::TextReader(QString fileName)
{
    QFile file(fileName);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)){
        return "";
    }
    QTextStream in(&file);
    in.setCodec("UTF-8");
    QString content = in.readAll();
    file.close();
    return content;
}

void Helper::TextWriter(QString fileName, QString text)
{
    QFile file(fileName);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Text)){
        return;
    }
    QTextStream out(&file);
    out.setCodec("UTF-8");
    out.setGenerateByteOrderMark(true);
    out << text;
    file.close();
}

QString Helper::ApplicationPath()
{
    return QCoreApplication::applicationDirPath();
}

void Helper::EvtFinished(QNetworkReply *)
{
}


HtmlDownladTask::HtmlDownladTask()
{
}

void HtmlDownladTask::run()
{
    QString fileName = Helper::MD5(this->getUrl())+".html";
    QString path = Helper::GetCacheFileFullName(fileName);
    QFile file(path);
    if(file.exists()){
        return;
    }
    QString html = Helper::HttpGet(this->getUrl());
    Helper::TextWriter(path,html);
}

QString HtmlDownladTask::getUrl() const
{
    return url;
}

void HtmlDownladTask::setUrl(const QString &value)
{
    url = value;
}

