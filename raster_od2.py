# 计算栅格转移矩阵
# 公式为：起始年栅格*10^n+末年

import arcpy
from arcpy import env
from arcpy.sa import *
import os
import sys
import csv
import math
import re


def check_file(workspace, fileout):
    env.workspace = workspace
    rasterslist = arcpy.ListRasters()
    if fileout not in rasterslist:
        pass
    else:
        arcpy.Delete_management(fileout)


def extract_numbers(string1):
    pattern1 = re.compile("(\d+)")
    result1 = re.findall(pattern1, string1)
    # print(result1)
    return int(result1[0])


def extract_characters(string1):
    pattern1 = re.compile("\D+")
    result1 = re.findall(pattern1, string1)
    # print(result1)
    return result1[0]


def extract_time1(valuei):
    pattern1 = re.compile("0.?(\d+)")
    result1 = re.findall(pattern1, valuei)[0]
    print(result1)
    # expression1 = "^[1-9].?(\d+)"
    # # expression1 = "^[1-9]\d+\%s" % result1[0]
    # print(expression1)
    # pattern2 = re.compile(expression1)
    # result2 = re.findall(pattern2, valuei)
    # print(result2)
    result2 = valuei.replace(result1, "")
    print(result2)


def extract_time2(valuei, digit_max):
    pos1 = 0 - digit_max
    result2 = valuei[pos1:]
    # print(result1, int(result1))
    pos2 = len(valuei) - digit_max
    result1 = valuei[0:pos2]
    # print(result2, int(result2))
    result1_int, result2_int = int(result1), int(result2)
    return result1_int, result2_int


def raster_od(in_raster1, in_raster2, out_raster3):
    # 获取栅格属性信息
    desc = arcpy.Describe(in_raster1)
    cellsize1 = desc.meanCellHeight
    print("像元大小为%s！" % cellsize1)
    # 栅格运算
    raster1_max = arcpy.GetRasterProperties_management(in_raster1, "MAXIMUM", "").getOutput(0)
    raster2_max = arcpy.GetRasterProperties_management(in_raster2, "MAXIMUM", "").getOutput(0)
    # print(raster1_max, type(raster1_max))
    digit1, digit2 = int(math.log(int(raster1_max), 10)), int(math.log(int(raster2_max), 10))
    digit_max = max(digit1, digit2) + 2
    print("像元值长度为%s！" % digit_max)
    multiplier = math.pow(10, digit_max)  # 位数+2，通常情况下代码的位数差距不超过1
    print("乘数因子为%s！" % multiplier)

    raster3 = in_raster1 * multiplier + in_raster2
    raster3_1 = Int(raster3)
    raster3_1.save(out_raster3)
    print("栅格OD图保存为%s！" % out_raster3)
    return cellsize1, digit_max


def get_parameter_values(in_raster1, in_raster2, out_raster3, output_file, val1, val2):
    # script arguments
    cellsize1, digit_max = raster_od(in_raster1, in_raster2, out_raster3)
    with open(output_file, 'a+', newline='') as f:
        csv_write = csv.writer(f)
        # value1, value2 = "T_%s" % val1, "T_%s" % val2
        # print(value1, value2)
        csv_write.writerow(["objectid", "Value", val1, val2, "Count", "Area"])
        cursors = arcpy.SearchCursor(out_raster3)
        num = 0
        try:
            for row in cursors:
                valuei = row.getValue('Value')
                # print(valuei)
                res1i, res2i = extract_time2(str(valuei), digit_max)
                # print(res1i, res2i)
                counti = row.getValue('Count')
                areai = counti * math.pow(cellsize1, 2)
                csv_write.writerow([num, valuei, res1i, res2i, counti, areai])
                num += 1
        except Exception as e:
            arcpy.AddError('Error!')


def main():
    # script arguments
    in_raster1 = arcpy.GetParameterAsText(0)
    in_raster2 = arcpy.GetParameterAsText(1)
    in_workspace = arcpy.GetParameterAsText(2)
    output_folder = arcpy.GetParameterAsText(3)
    output_csv = arcpy.GetParameterAsText(4)
    output_file = output_folder + "\\" + output_csv

    # 构建栅格OD图名
    val1, val2 = extract_numbers(in_raster1), extract_numbers(in_raster2)
    print("始末年份分别为%s、%s！" % (val1, val2))
    out_raster3 = extract_characters(in_raster1) + "_%s_%s" % (val1, val2)
    # 去重
    check_file(in_workspace, out_raster3)
    raster1, raster2 = arcpy.Raster(in_raster1), arcpy.Raster(in_raster2)
    # 分离文件名
    ras1, ras2 = os.path.basename(in_raster1), os.path.basename(in_raster2)
    get_parameter_values(raster1, raster2, out_raster3, output_file, ras1, ras2)
    print("已完成栅格转移矩阵！")


main()
