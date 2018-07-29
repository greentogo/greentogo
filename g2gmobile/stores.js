import { observable, action } from 'mobx';
import { enableLogging } from 'mobx-logger';
import simpleStore from 'react-native-simple-store';
import { createNavigationEnabledStore, NavigationReducer } from '@expo/ex-navigation';
import axios from './apiClient';

enableLogging({
    action: true,
    // reaction: true,
    // transaction: true,
    // compute: true
});

export class AppStore {
    @observable authToken = ''
    @observable user = {}
    // siteUrl = 'https://app.durhamgreentogo.com/api/v1'
    siteUrl = 'http://7f1107e4.ngrok.io/api/v1'

    constructor() {
        console.log('appStore constructor')
        simpleStore.get('authToken').then(token => {
            console.log('stored token', token || 'not found')
            this.authToken = token
        })
        simpleStore.get('user').then(user => {
            console.log('successfully got user from store', user)
            this.user = user
        })
    }

    makeUrl(path) {
        return this.siteUrl + path;
    }

    reduceBoxes(subscriptions, type) {
        return subscriptions.reduce((sum, subscription) => sum + subscription[type], 0)
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

    @action getUserData() {
        // Get the user data after successful login
        axios.get('/me/', {
            headers: {
                'Authorization': `Token ${this.authToken}`
            }
        }).then((response) => {
            console.log("User data success")
            this.setUserData(response.data.data);
        }).catch((err) => {
            console.log(err);
            console.log(this.clearAuthToken());
        })
    }
    
    @action setUserData(data) {
        this.user = data
        if (data.subscriptions) {
            this.user.maxBoxes = this.reduceBoxes(data.subscriptions, "max_boxes")
            this.user.availableBoxes = this.reduceBoxes(data.subscriptions, "available_boxes")
        }
        simpleStore.save('user', data)
        console.log("User data: ", this.user)
    }
}
