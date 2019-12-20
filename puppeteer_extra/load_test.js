const loadtest = require('loadtest');
var i = 0
var list = ['headrun','zomato','fiza','boom','christmas','anilkumble','mukeshbhatt','ambani','sbi','yesbank']

const options = {
        url: 'http://gson.head.run',
        maxRequests: list.length,
		requestGenerator: (params, options, client, callback) => {
        var message = '{"hi": "ho"}';
		let path='/v1/api/search?keyword=';
        options.path = path.concat(list[i]);
        i = i+1;
        var request = client(options, callback);
		request.write(message);
		return request;
	}
};

loadtest.loadTest(options, (error, results) => {
	if (error) {
		return console.error('Got an error: %s', error);
	}
	console.log(results);
	console.log('Tests run successfully');
});



