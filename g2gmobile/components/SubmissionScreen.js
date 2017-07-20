import React from 'react';
import axios from '../apiClient';
import {
    StyleSheet,
    Text,
    View,
    Picker
} from 'react-native';

import { Icon, Button } from 'native-base';

import { inject, observer } from 'mobx-react';

const apiEndpoint = '/api/v1';
let subscriptions = [];

@inject('appStore')
@observer
class SubmissionScreen extends React.Component {
   constructor(props) {
        super(props)
        this.state = {
            boxCount: 1
        }
    }

    componentWillMount() {
        // mock getting the subscriptions
        const response = {
            status: "success",
            data: {
                name: "Erin Brown",
                email: "emberbrown@gmail.com",
                subscriptions: [
                    {
                        id: 11,
                        name: "1 Box",
                        available_boxes: 1,
                        max_boxes: 1
                    },
                    {
                        id: 12,
                        name: "3 Boxes",
                        available_boxes: 3,
                        max_boxes: 3
                    }
                ]
            }
        };
        const promise = new Promise((resolve, reject) => {
            resolve(response);
        });

        promise.then((response) => {
            subscriptions = response.data.subscriptions;
            // @TODO handle empty array?
            this.subscriptionChange(subscriptions[0].id);
        });

        // let authToken = this.props.appStore.authToken;
        // axios.get('me', {
        //     headers: {
        //         'Authorization': `Token ${authToken}`
        //     }
        // })
        // .then((response) => console.log(response))
        // .then((response) => response.json())
        // .then((json) => {
        //     console.log(json);
        // })
        // .catch((error) => {
        //     console.log('In the error!');
        //     console.log(error);
        //     console.log(error.response);
        //     console.log(error.response.status);
        // })
    }

    static route = {
        navigationBar: {
            title: `Check In/Out`
        }
    }

    add = () => {
        let returnableBoxes = this.state.selectedSubscription.max_boxes - this.state.selectedSubscription.available_boxes;
        switch(this.props.appStore.action) {
            case 'return':
                if (this.state.boxCount === returnableBoxes) {
                    return;
                } else {
                    this.setState({boxCount: this.state.boxCount + 1})
                }
                break;
            case 'checkOut':
                if (this.state.boxCount === this.state.selectedSubscription.available_boxes) {
                    return;
                } else {
                    this.setState({boxCount: this.state.boxCount + 1})
                }
                break;
        }
    }

    subtract = () => {
        if (this.state.boxCount > 1) {
            this.setState({boxCount: this.state.boxCount - 1})
        }
    }

    subscriptionChange = (subscriptionId) => {
        let boxCount;
        let selectedSubscription;
        // find the selected subscription
        subscriptions.forEach((subscription) => {
            if (subscription.id === subscriptionId) {
                selectedSubscription = subscription;
            }
        });
        switch(this.props.appStore.action) {
            case 'return':
                console.log(selectedSubscription);
                if (selectedSubscription.available_boxes === selectedSubscription.max_boxes) {
                    boxCount = 0;
                } else {
                    boxCount = 1;
                }
                break;
            case 'checkOut':
                if (selectedSubscription.available_boxes === 0) {
                    boxCount = 0;
                } else {
                    boxCount = 1;
                }
                break;
        }

        this.setState({
            subscriptionId,
            boxCount,
            selectedSubscription
        });
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

        return (
            <View>
                <Text>{this.state.subscriptionId}</Text>
                <View style={{marginBottom: 10}}><Text style={styles.headerText}>How many boxes to {this.props.appStore.action}?</Text></View>
                <View style={styles.centeredRow}>
                    <Button
                        success
                        onPress={this.add} >
                        <Text style={styles.icon}>+</Text>
                    </Button>
                    <Text style={{marginLeft: 10, marginRight: 10, fontSize: 20}}>{this.state.boxCount}</Text>
                    <Button
                        success
                        onPress={this.subtract} >
                        <Text style={styles.icon}>-</Text>
                    </Button>
                </View>
                <View>
                    <Text style={styles.headerText}>Which subscription?</Text>
                    <Picker
                        mode="dropdown"
                        selectedValue={this.state.subscriptionId}
                        onValueChange={(itemValue, itemIndex) => this.subscriptionChange(itemValue)}
                    >
                        {
                            subscriptions.map((subscription, index) => {
                                return <Picker.Item
                                            key={index}
                                            label={`${subscription.name} (${subscription.available_boxes}/${subscription.max_boxes})`}
                                            value={subscription.id}
                                        />
                            })
                        }
                    </Picker>
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
