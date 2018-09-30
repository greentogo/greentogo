import React from 'react';
import {
    View,
    ScrollView,
} from 'react-native';
import { inject, observer } from "mobx-react";
import styles from "../styles";
import {
    List,
} from "native-base";
import ListMenuItem from './subcomponents/ListMenuItem';
import SubscriptionBanner from './subcomponents/SubscriptionBanner';
import G2GTitleImage from "./subcomponents/G2GTitleImage";
import G2GVideo from "./subcomponents/G2GVideo";


@inject("appStore")
@observer
class HomeScreen extends React.Component {
    constructor(props) {
        super(props)
        this.props.appStore.getUserData()
        this.props.appStore.getResturantData()
    }

    static navigationOptions = {
        headerTitle: <G2GTitleImage />,
    };

    goToMap = () => {
        this.props.navigation.navigate('map');
    }

    goToScanQRCode = () => {
        this.props.navigation.navigate('scanQRCode');
    }

    goToReturn = () => {
        this.props.navigation.navigate('returnBox');
    }

    goToAccount = () => {
        this.props.navigation.navigate('account');
    }

    logOut = () => {
        this.props.appStore.clearAuthToken()
    }

    render() {
        return (
            <View style={{ ...styles.container, paddingBottom: 50 }}>
                <ScrollView>
                    <G2GVideo />
                    <List>
                        <ListMenuItem
                            icon="log-out"
                            text="Check In/Out container"
                            onPress={this.goToScanQRCode}
                        />
                        <ListMenuItem
                            icon="map"
                            text="Map of restaurants"
                            onPress={this.goToMap}
                        />
                        <ListMenuItem
                            icon="person"
                            text="Your account"
                            onPress={this.goToAccount}
                        />
                        <ListMenuItem
                            icon="lock"
                            text="Log out"
                            onPress={this.logOut}
                        />
                    </List>
                </ScrollView>
                <View style={styles.bottomFixed}>
                    <SubscriptionBanner />
                </View>
            </View>
        )
    }
}

export default HomeScreen;
