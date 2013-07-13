#-------------------------------------------------
#
# Project created by QtCreator 2013-04-12T22:26:03
#
#-------------------------------------------------

QT       += core gui network webkitwidgets

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = WaterPress
TEMPLATE = app


SOURCES += main.cpp\
        Workbench.cpp \
    Helper.cpp \
    HtmlThread.cpp

HEADERS  += Workbench.h \
    Helper.h \
    HtmlThread.h
