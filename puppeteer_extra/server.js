
async function getVisibleHandle(selector, page) {
        const elements = await page.$$(selector);
        let hasVisibleElement = false,
        visibleElement = '';

        if (!elements.length) {
                return [hasVisibleElement, visibleElement];
         }
        let i = 0;
        for (let element of elements) {
            const isVisibleHandle = await page.evaluateHandle((e) => {
            const style = window.getComputedStyle(e);
            return (style && style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0');}, element);
            var visible = await isVisibleHandle.jsonValue();
            const box = await element.boxModel();
            if (visible && box) {hasVisibleElement = true;visibleElement = elements[i];break;}
            i++;
         }
        return [hasVisibleElement, visibleElement];
}

async function pageData(page) {
    var link_xpath = '//div[@class="r"]/a[@href]'
    var title_xpath = '//h3[@class="LC20lb"]/span/text()'
    var desc_xpath = '//div[@class="s"]/div/span[@class="st"]'
   
    await page.waitForXPath(link_xpath);
    
    var links = await page.$x(link_xpath);
    var title_array = await page.$x(title_xpath);
    var desc_array = await page.$x(desc_xpath);
    
    var title_list = [];
    var description_list = [];
  
    const link_urls = await page.evaluate((...links) => {return links.map(e => e.href);}, ...links);
    for (var j =0; j < title_array.length; j++)
    {
            title_list.push(await page.evaluate(el => el.textContent,title_array[j]));
    }
    if (title_array.length==0){
        title_xpath = '//h3[@class="LC20lb"]/text()'
        title_array = await page.$x(title_xpath);
        for (var j =0; j < title_array.length; j++){
            title_list.push(await page.evaluate(el => el.textContent,title_array[j]));
        };
    }
    for (var i =0; i< desc_array.length;i++)
    {
        description_list.push(await page.evaluate(el => el.textContent,desc_array[i]));
    }

    return [link_urls,title_list,description_list]
}

async function rightData(page){
    var labels = new Array();
    var data = new Array();
    var Subs_titles_arr = new Array();
    var is_more_available;
    var label = await page.$x("//span[@class='w8qArf']/a");
    var value1 = await page.$x("//span[@class='w8qArf']//following-sibling::span");
    var i =0;
    for (var j =0; j < label.length; j++)
            {
               logo = await page.evaluate(el => el.textContent,label[j]);console.log(logo);
               labels.push(logo)
               if (logo=='Subsidiaries')
                is_more_available = true
               if (logo=='Hours' && label.length!=value1.length){
                   hours_xpath = await page.$x("//span[@class='TLou0b']/span");
                   val = await page.evaluate(el => el.textContent,hours_xpath[0]);
               }
               else{
                try{
                    val = await page.evaluate(el => el.textContent,value1[i]);
                    i++;}
                catch(e){
                    val='none'}
               }
               data.push(val)
            }
    var sidetitle = await page.$x("//div[@class='SPZz6b']/div[@data-attrid='title']/span");
    var sidetype1 = await page.$x("//div[@class='SPZz6b']/div[@data-attrid='subtitle']/span");
    var sidetype2 = await page.$x("//span[@class='YhemCb']");

    var side_description1 = await page.$x("//h2[@class='bNg8Rb']/following-sibling::span/text()")
    var side_description2 = await page.$x("//span[@class='ILfuVd UiGGAb']/span[@class='e24Kjd']/text()")

    var side_url = await page.$x("//span[@class='ellip']")
    
    if (is_more_available){
      var puppeteer = require('puppeteer');
      var more_link = "//span[contains(text(),'MORE')]/.."
      var more_link_Arr = await page.$x(more_link);
      var href_link = await page.evaluate((...more_link)=> {return more_link.map(e => e.href);},...more_link_Arr)

      const browser = await puppeteer.launch({headless: true,args: ['--no-sandbox', '--disable-setuid-sandbox','--lang=en-GB']});
      const sub_Page = await browser.newPage();
      await sub_Page.goto(href_link[0],{waitUntil: 'networkidle2'});
      var Subsidiaries_title_path = "//div[@class='EDblX DAVP1']/a[@aria-label]"; 
      var Subs_titles = await sub_Page.$x(Subsidiaries_title_path);
 
      if(Subs_titles.length == 0) {
        Subsidiaries_title_path = "//div[@class = 'title']"
        Subs_titles = await sub_Page.$x(Subsidiaries_title_path);

      }
        for (var j =0; j < Subs_titles.length; j++){
            Subs_titles_arr.push(await sub_Page.evaluate(el => el.textContent,Subs_titles[j]));
        };

    }
    
    let title_txt = await page.evaluate(h1 => h1.textContent, sidetitle[0]);
    if (title_txt=="See results about"){
        return 'none'
    } 
    let type,desc;
    try{
    desc = await page.evaluate(h1 => h1.textContent, side_description1[0]);}
    catch(e){
        try{
            desc = await page.evaluate(h1 => h1.textContent, side_description2[0]);}
        catch(e){
        desc = 'none'}
    }
    try{
        type = await page.evaluate(h1 => h1.textContent, sidetype1[0]);}
    catch(e){
        try{
            type = await page.evaluate(h1 => h1.textContent, sidetype2[0]);}
        catch(e){
            type = 'none'}
    }
    try{
        url = await page.evaluate(h1 => h1.textContent, side_url[0]);}
    catch(e)
    {
        url='none'}
    return [title_txt,type,desc,url,labels,data, Subs_titles_arr]
}


async function run_duplicate(keyword,yield_json,is_meanKeyword) {
        var puppeteer = require('puppeteer');
        //const browser = await puppeteer.launch({headless: true,args: ['--no-sandbox', '--disable-setuid-sandbox','--lang=en-GB','--proxy-server=socks5://127.0.0.1:9050']});
        const browser = await puppeteer.launch({headless: true,args: ['--no-sandbox', '--disable-setuid-sandbox','--lang=en-GB']});
        try{
               const page = await browser.newPage();
               await page.goto("https://www.google.co.in/search?q="+keyword,{waitUntil: 'networkidle2'});
               let data = await pageData(page);
               try{
                    aux_data = await rightData(page);
               }
               catch(e){
                   aux_data = 'none'
               }
               link_urls = data[0]
               title_text = data[1]
               short_desc = data[2]
               var fs = require('fs');
               data= new Array();
               for(var i = 0; i<link_urls.length;i++)
               {
                data.push({url:link_urls[i], title:title_text[i], short_description:short_desc[i]})
               };
               var right_side_data ={}
               if (aux_data!='none'){
                   right_side_data["title"]=aux_data[0]
                   right_side_data["type"]=aux_data[1]
                   right_side_data["description"]=aux_data[2]
                   right_side_data["website_homepage"]=aux_data[3]
                   try{const labels = aux_data[4]
                        console.log('Labels:',labels)
                        const values = aux_data[5]
                        for(var i =0;i<labels.length;i++){
                          if(labels[i] == 'Subsidiaries') 
                              right_side_data[labels[i]] = aux_data[6]
                            else
                              right_side_data[labels[i]]=values[i]
                        };
                   }
                   catch(e){
                       console.log("pattern different")
                   }
                }
               if(JSON.stringify(right_side_data) === '{}'){
                   right_side_data={}
               }
               data.push({'right_side_data':right_side_data});
               did_u_mean_keyword = await page.$x("//span[contains(text(),'Did you mean:')]/parent::p[@class='gqLncc card-section']/a[@class='gL9Hy']/b/i/text()");
               try{
                    did_u_mean_keyword = await page.evaluate(el => el.textContent,did_u_mean_keyword[0]);console.log(did_u_mean_keyword);
                    yield_json['original_search_data']=data
                    is_meanKeyword = '1'
                    res=await run_duplicate(did_u_mean_keyword,yield_json,is_meanKeyword)
               }
               catch(e){
                   if (is_meanKeyword=='1'){
                    yield_json['did_you_mean_search_data']=data
                   }
                   else{
                       yield_json['original_search_data']=data
                   }
                }
               await browser.close();
               return JSON.stringify(yield_json, null, 4);
            }
            catch(e){
                await browser.close();
                return ("keyword not matched",204);
            } 
}


const express = require('express');

var bodyParser=require("body-parser");
const port = 8080 ;
const app = express();

app.use(bodyParser.json()); // support json encoded bodies
app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies

app.all('/v1/api/search',  async function(req, res){
    var keyword = req.body.keyword || req.query.keyword;
    if (!keyword || keyword ===""){
        res.status(400).send("no input provided")}
    else{
    console.log("Entered keyword is :",keyword);
    yield_json = {}
    const response=await run_duplicate(keyword,yield_json,'0');
    res.send(response);}
});

app.listen(port, (err) => {
  if (err) {
    return console.log('something bad happened', err)
  }
  console.log(`server is listening on ${port}`)
})



