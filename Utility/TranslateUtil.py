import os
import xlwt
import xlrd
import shutil
import logging
loggFileName = 'tra.log'
logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(message)s',
            datefmt='%m-%d %H:%M:%S',
            handlers=[logging.FileHandler(loggFileName, 'w', 'utf-8')])

langs = {"cs_CZ", "de_DE", "es_ES", "fr_CA", "fr_FR", "hu_HU", "it_IT", "ja_JP", "pl", "ru", "sl", "zh_CN",
             "zh_TW", "en_US"}

fullyFolder = "fully"
syncFolder = "syncs"
updateFolder = "update"
transFolder = "translated"
appliedFolder = "applied"

def fetchi18nToDic(filePath):
    _dictionary = {}
    with open(filePath, 'r', encoding="utf-8") as f:
        eng_contents = f.readlines()
        index = 0
        lines = len(eng_contents)
        for index in range(lines):
            key = eng_contents[index].split(" ", 1)
            if key[0] == "msgid":
                value = eng_contents[index + 1].split(" ", 1)
                # rstrip 去尾/n
                _dictionary[key[1].rstrip()] = value[1].rstrip()
            elif key[0] != "msgstr" and key[0] != "msgid" and key[0] != "\n":
                _dictionary[key[0].rstrip()] = key[0].rstrip()

    return _dictionary, eng_contents

# 將sync過的檔案覆蓋到專案的i18n
def replaceToEachLangFile(srcDir):
    PROJECT_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
    for lang in langs:
        sync_fpath = os.path.join(PROJECT_ROOT_PATH, srcDir, lang)
        lang_fpath = os.path.join(PROJECT_ROOT_PATH, "..", "i18n", lang, "LC_MESSAGES", "messages.po")
        shutil.copy(sync_fpath, lang_fpath)
        print("copy {src} to {dest}".format(src=sync_fpath, dest=lang_fpath))

    print("*** copy finished***")

def coveri18nFileToXLS(destDir, isFully):
    # 先將英文語系檔讀出放至dictionary
    enDictionary = {}
    PROJECT_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

    en_fpath = os.path.join(PROJECT_ROOT_PATH, destDir, "en_US")
    enDictionary = fetchi18nToDic(en_fpath)[0]

    for lang in langs:
        langDictionary = {}
        PROJECT_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
        lang_fpath = os.path.join(PROJECT_ROOT_PATH, destDir, lang)

        with open(lang_fpath, 'r', encoding="utf-8") as f:
            # with open('i18n.po', 'w', encoding="utf-8") as f2:
            lang_contents = f.readlines()
            index = 0
            lines = len(lang_contents)
            for index in range(lines):
                key = lang_contents[index].split(" ", 1)
                if key[0] == "msgid":
                    value = lang_contents[index + 1].split(" ", 1)
                    # rstrip 去尾/n
                    langDictionary[key[1].rstrip()] = value[1].rstrip()
                elif key[0] != "msgstr" and key[0] != "msgid" and key[0] != "\n":
                    langDictionary[key[0].rstrip()] = key[0].rstrip()

        destPath = os.path.join(destDir, lang)
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Traslate')
        ws.write(0, 0,"English/Original")
        ws.write(0, 1, "Translation")
        row = 1
        # 將column1, column2欄寬預設為100
        ws.col(0).width = 256 * 100 #  The value is an integer specifying the size measured in 1/256 of the width of the character ‘0’ as it appears in the sheet’s default font
                                    # 256 * characters wide (-ish)
        ws.col(1).width = 256 * 100
        for key in langDictionary:
            if isFully:
                if langDictionary[key] == enDictionary[key]:
                    ws.write(row, 0, langDictionary[key].replace("\"", ""))
                else:
                    ws.write(row, 0, enDictionary[key].replace("\"", ""))
                    ws.write(row, 1, langDictionary[key].replace("\"", ""))
                row+=1
            elif not isFully:
                if langDictionary[key] == enDictionary[key]:
                    ws.write(row, 0, langDictionary[key].replace("\"", ""))
                    row += 1

        wb.save(destPath+'.xls')
        print("***產生{lang}翻譯檔***".format(lang=lang))
    print("***已於{destDir}資料夾產生翻譯檔***".format(destDir=destDir))

def syncEachLangByEnglish(destDir):
    # 先將英文語系檔讀出放至dictionary
    enDictionary = {}
    PROJECT_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
    en_fpath = os.path.join(PROJECT_ROOT_PATH, "..", "i18n", "en_US", "LC_MESSAGES", "messages.po")
    enDictionary, eng_contents = fetchi18nToDic(en_fpath)

    # 將要比對的語系檔讀出放至dictionary
    for lang in langs:
        dictionary = {}
        fpath = os.path.join(PROJECT_ROOT_PATH, "..", "i18n", lang, "LC_MESSAGES", "messages.po")

        with open(fpath, 'r', encoding="utf-8") as f:
            # with open('i18n.po', 'w', encoding="utf-8") as f2:
            contents = f.readlines()
            index = 0
            lines = len(contents)
            for index in range(lines):
                key = contents[index].split(" ", 1)
                if key[0] == "msgid":
                    value = contents[index + 1].split(" ", 1)
                    # rstrip 去尾/n
                    dictionary[key[1].rstrip()] = value[1].rstrip()

        destPath = os.path.join(destDir,lang)
        with open(destPath, 'w+', encoding="utf-8") as tra:
            lines = len(eng_contents)
            # 把英文的po檔讀出來
            # 讀英文po檔的msgid所有id，若要sync的語系沒翻譯就直接將英文的msgid與msgstr貼上
            for index in range(lines):
                key = eng_contents[index].split(" ", 1)
                if len(key) > 1:
                    if key[0] == "msgid":
                        key[1] = key[1].rstrip()
                        if len(key) > 1 and key[1] in dictionary:
                            tra.write("msgid")
                            tra.write(" ")
                            tra.write(key[1])
                            tra.write("\n")
                            tra.write("msgstr")
                            tra.write(" ")
                            tra.write(dictionary[key[1]])
                            tra.write("\n")
                        elif len(key) > 1 and key[1] in enDictionary:
                            tra.write(eng_contents[index])
                            tra.write(eng_contents[index+1])
                else:
                    for c in key:
                        tra.write(c)

def readTransExcel(srcDir, destDir):
    PROJECT_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

    # 將i18n原始檔複製出來
    for lang in langs:
        lang_fpath = os.path.join(PROJECT_ROOT_PATH, "..", "i18n", lang, "LC_MESSAGES", "messages.po")

        ori_dir = os.path.join(PROJECT_ROOT_PATH, destDir, lang)
        shutil.copy(lang_fpath, ori_dir)

    for _lang in langs:
        _xlsPath = os.path.join(PROJECT_ROOT_PATH, srcDir,_lang+".xls")
        result = dict()
        if not os.path.exists(_xlsPath):
            continue

        print("*** {xls} found ***".format(xls=_xlsPath))
        print("*** 開始套用{lang}翻譯***".format(lang=_lang))

        # 先將英文語系檔讀出放至dictionary
        enDictionary = {}
        PROJECT_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
        en_fpath = os.path.join(PROJECT_ROOT_PATH, "..", "i18n", "en_US", "LC_MESSAGES", "messages.po")
        with open(en_fpath, 'r', encoding="utf-8") as f:
            # with open('i18n.po', 'w', encoding="utf-8") as f2e:
            eng_contents = f.readlines()
            index = 0
            lines = len(eng_contents)
            # print(eng_contents)
            for index in range(lines):
                key = eng_contents[index].split(" ", 1)
                if key[0] == "msgid":
                    value = eng_contents[index + 1].split(" ", 1)
                    # rstrip 去尾/n
                    enDictionary[key[1].rstrip()] = value[1].rstrip()

        langDictionary = {};
        translatedDictionary = {};

        wb = xlrd.open_workbook(_xlsPath, on_demand=True)  # on_demand = true => without loading the whole file
        for sheet in wb.sheets():
            if sheet.name.lower() == "traslate":
                number_of_rows = sheet.nrows
                for row in range(1, number_of_rows):
                    key = str(sheet.cell(row, 0).value)
                    #把qoute加回來
                    key = "\"" + key + "\""
                    value = str(sheet.cell(row, 1).value)
                    result[key] = "\"" + value + "\""
        for tranFileEnglish in result.keys():
            translatedDictionary[tranFileEnglish] = result[tranFileEnglish]

        PROJECT_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
        _lang_fpath = os.path.join(PROJECT_ROOT_PATH, "..", "i18n", _lang, "LC_MESSAGES", "messages.po")
        with open(_lang_fpath, 'r', encoding="utf-8") as f:
            # with open('i18n.po', 'w', encoding="utf-8") as f2e:
            lang_contents = f.readlines()
            index = 0
            lines = len(lang_contents)
            for index in range(lines):
                key = lang_contents[index].split(" ", 1)
                if key[0] == "msgid":
                    value = lang_contents[index + 1].split(" ", 1)
                    # rstrip 去尾/n
                    langDictionary[key[1].rstrip()] = value[1].rstrip()

        # 拿excel讀到的英文與英文的i18n檔做比較，找到在i18n對應的key
        logging.info("***開始套用{lang}的翻譯***".format(lang=_lang))
        count = 0
        notin = []
        inkey = []
        for i18nKey, eng in enDictionary.items():
            if eng in translatedDictionary.keys():
                inkey.append(eng)
                count+=1
                # logging.info("英文i18n key: {key}".format(key=i18nKey))
                # logging.info("英文i18n value:{value}".format(value=eng))
                # logging.info("翻譯: {value}".format(value=translatedDictionary[eng]))
                # logging.info("翻譯後value: "+translatedDictionary[eng])
                langDictionary[i18nKey] = translatedDictionary[eng]

        logging.info("***結束套用{lang}的翻譯共套用{count}個***".format(lang=_lang, count=count))
        # 找沒套到的
        for k in translatedDictionary.keys():
            if k not in inkey:
                logging.info("不在翻譯中的: " + k)

        PROJECT_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
        ori_fpath = os.path.join(PROJECT_ROOT_PATH, destDir, _lang)
        # ori_fpath = os.path.join(PROJECT_ROOT_PATH, ori_dir, "messages.po")

        # 要把翻譯文件按照格式寫回去，所以需要把原本的內容讀出來改過再寫回去
        with open(ori_fpath, 'r', encoding="utf-8") as f:
            ori_contents = f.readlines()
        with open(ori_fpath, 'w+', encoding="utf-8") as tra:
            index = 0
            lines = len(ori_contents)
            tra.write("# Copyright (C) CyberPower Systems, Inc. ALL RIGHTS RESERVED.\n")
            tra.write("msgid \"\"\n")
            tra.write("msgstr \"\"\n")
            tra.write("\"Project-Id-Version: \\n\"\n")
            tra.write("\"POT-Creation-Date: 2017-06-05 11:32+0800\\n\"\n")
            tra.write("\"PO-Revision-Date: 2017-06-05 11:34+0800\\n\"\n")
            tra.write("\"Last-Translator: \\n\"\n")
            tra.write("\"Language-Team: \\n\"\n")
            tra.write("\"MIME-Version: 1.0\\n\"\n")
            tra.write("\"Content-Type: text/plain; charset=UTF-8\\n\"\n")
            tra.write("\"Content-Transfer-Encoding: 8bit\\n\"\n")
            tra.write("\"Plural-Forms: nplurals=1; plural=0;\\n\"\n")

            for index in range(lines):
                key = ori_contents[index].split(" ", 1)
                if len(key) > 1:
                    if key[0] == "msgid":
                        key[1] = key[1].rstrip()
                        # key[0] != "" ------ skip msgid "" PO檔規定需要放在header，所以在上面程式固定會寫入在header，skip是避免parse時寫入
                        if len(key) > 1 and key[1] == "\"\"":
                            # do nothing
                            pass
                        elif len(key) > 1 and key[1] in langDictionary:
                            tra.write("msgid")
                            tra.write(" ")
                            tra.write(key[1])
                            tra.write("\n")
                            tra.write("msgstr")
                            tra.write(" ")
                            tra.write(langDictionary[key[1]])
                            tra.write("\n")
                        else:
                            tra.write(ori_contents[index])
                else:
                    tra.write(ori_contents[index])

    print("***套用翻譯結束，詳細結果請參考{log}***".format(log=loggFileName))

if __name__ == "__main__":
    while True:
        print("Translate File Tool Options")
        print("1: Generate each Language File by English File (fully)")
        print("2: Generate each Language File by English File (update)")
        print("3: Appy ** 將fully或update資料夾中產生的xls翻譯檔給相關人員翻譯，再將翻譯回來的xls檔放入translated資料夾後執行這個選項")
        print("4: 檢查i18n資料夾底下各語系未翻譯的部分，將未翻譯的文字以英文補上 ** 注意: 此操作會修改i18n資料夾底下各語系的message.po")
        print("5: 將applied資料夾的翻譯套用至i18n資料夾 ** 注意: 此操作會修改i18n資料夾底下各語系的message.po")
        print("enter exit to exit")
        text = input()  # Python 3

        if text == "1":
            if not os.path.isdir(fullyFolder):
                os.mkdir(fullyFolder)
            syncEachLangByEnglish(fullyFolder)
            coveri18nFileToXLS(fullyFolder, True)
        elif text == "2":
            if not os.path.isdir(updateFolder):
                os.mkdir(updateFolder)
            syncEachLangByEnglish(updateFolder)
            coveri18nFileToXLS(updateFolder, False)
        elif text == "3":
            if not os.path.isdir(transFolder):
                print("找不到translated資料夾")
                exit(0)
            elif os.listdir(transFolder).__len__() <= 0:
                print("translated資料夾裡沒有任何翻譯檔")
                exit(0)

            if not os.path.isdir(appliedFolder):
                os.mkdir(appliedFolder)

            readTransExcel(transFolder, appliedFolder)

        elif text == "4":
            if not os.path.isdir(syncFolder):
                os.mkdir(syncFolder)
            syncEachLangByEnglish(syncFolder)
            replaceToEachLangFile(syncFolder)

        elif text == "5":
            if not os.path.isdir(appliedFolder):
                print("找不到applied資料夾")
                exit(0)
            replaceToEachLangFile(appliedFolder)

        elif text == "exit":
            exit(0)



