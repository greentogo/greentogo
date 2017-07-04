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

    constructor() {
        console.log('appStore constructor')
        simpleStore.get('authToken').then(token => {
            console.log('stored token', token || 'not found')
            this.authToken = token
        })
    }

    @action setAuthToken(token) {
        console.log('setting authToken', token);
        this.authToken = token;
        return simpleStore.save('authToken', token)
    }
}
