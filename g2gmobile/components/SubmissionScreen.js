import React from 'react';
import {
    StyleSheet,
    Text,
    View,
    Picker
} from 'react-native';

import { Icon, Button } from 'native-base';

import { inject, observer } from 'mobx-react';

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
        console.log(authToken);
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

        let request = new Request('https://g2g.dreisbach.us/api/v1/me', myInit);

        console.log(request);

        fetch(request)
        .then((response) => console.log(response))
        .then((response) => response.json())
        .then((json) => {
            console.log('JSON');
            console.log(json);
        })
        .catch((error) => {
            console.log('in the error');
            console.log(error)
        })
    }

    static route = {
        navigationBar: {
            title: `Check Out/In Containers`
        }
    }



    _add = () => this.setState({count: this.state.count + 1})
    _subtract = () => {
        if (this.state.count > 1) {
            this.setState({count: this.state.count - 1})
        }
    }

    handlePressIN

    render() {
        const code = this.props.appStore.locationCode;
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
                fontSize: 20,
                fontWeight: '800'
            }
        });
        // api/v1/me
        return (
            <View>
                <Text>{code}</Text>
                <View style={{marginBottom: 10}}><Text style={{textAlign: 'center'}}>How many boxes?</Text></View>
                <View style={styles.centeredRow}>
                    <Button
                        onPress={this._add} >
                        <Text style={styles.icon}>+</Text>
                    </ Button>
                    <Text style={{marginLeft: 10, marginRight: 10, fontSize: 20}}>{this.state.count}</Text>
                    <Button
                        onPress={this._subtract} >
                        <Text style={styles.icon}>-</Text>
                    </ Button>
                </View>
                <View>
                    <Text style={styles.headerText}>What Subscription?</Text>
                    <Text>{this.state.subscriptionId}</Text>
                    <Picker
                        selectedValue={this.state.subscriptionId}
                        onValueChange={(itemValue, itemIndex) => this.setState({subscriptionId: itemValue})}
                    >
                        <Picker.Item label="Hey" value="hey" />
                        <Picker.Item label="Arnold!" value="arnold"/>
                    </ Picker>
                </View>
            </View>
        )
    }
}

export default SubmissionScreen;
