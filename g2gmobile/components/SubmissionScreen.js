import React from 'react';
import axios from '../apiClient';
import { Icon, Button } from 'native-base';
import { inject, observer } from 'mobx-react';
import {
    StyleSheet,
    Text,
    View,
    Picker,
    WebView,
    Linking
} from 'react-native';
import styles from "../styles";

@inject('appStore')
@observer
class SubmissionScreen extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            subscriptions: [],
            subscriptionId: false,
            selectedSubscription: false,
            boxCount: 1,
            locationData: this.props.route.params.locationData,
        }
    }

    componentWillMount() {
        let authToken = this.props.appStore.authToken;
        axios.get('me/', {
            headers: {
                'Authorization': `Token ${authToken}`
            }
        }).then((response) => {
            if (response.data.data.email) this.props.appStore.email = response.data.data.email;
            console.log(response.data.data)
            this.setState({ subscriptions: response.data.data.subscriptions }, () => {
                if (this.state.subscriptions.length > 0) {
                    this.subscriptionChange(subscriptions[0].id);
                }
            })
            console.log(response.data.data)
        }).catch((error) => {
            if (err.response.status === 401) {
                this.props.appStore.clearAuthToken();
            };
            console.log('In the error! SUBMISSIONSCREEN.JS');
            console.log(error);
        })
    }

    componentDidMount() {
        console.log("MOUNTED")
        console.log(this.state.locationData);
    }

    static route = {
        navigationBar: {
            title: `Check In/Out`
        }
    }

    add = () => {
        let returnableBoxes = this.state.selectedSubscription.max_boxes - this.state.selectedSubscription.available_boxes;
        switch (this.state.locationData.service) {
            case 'IN':
                if (this.state.boxCount === returnableBoxes) {
                    return;
                } else {
                    this.setState({ boxCount: this.state.boxCount + 1 })
                }
                break;
            case 'OUT':
                if (this.state.boxCount === this.state.selectedSubscription.available_boxes) {
                    return;
                } else {
                    this.setState({ boxCount: this.state.boxCount + 1 })
                }
                break;
        }
    }

    subtract = () => {
        if (this.state.boxCount > 1) {
            this.setState({ boxCount: this.state.boxCount - 1 })
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
        switch (this.state.locationData.service) {
            case 'IN':
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
        if (boxCount === undefined) { boxCount = 1 };
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
            location: this.state.locationData.code,
            action: this.state.locationData.service,
            number_of_boxes: this.state.boxCount
        }, config).then((response) => {
            // console.log(response)
            // TODO: Route to a success screen
            this.props.navigator.push('containerSuccessScreen', { boxCount: this.state.boxCount, locationData: this.state.locationData });
        }).catch((error) => {
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
                color: 'white',
                textAlign: 'center',
                width: 50,
                // height: 50,
                alignSelf: 'center'
            },
            headerText: {
                fontSize: 18,
                fontWeight: '800',
                textAlign: 'center'
            },
            noSubText: {

            }
        });
        if (this.state.redirectToWeb) {
            let uri = this.state.redirectToWeb;
            return (
                <WebView
                    ref={(ref) => { this.webview = ref; }}
                    source={{ uri }}
                    onNavigationStateChange={(event) => {
                        this.setState({ redirectToWeb: false })
                        Linking.openURL(event.url);
                        this.webview.stopLoading();
                    }}
                />
            );
        } else {
            return (
                subscriptions.length > 10 ? (
                    <View>
                        {/* TODO: Add this back in once the tag/ endpoint accepts # of boxes */}
                        <View style={{ marginBottom: 10 }}><Text style={styles.headerText}>{this.state.locationData.name}</Text></View>
                        <View style={{ marginBottom: 10 }}><Text style={styles.headerText}>How many boxes to check {this.state.locationData.service.toLowerCase()}?</Text></View>
                        <View style={styles.centeredRow}>
                            <Button
                                success
                                onPress={this.subtract} >
                                <Text style={styles.icon}>-</Text>
                            </Button>
                            <Text style={{ marginLeft: 10, marginRight: 10, fontSize: 20, alignSelf: 'center' }}>{this.state.boxCount}</Text>
                            <Button
                                success
                                onPress={this.add} >
                                <Text style={styles.icon}>+</Text>
                            </Button>
                        </View>
                        <View>
                            <Text style={styles.headerText}>Check {this.state.locationData.service.toLowerCase()} {this.state.boxCount === 1 ? `${this.state.boxCount} box` : `${this.state.boxCount} boxes`} on which subscription?</Text>
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
                                    onPress={this.submit}>
                                    <Text style={{ color: '#FFFFFF' }}>Submit</Text>
                                </Button>
                            </View>
                        </View>
                    </View>
                ) : (
                        <View>
                            <Button style={{ backgroundColor: styles.primaryCream }} light full onPress={() => { this.setState({ redirectToWeb: 'https://app.durhamgreentogo.com/subscriptions/new/' }) }}>
                                <Text style={{ backgroundColor: styles.primaryCream, color: styles.primaryColor, fontWeight: 'bold', fontSize: 20 }}>
                                    Your account has no subscriptions. Tap here to add a subscription.
                            </Text>
                            </Button>
                        </View>
                    )
            )
        }
    }
}

export default SubmissionScreen;
