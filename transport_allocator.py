import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from enum import Enum
import re
import os

class transportAllocator(QWidget):
   def __init__(self, parent = None):
      super(transportAllocator, self).__init__(parent)
      self.labelFont = QFont("Helvetica", 10)
      # self.setStyleSheet("background:white")
      self.setGeometry(0,0,1600,900)
      qtRectangle = self.frameGeometry()
      centerPoint = QDesktopWidget().availableGeometry().center()
      qtRectangle.moveCenter(centerPoint)
      self.move(qtRectangle.topLeft())
      if getattr(sys, 'frozen', False):
         print("entered....")
         # If the application is bundled
         self.base_path = sys._MEIPASS
         print(self.base_path)
      else:
         # If the application is not bundled
         self.base_path = os.path.abspath(".")

      self.transporter=[Category("ARPL"),Category("Axis"),Category("Mahindra"),Category("JCB")]
      self.destination=[Category("Trichy"),Category("Madurai"),Category("Coimbatore"),Category("Chennai"),Category("Pudukottai")]
      # self.destination=[Category("Trichy"+str(i),True) for i in range(20)]
      # self.transporter=[Category("ARPL"+str(i),True) for i in range(20)]
      self.supply={}
      self.demand={}
      self.minimumLoad={}
      
      self.masterLayout = QVBoxLayout()

      self.titleFrame = self.setupTitleLayout()      
      self.bodyFrame = self.setupBodyLayout()
      self.allocationFrame = self.setupAllocationPage()

      # supplyDemandLayout./
      self.masterLayout.addWidget(self.titleFrame)
      self.masterLayout.addWidget(self.bodyFrame)
      self.masterLayout.addWidget(self.allocationFrame)
      # masterLayout.addStretch()

      self.setLayout(self.masterLayout)
      self.setWindowTitle("Transport Allocator")
		
   def getfile(self):
      fname = QFileDialog.getOpenFileName(self, 'Open Cost file', 
         '.',"CSV files (*.csv)")
      print(fname)
      if fname is not None:
         self.costFilePath.setText(fname[0])
   
   def createNumberBox(self, lowBound=1,highBound=1000000):
      numberBox = QLineEdit()
      numberBox.setFont(self.labelFont)
      numberBox.setAlignment(Qt.AlignCenter)
      numberBox.setValidator(QIntValidator(lowBound, highBound, self))
      return numberBox
   
   def nextBtnHandler(self):
      self.bodyFrame.hide()
      self.setupAllocationTable()
      self.allocationFrame.show()
      if self.allocationMatrix.horizontalScrollBar().isVisible():
         self.allocationMatrix.setMaximumHeight(self.allocationMatrix.maximumHeight()+self.allocationMatrix.horizontalScrollBar().height())
      if self.allocationMatrix.verticalScrollBar().isVisible():
         self.allocationMatrix.setMaximumWidth(self.allocationMatrix.maximumWidth()+self.allocationMatrix.verticalScrollBar().width())
      print('horizontalScrollBar',self.allocationMatrix.horizontalScrollBar().isVisible())
      print('verticalScrollBar',self.allocationMatrix.verticalScrollBar().isVisible())

   def backBtnHandler(self):
      self.allocationFrame.hide()
      self.bodyFrame.show()
   
   def addDestinationBtnHandler(self):
      dialog = CategorySelector(self.destination)
      dialog.dialogClosed.connect(self.onDestinationDialogClosed)
      dialog.exec_()
   
   def onDestinationDialogClosed(self, result):
      self.destination = result
      demand={}
      for category in self.destination:
         if category.isChecked:
            if category.value not in self.demand.keys():
               demand[category.value]=0 
            else:
               demand[category.value]=self.demand[category.value]
      print(demand)
      self.demand = demand
      self.fillDestinationTable()
   
   def setupTitleLayout(self):
      titleFrame = QFrame()
      # titleFrame.setStyleSheet("background:white")
      titleLayout = QHBoxLayout() 

      #Logo
      self.logoLbl = QLabel()
      logoPath = os.path.join(self.base_path, "images", "Renault_Nissan_logo.jpg")
      self.pixmap = QPixmap(logoPath)
      self.pixmap = self.pixmap.scaled(QSize(300,60))
      self.logoLbl.setPixmap(self.pixmap)
      self.logoLbl.resize(self.pixmap.width(), self.pixmap.height())
      titleLayout.addWidget(self.logoLbl)

      #Header
      # titleLayout.setSizeConstraint(QLayout.SetFixedSize)
      self.companyLbl = QLabel("TRANSPORT ALLOCATOR")
      self.titleFont = QFont("Helvetica", 12)
      self.titleFont.setBold(True)
      self.companyLbl.setFont(self.titleFont)
      titleLayout.addWidget(self.companyLbl)
      titleFrame.setStyleSheet("background-color:white")
      titleLayout.setContentsMargins(0,0,300,0)
      titleFrame.setLayout(titleLayout)
      return titleFrame

   def setupBodyLayout(self):
      bodyLayout = QVBoxLayout()
      self.bodyFrame = QFrame()

      costLayout = self.setupCostFileLayout()
      bodyLayout.addLayout(costLayout)

      supplyDemandLayout = self.setupDemandSupplyLayout()
      bodyLayout.addLayout(supplyDemandLayout)

      footerLayout = self.setupNextFooterLayout()
      bodyLayout.addLayout(footerLayout)

      self.bodyFrame.setLayout(bodyLayout)
      return self.bodyFrame      
      
   def setupCostFileLayout(self):
      costLayout = QHBoxLayout()

      #Cost File Label
      self.costFileLbl = QLabel("Cost File")
      self.costFileLbl.setFont(self.labelFont)
      costLayout.addWidget(self.costFileLbl)
		
      #Cost File Path TextBox
      self.costFilePath = QLineEdit()
      self.costFilePath.setFont(self.labelFont)
      self.costFilePath.setAlignment(Qt.AlignVCenter)
      self.costFilePath.setFixedHeight(40)
      costLayout.addWidget(self.costFilePath)
      
      #Browse Button
      self.browseBtn = QPushButton("Browse")
      self.browseBtn.setFont(self.labelFont)
      self.browseBtn.setFixedSize(120,40)
      self.browseBtn.clicked.connect(self.getfile)
      costLayout.addWidget(self.browseBtn)
      return costLayout   

   def setupDemandSupplyLayout(self):
      supplyDemandLayout = QHBoxLayout()
      
      demandFrame = self.setupDemandLayout()      
      supplyDemandLayout.addWidget(demandFrame)
         
      supplyFrame = self.setupSupplyLayout()
      supplyDemandLayout.addWidget(supplyFrame)

      # allocationFrame = self.setupAllocationMatrix()
      # supplyDemandLayout.addWidget(allocationFrame)

      return supplyDemandLayout
   
   def setupDemandLayout(self):
      demandLayout = QVBoxLayout()
      demandHeaderLayout = QHBoxLayout()
      self.demandHeader = QLabel("Destination")
      self.demandHeader.setFont(self.labelFont)
      demandHeaderLayout.addWidget(self.demandHeader)
      self.destinationAddButton = QPushButton("Add +")
      self.destinationAddButton.setFont(self.labelFont)
      self.destinationAddButton.setFixedSize(100,40)
      self.destinationAddButton.clicked.connect(self.addDestinationBtnHandler)
      demandHeaderLayout.addWidget(self.destinationAddButton)
      demandLayout.addLayout(demandHeaderLayout)

      self.destinationTable = QTableWidget()
      self.destinationTable.verticalHeader().setVisible(False)
      self.destinationTable.setColumnCount(2)
      self.destinationTable.setHorizontalHeaderLabels(["Destination","Demand"])
      destinationTableHeader = self.destinationTable.horizontalHeader()
      destinationTableHeader.setFont(self.labelFont)
      destinationTableHeader.setFixedHeight(50)
      destinationTableHeader.setStyleSheet("QHeaderView::section { background-color: lightgrey ;}")
      destinationTableHeader.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
      destinationTableHeader.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
      self.destinationTable.setRowCount(0)
      self.fillDestinationTable()
      demandLayout.addWidget(self.destinationTable)
      self.demandFrame = QFrame()
      self.demandFrame.setLayout(demandLayout)
      return self.demandFrame
   
   def fillDestinationTable(self):
      self.destinationTable.setRowCount(0)
      for city in self.demand.keys():
         currPos = self.destinationTable.rowCount()
         self.destinationTable.insertRow(currPos)
         label = QLabel(city)
         label.setFont(self.labelFont)
         label.setStyleSheet("padding-left:10px;")
         self.destinationTable.setCellWidget(currPos,0,label)
         numberBox = self.createNumberBox()
         numberBox.setProperty("city", city)
         if self.demand[city] != 0:
            numberBox.setText(str(self.demand[city]))
         numberBox.textChanged.connect(self.onDemandChanged)
         self.destinationTable.setCellWidget(currPos,1,numberBox)
   
   @pyqtSlot(str)
   def onDemandChanged(self,text):
      sender = self.sender()
      city = sender.property("city")
      if text is None or text == "":
         self.demand[city] = 0
      else:
         self.demand[city] = int(text)
      print(self.demand,city,text)

   def setupSupplyLayout(self):
      supplyLayout = QVBoxLayout()

      #Supply Header
      supplyHeaderLayout = QHBoxLayout()
      self.supplyHeader = QLabel("Transporter")
      self.supplyHeader.setFont(self.labelFont)
      supplyHeaderLayout.addWidget(self.supplyHeader)

      #Add Button
      self.transporterAddButton = QPushButton("Add +")
      self.transporterAddButton.setFont(self.labelFont)
      self.transporterAddButton.setFixedSize(100,40)
      self.transporterAddButton.clicked.connect(self.addTransporterBtnHandler)
      supplyHeaderLayout.addWidget(self.transporterAddButton)
      supplyLayout.addLayout(supplyHeaderLayout)

      #Transporter Table
      self.transporterTable = QTableWidget()
      self.transporterTable.verticalHeader().setVisible(False)
      self.transporterTable.setColumnCount(3)
      self.transporterTable.setHorizontalHeaderLabels(["Transporter","Capacity","Minimum"])
      transporterTableHeader = self.transporterTable.horizontalHeader()
      transporterTableHeader.setFont(self.labelFont)
      transporterTableHeader.setFixedHeight(50)
      transporterTableHeader.setStyleSheet("QHeaderView::section { background-color: lightgrey ;}")
      transporterTableHeader.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
      transporterTableHeader.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
      transporterTableHeader.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
      self.transporterTable.setRowCount(0)
      self.fillTransporterTable()
      supplyLayout.addWidget(self.transporterTable)
      self.supplyFrame = QFrame()
      self.supplyFrame.setLayout(supplyLayout)
      # self.supplyFrame.setStyleSheet("padding:0")
      return self.supplyFrame
   
   def fillTransporterTable(self):
      self.transporterTable.setRowCount(0)
      for tpt in self.supply.keys():
         currPos = self.transporterTable.rowCount()
         self.transporterTable.insertRow(currPos)
         label = QLabel(tpt)
         label.setFont(self.labelFont)
         label.setStyleSheet("padding-left:10px;")
         self.transporterTable.setCellWidget(currPos,0,label)
         numberBox = self.createNumberBox()
         numberBox.setProperty("tpt", tpt)
         if self.supply[tpt] != 0:
            numberBox.setText(str(self.supply[tpt]))
         numberBox.textChanged.connect(self.onSupplyChanged)
         self.transporterTable.setCellWidget(currPos,1,numberBox)
         numberBox = self.createNumberBox()
         numberBox.setProperty("tpt", tpt)
         if self.minimumLoad[tpt] != 0:
            numberBox.setText(str(self.minimumLoad[tpt]))
         numberBox.textChanged.connect(self.onMiniumLoadChanged)
         self.transporterTable.setCellWidget(currPos,2,numberBox)
   
   @pyqtSlot(str)
   def onSupplyChanged(self,text):
      sender = self.sender()
      tpt = sender.property("tpt")
      if text is None or text == "":
         self.supply[tpt] = 0
      else:
         self.supply[tpt] = int(text)
      print(self.supply,tpt,text)
      
   @pyqtSlot(str)
   def onMiniumLoadChanged(self,text):
      sender = self.sender()
      tpt = sender.property("tpt")
      if text is None or text == "":
         self.minimumLoad[tpt] = 0
      else:
         self.minimumLoad[tpt] = int(text)
      print(self.supply,tpt,text)
   
   def addTransporterBtnHandler(self):
      dialog = CategorySelector(self.transporter)
      dialog.dialogClosed.connect(self.onTransporterDialogClosed)
      dialog.exec_()
   
   def onTransporterDialogClosed(self, result):
      self.transporter = result
      supply={}
      minLoad={}
      print("minimumLoad",self.minimumLoad)
      for category in self.transporter:
         if category.isChecked:
            if category.value not in self.supply.keys():
               supply[category.value]=0 
               minLoad[category.value]=0 
            else:
               supply[category.value]=self.supply[category.value]
               minLoad[category.value]=self.minimumLoad[category.value]
      print(minLoad)
      self.supply = supply
      self.minimumLoad = minLoad
      self.fillTransporterTable()
  
   def setupNextFooterLayout(self):
      footerLayout = QHBoxLayout()

      #Next Button
      self.nextBtn = QPushButton("Next")
      self.nextBtn.setFont(self.labelFont)
      self.nextBtn.setFixedSize(120,40)
      self.nextBtn.clicked.connect(self.nextBtnHandler)
      footerLayout.addWidget(self.nextBtn,alignment=Qt.AlignRight)

      return footerLayout
   
   def setupFinalFooterLayout(self):
      finalFooterLayout = QHBoxLayout()
      #Back Button
      self.backBtn = QPushButton("Back")
      self.backBtn.setFont(self.labelFont)
      self.backBtn.setFixedSize(120,40)
      self.backBtn.clicked.connect(self.backBtnHandler)
      finalFooterLayout.addWidget(self.backBtn)
      
      #Re-Allocate Button
      self.reAllocateBtn = QPushButton("Re-Allocate")
      self.reAllocateBtn.setFont(self.labelFont)
      self.reAllocateBtn.setFixedSize(120,40)
      finalFooterLayout.addWidget(self.reAllocateBtn)
      
      #Next Button
      self.exportBtn = QPushButton("Export")
      self.exportBtn.setFont(self.labelFont)
      self.exportBtn.setFixedSize(120,40)
      finalFooterLayout.addWidget(self.exportBtn)
      
      finalFooterLayout.addStretch()
      finalFooterLayout.setDirection(QBoxLayout.RightToLeft)
      return finalFooterLayout

   def setupAllocationPage(self):
      allocationFrame = QFrame()
      allocationPageLayout = QVBoxLayout()
      allocationMatrixLayout = self.setupAllocationMatrix()
      self.allocationMatrixContainer = QWidget()
      self.allocationMatrixContainer.setLayout(allocationMatrixLayout)
      allocationPageLayout.addWidget(self.allocationMatrixContainer)
      allocationPageLayout.setStretchFactor(self.allocationMatrixContainer, 1)
      finalFooterLayout = self.setupFinalFooterLayout()
      allocationPageLayout.addLayout(finalFooterLayout)
      allocationPageLayout.addStretch()
      allocationFrame.setLayout(allocationPageLayout)
      allocationFrame.hide()
      return allocationFrame

   def setupAllocationMatrix(self):
      allocationLayout = QHBoxLayout()
      self.allocationMatrix = QTableWidget()
      self.setupAllocationTable()
      # self.allocationMatrix.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
      allocationLayout.addWidget(self.allocationMatrix)
      return allocationLayout

   def setupAllocationTable(self):
      self.allocationMatrix.setColumnCount(len(self.supply))
      self.allocationMatrix.setRowCount(len(self.demand))
      self.allocationMatrix.setHorizontalHeaderLabels(self.supply.keys())
      self.allocationMatrix.setVerticalHeaderLabels(sorted(self.demand.keys()))
      self.allocationMatrix.setStyleSheet("""
            QTableCornerButton::section {
                background-color: lightgrey;
            }
        """)
      allocationMatrixHorizontalHeader = self.allocationMatrix.horizontalHeader()
      allocationMatrixHorizontalHeader.setFont(self.labelFont)
      allocationMatrixHorizontalHeader.setFixedHeight(50)
      allocationMatrixHorizontalHeader.setStyleSheet("QHeaderView::section { background-color: lightgrey ;}")
      
      allocationMatrixVerticalHeader = self.allocationMatrix.verticalHeader()
      allocationMatrixVerticalHeader.setFont(self.labelFont)
      # allocationMatrixVerticalHeader.setFixedHeight(50)
      allocationMatrixVerticalHeader.setStyleSheet("QHeaderView::section { background-color: lightgrey ;}")
      for i in range(len(self.supply)):
         allocationMatrixHorizontalHeader.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
      self.fillAllocationTable()
      
   def fillAllocationTable(self):
      self.allocateTransport()
      i=0
      for city in self.demand.keys():
         j=0
         self.allocationMatrix.setRowHeight(i,50)
         for tpt in self.supply.keys():
            cellWidget = QPushButton()
            cellLayout = QHBoxLayout()
            cellLayout.setDirection(QBoxLayout.RightToLeft)
            logoLbl = QLabel()
            image_path = os.path.join(self.base_path, "images", "release.png")
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(QSize(28,28))
            logoLbl.setPixmap(pixmap)
            logoLbl.resize(pixmap.width(), pixmap.height())
            logoLbl.setContentsMargins(0,0,0,0)
            logoLbl.setFixedWidth(30)
            cellLayout.addWidget(logoLbl)
            
            label = QLabel("")
            label.setFont(self.labelFont)
            if self.allocation[city][tpt]['value'] != 0:
               label.setText(str(self.allocation[city][tpt]['value']))
               cellWidget.setStyleSheet("background-color:lightgreen")
            else:
               cellWidget.setDisabled(True)
            label.setContentsMargins(0,0,0,0)
            cellLayout.addWidget(label,1) 
            cellLayout.setSpacing(0)
            cellWidget.setProperty("city",city)
            cellWidget.setProperty("tpt",tpt)
            cellWidget.setLayout(cellLayout)
            # cellWidget.setStyleSheet("background-color:red;padding:0px")
            cellWidget.setContentsMargins(0,0,0,0)
            cellWidget.clicked.connect(self.onAllocationCellClicked)
            self.allocationMatrix.setCellWidget(i,j,cellWidget)
            j+=1
         i+=1
      # self.allocationMatrix.setCellWidget
      
      table_width = self.allocationMatrix.verticalHeader().width() + self.allocationMatrix.horizontalHeader().length() + self.allocationMatrix.frameWidth() * 2
      table_height = self.allocationMatrix.horizontalHeader().height() + self.allocationMatrix.verticalHeader().length() + self.allocationMatrix.frameWidth() * 2
      # print("table height" ,self.allocationMatrix.height(),table_height)
      self.allocationMatrix.setMaximumSize(table_width, table_height)

   def onAllocationCellClicked(self):
      senderBtn = self.sender()
      city = senderBtn.property('city')
      tpt = senderBtn.property('tpt')
      match self.allocation[city][tpt]['state']:
         case AllocationState.RELEASE:
            self.allocation[city][tpt]['state'] = AllocationState.LOCKED
            senderBtn.setStyleSheet("background-color:grey;color:white")
            logoPath = os.path.join(self.base_path, "images", "lock.png")
         case AllocationState.LOCKED:
            self.allocation[city][tpt]['state'] = AllocationState.BLOCKED
            senderBtn.setStyleSheet("background-color:#880808;color:white")
            logoPath = os.path.join(self.base_path, "images", "block.png")
         case AllocationState.BLOCKED:
            self.allocation[city][tpt]['state'] = AllocationState.RELEASE
            senderBtn.setStyleSheet("background-color:lightgreen;color:black")
            logoPath = os.path.join(self.base_path, "images", "release.png")
      print(logoPath)
      hbox_layout = senderBtn.layout()
      if hbox_layout:
         logoLbl = hbox_layout.itemAt(0).widget() 
         pixmap = QPixmap(logoPath)
         pixmap = pixmap.scaled(QSize(28,28))
         logoLbl.setPixmap(pixmap)
         logoLbl.resize(pixmap.width(), pixmap.height())
      
      # senderBtn.setStyleSheet("background:")

   def allocateTransport(self):
      self.allocation = {}
      for city in self.demand.keys():
         cityAllocation={}
         for tpt in self.supply.keys():
            if len(cityAllocation)== 0:
               cityAllocation[tpt]={"value":0,"state":AllocationState.RELEASE}
            else:
               cityAllocation[tpt]={"value":1,"state":AllocationState.RELEASE}
         self.allocation[city]=cityAllocation
      

class CategorySelector(QDialog):
   dialogClosed = pyqtSignal(list)
   def __init__(self,categories,label="Category Selector"):
      super().__init__()
      self.categories = categories
      self.labelFont = QFont("Helvetica", 10)
      self.setGeometry(0,0,500,600)
      qtRectangle = self.frameGeometry()
      centerPoint = QDesktopWidget().availableGeometry().center()
      qtRectangle.moveCenter(centerPoint)
      self.move(qtRectangle.topLeft())
      self.setWindowTitle("HELLO!")

      selectorLayout = QVBoxLayout()

      self.selectorTable = QTableWidget()
      self.selectorTable.verticalHeader().setVisible(False)
      self.selectorTable.horizontalHeader().setVisible(False)
      self.selectorTable.setColumnCount(1)
      self.selectorTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
      for category in self.categories:
         currPos = self.selectorTable.rowCount()
         self.selectorTable.insertRow(currPos)
         checkbox = QCheckBox(category.value)
         checkbox.setChecked(category.isChecked)
         checkbox.setFont(self.labelFont)
         checkbox.stateChanged.connect(lambda state, category=category: self.onCheckboxChanged(state, category))
         checkbox.setStyleSheet("padding-left:10px")
         self.selectorTable.setCellWidget(currPos,0,checkbox)
      
      self.searchBox = QLineEdit()
      self.searchBox.setPlaceholderText("Search")
      self.searchBox.setFont(self.labelFont)
      self.searchBox.setFixedHeight(40)
      self.searchBox.setStyleSheet('''
            QLineEdit {
                border: 1px solid gray;
                border-radius: 10px;
                padding: 2px 10px;
            }
        ''')
      self.searchBox.textChanged.connect(self.onSearchTextChanged)
      selectorLayout.addWidget(self.searchBox)

      selectorLayout.addWidget(self.selectorTable)
      self.okBtn = QPushButton('OK')
      self.okBtn.clicked.connect(self.onOkClicked)
      self.okBtn.setFixedSize(100,40)
      selectorLayout.addWidget(self.okBtn,alignment=Qt.AlignRight)
      self.setLayout(selectorLayout)

   def onCheckboxChanged(self,state,category):
      category.isChecked = state == Qt.Checked

   def onOkClicked(self):
      self.dialogClosed.emit(self.categories)
      self.close()
   
   def onSearchTextChanged(self,text):
      print(text,self.selectorTable.rowCount(),self.selectorTable.columnCount())
      regex_pattern = r'^{}.*'.format(re.escape(text))
      regex = re.compile(regex_pattern, re.IGNORECASE)
      for i in range(self.selectorTable.rowCount()):
         item = self.selectorTable.cellWidget(i, 0)  
         print('item',item)
         if item:
            category = item.text()
            print('category',category)
            match = regex.match(category)
            self.selectorTable.setRowHidden(i, match is None)
   
class AllocationState(Enum):
   RELEASE = 1
   BLOCKED = 2
   LOCKED = 3
   
class Category:
   def __init__(self):
      self.value=""
      self.isChecked = False
      
   def __init__(self,value,isChecked=False):
      self.value=value
      self.isChecked = isChecked
				

def main():
   app = QApplication(sys.argv)
   custom_font = QFont()
   custom_font.setWeight(32)
   # QApplication.setFont(custom_font, "QLabel")
   # QApplication.setFont(custom_font, "QTextEdit")
   # app.setStyleSheet('.QLabel { font-size: 10pt;}')
   ex = transportAllocator()
   ex.show()
   sys.exit(app.exec_())
	
if __name__ == '__main__':
   main()