import { observable, action } from 'mobx';
import { enableLogging } from 'mobx-logger';
import simpleStore from 'react-native-simple-store';

enableLogging({
    action: true,
    // reaction: true,
    // transaction: true,
    // compute: true
});

export class AppStore {
    @observable authToken = '';
    @observable loading = false;

    constructor() {
        console.log('appStore constructor')
        simpleStore.get('authToken').then(token => {
            console.log('stored token', token || 'not found')
            this.authToken = token
        })
    }

    @action attemptLogin(username, password) {
        this.loading = true;
        fetch('https://g2g.dreisbach.us/auth/login/', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password,
            })
        })
        .then((response) => response.json())
        .then((json) => {
            if (json.auth_token) {
                console.log('setting authToken', json.auth_token);
                this.authToken = json.auth_token;
                simpleStore.save('authToken', json.auth_token)
            }
        })
        .catch((error) => {
            console.log(error);
        })
        .then(() => {
            this.loading = false;
        });
    }
}
