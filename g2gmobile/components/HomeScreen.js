import React from 'react';
import {
  StyleSheet,
  View,
  TouchableHighlight
} from 'react-native';
import {inject, observer} from "mobx-react";
import styles from "../styles";
import HomeScreenGreenToGoImage from "./HomeScreenGreenToGoImage";
import {
    Header,
    Body,
    Content,
    List,
    ListItem,
    Text,
    Icon,
    Left
} from "native-base";

class ListMenuItem extends React.Component {
    render() {
        const onPress = this.props.onPress || function () { };
        return (
            <TouchableHighlight>
                <ListItem style={{flex: 1, height: 100, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: styles.primaryColor, backgroundColor: styles.primaryCream }} icon onPress={onPress}>
                    <Left>
                        <Icon style={{color: styles.primaryColor}} name={this.props.icon}/>
                    </Left>
                    <Body style={{borderBottomWidth: 0 }}>
                        <Text>{this.props.text}</Text>
                    </Body>
                </ListItem>
            </TouchableHighlight>
        );
    }
}

@inject("appStore")
@observer
class HomeScreen extends React.Component {
    static route = {
        navigationBar: {
            renderTitle: (route, props) => <HomeScreenGreenToGoImage />, 
            backgroundColor: '#628e86'
        }
    }

    goToMap = () => {
        this.props.navigator.push('map');
    }

    goToCheckOut = () => {
        this.props.navigator.push('checkOutBox');
    }

    goToReturn = () => {
        this.props.navigator.push('returnBox');
    }

    logOut = () => {
        this.props.appStore.clearAuthToken()
    }

    render() {
        return (
            <Content style={{flex: 1, backgroundColor: styles.primaryCream}}>
                <List>
                    <ListMenuItem
                        icon="log-out"
                        text="Checkout container"
                        onPress={this.goToCheckOut}
                    />
                    <ListMenuItem
                        icon="log-in"
                        text="Return container"
                        onPress={this.goToReturn}
                    />
                    <ListMenuItem
                        icon="map"
                        text="Map of participating restaurants"
                        onPress={this.goToMap}
                    />
                    <ListMenuItem
                        icon="person" 
                        text="Your account"
                    />
                    <ListMenuItem
                        icon="unlock"
                        text="Log out"
                        onPress={this.logOut}
                    />
                </List>
            </Content>
        )
    }
}

export default HomeScreen;
