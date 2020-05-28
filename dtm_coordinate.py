import sys
from osgeo import gdal
from osgeo import osr
from PySide2.QtWidgets import (QLineEdit, QPushButton, QApplication,
     QDialog, QFileDialog, QGridLayout, QMessageBox)
from PySide2.QtCore import QDateTime, Qt


class Cramolayout(QDialog):

   def __init__(self, parent=None):
      super(Cramolayout, self).__init__(parent)
      layout = QGridLayout()
      # layout.setColumnStretch(1, 3)
      # layout.setRowStretch(1, 3)
      layout.setColumnMinimumWidth(0, 100)
      layout.setColumnMinimumWidth(1, 100)
      layout.setColumnMinimumWidth(2, 200)
      layout.setColumnMinimumWidth(3, 100)

      self.btn_get_dtm = QPushButton("DTM file")
      self.btn_get_dtm.clicked.connect(self.get_dtm)
      layout.addWidget(self.btn_get_dtm, 0, 0)

      self.dtm_line = QLineEdit()
      layout.addWidget(self.dtm_line, 0, 1, 1, 3)

      self.start_btn = QPushButton("Create txt")
      self.start_btn.clicked.connect(self.start_time)
      self.start_btn.clicked.connect(self.create_txt)
      self.start_btn.clicked.connect(self.end_time)
      self.start_btn.clicked.connect(self.msgbox)
      layout.addWidget(self.start_btn, 1, 0, 1, 4)

      self.setWindowTitle("DTM coordinate")
      self.setLayout(layout)


   def start_time(self):
       start_time = QDateTime.currentDateTime()
       self.s_time = start_time.toString(Qt.DefaultLocaleShortDate)
       # print('start time', self.s_time)



   def get_dtm(self):
      dtm_path, filtr = QFileDialog.getOpenFileName(self,
                                                              "QFileDialog.getOpenFileName()",
                                                    self.dtm_line.text(),
                                                               "DTM file (*.tif *.bsq *.img *tiff)", "")
      if dtm_path:
         self.dtm_line.setText(dtm_path)


   def create_txt(self):

       data_raster = gdal.Open(self.dtm_line.displayText())
       geo_info = data_raster.GetGeoTransform()
       band = data_raster.GetRasterBand(1)
       data_proj = data_raster.GetProjectionRef()
       data_srs = osr.SpatialReference(data_proj)
       geo_srs = data_srs.CloneGeogCS()  # new srs obj to go from x,y -> φ,λ
       geo_transform = osr.CoordinateTransformation(data_srs, geo_srs)

       dtm_arr = band.ReadAsArray()
       dtm_path = self.dtm_line.displayText()
       dtm_array = dtm_path.split('.')[0] + '_array_1.txt'
       array_txt = open(dtm_array, 'w')
       array_txt.write('Heights  ' + 'x  ' + 'y' + '\n')
       line_count = 0
       txt_count = 1

       bag = gdal.Open(self.dtm_line.displayText())  # replace it with your file
       bag_gtrn = bag.GetGeoTransform()
       bag_proj = bag.GetProjectionRef()
       bag_srs = osr.SpatialReference(bag_proj)
       geo_srs = bag_srs.CloneGeogCS()  # new srs obj to go from x,y -> φ,λ
       transform = osr.CoordinateTransformation(bag_srs, geo_srs)


       y_index = 0
       for lines in dtm_arr:
           x_index = 0
           for h_value in lines:
               line_count += 1
               if line_count == 200000:
                   temp_dtm_txt = dtm_path.split('.')[0] + '_array_' + str(txt_count) + '.txt'
                   array_txt = open(temp_dtm_txt, 'w')
                   array_txt.write('Heights  ' + 'x  ' +'y'+ '\n')
                   line_count = 0
                   txt_count += 1
               # print('n =', n)
               x2 = geo_info[0] + geo_info[1] * x_index + geo_info[2] * y_index
               y2 = geo_info[3] + geo_info[4] * x_index + geo_info[5] * y_index
               geo_pt = transform.TransformPoint(x2, y2) [:2]
               geo_x = geo_pt[0]
               geo_y = geo_pt[1]
               min_delim = "' "
               sec = r'" '
               # print(x_index, y_index, geo_pt)
               if geo_pt[0] < 0:
                   x_degree = int(-geo_x // 1)
                   x_min = int((-geo_x - x_degree) * 60)
                   x_sec = ((-geo_x - x_degree) * 60 - x_min) * 60
                   x_coord = str(x_degree) + '° ' + str(x_min) + min_delim + str(x_sec) + sec + ' S'
               else:
                   x_degree = int(geo_x // 1)
                   x_min = (int(geo_x - x_degree) * 60)
                   x_sec = ((geo_x - x_degree) * 60 - x_min) * 60
                   x_coord = str(x_degree) + '° ' + str(x_min) + min_delim + str(x_sec) + sec + ' N'
               if geo_pt[1] < 0:
                   y_degree = int(-geo_y // 1)
                   y_min = int((-geo_y - y_degree) * 60)
                   y_sec = ((-geo_y - y_degree) * 60 - y_min) * 60
                   y_coord = str(y_degree) + '° ' + str(y_min) + min_delim + str(y_sec) + sec + ' W'
               else:
                   y_degree = int(geo_y // 1)
                   y_min = int((geo_y - y_degree) * 60)
                   y_sec = ((geo_y - y_degree) * 60 - y_min) * 60

                   y_coord = str(y_degree) + '° ' + str(y_min) + min_delim + str(y_sec) + sec + 'W'

               # print(x_degree, x_min, x_sec)
               # print(y_degree, y_min, y_sec)
               array_txt.write(str(float(h_value)) + '   ' + x_coord + '    '+ y_coord + '  '  + '\n')
               x_index += 1
           y_index += 1


   def end_time(self):
        end_time = QDateTime.currentDateTime()
        self.e_time = end_time.toString(Qt.DefaultLocaleShortDate)
        # print('end_time', self.e_time)


   def msgbox(self):
       msgb1 = QMessageBox()
       msgb1.setWindowTitle("Complited")
       msgb1.setIcon(QMessageBox.Information)
       msgb1.setText('start time:  ' + self.s_time + '\n' + 'end-time:  ' + self.e_time)
       msgb1.setGeometry(200, 80, 250, 20)
       retval = msgb1.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Cramolayout()
    form.show()
    sys.exit(app.exec_())