from datetime import timedelta,time,datetime,date
from tkinter import *
from os import popen
from shelve import open as shelve
from time import sleep
from pyperclip import copy
from json import loads
from functools import partial
from subprocess import Popen
from sys import exit
today=date.today()
day=today.weekday();
if day==6 or day==5:exit(0)#sunday or saturday
memory=shelve('holidays')
try:#check holiday
    memory[today.strftime('%d-%m-%Y')]
    memory.close()
    exit(0)
except KeyError:memory.close()
week=('Monday','Tuesday','Wednesday','Thursday','Friday')
with open('settings.json') as f:
    memory=loads(f.read())
    wait=timedelta(minutes=memory['alert'])
    start_meeting=partial(Popen,[memory['exe_path']])
    cmd_class=memory['command_after_class']
    cmd_day=memory['command_after_day']
    over=memory['over by']
    over=datetime.combine(today,time(hour=int(over[:2]),minute=int(over[3:])))
dow=week[day]
if over<datetime.now():exit(0)#school over
#view whole schedule
tt=Tk()
tt.lift()
tt.resizable(False,False)
tt.iconbitmap('schedule.ico')
tt.title('Online Classes Today')
Label(tt,text=dow,font=('',12,'bold')).grid(columnspan=2,row=0)
period=timedelta(minutes=40);form='%H:%M'
with shelve('classes') as memory:
    schedule=memory[dow]
    rooms,subjects,times=[],[],[]
    for row,class_ in enumerate(schedule,1):
        subject=class_['subject']
        time=datetime.combine(today,class_['time'])
        Label(tt,text=subject+'     ').grid(column=0,row=row)
        Label(tt,text='{} - {}'.format(time.strftime(form),(time+period).strftime(form))).grid(column=1,row=row)
        rooms.append(memory[subject])
        subjects.append(subject)
        times.append(time)
tt.mainloop()
for subject,room,t in zip(subjects,rooms,times):
    time=datetime.now()
    s=t-time-wait
    if s.days>=0:sleep(s.total_seconds())#wait for time
    #start gui
    reminder=Tk()
    reminder.lift()
    reminder.resizable(False,False);
    reminder.iconbitmap('period.ico')
    photo=PhotoImage(file='bis.png')
    reminder.title('Class about to begin')
    Label(reminder,text=room['teacher']+'\'s '+subject+' class',font=('',12,'bold')).grid(columnspan=2,row=0)
    Label(reminder,text='Time - '+t.strftime('%H:%M')).grid(columnspan=2,row=1)
    id=room['id'];passcode=room['passcode']
    Label(reminder,text='Meeting ID - '+id).grid(column=0,row=2)
    Button(reminder,image=photo,command=partial(copy,id)).grid(column=1,row=2)
    Label(reminder,text='Passcode - '+passcode).grid(column=0,row=3)
    Button(reminder,image=photo,command=partial(copy,passcode)).grid(column=1,row=3)
    Button(reminder,text='Start',command=start_meeting).grid(columnspan=2,row=4,sticky=NSEW)
    reminder.mainloop()
    popen(cmd_class)
popen(cmd_day)
