#include "Workbench.h"

Workbench::Workbench(QWidget *parent)
    : QMainWindow(parent)
{
    this->resize(800,600);
    this->centerPanel = new QWidget(this);
    this->webView = new QWebView(this);
    this->mainLayout = new QVBoxLayout();
    this->mainLayout->addWidget(this->webView);
    this->centerPanel->setLayout(this->mainLayout);
    this->setCentralWidget(this->centerPanel);
    this->extractMatchsThread = new HtmlThread();
    QObject::connect(this->extractMatchsThread,SIGNAL(ParseHtml(QString,QWebElement&,QString&)),SLOT(OnParseHtml(QString, QWebElement&,QString&)));
    QString url = "http://live.500.com/zucai.php?e=13053";
    this->extractMatchsThread->setUrl(url);
    this->extractMatchsThread->start();
}

Workbench::~Workbench()
{
    
}

void Workbench::OnParseHtml(QString url, QWebElement &root, QString &flag)
{
    root = Helper::Soup(url,this->webView);
    flag = "True";
    qDebug()<<flag;
}
