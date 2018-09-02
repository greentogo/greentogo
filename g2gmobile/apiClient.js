import axios from 'axios';

const url = 'https://app.durhamgreentogo.com/api/v1'; // Production
// const url = 'https://g2g.dreisbach.us/api/v1'; // Staging
// const url = 'http://7f1107e4.ngrok.io/api/v1'; // Testing

const instance = axios.create({
  baseURL: url,
  timeout: 5000,
  headers: {
    Accept: 'application/json'
  }
});

instance.defaults.headers.post['Content-Type'] = 'application/json';

export default instance;
