from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.common.exceptions import JavascriptException
from pickle import load,dump
chromeOptions=Options()
chromeOptions.add_argument('--headless');chromeOptions.add_experimental_option('excludeSwitches',['enable-logging'])#stop logging
with open('data shelve.pkl','rb') as ds:memory=load(ds)#get memory
browser=Chrome(executable_path=memory['driver'],options=chromeOptions)#create crawler
print('Created crawler ...\nLoaded memory ...')
browser.get(memory['portal url'])#open portal
_=memory['id']
def runJs(jsLine):
	while True:
		try:return browser.execute_script(jsLine)
		except JavascriptException:sleep(0.5)
#go to page for extraction
for js in (
	'document.querySelector("#txtUserName").value='+_+';',#fill id
	'document.querySelector("#txtPassword").value='+_+memory['dob']+';',#fill password
	'document.getElementById("btnLogin").click();',#click login button
	'__doPostBack("grdUnreadAcademicPost","Select$0");',#go to "Learning material"
	'document.getElementById("learningMaterials").click();',#click "Learning Materials"
):runJs(js)
print('\tOpened portal')
#extract
material=memory['material'];subjects=material.keys();dumpFolder=memory['dump']
def materialFromList():
	for i,(number,subject) in enumerate(runJs('''
	var info=[],s,_,i=2;
	while(true){
		s=document.querySelector('#grdPost > tbody > tr:nth-child('+i+++') > td:nth-child(3)').textContent;
		if(s=='\\xa0')break;
		if(s.startsWith('Content ') && s.endsWith(' - Class XI\\n')){
			_=s.indexOf('-');
			info.push([Number(s.substring(8,_-1)),s.substring(_+2,s.length-12)]);
		}else
			info.push([null,null]);
	}
	return info;
	''')):
		if subject in subjects and number not in material[subject]:#material needed
			browser.command_executor._commands["send_command"]=("POST",'/session/$sessionId/chromium/send_command')#bypass security feature
			params={'cmd':'Page.setDownloadBehavior','params':{'behavior':'allow', 'downloadPath':dumpFolder+'\\'+subject}}
			browser.execute("send_command",params)#enable download
			for js in (
					'__doPostBack("grdPost","Select$' + str(i) + '")',#go to download page
					'document.getElementById("grdDoc_btnDownload_0").click()', #click button to download
					'window.history.back();',#go back to list
			): runJs(js)
			print('\t\t\t'+subject,number)
			material[subject].add(number)#remember got
print('\t\tPage1')
materialFromList()
runJs('__doPostBack("grdPost","Page$2");')
print('\t\tPage2')
materialFromList()
runJs('__doPostBack("grdPost","Page$3");')
print('\t\tPage3')
materialFromList()
runJs('__doPostBack("grdPost","Page$4");')
print('\t\tPage4')
materialFromList()
browser.quit()#kill crawler
print('Killed crawler')
with open('data shelve.pkl','wb') as ds:dump(memory,ds)#memorize
print('Stored memory')
