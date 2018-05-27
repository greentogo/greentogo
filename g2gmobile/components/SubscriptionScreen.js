import React from 'react';
import {
    Image,
    View,
    Text
} from 'react-native';
import styles from "../styles";

class Subscription extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            subscriptions: [
                { boxesAvailable: 2, totalBoxes: 4, expDate: '12/12/17' },
                { boxesAvailable: 1, totalBoxes: 2, expDate: '2/5/19' }
            ],
            availableBoxes: 0,
            totalBoxes: 0,
            expDate: null
        }
    }

    componentDidMount() {
        this.setState({ availableBoxes: this.sumBoxes(this.state.subscriptions, 'boxesAvailable') });
        this.setState({ totalBoxes: this.sumBoxes(this.state.subscriptions, 'totalBoxes') })
    }

    sumBoxes = (subscriptions, type) => {
        return subscriptions.reduce((sum, subscription) => {
            return sum + subscription[type];
        }, 0);
    }

    render() {
        return (
            <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', flexDirection: 'row' }}>
                <Text style={{ color: styles.primaryColor, fontWeight: 'bold', fontSize: 20 }}>You have {this.state.availableBoxes} of {this.state.totalBoxes} boxes available</Text>
            </View>
        );
    }
}

export default Subscription;

