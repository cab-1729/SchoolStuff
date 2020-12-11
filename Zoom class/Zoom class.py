from datetime import timedelta,datetime
from tkinter import *
from os import popen
import shelve
from time import sleep
from xerox import copy
from functools import partial
from subprocess import Popen
from sys import exit
time=datetime.now()
day=time.weekday()
if day==6 or day==5:exit(0)#sunday or saturday
a=datetime(day=time.day,month=time.month,year=time.year,hour=8)
week=('Monday','Tuesday','Wednesday','Thursday','Friday')
with shelve.open('memory') as db:
	wait=db['alert']
	start_meeting=partial(Popen,[db['exe path']])
	periods=db['time table'][day]
	eq=eval(db['time equation'])
	cmd_class=db['command after class']
	cmd_day=db['command after day']
	classes,timings,periods=[],[],[]
	for i,t in enumerate(db['time table'][day]):
		if t!=None:
			timings.append(a+timedelta(minutes=eq(i)))#class begin timings
			classes.append(db['classrooms'][t])
			periods.append(t)
#view whole daily schedule
tt=Tk()
tt.lift()
tt.resizable(False,False)
tt.iconbitmap('schedule.ico')
tt.title('Online Classes Today')
Label(tt,text=week[day],font=('',12,'bold')).grid(columnspan=2,row=0)
for i,(t,e) in enumerate(zip(timings,periods)):
	if e!=None:
		r=i+1
		n=t+timedelta(minutes=40)
		m1=str(t.minute);m2=str(n.minute)
		if len(m1)==1:m1='0'+m1
		if len(m2)==1:m2='0'+m2
		Label(tt,text=e+'     ').grid(column=0,row=r)
		Label(tt,text=str(t.hour)+':'+m1+' - '+str(n.hour)+':'+m2).grid(column=1,row=r)
tt.mainloop()
for t,class_,subject in zip(timings,classes,periods):
	time=datetime.now()
	if (t-time).seconds>0 and periods[i]!=None:
		s=t-time-wait
		if s.days>=0:sleep(s.seconds)#wait for time
		#start gui and app
		m=str(t.minute)
		if len(m)==1:m='0'+m
		reminder=Tk()
		reminder.lift()
		reminder.resizable(False,False)
		reminder.iconbitmap('period.ico')
		photo=PhotoImage(file='bis.png')
		reminder.title('Zoom class about to begin')
		Label(reminder,text=class_['teacher']+'\'s '+subject+' class',font=('',12,'bold')).grid(columnspan=2,row=0)
		Label(reminder,text='Time - '+str(t.hour)+':'+m).grid(columnspan=2,row=1)
		id=class_['id'];passcode=class_['passcode']
		Label(reminder,text='Meeting ID - '+id).grid(column=0,row=2)
		Button(reminder,image=photo,command=partial(copy,id)).grid(column=1,row=2)
		Label(reminder,text='Passcode - '+passcode).grid(column=0,row=3)
		Button(reminder,image=photo,command=partial(copy,passcode)).grid(column=1,row=3)
		Button(reminder,text='Start',command=start_meeting).grid(columnspan=2,row=4,sticky=NSEW)
		reminder.mainloop()
		popen(cmd_class)
popen(cmd_day)
