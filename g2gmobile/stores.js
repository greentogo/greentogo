import { observable, action } from 'mobx';
import { enableLogging } from 'mobx-logger';
import simpleStore from 'react-native-simple-store';
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

    constructor() {
        console.log('appStore constructor')
        simpleStore.get('authToken').then(token => {
            console.log('stored token', token || 'not found')
            this.authToken = token
        })
        simpleStore.get('user').then(user => {
            console.log('user store', user || 'not found')
            this.user = user
        })
        simpleStore.get('resturants').then(resturants => {
            this.resturants = resturants
        })
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
        simpleStore.save('user', null)
    }

    @action getUserData() {
        // Get the user data after successful login
        axios.get('/me/', {
            headers: {
                'Authorization': `Token ${this.authToken}`
            }
        }).then((response) => {
            this.setUserData(response.data.data);
        }).catch((error) => {
            console.log(error);
            console.log(this.clearAuthToken());
        })
    }

    @action getResturantData() {
        // Get the restaurant data on load
        axios.get('/restaurants/')
        .then((json) => {
            simpleStore.save('resturants', json.data.data)
        })
        .catch((e) => console.log(e))
    }
    
    @action setUserData(data) {
        this.user = data;
        if (data.subscriptions) {
            this.user.maxBoxes = this.reduceBoxes(data.subscriptions, "max_boxes");
            this.user.availableBoxes = this.reduceBoxes(data.subscriptions, "available_boxes");
        }
        simpleStore.save('user', data);
    }
}
