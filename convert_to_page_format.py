import os
from glob import glob
import cv2
import numpy as np
from tqdm import tqdm
from datetime import datetime
import lxml.etree as ET

_ns = {'p': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
output_folder='ahte_jults_identity_blobs_raw_result_xml/'
#os.makedirs('uutls_ahte_prediction_xml')
polygon_labels_dir= 'ahte_jults_identity_blobs_raw_result/'
original_pages_dir= '../../../datasets/ahte_dataset/ahte_test/'

def get_page_filename(image_filename: str) -> str:
    return os.path.join(os.path.dirname(image_filename),
                        '{}.xml'.format(os.path.basename(image_filename)[:-4]))


def get_basename(image_filename: str) -> str:
    directory, basename = os.path.split(image_filename)
    return '{}'.format( basename)


def save_and_resize(img: np.array, filename: str, size=None) -> None:
    if size is not None:
        h, w = img.shape[:2]
        resized = cv2.resize(img, (int(w*size), int(h*size)),
                             interpolation=cv2.INTER_LINEAR)
        cv2.imwrite(filename, resized)
    else:
        cv2.imwrite(filename, img)


def xml_to_coordinates(t):
    result = []
    for p in t.split(' '):
        values = p.split(',')
        assert len(values) == 2
        x, y = int(float(values[0])), int(float(values[1]))
        result.append((x,y))
    result=np.array(result)
    return result

def coordinates(cnt):
    coords=''
    for i in range(len(cnt[0])):
        coord=str(cnt[0][i][0][0])+','+str(cnt[0][i][0][1])+' '
        coords=coords+coord
    return coords[:-1]
    
def clean(img):
  #find all your connected components (white blobs in your image)
  nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(img, connectivity=8)
  #connectedComponentswithStats yields every seperated component with information on each of them, such as size
  #the following part is just taking out the background which is also considered a component, but most of the time we don't want that.
  sizes = stats[1:, -1]; nb_components = nb_components - 1
  
  # minimum size of particles we want to keep (number of pixels)
  #here, it's a fixed value, but you can set it as you want, eg the mean of the sizes or whatever
  min_size = 1000  
  
  #your answer image
  img2 = np.zeros((output.shape),dtype=np.uint8)
  #for every component in the image, you keep it only if it's above min_size
  for i in range(0, nb_components):
      if sizes[i] >= min_size:
          img2[output == i + 1] = 255
  return img2

original_path_list = glob('{}/*.png'.format(original_pages_dir))
for original_path in original_path_list:
    xmlns = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2018-07-15"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    schemaLocation = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15 http://schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd"

    PcGts = ET.Element("{" + xmlns + "}PcGts",
                       attrib={"{" + xsi + "}schemaLocation": schemaLocation},
                       nsmap={'xsi': xsi, None: xmlns})

    Metadata = ET.SubElement(PcGts, 'Metadata')
    Creator = ET.SubElement(Metadata, 'Creator')
    Creator.text = 'Berat'
    Metadata.append(Creator)
    Created = ET.SubElement(Metadata, 'Created')
    Created.text = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    Metadata.append(Created)
    LastChange = ET.SubElement(Metadata, 'LastChange')
    LastChange.text = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    Metadata.append(LastChange)
    PcGts.append(Metadata)

    original_page_name=get_basename(original_path)
    original_page = cv2.imread(original_path, 1)
    rows, cols, ch = original_page.shape
    Page = ET.SubElement(PcGts, 'Page')
    Page.set('imageFilename', original_page_name)
    Page.set('imageWidth', str(cols))
    Page.set('imageHeight', str(rows))

    TextRegion = ET.SubElement(Page, 'TextRegion')
    TextRegion.set('id', 'region_textline')
    TextRegion.set('custom', '0')
    Coords = ET.SubElement(TextRegion, 'Coords')
    TextRegion.append(Coords)


    polygon_labels = cv2.imread(polygon_labels_dir + original_page_name, 0)


    labels = np.unique(polygon_labels)[1:]
    textlineid = 0
    for tlabel in labels:
        textline = np.zeros((rows, cols), dtype=np.uint8)
        textline[polygon_labels == tlabel] = 255
        textline=clean(textline)
        #cv2.imwrite('dene/line'+str(textlineid)+'.png',textline)
        #tcontours, hierarchy = cv2.findContours(textline, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        tcontours, hierarchy = cv2.findContours(textline, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        rgb = cv2.merge((textline,textline,textline))
        cv2.drawContours(rgb, tcontours, -1, (0, 255, 0), 3)
        cv2.imwrite('dene/line'+str(textlineid)+'.png',rgb)
        tcoords = coordinates(tcontours)
        print(len(tcoords))
        TextLine = ET.SubElement(TextRegion, 'TextLine')
        TextLine.set('id', 'textline_' + str(textlineid))
        TextLine.set('custom', '0')
        textlineid = textlineid + 1
        Coords = ET.SubElement(TextLine, 'Coords')
        Coords.set('points', tcoords)
        TextLine.append(Coords)
        TextRegion.append(TextLine)

    Page.append(TextRegion)

    PcGts.append(Page)

    mydata = ET.tostring(PcGts, pretty_print=True, encoding='utf-8', xml_declaration=True)
    myfile = open('uutls_ahte_prediction_xml/' + original_page_name[:-4] + '.xml', "w")
    myfile.write(mydata.decode("utf-8"))
    myfile.close()

