import axios from 'axios';

// const url = 'https://app.durhamgreentogo.com/api/v1';
const url = 'http://d0113866.ngrok.io/api/v1';

const instance = axios.create({
  baseURL: url,
  timeout: 5000,
  headers: {
    Accept: 'application/json'
  }
});

instance.defaults.headers.post['Content-Type'] = 'application/json';

export default instance;
