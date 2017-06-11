import { observable, action } from 'mobx';
import { enableLogging } from 'mobx-logger';

enableLogging({
    action: true,
    // reaction: true,
    // transaction: true,
    // compute: true
});

export class AppStore {
    @observable authToken = "";

    @action attemptLogin(username, password) {
        fetch('https://greentogo.ngrok.io/auth/login/', {
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
                    console.log("setting authToken", json.auth_token);
                    this.authToken = json.auth_token;
                }
            })
            .catch((error) => {
                console.log(error)
            })
    }
}
