
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
        title_xpath = '//h3[@class="LC20lb DKV0Md"]/text()'
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

async function rightData(page, keyword){
    const fs = require('fs');
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
    var sidetitle1 = await page.$x("//div[@class='SPZz6b']/div[@data-attrid='title']/span");
    var sidetitle2 = await page.$x("//div[@class='DRolee']");
    var sidetype1 = await page.$x("//div[@class='SPZz6b']/div[@data-attrid='subtitle']/span");
    var sidetype2 = await page.$x("//span[@class='YhemCb']");

    var side_description1 = await page.$x("//h2[@class='bNg8Rb']/following-sibling::span/text()")
    var side_description2 = await page.$x("//span[@class='ILfuVd UiGGAb']/span[@class='e24Kjd']/text()")
    var side_description3 = await page.$x("//span[@class='ILfuVd rjOVwe']")

    var side_url = await page.$x("//span[@class='ellip']")
    
    if (is_more_available){
      var puppeteer = require('puppeteer-extra');
      const StealthPlugin = require('puppeteer-extra-plugin-stealth');
      puppeteer.use(StealthPlugin());
      var more_link = "//span[contains(text(),'MORE')]/.."
      var more_link_Arr = await page.$x(more_link);
      var href_link = await page.evaluate((...more_link)=> {return more_link.map(e => e.href);},...more_link_Arr)
      const browser = await puppeteer.launch({ignoreHTTPSErrors: true, headless: true,args: ['--no-sandbox', '--disable-setuid-sandbox','--lang=en-GB','--proxy-server=http://zproxy.lum-superproxy.io:22225']});
      const sub_Page = await browser.newPage();
      await sub_Page.authenticate({
                        username: 'lum-customer-headrunmain-zone-static-country-in',
                        password: 'v4iey84gn7b7'
               });
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
    await browser.close();
    }
    try{
        title_txt = await page.evaluate(h1 => h1.textContent, sidetitle1[0]);
    }
    catch(e){
        title_txt = await page.evaluate(h1 => h1.textContent, sidetitle2[0]);
    }
    if (title_txt=="See results about"){
        return 'none'
    }
 
    let type='',desc='';
    try{
    desc = await page.evaluate(h1 => h1.textContent, side_description1[0]);}
    catch(e){
        try{
            desc = await page.evaluate(h1 => h1.textContent, side_description2[0]);}
    catch(e){
        for(var i =0; i < side_description3.length; i++){
            txt = await page.evaluate(h1 => h1.textContent,side_description3[i]);
            desc = desc+txt
        }
    }
    }
    try{
        type = await page.evaluate(h1 => h1.textContent, sidetype1[0]);}
    catch(e){
        try{
        for(var i =0; i < sidetype2.length; i++){
                txt = await page.evaluate(h1 => h1.textContent, sidetype2[i]);
        type=type+txt
        }
    }
        catch(e){
            type = 'none'}
    } 
    try{
        url = await page.evaluate(h1 => h1.textContent, side_url[0]);}
    catch(e)
    {
        url='none'}

    var logo_xpath = await page.$x("//g-img[@class='BA0A6c']/img[@class='rISBZc M4dUYb']");
    try{
        logo_url = await page.evaluate((...logo_xpath) => {return logo_xpath.map(e => e.src);}, ...logo_xpath);
        var viewSource = await page.goto(logo_url[0],{waitUntil: 'networkidle2'});
        fs.writeFile("./images/"+keyword, await viewSource.buffer(), function(err) {
            if(err) {
                    return console.log(err);
            }
        console.log("The file was saved!");
        logo='yes';
        });}
    catch(e){
        logo='none'}
    return [title_txt,type,desc,url,labels,data, Subs_titles_arr, logo]
}


async function run_duplicate(keyword,yield_json,is_meanKeyword) {
        var puppeteer = require('puppeteer-extra');
        const StealthPlugin = require('puppeteer-extra-plugin-stealth');
        puppeteer.use(StealthPlugin());
        const browser = await puppeteer.launch({ignoreHTTPSErrors: true, headless: true,args: ['--no-sandbox', '--disable-setuid-sandbox','--lang=en-GB','--proxy-server=http://zproxy.lum-superproxy.io:22225']});
        try{
               const page = await browser.newPage();
               await page.authenticate({
                        username: 'lum-customer-headrunmain-zone-static-country-in',
                        password: 'v4iey84gn7b7'
               });
               await page.goto("https://www.google.co.in/search?q="+keyword,{waitUntil: 'networkidle2'});
               let data = await pageData(page);
               try{
                    aux_data = await rightData(page, keyword);;
               }
               catch(e){
                   aux_data = 'none'
               }
               link_urls = data[0]
               title_text = data[1]
               short_desc = data[2]
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
                        const values = aux_data[5]
                        for(var i =0;i<labels.length;i++){
                          if(labels[i] == 'Subsidiaries') 
                              right_side_data[labels[i]] = aux_data[6]
                            else
                              right_side_data[labels[i]]=values[i]
                        };
                        if(aux_data[7]!='none'){
                            right_side_data['logo_url']="http://gson.head.run/image/"+keyword}
                        else{
                            right_side_data['logo_url']=''}

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
const mysql = require('mysql');
var datetime = require('node-datetime');
var bodyParser=require("body-parser");
const port = 8080 ;
const app = express();
var path = require('path');
app.use(bodyParser.json()); // support json encoded bodies
app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies
//app.use("/image", express.static("./images"));
app.use(express.static(path.join(__dirname, 'images')));

var connection = mysql.createConnection ({
    host: 'localhost',
    user: 'root',
    password: '',
    database: 'yesbank'
});

connection.connect((err) => {
    if (err) {
        throw err;
    }
    console.log('Connected to database');
});




app.all('/v1/api/search',  async function(req, res){
  let right_side_data_json = {};
  let right_side_data = {};
    var keyword = req.body.keyword || req.query.keyword;
    if (!keyword || keyword ===""){
        res.status(400).send("no input provided")}
    else{
    var dt = datetime.create();
    console.log("Entered keyword is :"+keyword+' '+dt.format('d/m/Y H:M:S'));
    yield_json = {}
    const response=await run_duplicate(keyword,yield_json,'0');
    res.send(response);
    let fin_result_json = JSON.parse(response)['original_search_data']
    if (fin_result_json[fin_result_json.length - 1]['right_side_data'])
      right_side_data_json =  fin_result_json[fin_result_json.length - 1]['right_side_data']        
      right_side_data = new Object({
        title : right_side_data_json['title']? right_side_data_json['title'] : '',
        type : right_side_data_json['type']? right_side_data_json['type'] : '', 
        description: right_side_data_json['description']? right_side_data_json['description'] : '',
        homepage: right_side_data_json['website_homepage']? right_side_data_json['website_homepage'] : '',
        subsidiaries: right_side_data_json['Subsidiaries']? right_side_data_json['Subsidiaries'].toString() : '', 
        status_code: res.statusCode ? res.statusCode : '', 
        headquarters : right_side_data_json['Headquarters']? right_side_data_json['Headquarters'] : '',
        founded : right_side_data_json['Founded']? right_side_data_json['Founded'] : '', 
        founder: right_side_data_json['Founder']? right_side_data_json['Founder'] : '', 
        logo_url: right_side_data_json['logo_url']? right_side_data_json['logo_url'] : '', 
        customer_service: right_side_data_json['Customer service']? right_side_data_json['Customer service'] : '', 
        parent_organization: right_side_data_json['Parent organization']? right_side_data_json['Parent organization'] : '',
        number_of_employees: right_side_data_json['Number of employees']? right_side_data_json['Number of employees'] : '',
        ceo:right_side_data_json['CEO']? right_side_data_json['CEO'] : '',
        phone:right_side_data_json['Phone']?right_side_data_json['Phone']: '',
        customer_care:right_side_data_json['Customer service']?right_side_data_json['Customer service']: '',
        status_msg: res.statusMessage ? res.statusMessage : ''
      })
      
    var sql = `INSERT INTO right_side_data (title, type, description, homepage, subsidiaries, status_code, headquarters, founded, founder, logo_url, customer_service, parent_organization, number_of_employees, ceo, phone, customer_care, address, status_msg) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`;
    connection.query(sql, [right_side_data["title"], right_side_data["type"], right_side_data["description"], right_side_data['website_homepage'], right_side_data['subsidiaries'], right_side_data['status_code'], right_side_data['headquarters'], right_side_data['founded'], right_side_data['founder'], right_side_data['logo_url'], right_side_data['customer_service'], right_side_data['parent_organization'], right_side_data_json['Number of employees'], right_side_data_json['CEO'], right_side_data_json['Phone'], right_side_data_json['Customer service'], right_side_data_json['Address'], right_side_data['status_msg']], function (err, data) {
        if (err) {
            throw err;
        } else {
            console.log('successfully inserted into db')
        }
  });
  }
});

app.get('/image/:name', function(req,res){
	app.set('views', __dirname);
	app.engine('html', require('ejs').renderFile);
	app.set('view engine', 'ejs');
	console.log(req.url.split('/')[2])
	var img_name = req.url.split('/')[2]
	res.render('image.html', {name:img_name}); 
});

app.listen(port, (err) => {
  if (err) {
    console.log('something bad happened', err);
    return console.log('something bad happened', err)
  }
  console.log(`server is listening on ${port}`)
})


