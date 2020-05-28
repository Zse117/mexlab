import sys
import os
from osgeo import gdal
from osgeo import ogr
from PySide2.QtWidgets import (QLineEdit, QPushButton, QApplication,
    QVBoxLayout, QDialog, QFileDialog, QComboBox, QGridLayout, QLabel)
from PySide2.QtWidgets import *
from PySide2.QtCore import *

class Cramolayout(QDialog):

   def __init__(self, parent=None):
      super(Cramolayout, self).__init__(parent)
      layout = QGridLayout()
      # layout.setColumnStretch(1, 3)
      # layout.setRowStretch(1, 3)
      layout.setColumnMinimumWidth(0, 100)
      layout.setColumnMinimumWidth(1, 100)
      layout.setColumnMinimumWidth(2, 100)
      layout.setColumnMinimumWidth(3, 100)


      self.btn_get_dtm = QPushButton("DTM file")
      self.btn_get_dtm.clicked.connect(self.get_dtm)
      layout.addWidget(self.btn_get_dtm, 0, 0)

      self.dtm_line = QLineEdit()
      layout.addWidget(self.dtm_line, 0, 1, 1, 3)

      self.btn_get_shp = QPushButton("shp file")
      self.btn_get_shp.clicked.connect(self.get_column_names)
      layout.addWidget(self.btn_get_shp, 1, 0)

      self.shp_line = QLineEdit()
      layout.addWidget(self.shp_line, 1, 1, 1, 3)

      self.lblName = QLabel('Id', self)
      self.lblName.setStyleSheet("font: 9pt Myriad Pro")
      layout.addWidget(self.lblName, 3, 0)

      self.lblName = QLabel('Crater size', self)
      self.lblName.setStyleSheet("font: 9pt Myriad Pro")
      layout.addWidget(self.lblName, 3, 1)

      self.lblName = QLabel('X coord', self)
      self.lblName.setStyleSheet("font: 9pt Myriad Pro")
      layout.addWidget(self.lblName, 3, 2)

      self.lblName = QLabel('Y coord', self)
      self.lblName.setStyleSheet("font: 9pt Myriad Pro")
      layout.addWidget(self.lblName, 3, 3)

      self.id_box = QComboBox()
      layout.addWidget(self.id_box, 4, 0)

      self.size_box = QComboBox()
      layout.addWidget(self.size_box,4, 1)

      self.x_coord_box = QComboBox()
      layout.addWidget(self.x_coord_box, 4, 2)

      self.y_coord_box = QComboBox()
      layout.addWidget(self.y_coord_box, 4, 3)

      self.chk_size = QCheckBox('Radius', self)
      self.chk_size.toggle()
      layout.addWidget(self.chk_size, 5, 1)

      self.chk_unit = QCheckBox('Size in meters', self)
      self.chk_unit.toggle()
      layout.addWidget(self.chk_unit, 6, 1)

      self.start_btn = QPushButton("Start cramo")
      # self.start_btn.clicked.connect(self.choose_parameters)
      self.start_btn.clicked.connect(self.create_for_txt_file)
      self.start_btn.clicked.connect(self.start_cramo)
      layout.addWidget(self.start_btn, 7, 0, 1, 4)

      # self.textEdit = QTextEdit(self)
      # self.textEdit.setStyleSheet("font: 9pt Myriad Pro")
      # layout.addWidget(self.start_btn, 8, 0)

      self.setWindowTitle("easyCramo V2")
      self.setLayout(layout)

   def get_dtm(self):
      dtm_path, filtr = QFileDialog.getOpenFileName(self,
                                                              "QFileDialog.getOpenFileName()",
                                                    self.dtm_line.text(),
                                                               "DTM file (*.tif *.bsq *.img *tiff)", "")
      if dtm_path:
         self.dtm_line.setText(dtm_path)
         # print(dtm_path)
      return dtm_path


   def get_shp(self):
      shp_path, filtr = QFileDialog.getOpenFileName(self,
                                                              "QFileDialog.getOpenFileName()",
                                                    self.shp_line.text(),
                                                              "Shp Files (*.shp)", "")
      if shp_path:
         self.shp_line.setText(shp_path)
         # print(shp_path)
      return shp_path


   def get_column_names(self):
      shp_file = self.get_shp()
      driver = ogr.GetDriverByName('ESRI Shapefile')
      ogrData = driver.Open(shp_file, 0)
      layer = ogrData.GetLayer(0)
      featDef = layer.GetLayerDefn()
      for i in range(featDef.GetFieldCount()):
         fieldDef = featDef.GetFieldDefn(i)
         field_name = fieldDef.GetNameRef()
         self.id_box.addItem(field_name)
         self.size_box.addItem(field_name)
         self.x_coord_box.addItem(field_name)
         self.y_coord_box.addItem(field_name)

   def choose_parameters(self):
      if self.chk_size.isChecked() is True:
         size = 2
      else:
         size = 1
      if self.chk_unit.isChecked() is True:
         length_unit = 1
      else:
         length_unit = 1000
      return (length_unit, size)

   def check_dtm(self):
      dtm_path = self.dtm_line.displayText()

   def get_geo_info(self):
      gdalData = gdal.Open(self.dtm_line.displayText())
      geo_info = gdalData.GetGeoTransform()
      return geo_info

   def create_for_txt_file(self):
      shp_path = self.shp_line.displayText()
      dtm_path = self.dtm_line.displayText()
      start_dir = os.path.dirname(shp_path)
      start_file = str(os.path.basename(shp_path))
      for_cramo_abs_path = start_dir + '\\for_' + start_file.split('.')[0] + '.txt'
      for_txt = open(for_cramo_abs_path, 'w')
      # print(start_file.split('.')[0])
      # print(shp_path)
      # print(for_cramo_abs_path)

      geo_info = self.get_geo_info()
      pix_scale = geo_info[1]
      x0 = geo_info[0]
      y0 = geo_info[3]

      driver = ogr.GetDriverByName('ESRI Shapefile')
      ogrData = driver.Open(shp_path, 0)
      layer = ogrData.GetLayer(0)
      circle_coef = int(self.choose_parameters()[0])
      unit = int(self.choose_parameters()[1])
      print(circle_coef, unit)
      # print(type(circle_coef), type(unit))
      for crat_feature in layer:
         crat_id = str(int(crat_feature.GetField(self.id_box.currentText())))
         size = str(
                     int(
                        (crat_feature.GetField(self.size_box.currentText())) # / 2 # проверить как лучше так или делить на 2
                        * (unit) * (circle_coef) // pix_scale
                        )
                   )
         x_coord = str(int(
            (crat_feature.GetField(self.x_coord_box.currentText()) - x0) // pix_scale
                           ))
         y_coord = str(int(
            (y0 - crat_feature.GetField(self.y_coord_box.currentText())) // pix_scale
                           ))
         for_txt.write(crat_id + ' ' + x_coord + ' ' + y_coord + ' ' + size + '\n')

   def start_cramo(self):
      start_time = QDateTime.currentDateTime()
      s_time = start_time.toString(Qt.DefaultLocaleShortDate)
      print(s_time)

      shp_path = self.shp_line.displayText()
      dtm_path = self.dtm_line.displayText()
      start_file = str(os.path.basename(shp_path))
      start_dir = str(os.path.dirname(shp_path))
      start_dtm_file = str(os.path.basename(dtm_path))
      for_cramo_txt = 'for_' + start_file.split('.')[0] + '.txt'
      res_cramo_txt ='res_' + start_file.split('.')[0] + '.txt'

      cmdcommand = 'cramo_app.ex' + ' ' + start_dtm_file + ' < ' + for_cramo_txt + ' > ' + res_cramo_txt
      print(cmdcommand)
      # print('cramo=', cmd_cram)
      infodir = 'info_' + start_file.split('.')[0] + '.txt'
      infotxt = open(infodir, 'w')
      infotxt.write(cmdcommand)
      infotxt.close()
      os.chdir(start_dir)
      os.system(cmdcommand)
      end_time = QDateTime.currentDateTime()
      e_time = end_time.toString(Qt.DefaultLocaleShortDate)
      print(e_time)
      print('ready')




if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Cramolayout()
    form.show()
    sys.exit(app.exec_())