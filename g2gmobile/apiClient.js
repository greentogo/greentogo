import axios from 'axios';

const instance = axios.create({
  baseURL: 'https://app.durhamgreentogo.com/api/v1',
  timeout: 5000,
  headers: {
    Accept: 'application/json'
  }
});

instance.defaults.headers.post['Content-Type'] = 'application/json';

export default instance;
