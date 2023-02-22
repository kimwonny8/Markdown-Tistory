import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json
import requests
import mistune

output = 'json'						#고정값
grant_type = 'authorization_code'   #고정값 
visibility = 0  #0은 비공개, 3은 공개 발행
category_id_list = {}
tags = []

# 실행시 json에서 데이터 가져와서 저장
def getData():
    with open('tistory.json', 'r') as f:
        global json_data
        json_data = json.load(f)

        global client_id
        client_id = json_data['client_id']

        global client_secret
        client_secret = json_data['client_secret']

        global code
        code = json_data['code']

        global redirect_uri
        redirect_uri = json_data['redirect_uri']

        global blogName
        blogName = json_data['blogName']

        if chkJsonKey(json_data, 'access_token')==False:
            getToken()

        else :
            global access_token
            access_token = json_data['access_token']


# json파일에 key여부 확인
def chkJsonKey(json, key):
    try:
        tmp = json[key]
        print(tmp)
        if "error" in tmp:
            print("토큰 오류")
            return False
        else: 
            print("토큰 있음")
            return True
    except:
        print("토큰 없음")
        return False


# access_token 가져오기
def getToken():
    url = 'https://www.tistory.com/oauth/access_token?'
    data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'code': code,
            'grant_type': grant_type
            }
    r = requests.get(url, data)
    print (r.text)
    global access_token
    access_token=r.text[13:len(r.text)]
    print (access_token)
    setToken()


def setToken():
    with open('tistory.json', 'r') as f:
        data = json.load(f)
        data["access_token"] = access_token

    with open('tistory.json', 'w', encoding="utf-8") as f2:
        json.dump(data, f2, indent="\t")
        


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 툴바 - 파일 추가
        openFile = QAction(QIcon('./img/folder.png'), '파일 선택', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('티스토리에 업로드할 파일 선택해주세요.')
        openFile.triggered.connect(self.showDialog)

        # 툴바 - 카테고리 추가 버튼
        addTagBtn = QAction(QIcon('./img/tag.png'), '태그 입력', self)
        addTagBtn.setShortcut('Ctrl+T')
        addTagBtn.setStatusTip('티스토리에 업로드할 글의 태그를 추가해주세요.')
        addTagBtn.triggered.connect(self.openAddTag)

        # 툴바 - 업로드 버튼
        uploadBtn = QAction(QIcon('./img/upload.png'), '공개 글로 작성', self)
        uploadBtn.setShortcut('Ctrl+S')
        uploadBtn.setStatusTip('클릭시 티스토리에 공개 글로 자동 업로드됩니다.')
        uploadBtn.triggered.connect(self.openPosting)

        uploadBtn2 = QAction(QIcon('./img/secret_upload.png'), '비공개 글로 작성', self)
        uploadBtn2.setShortcut('Ctrl+D')
        uploadBtn2.setStatusTip('클릭시 티스토리에 비공개 글로 자동 업로드됩니다.')
        uploadBtn2.triggered.connect(self.secretPosting)

        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)

        self.statusBar()
        self.toolbar = self.addToolBar('업로드')
        self.toolbar.addAction(openFile)
        self.toolbar.addSeparator()
        self.toolbar.addAction(addTagBtn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(uploadBtn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(uploadBtn2)
        
        self.setWindowTitle('Markdown to Tistory by kimwonny8')
        self.resize(700, 700)
        self.center()
        self.show()

        # QDialog 설정
        self.dialog = QDialog()

    def openAddTag(self):
        lbl1 = QLabel('추가할 태그를 한 줄 단위로 적어주세요.', self.dialog)
        lbl1.move(40,15)
        
        self.dialog.te = QTextEdit(self.dialog)
        self.dialog.te.move(50, 50)

        # 추가 버튼
        btnDialog = QPushButton("추가", self.dialog)
        btnDialog.move(80, 270)
        btnDialog.clicked.connect(self.addTag)
        
        # 닫기 버튼
        btnDialog2 = QPushButton("닫기", self.dialog)
        btnDialog2.move(190, 270)
        btnDialog2.clicked.connect(self.dialogClose)

        # QDialog 세팅
        self.dialog.setWindowTitle('태그 추가하기')
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.resize(350, 320)
        self.dialog.show()
        self.center()


    # Dialog 닫기 이벤트
    def dialogClose(self):
        self.dialog.close()

    def addTag(self):
        global tags
        tags = self.dialog.te.toPlainText().split('\n')
        tags = list(filter(None, tags))
        print(tags)
        if len(tags) == 0 :
            QMessageBox.warning(self,'태그 추가 실패', "추가한 태그가 없습니다.")
        else :
            res = self.QuestionInfo("추가할 태그가 "+ ", ".join(tags) +" 맞습니까?")
            if res == True :
                self.dialogClose()
            else :
                QMessageBox.warning(self,'태그 추가 실패', "한 줄 단위로 다시 입력해주세요")
      

    # Question-information 버튼 클릭 이벤트
    def QuestionInfo(self, msg):
        buttonReply = QMessageBox.information(
            self, 'Check', msg, 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No )

        if buttonReply == QMessageBox.Yes:
            print('Yes clicked.')
            return True
        else:
            print('No clicked.')
            return False    

    # ERROR 클릭 이벤트
    def ERROR(self, msg) :
        QMessageBox.critical(self,'ERROR!', msg)

    # Question-Warning 버튼 클릭 이벤트
    def QuestionWarning(self):
        buttonReply = QMessageBox.warning(
            self, 'ERROR', "카테고리가 잘못 선택되었습니다.\n확인을 누르시면 카테고리 없이 등록됩니다.", 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No )

        if buttonReply == QMessageBox.Yes:
            print('Yes clicked.')
            global category
            category = -1
        else:
            print('No clicked.')

    # 중앙정렬
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 파일 읽어와서 띄우기    
    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')

        try:
            if fname[0]:
                f = open(fname[0], 'r', encoding="utf-8")
                global select_file
                select_file = f.name
                print(select_file)
            
                # markdown to html
                with f:
                    data = f.read()
                    global html_text
                    html_text = mistune.markdown(data)
                    self.textEdit.setText(html_text)
        except:
             self.ERROR('잘못된 파일 형식입니다.')

    def secretPosting(self):
        global visibility
        visibility = 0
        self.findSelectedFile()

    def openPosting(self):
        global visibility
        visibility = 3 
        self.findSelectedFile()

    # 선택한 파일 잘라서 이름, 카테고리 알기
    def findSelectedFile(self):
        try:
            global select_file_list
            select_file_list = select_file.split('/')
        except:
            self.ERROR('파일을 선택 후 진행해 주세요')

        global select_file_name
        select_file_name = select_file_list[len(select_file_list)-1].rstrip('.md')
        print(select_file_name)

        global select_file_category
        select_file_category = select_file_list[len(select_file_list)-2]
        print(select_file_category)

        self.getCategory()
        try :
            self.post()
        except:
            self.ERROR('파일 업로드에 실패하였습니다.')

    # 카테고리 리스트
    def getCategory(self):
        url = 'https://www.tistory.com/apis/category/list?'
        data = {
                'access_token': access_token,
                'output': output,
                'blogName': blogName,
                }
        r = requests.get(url, data)
        print(r)

        if r.status_code == 200:
            r_json = r.json()
            data = r_json['tistory']['item']['categories']

            for i in data:
                category_id_list[i["name"]]=i["id"]

            try: 
                global category
                category = category_id_list[select_file_category]
            except:
                self.QuestionWarning()

    
    # 글 작성
    def post(self):
            tag = []
            global tags
            if len(tags)==0 :
                tag = ""
            else : tag = ','.join(tags) 

            url = 'https://www.tistory.com/apis/post/write?'
            data = {
                    'access_token': access_token,
                    'output': output,
                    'blogName': blogName,
                    'title': select_file_name,
                    'content': html_text,
                    'visibility': visibility,
                    'category': category,
                    'tag': tag,
                    }
            r = requests.post(url, data=data)
            print(category)
            print(select_file_name,"자동 포스팅 완료")
            QMessageBox.information(self,'success!', select_file_name+' 글이 블로그에 업로드 되었습니다.')
          

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    try:
        getData()
    except:
        MyApp.ERROR('tistory.json 파일에 내용을 입력 후 진행해주세요.')
    
    sys.exit(app.exec_())
