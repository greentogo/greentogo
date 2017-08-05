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
        let authToken = this.props.appStore.authToken;
        axios.get('me/', {
            headers: {
                'Authorization': `Token ${authToken}`
            }
        })
        .then((response) => {
            subscriptions = response.data.data.subscriptions;
            if (subscriptions.length > 0) {
                this.subscriptionChange(subscriptions[0].id);
            }
        })
        .catch((error) => {
            console.log('In the error!');
            console.log(error);
        })
    }

    static route = {
        navigationBar: {
            title: `Check In/Out`
        }
    }

    add = () => {
        let returnableBoxes = this.state.selectedSubscription.max_boxes - this.state.selectedSubscription.available_boxes;
        switch(this.props.appStore.action) {
            case 'IN':
                if (this.state.boxCount === returnableBoxes) {
                    return;
                } else {
                    this.setState({boxCount: this.state.boxCount + 1})
                }
                break;
            case 'OUT':
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
            case 'IN':
                console.log(selectedSubscription);
                if (selectedSubscription.available_boxes === selectedSubscription.max_boxes) {
                    boxCount = 0;
                } else {
                    boxCount = 1;
                }
                break;
            case 'OUT':
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
        let config = {
            headers: {
                'Authorization': `Token ${this.props.appStore.authToken}`
            }
        }
        axios.post('tag/', {
            subscription: this.state.subscriptionId,
            location: this.props.appStore.locationCode,
            action: this.props.appStore.action
        }, config)
        .then((response) => {
            // TODO: Route to a success screen
            if(this.props.appStore.action === 'OUT') {
              this.props.navigator.push('checkOutSuccess', {boxCount: this.state.boxCount});
            } else {
              this.props.navigator.push('returnSuccess', {boxCount: this.state.boxCount});
            }
        })
        .catch((error) => {
            console.log(error.response);
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
            subscriptions.length > 0 ? (
                <View>
                     {/* TODO: Add this back in once the tag/ endpoint accepts # of boxes
                     <View style={{marginBottom: 10}}><Text style={styles.headerText}>How many boxes to {this.props.appStore.action}?</Text></View>
                    <View style={styles.centeredRow}>
                        <Button
                            success
                            onPress={this.add} >
                            <Text style={styles.icon}>+</Text>
                        </ Button>
                        <Text style={{marginLeft: 10, marginRight: 10, fontSize: 20}}>{this.state.boxCount}</Text>
                        <Button
                            success
                            onPress={this.subtract} >
                            <Text style={styles.icon}>-</Text>
                        </ Button>
                    </View> */}
                    <View>
                        <Text style={styles.headerText}>Check {this.props.appStore.action.toLowerCase()} 1 box on which subscription?</Text>
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
            ) : (
                <View><Text>Your account has no subscriptions</Text></View>
            )
        )
    }
}

export default SubmissionScreen;
