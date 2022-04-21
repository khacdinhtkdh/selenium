import os
import shutil
import string
import time
import tkinter.ttk
from tkinter import *
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from unidecode import unidecode
import random
import re
from subprocess import CREATE_NO_WINDOW
from threading import Thread


link = "https://demo.computervision.com.vn/"
link_cmt = "https://demo.computervision.com.vn/ocr?type=CMND/CCCD"
link_gplx = "https://demo.computervision.com.vn/ocr?type=giay-phep-lai-xe-1"
upload = '//*[@id="gatsby-focus-wrapper"]/section/section/main/div/div/div[5]/div/div[1]/span/div/span/div'
upload2 = '//*[@id="gatsby-focus-wrapper"]/section/section/main/div/div/div[5]/div/div[1]/span/div/span/input'
xu_ly = '//*[@id="gatsby-focus-wrapper"]/section/section/main/div/div/div[5]/div/div[1]/button'
info = '//*[@id="gatsby-focus-wrapper"]/section/section/main/div/div/div[5]/div/div[2]/div/div'

image_add = 'https://www.hoclaixetphcm.com/wp-content/uploads/2016/05/giay-phep-lai-xe-hang-a1.jpg'
image_2 = 'https://daotaolaixeoto.com.vn/Images/images/gplx-ghep.jpg'

mydict_cmt = {"So the:": "CMT", "Ho ten:": "FULL NAME", "Ngay sinh:": "Birthday", "Thuong tru:": "ADDRESS"}
mydict_gplx = {"So the:": "GPLX", "Ho ten:": "FULL NAME", "Ngay sinh:": "Birthday", "Noi cu tru:": "ADDRESS"}

dict_txt_cmt = {'FULL NAME': '', 'Birthday': '', 'PHONE': '', 'EMAIL': '', 'PASS PAYPAL': '',
                'ADDRESS': '', 'ZIPCODE': '', 'CMT': '', 'VISA': ''}
dict_txt_gplx = {'FULL NAME': '', 'Birthday': '', 'PHONE': '', 'EMAIL': '', 'PASS PAYPAL': '',
                 'ADDRESS': '', 'ZIPCODE': '', 'GPLX': '', 'VISA': ''}

res_info_final = ""
folder_image = ""
zip_code = dict()
pattern = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"


def func_select_folder():
    global folder_image
    folder_image = filedialog.askdirectory()


def get_info(get_type):
    global res_info_final, folder_image
    options = webdriver.ChromeOptions()
    # options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    options.add_argument('headless')
    # options.add_argument('window-size=0x0')

    if get_type == 'CMT':
        get_link = link_cmt
        mydict = mydict_cmt
        dict_txt = dict_txt_cmt
    else:
        get_link = link_gplx
        mydict = mydict_gplx
        dict_txt = dict_txt_gplx

    # clear output file
    # output file in selected folder + output
    dir_out = os.path.join(folder_image, 'output')
    if os.path.isdir(dir_out):
        shutil.rmtree(dir_out)

    # chon folder anh muon lay thong tin
    list_image_dirs = []
    for root_dir, dirs, files in os.walk(folder_image):
        for file in files:
            dir_1 = os.path.join(root_dir, file)
            dir_2 = dir_1.replace('/', '\\')
            list_image_dirs.append(dir_2)
    print(list_image_dirs)

    # Get zipcode in zipcode file
    file_zip = open('plugins/zipcode.txt', 'r')
    for line in file_zip:
        address = line.split(':')[0]
        address = address.lower()
        code = line.split(':')[1].replace('\n', '')
        if '-' in code:
            code = code.split('-')[0]
        zip_code[address] = code
    file_zip.close()

    service = Service(executable_path="plugins/chromedriver.exe")
    service.creationflags = CREATE_NO_WINDOW
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(2)
    # driver.execute_script("window.open('{}', 'new_window')".format(link2))
    driver.get(get_link)

    # get info
    for list_image_dir in list_image_dirs:
        # file name
        file_name = list_image_dir.split('\\')[-1]
        file_name = file_name.split('.')[0]

        # click upload file
        upload_e = driver.find_element(By.XPATH, upload2)
        upload_e.send_keys(list_image_dir)
        # upload_e.click()
        # time.sleep(2)
        # send_keys(list_image_dir)
        # time.sleep(5)
        # send_keys('{VK_RETURN}')

        # doi chon anh xong roi bam vao xu ly//
        time.sleep(2)
        xu_ly_e = driver.find_element(By.XPATH, xu_ly)
        driver.execute_script("arguments[0].click();", xu_ly_e)

        # cho load thong tin
        time.sleep(10)

        # get thong tin
        info_e = driver.find_element(By.XPATH, info)
        # print(info_e.text)
        line_eng = unidecode(info_e.text)
        lines = line_eng.split('\n')
        pre = ""
        for line in lines:
            if pre in mydict.keys():
                mm = line.split(' -')[0]
                dict_txt[mydict.get(pre)] = mm
            pre = line

        pass_pay = ''
        while not re.findall(pattern, pass_pay):
            pass_pay = ''.join(
                random.choice(string.ascii_uppercase + string.ascii_lowercase
                              + string.digits + "@#^&*") for _ in range(10))

        dict_txt['PASS PAYPAL'] = pass_pay

        # parse zipcode
        address_info = dict_txt['ADDRESS']
        tinh = address_info.split(', ')[-1]
        tinh = tinh.lower()
        if 'tp ' in tinh:
            tinh = tinh.replace('tp ', '')
        if '-' in tinh:
            tinh = tinh.split('-')[0]
        if 't ' in tinh:
            tinh = tinh.replace('t ', '')
        print('get:' + tinh)
        for key in zip_code.keys():
            if tinh in key:
                dict_txt['ZIPCODE'] = zip_code[key]
                break

        # write output
        file_name = file_name + '.txt'

        if not os.path.isdir(dir_out):
            os.mkdir(dir_out)
        file_name_output = os.path.join(dir_out, file_name)
        res_info_final = ""
        my_file = open(file_name_output, 'w+')

        for x, y in dict_txt.items():
            res_info_final = res_info_final + x + ': ' + y + '\n'
        my_file.write(res_info_final)
        my_file.close()

    driver.quit()


class Main(object):
    def __init__(self, master):
        self.master = master
        button1 = Button(master, text='Select folder', command=func_select_folder)
        button1.grid(row=1, column=0, pady=10, padx=10)
        button2 = Button(master, text='Get CMT Info', command=lambda x="CMT": self.get_info_image(x))
        button2.grid(row=1, column=1, pady=10, padx=10)
        button2 = Button(master, text='Get GPLX Info', command=lambda x="GPLX": self.get_info_image(x))
        button2.grid(row=1, column=2, pady=10, padx=10)
        self.progress = tkinter.ttk.Progressbar(master, length=280, orient=HORIZONTAL, mode='indeterminate')
        # self.progress.grid(row=2, column=0, columnspan=3, padx=5, pady=10)

    def monitor_convert(self, thread):
        if thread.is_alive():
            self.master.after(100, lambda: self.monitor_convert(thread))
        else:
            self.progress.stop()
            self.progress.grid_forget()
            print("done")

    def get_info_image(self, type_get):
        get_info_thread = GetInfo(type_get)
        get_info_thread.start()
        self.monitor_convert(get_info_thread)
        self.progress.grid(row=2, column=0, columnspan=3, padx=5, pady=10)
        self.progress.start()


class GetInfo(Thread):
    def __init__(self, type_get):
        super().__init__()
        self.type = type_get

    def run(self):
        get_info(self.type)


root = Tk()
app = Main(root)
root.title('Image to Text')
# root.geometry("400x300")
root.mainloop()
