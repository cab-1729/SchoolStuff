//IMPORTANT : Project prone to frequent changes, keep code and dev environ for readily changing
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Threading;
using System.Text.RegularExpressions;
using Newtonsoft.Json;
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
namespace School_material{
class Program{
	static ChromeDriver browser;
	static Dictionary<string,object> disable_security;
	static Dictionary<string,List<byte>> memory;
	static Regex subjects;
	static string download_dir;
	static void Main(string[] args){
		Console.ForegroundColor=ConsoleColor.Green;
		Console.WriteLine("Configuring settings ...");
		disable_security=new Dictionary<string,object>{{"behavior","allow"}};
		Dictionary<string,string> settings=JsonConvert.DeserializeObject<Dictionary<string,string>>(File.ReadAllText("settings.json"));//read settings
		memory=JsonConvert.DeserializeObject<Dictionary<string,List<byte>>>(File.ReadAllText("memory.json"));//read already downloaded
		subjects=new Regex(settings["content regex"],RegexOptions.Compiled);
		download_dir=settings["download in"];
		Console.WriteLine("Creating web crawler ...");
		ChromeDriverService service=ChromeDriverService.CreateDefaultService(settings["chromedriver directory"]);//create service with chromedriver
		ChromeOptions chrome_options=new ChromeOptions();chrome_options.AddArguments("no-sandbox"/*dunno,crashes without*/,"headless"/*invisible,faster*/);
		service.SuppressInitialDiagnosticInformation=true;service.HideCommandPromptWindow=true;//stop unnecessary logging
		browser=new ChromeDriver(service,chrome_options);//open chrome
		browser.Url=settings["portal"];
		RunJS("document.getElementById(\'txtUserName\').value=\'"+settings["id"]+"\';document.getElementById(\'txtPassword\').value=\'"+settings["password"]+"\';document.getElementById(\'btnLogin\').click();");//fill details and enter portal
		Console.WriteLine("Opened School Portal");
		RunJS("__doPostBack(\'grdUnreadAcademicPost\',\'Select$0\');");//click "Click" beside "Learning material"
		RunJS("document.querySelector(\'#learningMaterials > div > input\').click();");//click "Learning Materials"
		//in page with material
		Page(1,"","");
		if(Convert.ToBoolean(RunJS("return document.querySelector(\'#grdPost > tbody > tr:nth-child(18) > td > table > tbody > tr\')!=null"))){//if page numbers present at bottom
			byte pages=Convert.ToByte(RunJS("return document.querySelector(\'#grdPost > tbody > tr:nth-child(18) > td > table > tbody > tr\').childElementCount;"));
			for(byte page=2;page<=pages;page++)
				Page(page,
					"document.querySelector(\'#grdPost > tbody > tr:nth-child(18) > td > table > tbody > tr > td:nth-child("+page+") > a\').click();",
					"if(document.querySelector('#grdPost > tbody > tr:nth-child('+document.querySelector('#grdPost > tbody').childElementCount+') > td > table > tbody > tr > td:nth-child("+page+")').innerHTML!=\'<span>"+page+"</span>\')throw Error;"
				);//go to next page and wait
		}
		else{Console.WriteLine("\tNo More Pages");}
		browser.Quit();//close internet
		Console.WriteLine("Got all new material\nKilled Crawler\nMemorizing ...");
		File.WriteAllText("memory.json",JsonConvert.SerializeObject(memory,Formatting.Indented));//memorize
		Console.WriteLine("\nDone\nPress any key to close");
		Console.ReadKey();
	}
	static void Page(byte number,string go_to_page,string wait_for_page){//download material from page
		Console.WriteLine("\tPage"+number);
		RunJS(go_to_page);
		RunJS(wait_for_page);//wait for page
		ReadOnlyCollection<object> table_items=(ReadOnlyCollection<object>)RunJS("let ret=[],table=document.querySelector(\'#grdPost > tbody\').children;let l=table.length-2;for(let i=1;i<l;i++)ret.push(table[i].children[2].innerText);return ret");//get all items on page
		byte i=2,j,content_number;int hyphen;string subject;List<byte> haves;
		foreach(string table_value in table_items){
			if(subjects.IsMatch(table_value)){//my subject
				hyphen=table_value.IndexOf('-');
				subject=table_value.Substring(hyphen+2,table_value.LastIndexOf('-')-hyphen-3);
				content_number=Convert.ToByte(table_value.Substring(8,hyphen-9));
				haves=memory[subject];
				if(!haves.Contains(content_number)){//need material
					//download
					RunJS("document.querySelector(\'#grdPost > tbody > tr:nth-child("+i+") > td:nth-child(5) > input[type=button]\').click()");//click "Click" and go to download page
					j=0;
					ReadOnlyCollection<object> files=(ReadOnlyCollection<object>)RunJS("let ret=[],table=document.querySelector(\'#grdDoc > tbody\').children;let l=table.length-1;for(let i=1;i<l;i++)ret.push(table[i].children[1].innerText);return ret;");//get filename
					foreach(string filename in files){
						disable_security["downloadPath"]=String.Format(download_dir,subject);//set download path
						browser.ExecuteChromeCommand("Page.setDownloadBehavior",disable_security);//disables Chrome security feature,copied from Stack Overflow
						RunJS("document.querySelector(\'#grdDoc_btnDownload_"+j+"\').click()");//click "Click"
						Console.WriteLine("\t\t"+filename);
						j++;
					}
					haves.Add(content_number);//remember
					browser.Navigate().Back();//move back
					RunJS(go_to_page);RunJS(wait_for_page);//counter to website bug
				}
			}
			i++;
		}
	}
	static Object RunJS(string js_code){//wrapper
		for(;;){//keep trying
			try{
				return browser.ExecuteScript(js_code);
			}catch(WebDriverException){
				Thread.Sleep(500);//wait
			}
		}
	}
}
}
