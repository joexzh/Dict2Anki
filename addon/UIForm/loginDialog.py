# Form implementation generated from reading ui file '.\loginDialog.ui'
#
# Created by: PyQt6 UI code generator 6.8.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
        LoginDialog.resize(505, 480)
        self.gridLayout = QtWidgets.QGridLayout(LoginDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.reloadBtn = QtWidgets.QPushButton(parent=LoginDialog)
        self.reloadBtn.setObjectName("reloadBtn")
        self.gridLayout.addWidget(self.reloadBtn, 0, 1, 1, 1)
        self.pageContainer = QtWidgets.QVBoxLayout()
        self.pageContainer.setObjectName("pageContainer")
        self.gridLayout.addLayout(self.pageContainer, 1, 0, 1, 2)
        self.address = QtWidgets.QLineEdit(parent=LoginDialog)
        self.address.setClearButtonEnabled(True)
        self.address.setObjectName("address")
        self.gridLayout.addWidget(self.address, 0, 0, 1, 1)

        self.retranslateUi(LoginDialog)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        _translate = QtCore.QCoreApplication.translate
        LoginDialog.setWindowTitle(_translate("LoginDialog", "Login"))
        self.reloadBtn.setText(_translate("LoginDialog", "reload"))
