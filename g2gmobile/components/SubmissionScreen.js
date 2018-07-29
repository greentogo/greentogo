import React from 'react';
import axios from '../apiClient';
import { Icon, Button } from 'native-base';
import { inject, observer } from 'mobx-react';
import { NavigationActions } from '@expo/ex-navigation';
import {
    StyleSheet,
    Text,
    View,
    Picker,
    WebView,
    Linking,
    TouchableOpacity,
    ActivityIndicator,
    ScrollView
} from 'react-native';
import styles from "../styles";

@inject('appStore')
@observer
class SubmissionScreen extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            error: false,
            subscriptions: [],
            subscriptionId: false,
            selectedSubscription: false,
            boxCount: 1,
            locationData: this.props.navigation.state.params.locationData,
        }
    }

    static navigationOptions = ({ navigation }) => {
        return {
            title: 'Check In/Out',
            headerLeft: (
                <TouchableOpacity><Text style={styles.popToTopStyle} onPress={() => navigation.popToTop()}>X</Text></TouchableOpacity>
            ),
        }
    };

    componentWillMount() {
        let authToken = this.props.appStore.authToken;
        axios.get('me/', {
            headers: {
                'Authorization': `Token ${authToken}`
            }
        }).then((response) => {
            if (response.data.data.email) this.props.appStore.email = response.data.data.email;
            this.setState({ subscriptions: response.data.data.subscriptions, loading: false }, () => {
                if (this.state.subscriptions.length > 0) {
                    this.subscriptionChange(subscriptions[0].id);
                }
            })
        }).catch((error) => {
            if (err.response.status === 401) {
                this.props.appStore.clearAuthToken();
            };
            console.log('In the error! SUBMISSIONSCREEN.JS');
            console.log(error);
        })
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
        let error;
        this.state.subscriptions.forEach((subscription) => {
            if (subscription.id === subscriptionId) {
                selectedSubscription = subscription;
            }
        });
        switch (this.state.locationData.service) {
            case 'IN':
                if (selectedSubscription.available_boxes >= selectedSubscription.max_boxes) {
                    boxCount = 0;
                    error = "You have checked in all of your boxes for this subscription";
                } else {
                    boxCount = 1;
                    error = false;
                }
                break;
            case 'OUT':
                if (selectedSubscription.available_boxes === 0) {
                    boxCount = 0;
                    error = "You have checked out all of your boxes for this subscription";
                } else {
                    boxCount = 1;
                    error = false;
                }
                break;
        }
        if (boxCount === undefined) { boxCount = 1 };
        this.setState({
            error,
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
            this.props.navigation.navigate('containerSuccessScreen', { boxCount: this.state.boxCount, locationData: this.state.locationData });
        }).catch((error) => {
            console.log(error.response);
        });
    }

    render() {
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
                this.state.loading ? (
                    <View style={styles.loadingContainer}>
                        <ActivityIndicator size="large" color="#0000ff" />
                    </View>
                ) : (
                        this.state.subscriptions.length > 0 ? (
                            <ScrollView style={styles.container}>
                                {/* TODO: Add this back in once the tag/ endpoint accepts # of boxes */}
                                <View>
                                    <Text style={styles.boldCenteredText}>{this.state.locationData.name}</Text>
                                    <Text style={styles.boldCenteredText}>How many boxes to do you want to check {this.state.locationData.service.toLowerCase()}?</Text>
                                </View>
                                <View style={styles.centeredRow}>
                                    <Button
                                        success
                                        onPress={this.subtract} >
                                        <Text style={styles.submissionAddSubIcon}>-</Text>
                                    </Button>
                                    <Text style={styles.submissionBoxCountStyle}>{this.state.boxCount}</Text>
                                    <Button
                                        success
                                        onPress={this.add} >
                                        <Text style={styles.submissionAddSubIcon}>+</Text>
                                    </Button>
                                </View>
                                <View style={styles.pickerStyle}>
                                    <Picker
                                        mode="dialog"
                                        selectedValue={this.state.subscriptionId}
                                        onValueChange={(itemValue, itemIndex) => this.subscriptionChange(itemValue)}
                                    >
                                        {
                                            this.state.subscriptions.map((subscription, index) => {
                                                return <Picker.Item
                                                    key={index}
                                                    label={`${subscription.name} (${subscription.available_boxes}/${subscription.max_boxes})`}
                                                    value={subscription.id}
                                                />
                                            })
                                        }
                                    </Picker>
                                </View>
                                <View>
                                    {this.state.error &&
                                        <View style={styles.centeredRow}>
                                            <Text style={styles.headerText}>{this.state.error}</Text>
                                        </View>
                                    }
                                    <View style={styles.centeredRow}>
                                        {this.state.error ? (
                                            <TouchableOpacity style={styles.submissionSubmitButtonBlocked}>
                                                <Text style={styles.submissionSubmitTextStyle}>Cannot Check {this.state.locationData.service.toLowerCase()}</Text>
                                            </TouchableOpacity>
                                        ) : (
                                                <TouchableOpacity style={styles.submissionSubmitButton} onPress={this.submit}>
                                                    <Text style={styles.submissionSubmitTextStyle}>Check {this.state.locationData.service.toLowerCase()}</Text>
                                                </TouchableOpacity>
                                            )}
                                    </View>
                                </View>
                            </ScrollView>
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
            )

        }
    }
}

export default SubmissionScreen;
