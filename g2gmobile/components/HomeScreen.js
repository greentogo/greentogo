import React from 'react';
import {
    StyleSheet,
    Text,
    View,
} from 'react-native';
import {observer} from "mobx-react";
import styles from "../styles";

@observer
class HomeScreen extends React.Component {
    static route = {
        navigationBar: {
            title: 'Home',
        }
    }

    render() {
        return (
            <View style={styles.container}>
                <Text>Open up main.js to start working on your app!</Text>
            </View>
        )
    }
}

export default HomeScreen;
