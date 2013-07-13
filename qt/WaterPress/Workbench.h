#ifndef WORKBENCH_H
#define WORKBENCH_H

#include <QMainWindow>
#include <QWebView>
#include <QWebElement>
#include <QWebElementCollection>
#include <QVBoxLayout>
#include "Helper.h"
#include <iostream>
#include "HtmlThread.h"

using namespace std;

class Workbench : public QMainWindow
{
    Q_OBJECT
private:
    QWidget* centerPanel;
    QWebView* webView;
    QVBoxLayout* mainLayout;
    HtmlThread* extractMatchsThread;
public:
    Workbench(QWidget *parent = 0);
    ~Workbench();

public slots:
    void OnParseHtml(QString url,QWebElement& root,QString& flag);
};

#endif // WORKBENCH_H
