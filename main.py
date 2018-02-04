import deployserver


deployserver.init({
    'server_address': 'https://9feaf78b.ngrok.io',
    'port': 7755,
    'deploy': 'ls',
    'secret_token': 'pwd'
})