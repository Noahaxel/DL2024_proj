import os
import numpy as np
import data_utils.transform as tr
from config import INIT_TRAINER
from torchvision import transforms
from converter.common_utils import hdf5_reader
from analysis.analysis_tools import calculate_CAMs, save_heatmap
from data_utils.csv_reader import csv_reader_single

mod = "ResNet1.0"

test_csv_path = './csv_file/cub_200_2011.csv_test.csv'
label_dict = csv_reader_single(test_csv_path, key_col='id', value_col='label')
testlist = label_dict.keys()
item = []
sort = []

for i in testlist:
    p = i[44:].split("/")
    sort.append(p[0])
    item.append(p[1][:-4])
features = []
img_paths = []

for i in range(len(item)):
    features.append(hdf5_reader('./analysis/mid_feature/%s/fold1/%s'%(mod,item[i]),'feature_in'))
    # 默认的hook获取池化层的输入和输出，池化层的输入'feature_in'即为最后一层卷积层的输出
    img_paths.append('./datasets/CUB_200_2011/CUB_200_2011/images/%s/%s.jpg'%(sort[i],item[i]))
    # 对应的原始图像路径


weight = np.load('./analysis/result/%s/fold1_fc_weight.npy'%mod)
# 线性层的权重
transformer = transforms.Compose([
    tr.ToCVImage(),
    tr.RandomResizedCrop(size=INIT_TRAINER['image_size'], scale=(1.0, 1.0)),
    tr.ToTensor(),
    tr.Normalize(INIT_TRAINER['train_mean'], INIT_TRAINER['train_std']),
    tr.ToArray(),
])

classes = 200 # 总类别数
class_idx = 0 # 模型预测类别，也可以从最终结果的csv里面批量读取
cam_path = './analysis/result/%s/cams/'%mod

for i in range(len(item)):
    cams = calculate_CAMs(features[i], weight, range(classes))  
    save_heatmap(cams, img_paths[i], class_idx, cam_path, transform=transformer)
