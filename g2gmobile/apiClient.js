import axios from 'axios';

// baseURL: 'https://app.durhamgreentogo.com/api/v1',
const instance = axios.create({
  baseURL: 'http://56009b6f.ngrok.io/api/v1',
  timeout: 5000,
  headers: {
    Accept: 'application/json'
  }
});

instance.defaults.headers.post['Content-Type'] = 'application/json';

export default instance;
