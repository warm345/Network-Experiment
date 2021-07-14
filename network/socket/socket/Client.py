import socket
import tkinter
import tkinter.messagebox
import threading
import json
import queue
import tkinter.filedialog
import os
import struct
import sounddevice
import soundfile
import datetime
import time
import pyaudio
from scipy.io.wavfile import write
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog

IP = ''
PORT = ''
user = ''
listbox1 = ''  # 用于显示在线用户的列表框
show = 1  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
chat = '-----------------'  # 聊天对象
filequeue = queue.Queue()
voice_socket=''
num = 1

#登陆窗口

root0 = tkinter.Tk()
root0.geometry("550x300")
root0.title('用户登陆窗口')
root0.resizable(0,0)
one = tkinter.Label(root0,width=600,height=300,bg="LightBlue") 
one.pack()

IP0 = tkinter.StringVar()	#从输入中获取IP
IP0.set('127.0.0.1') 	#设置初始IP
PORT = tkinter.StringVar()	#从输入中获取端口
PORT.set('6789')	#设置初始端口
USER = tkinter.StringVar() 	#从输入中获取用户名
USER.set('')

#设置输入IP框
labelIP = tkinter.Label(root0,text='IP地址',bg="LightBlue")
labelIP.place(x=120,y=50,width=100,height=40)
entryIP = tkinter.Entry(root0, width=60, textvariable=IP0)
entryIP.place(x=220,y=55,width=100,height=30)

#设置输入端口框
labelPORT = tkinter.Label(root0,text='端口号',bg="LightBlue")
labelPORT.place(x=120,y=100,width=100,height=40)
entryPORT = tkinter.Entry(root0, width=60, textvariable=PORT)
entryPORT.place(x=220,y=105,width=100,height=30)

##设置输入用户名框
labelUSER = tkinter.Label(root0,text='用户名',bg="LightBlue")
labelUSER.place(x=120,y=150,width=100,height=40)
entryUSER = tkinter.Entry(root0, width=60, textvariable=USER)
entryUSER.place(x=220,y=155,width=100,height=30)

def Login(*args):
	global IP, PORT, user
	#获取IP，PORT，USER
	IP = entryIP.get()
	PORT = entryPORT.get()
	user = entryUSER.get()
	#判断用户名是否为空
	if not user:
		tkinter.messagebox.showwarning('提示', message='用户名为空!')
	else:
		tkinter.messagebox.showwarning('提示', message='登陆成功!')
		root0.destroy()

#登录按钮
loginButton = tkinter.Button(root0, text ="登录", command = Login,bg="LightGreen")
loginButton.place(x=250,y=210,width=40,height=25)
root0.bind('<Return>', Login)

root0.mainloop()

# 建立连接
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, int(PORT)))
s.send(user.encode())  # 发送用户名


# 聊天窗口
root1 = tkinter.Tk()
root1.geometry("640x480")
root1.title('聊天室   用户:'+user)
root1.resizable(0,0)

# 消息界面
listbox = ScrolledText(root1)
listbox.place(x=5, y=0, width=640, height=320)
listbox.tag_config('tag', foreground='red')
listbox.insert(tkinter.END,'欢迎加入聊天室！','tag')
listbox.tag_config('tag1', foreground='blue')
listbox.tag_config('tag2', foreground='green')

#获取输入
INPUT = tkinter.StringVar()
INPUT.set('')
entryIuput = tkinter.Entry(root1, width=120, textvariable=INPUT)
entryIuput.place(x=5,y=320,width=640,height=170)

# 在线用户列表
listbox1 = tkinter.Listbox(root1)
listbox1.place(x=510, y=0, width=130, height=320)


def send(*args):
	if entryIuput.get():
		timeNow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		message ={'depcode':1,'msg': entryIuput.get()+':'+timeNow, 'user': user }
		message = json.dumps(message)
		msgsize = struct.pack("i",len(message))
		s.send(msgsize)      
		s.send(message.encode())
		INPUT.set('')
	else:
		tkinter.messagebox.showwarning('提示', message='输入为空！')

def clearing():
	INPUT.set('')

sendButton = tkinter.Button(root1, text ="发送",anchor = 'n',command = send,bg = 'LightBlue')
sendButton.place(x=530,y=430)
root1.bind('<Return>', send)

clearButton = tkinter.Button(root1, text ="清空",anchor = 'n',command = clearing,bg = 'LightBlue')
clearButton.place(x=585,y=430)

#读文件
def readSendFile(filename, tcp_cli):
        try:
            with open(filename, 'rb') as f:
                file_content = f.read()
                tcp_cli.send(file_content)
        except Exception as e:
            print(e)
            req = '没有该文件'
            tcp_cli.send(req.encode())
#发送文件
def sendFile():
    file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__))
    filename = os.path.basename(file)
    filequeue.put((file,filename))
    size = os.stat(file).st_size
    temp = {'depcode':3,'msg':filename+'~'+str(size)}
    if os.path.isfile(file):
        print(size,'  ',temp)
    temp = json.dumps(temp)
    msgsize = struct.pack("i",len(temp))
    s.send(msgsize)
    s.send(temp.encode())

sendFileButton = tkinter.Button(root1, text = "发送文件",command = sendFile,bg = 'LightBlue')
sendFileButton.place(x=5,y=300,width=50,height=50)
#发送语音
def sendVoice():
	# tkinter.messagebox.showwarning('提示', message='语音正在录入!')
    fs = 44100 
    seconds = 3 
	
    myrecording = sounddevice.rec(int(seconds * fs), samplerate=fs, channels=2)
    sounddevice.wait()  # Wait until recording is finished
    write('output.wav', fs, myrecording)  # Save as WAV file 
    if os.path.isfile('output.wav'):
        sendFile()

sendVoiceButton = tkinter.Button(root1, text = "发送语音",command = sendVoice,bg = 'LightBlue')
sendVoiceButton.place(x=75,y=300,width=50,height=50)
#播放语音
def playVoice():
    filename = 'output.wav'
    # Extract data and sampling rate from file
    data, fs = soundfile.read(filename, dtype='float32')  
    sounddevice.play(data, fs)
    status = sounddevice.wait()  # Wait until file is done playing

playVoiceButton = tkinter.Button(root1, text = "播放语音",command = playVoice,bg = 'LightBlue')
playVoiceButton.place(x=145,y=300,width=50,height=50)

def callVoice():
	global voice_socket
	voice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	voice_socket.connect(('127.0.0.1',5678))
	chunk_size = 1024  # 512
	audio_format = pyaudio.paInt16
	channels = 1
	rate = 20000

	p = pyaudio.PyAudio()
	playing_stream = p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                          frames_per_buffer=chunk_size)
	recording_stream = p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                            frames_per_buffer=chunk_size)

	print("Connected to Server")
	tkinter.messagebox.showwarning('提示', message='语音已开启!')
	def receive_server_data():
		while True:
			try:
				data = voice_socket.recv(1024)
				playing_stream.write(data)
			except:
				pass

	def send_data_to_server():
		while True:
			try:
				data = recording_stream.read(1024)
				voice_socket.sendall(data)
			except:
				pass

	# temp = {'depcode':6,'msg':'发来语音通话'}
	# temp = json.dumps(temp)
	# msgsize = struct.pack("i",len(temp))
	# s.send(msgsize)
	# s.send(temp.encode())

    # start threads
	receive_thread = threading.Thread(target=receive_server_data).start()
	send_thread = threading.Thread(target=send_data_to_server).start()



callVoiceButton = tkinter.Button(root1, text = "语音通话",command = callVoice,bg = 'LightBlue')
callVoiceButton.place(x=215,y=300,width=50,height=50)

#是否接收语音通话
# def isRecvVoice(thing):
	# userName,mes = thing.split('~') 
	# v = tkinter.messagebox.askquestion(root1,message=userName + ':' + mes)
	# print(v)
	# if v == 'yes':
	# 	temp = {'depcode':8,'msg':mes}
	# 	temp = json.dumps(temp)
	# 	msgsize = struct.pack("i",len(temp))
	# 	s.send(msgsize)
	# 	s.send(temp.encode())

def disconnectVoice():
	voice_socket.close()
	tkinter.messagebox.showwarning('提示', message='语音已关闭!')

disconnectVoiceButton = tkinter.Button(root1, text = "断开语音",command = disconnectVoice,bg = 'LightBlue')
disconnectVoiceButton.place(x=285,y=300,width=50,height=50)

#是否接受文件
def isRecvFile(file):
    userName,filename = file.split('~') 
    v = tkinter.messagebox.askquestion(root1,message=userName + ':' + filename)
    print(v)
    if v == 'yes':
        temp = {'depcode':4,'msg':filename}
        temp = json.dumps(temp)
        msgsize = struct.pack("i",len(temp))
        s.send(msgsize)
        s.send(temp.encode())
    
def receive():
	global uses
	while True:
		head = s.recv(4)
		msgsize = struct.unpack("i",head)[0]     
		data = s.recv(msgsize)
		data = data.decode()
		print(data)
		temp = json.loads(data)
		if temp['depcode'] == 2:
			uses = temp['msg']            
			listbox1.delete(0, tkinter.END)
			listbox1.insert(tkinter.END, "当前在线用户:"+str(uses[0]))
			listbox1.insert(tkinter.END, chat)
			del(uses[0])
			for x in range(len(uses)):
				listbox1.insert(tkinter.END, uses[x])
			users.append(chat)
		elif temp['depcode'] == 7:
			thing = temp['msg']
			isRecvVoice(thing)
		elif temp['depcode'] == 1:
			message = temp['msg']
			userName = temp['user']
			bt=message.split(':')
			message = bt[0]+'  '+bt[2]+':'+bt[3]+':'+bt[4]+'\n'
			message = '\n'+message
			listbox.insert(tkinter.END, message,'tag1')
			mss = '  '+ bt[1]
			print('?'+bt[0].lstrip(' ')+' '+user+'?')
			print(bt[0].lstrip(' ') is user)
			if bt[0].lstrip(' ') is user:
				listbox.insert(tkinter.END, mss,'tag2')
			else:
				listbox.insert(tkinter.END, mss)
			listbox.see(tkinter.END)
		elif temp['depcode']==3:
			filename,filesize = temp['msg'].split('~')
			filesize = int(filesize)
			f = open(filename, "wb")
			received_size = 0


			while received_size < filesize:
				size = 0  # 准确接收数据大小，解决粘包
				if filesize - received_size > 1024: # 多次接收
						size = 1024
				else:  # 最后一次接收完毕
					size = filesize - received_size
				data = s.recv(size)  # 多次接收内容
				data_len = len(data)
				received_size += data_len
				print("已接收：", int(received_size/filesize*100), "%")
				f.write(data)
			f.close()
		elif temp['depcode']==5:
			filename = temp['msg']
			isRecvFile(filename)
		elif temp['depcode']==4:
			print(temp)
			file,filename = filequeue.get()
			if filename == temp['msg']:
				readSendFile(file,s)
r = threading.Thread(target=receive)
r.start()  # 开始线程接收信息

root1.mainloop()
s.close()
