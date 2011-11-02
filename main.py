#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *


def parseFile(filename):
    """
    parse json file into a list of entries.

    Google Reader can export data in two formats, namely `JSON Activity 
    Stream format` and `Google Reader JSON format`.
    Files in the former format will have suffix `jas` in their basenames.

    After parsing, each entry will be a dict of some extracted fields:

    e = {
        'url': xxx, 
        'title': xxx,
        'content': xxx,
        }
    """

    fp = open(filename, 'r')
    js = json.load(fp)
    fp.close()
    print filename

    if os.path.basename(filename).endswith('jas.json'):
        return parseJas(js)
    else:
        return parseGr(js)



def parseJas(js):
    entries = []
    
    for item in js[u'items']:
        try:
            entry = {}

            objectType = item[u'object'][u'objectType']

            if objectType == u'post':
                entry['url']  = item[u'object'][u'url']
                entry['title'] = item[u'object'][u'displayName']
            else:
                entry['title'] = 'annotation'
                entry['url'] = ''

            entry['content'] = item[u'object'][u'content']

            entries.append(entry)

        except Exception, e:
            print e

    return entries


def parseGr(js):
    entries = []

    for item in js[u'items']:
        try:
            entry = {}
            entry['url'] = item[u'alternate'][0][u'href']

            entry['title'] = item[u'title']

            if item.has_key(u'content'):
                entry['content'] = item[u'content'][u'content']
            elif item.has_key(u'summary'):
                entry['content'] = item[u'summary'][u'content']

            entries.append(entry)

        except Exception, e:
            print e

    return entries


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.createActions()
        self.createMenus()
        self.createCentralWidgets()
        self.createConnections()

        self.setWindowTitle("GR Json Reader")

        self.entries = []

    def createActions(self):
        self.openAct = QAction("&Open", self,
                shortcut=QKeySequence.Open,
                statusTip="Open a Google Reader JSON file",
                triggered=self.open)

        self.quitAct = QAction("Quit", self,
                shortcut=QKeySequence.Quit,
                statusTip="Exit the application",
                triggered=self.close)

        self.aboutAct = QAction("&About", self,
                statusTip="About this application",
                triggered=self.about)


    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.quitAct)

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)


    def createCentralWidgets(self):
        """
        layout:

        +-----------+------------------------------+
        | +-------+ |                        url   |
        | |search | + -----------------------------+
        | +-------+ |                              | 
        | +-------+ |          content             | 
        | |       | |                              | 
        | |       |<->                             | 
        | |       | |                              | 
        | | items | |                              | 
        | |       | |                              |
        | |       | |                              | 
        | |       | |                              | 
        | +-------+ |                              | 
        +-----------+------------------------------+

        """

        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)

        leftPanel = QWidget()
        leftLayout = QVBoxLayout()
        rightPanel = QWidget()
        rightLayout = QVBoxLayout()

        self.searchEdit = QLineEdit()
        self.searchEdit.setText("Search")
        self.itemsView = QListWidget()
        self.webView = QWebView()
        self.webView.load(QUrl("about:blank"))
        self.urlLabel = QLabel()
        self.urlLabel.setMaximumHeight(20)

        leftLayout.addWidget(self.searchEdit)
        leftLayout.addWidget(self.itemsView)
        rightLayout.addWidget(self.urlLabel)
        rightLayout.addWidget(self.webView)
        leftPanel.setLayout(leftLayout)
        rightPanel.setLayout(rightLayout)

        splitter.addWidget(leftPanel)
        splitter.addWidget(rightPanel)

        # adds a line between the two panels to show the splitter handler
        handle = splitter.handle(1)

        line = QFrame(handle)
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QHBoxLayout(handle)
        layout.setSpacing(0)
        layout.setMargin(0)
        layout.addWidget(line)

        # set central widget
        self.setCentralWidget(splitter)

        self.urlLabel.setMaximumWidth(self.webView.width())


    def createConnections(self):
        self.itemsView.itemSelectionChanged.connect(self.selectItem)
        self.urlLabel.linkActivated.connect(self.loadUrl)
        self.searchEdit.textEdited.connect(self.search)


    def open(self):
        filename = QFileDialog.getOpenFileName(self, "Open JSON", "", 
                "JSON Files (*.json)")
        if filename:
            try:
                entries = parseFile(filename.__str__())
                self.setEntries(entries)
            except Exception, e:
                print e
                QMessageBox.warning(self, "Error", "Unable to open file")


    def about(self):
        QMessageBox.about(self, 'About', 
            'homepage: <a href="https://github.com/qiao">https://github.com/qiao</a>')


    def setEntries(self, entries):
        self.entries = entries
        self.showEntries(entries)


    def showEntries(self, entries):
        self.itemsView.clear()
        for entry in entries:
            title = entry['title']
            self.itemsView.addItem(title)

        self.itemsView.setCurrentRow(0)


    def search(self, text):
        if not self.entries:
            return

        text = text.__str__()
        if text:
            entries = filter(lambda e: text in e['title'], self.entries)
            self.showEntries(entries)
        else:
            self.showEntries(self.entries)


    def selectItem(self):
        row = self.itemsView.currentRow()
        entry = self.entries[row]

        content = entry['content']
        url = entry['url']

        self.webView.setHtml(content)
        self.urlLabel.setText('<a href="' + url + '">' + url + '<a>')


    def loadUrl(self, url):
        self.webView.load(QUrl(url))


def main():

    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
