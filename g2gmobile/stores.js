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
    @observable authToken = ''
    siteUrl = "https://g2g.dreisbach.us"

    constructor() {
        console.log('appStore constructor')
        simpleStore.get('authToken').then(token => {
            console.log('stored token', token || 'not found')
            this.authToken = token
        })
    }

    makeUrl(path) {
        return this.siteUrl + path;
    }

    @action setAuthToken(token) {
        console.log('setting authToken', token)
        this.authToken = token
        simpleStore.save('authToken', token)
    }

    @action clearAuthToken() {
        console.log('clearing authToken')
        this.authToken = null
        simpleStore.save('authToken', null)
    }
}
