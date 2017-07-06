import React from 'react';
import {
    StyleSheet,
    Text,
    View,
    Picker
} from 'react-native';

import { Icon, Button } from 'native-base';

import { inject, observer } from 'mobx-react';

const apiEndpoint = 'https://g2g.dreisbach.us/api/v1';

@inject('appStore')
@observer
class SubmissionScreen extends React.Component {
   constructor(props) {
        super(props)
        this.state = {
            count: 1
        }
    }

    componentDidMount() {
        // Get subsciptions for the account
        let authToken = this.props.appStore.authToken;
        let myHeaders = new Headers({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Token ' + authToken
        });

        let myInit = {
            method: 'GET',
            headers: myHeaders,
            credentials: 'include'
        };

        let request = new Request(`${apiEndpoint}/me`, myInit);

        fetch(request)
        .then((response) => console.log(response))
        .then((response) => response.json())
        .then((json) => {
            console.log(json);
        })
        .catch((error) => {
            console.log(error)
        })
    }

    static route = {
        navigationBar: {
            title: `Check In/Out`
        }
    }

    add = () => this.setState({count: this.state.count + 1})
    subtract = () => {
        if (this.state.count > 1) {
            this.setState({count: this.state.count - 1})
        }
    }

    submit = () => {
       fetch(`${apiEndpoint}/tag`, {
           method: 'POST',
           headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': `Token ${this.props.appStore.authToken}`
           },
           body: JSON.stringify({
               subscription: this.state.subscriptionId,
               location: this.props.appStore.locationCode
               // @TODO should also send number of boxes
           })
       })
       .then((response) => console.log(response))
       .then((response) => response.json())
       .then((json) => {
           this.props.navigator.push('home');
       })
       .catch((error) => {
           console.log(error);
       });
    }

    render() {
        const styles = StyleSheet.create({
            centeredRow: {
                flexDirection: 'row',
                justifyContent: 'center'
            },
            icon: {
                fontSize: 20,
                fontWeight: '800',
                color: 'white'
            },
            headerText: {
                fontSize: 18,
                fontWeight: '800',
                textAlign: 'center'
            }
        });
        // api/v1/me
        return (
            <View>
                <View style={{marginBottom: 10}}><Text style={styles.headerText}>How many boxes to {this.props.appStore.action}?</Text></View>
                <View style={styles.centeredRow}>
                    <Button
                        success
                        onPress={this.add} >
                        <Text style={styles.icon}>+</Text>
                    </ Button>
                    <Text style={{marginLeft: 10, marginRight: 10, fontSize: 20}}>{this.state.count}</Text>
                    <Button
                        success
                        onPress={this.subtract} >
                        <Text style={styles.icon}>-</Text>
                    </ Button>
                </View>
                <View>
                    <Text style={styles.headerText}>Which subscription?</Text>
                    <Picker
                        mode="dropdown"
                        selectedValue={this.state.subscriptionId}
                        onValueChange={(itemValue, itemIndex) => this.setState({subscriptionId: itemValue})}
                    >
                        <Picker.Item label="2 Box Subscription (1/2)" value="1" />
                        <Picker.Item label="4 Box Subscription (3/4)" value="2"/>
                    </ Picker>
                    <View style={styles.centeredRow}>
                        <Button
                            success
                            onPress={this.submit}
                        >
                            <Text style={{color: '#FFFFFF'}}>Submit</Text>
                        </Button>
                    </View>
                </View>
            </View>
        )
    }
}

export default SubmissionScreen;
